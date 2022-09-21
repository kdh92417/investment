from django.db import models


class Account(models.Model):
    """계좌 모델"""

    account_number = models.CharField("계좌번호", max_length=30)
    account_name = models.CharField("계좌명", max_length=45, null=False)
    total_assets = models.DecimalField(
        "계좌 총 자산", max_digits=17, decimal_places=2, default=0, null=True, blank=True
    )

    class Meta:
        db_table = "accounts"

    def __str__(self):
        return self.account_name


class User(models.Model):
    """유저 모델"""

    account = models.OneToOneField(
        Account,
        on_delete=models.SET_DEFAULT,
        related_name="user",
        default="0",
    )
    name = models.CharField(max_length=45, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.name


class Investment(models.Model):
    """투자 모델"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="investment"
    )
    brokerage = models.CharField("증권사", max_length=45)
    principal = models.DecimalField(
        "투자 원금", max_digits=17, decimal_places=2, null=True, blank=True
    )

    class Meta:
        db_table = "investments"


class Holding(models.Model):
    """종목 모델"""

    name = models.CharField("종목명", max_length=45, unique=True, null=False, blank=False)
    isin = models.CharField("ISIN", max_length=20, unique=True, null=False, blank=False)
    asset_group = models.CharField("자산그룹", max_length=45)

    class Meta:
        db_table = "holdings"

    def __str__(self):
        return self.name


class UserHolding(models.Model):
    """유저 보유종목 모델"""

    holding = models.ForeignKey(Holding, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="user_holdings"
    )
    quantity = models.IntegerField("보유 종목 수량", default=1)
    current_price = models.FloatField("현재가", null=True, blank=True)

    class Meta:
        db_table = "users_holdings"


class DepositLog(models.Model):
    """입금정보 모델"""

    user_name = models.CharField(max_length=45, null=False, blank=False)
    account_number = models.CharField("계좌번호", max_length=30)
    transfer_amount = models.DecimalField(
        max_digits=17, decimal_places=2, null=False, blank=False
    )
    exp = models.DateTimeField()
    signature = models.CharField(max_length=300)
    status = models.BooleanField(default=False)

    class Meta:
        db_table = "deposit_logs"
