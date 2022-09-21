import jwt
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import User, Investment, UserHolding, DepositLog, Account
from backend.settings.base import SECRET_KEY, SIGNATURE_ALGORITHM


class InvestmentViewSerializer(serializers.ModelSerializer):
    """투자화면 Serializer"""

    account_number = serializers.ReadOnlyField(source="account.account_number")
    account_name = serializers.ReadOnlyField(source="account.account_name")
    account_total_assets = serializers.ReadOnlyField(source="account.total_assets")
    brokerage = serializers.ReadOnlyField(source="investment.brokerage")

    class Meta:
        model = User
        fields = [
            "name",
            "account_number",
            "account_name",
            "brokerage",
            "account_total_assets",
            "investment",
        ]


class InvestmentDetailViewSerializer(serializers.ModelSerializer):
    """투자상세화면 Serializer"""

    account_number = serializers.ReadOnlyField(source="user.account.account_number")
    account_name = serializers.ReadOnlyField(source="user.account.account_name")
    account_total_assets = serializers.ReadOnlyField(source="user.account.total_assets")
    total_proceeds = serializers.SerializerMethodField()
    proceeds_rate = serializers.SerializerMethodField()

    class Meta:
        model = Investment
        fields = [
            "account_name",
            "brokerage",
            "account_number",
            "account_total_assets",
            "principal",
            "total_proceeds",
            "proceeds_rate",
            "user",
        ]

    def get_total_proceeds(self, obj):
        return obj.user.account.total_assets - obj.principal

    def get_proceeds_rate(self, obj):
        return (obj.user.account.total_assets - obj.principal) / (obj.principal * 100)


class UserHoldingViewSerializer(serializers.ModelSerializer):
    """보유종목 화면 Serializer"""

    holding_name = serializers.ReadOnlyField(source="holding.name")
    asset_group = serializers.ReadOnlyField(source="holding.asset_group")
    isin = serializers.ReadOnlyField(source="holding.isin")
    appraisal_amount = serializers.SerializerMethodField()

    class Meta:
        model = UserHolding
        fields = ["holding_name", "asset_group", "isin", "appraisal_amount"]

    #
    def get_appraisal_amount(self, obj):
        return obj.quantity * obj.current_price


class DepositLogSerializer(serializers.ModelSerializer):
    """입금거래 정보 Serializer"""

    transfer_identifier = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = DepositLog
        fields = [
            "user_name",
            "account_number",
            "exp",
            "transfer_amount",
            "signature",
            "transfer_identifier",
        ]
        extra_kwargs = {
            "exp": {"write_only": True},
            "user_name": {"write_only": True},
            "account_number": {"write_only": True},
            "transfer_amount": {"write_only": True},
            "signature": {"write_only": True},
        }


class AssetSerializer(serializers.ModelSerializer):
    """자산 Serializer"""

    transfer_identifier = serializers.IntegerField(source="id", write_only=True)

    class Meta:
        model = DepositLog
        fields = ["signature", "transfer_identifier", "status"]
        extra_kwargs = {
            "signature": {"write_only": True},
            "status": {"read_only": True},
        }

    @transaction.atomic
    def update(self, instance, validated_data):
        signature = validated_data.pop("signature")

        try:
            # signature 디코드
            encoded_data = jwt.decode(
                signature, SECRET_KEY, algorithms=[SIGNATURE_ALGORITHM]
            )

            # 클레임에 담긴 정보들
            account_number = encoded_data.get("account_number", None)
            user_name = encoded_data.get("user_name", None)
            transfer_amount = encoded_data.get("transfer_amount", None)

            # phase1 API에서 등록정보들이 클레임에담긴 정보와 일치하는지 확인
            if (
                account_number == instance.account_number
                and user_name == instance.user_name
                and transfer_amount == instance.transfer_amount
            ):
                instance.status = True
                instance.save()

                # 트랜잭션이 몰릴경우 동시성 문제를 해결하기 위해 select_for_update 사용
                # nowait = True : 해당 row 락이 잡혀있으면 풀릴때까지 기다림
                account = Account.objects.select_for_update(nowait=False).get(
                    account_number=account_number
                )

                # 유효한 정보면 자산업데이트
                account.total_assets += transfer_amount
                account.save()

                return instance

        except Exception as e:
            transaction.set_rollback(rollback=True)
            raise ValidationError(str(e))
