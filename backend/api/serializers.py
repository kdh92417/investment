from rest_framework import serializers

from api.models import User, Investment, UserHolding


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

    def get_appraisal_amount(self, obj):
        return obj.quantity * obj.current_price
