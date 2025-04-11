from django.contrib import admin
from .models import Transaction, Expense, Income, Budget, BudgetItem, FinancialReport


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'transaction_type', 'description', 'farm', 'created_by')
    list_filter = ('transaction_type', 'date', 'farm')
    search_fields = ('description', 'farm__name')
    date_hierarchy = 'date'


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'category', 'description', 'farm', 'created_by')
    list_filter = ('category', 'date', 'farm')
    search_fields = ('description', 'farm__name')
    date_hierarchy = 'date'


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'source', 'description', 'farm', 'created_by')
    list_filter = ('source', 'date', 'farm')
    search_fields = ('description', 'farm__name')
    date_hierarchy = 'date'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'total_amount', 'farm', 'created_by')
    list_filter = ('start_date', 'end_date', 'farm')
    search_fields = ('name', 'farm__name')


class BudgetItemInline(admin.TabularInline):
    model = BudgetItem
    extra = 1


@admin.register(BudgetItem)
class BudgetItemAdmin(admin.ModelAdmin):
    list_display = ('budget', 'name', 'amount', 'category')
    list_filter = ('category', 'budget')
    search_fields = ('name', 'budget__name')


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'start_date', 'end_date', 'farm', 'created_by')
    list_filter = ('report_type', 'start_date', 'end_date', 'farm')
    search_fields = ('title', 'farm__name')
    date_hierarchy = 'created_at'
