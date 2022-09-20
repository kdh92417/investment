import jwt

from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import User, Investment, UserHolding, DepositLog
from api.serializers import (
    InvestmentViewSerializer,
    InvestmentDetailViewSerializer,
    UserHoldingViewSerializer,
    DepositLogSerializer,
    AssetSerializer,
)
from backend.settings.base import SECRET_KEY, SIGNATURE_ALGORITHM


class InvestmentView(APIView):
    """투자화면 상세 API"""

    def get(self, request, pk):
        queryset = User.objects.get(id=pk)
        serializer = InvestmentViewSerializer(queryset)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class InvestmentDetailView(APIView):
    """투자상세 화면 API"""

    def get(self, request, pk):
        queryset = Investment.objects.get(id=pk)
        serializer = InvestmentDetailViewSerializer(queryset)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserHoldingView(APIView):
    """보유종목 화면 API"""

    def get(self, request, pk):
        queryset = UserHolding.objects.filter(user=User.objects.get(id=pk))
        serializer = UserHoldingViewSerializer(queryset, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class InvestmentDeposit(APIView):
    """입금 거래 API"""

    def post(self, request):
        payload = {**request.data, "exp": datetime.utcnow() + timedelta(days=3)}
        signature = jwt.encode(
            payload, SECRET_KEY, algorithm=SIGNATURE_ALGORITHM
        )  # jwt를 이용하여 해싱
        serializer = DepositLogSerializer(data={**payload, "signature": signature})

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def put(self, request):
        deposit_log = DepositLog.objects.get(id=request.data.get("transfer_identifier"))
        serializer = AssetSerializer(deposit_log, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)
