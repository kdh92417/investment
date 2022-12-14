from django.urls import path

from api import views

urlpatterns = [
    path("investments/<int:pk>", views.InvestmentView.as_view(), name="investment"),
    path(
        "investments/detail/<int:pk>",
        views.InvestmentDetailView.as_view(),
        name="investment-detail",
    ),
    path(
        "users/<int:pk>/holdings",
        views.UserHoldingView.as_view(),
        name="user-holdings",
    ),
    path(
        "investments/deposit",
        views.InvestmentDeposit.as_view(),
        name="investment-deposit",
    ),
]
