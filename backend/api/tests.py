from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from api.models import Account, User, Investment, Holding, UserHolding


class InvestmentAPITest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        account1 = Account.objects.create(
            account_number="1234", account_name="계좌1", total_assets=0
        )
        account2 = Account.objects.create(
            account_number="12345", account_name="계좌2", total_assets=0
        )
        account3 = Account.objects.create(
            account_number="12346", account_name="계좌3", total_assets=0
        )

        user1 = User.objects.create(account=account1, user_name="홍길동")
        user2 = User.objects.create(account=account2, user_name="홍길동2")
        user3 = User.objects.create(account=account3, user_name="홍길동3")

        Investment.objects.bulk_create(
            [
                Investment(user=user1, brokerage="국민", principal=1000000),
                Investment(user=user2, brokerage="K뱅크", principal=1500000),
                Investment(user=user3, brokerage="하나", principal=2000000),
            ]
        )

        holding1 = Holding.objects.create(name="삼성", isin="K11111", asset_group="한국주식")
        holding2 = Holding.objects.create(name="LG", isin="K11112", asset_group="한국주식")
        holding3 = Holding.objects.create(name="애플", isin="G11112", asset_group="미국주식")

        UserHolding.objects.bulk_create(
            [
                UserHolding(
                    holding=holding1,
                    user=user1,
                    quantity=10,
                    current_price=1000,
                ),
                UserHolding(
                    holding=holding2,
                    user=user1,
                    quantity=20,
                    current_price=2000,
                ),
                UserHolding(
                    holding=holding3,
                    user=user1,
                    quantity=3,
                    current_price=3000,
                ),
            ]
        )

    def tearDown(self):
        UserHolding.objects.all().delete()
        Holding.objects.all().delete()
        Investment.objects.all().delete()
        User.objects.all().delete()
        Account.objects.all().delete()

    def test_get_investment_data(self):
        """투자화면 API Success Case Test"""
        response = self.client.get(reverse("investment", args=[1]))
        expected_data = {
            "user_name": "홍길동",
            "account_number": "1234",
            "brokerage": "국민",
            "account_total_assets": 0.0,
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_data)
