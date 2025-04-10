from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FinancialRecordViewSet, ExpenseViewSet, IncomeViewSet,
    BudgetViewSet, BudgetCategoryViewSet, FinancialSummaryViewSet,
    LoanRecordViewSet, PaymentRecordViewSet
)

router = DefaultRouter()
router.register(r'records', FinancialRecordViewSet, basename='financial-record')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'income', IncomeViewSet, basename='income')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'budget-categories', BudgetCategoryViewSet, basename='budget-category')
router.register(r'summaries', FinancialSummaryViewSet, basename='financial-summary')
router.register(r'loans', LoanRecordViewSet, basename='loan')
router.register(r'payments', PaymentRecordViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]