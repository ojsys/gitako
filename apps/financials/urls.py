from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TransactionViewSet, ExpenseViewSet, IncomeViewSet,
    BudgetViewSet, BudgetItemViewSet, FinancialReportViewSet,
    financial_dashboard, transaction_list, expense_list, income_list,
    budget_list, budget_detail, create_transaction, edit_transaction,
    delete_transaction
)

# API router
router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'income', IncomeViewSet, basename='income')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'budget-items', BudgetItemViewSet, basename='budget-item')
router.register(r'reports', FinancialReportViewSet, basename='financial-report')

app_name = 'financials'

urlpatterns = [
    # Dashboard and overview
    path('dashboard/', financial_dashboard, name='dashboard'),
    
    # Transaction management
    path('transactions/', transaction_list, name='transaction_list'),
    path('transactions/create/', create_transaction, name='create_transaction'),
    path('transactions/<int:pk>/edit/', edit_transaction, name='edit_transaction'),
    path('transactions/<int:pk>/delete/', delete_transaction, name='delete_transaction'),
    
    # Expense management
    path('expenses/', expense_list, name='expense_list'),
    
    # Income management
    path('income/', income_list, name='income_list'),
    
    # Budget management
    path('budgets/', budget_list, name='budget_list'),
    path('budgets/<int:pk>/', budget_detail, name='budget_detail'),
    
    # API endpoints
    path('api/', include(router.urls)),
]