from rest_framework import serializers
from .models import (
    FinancialRecord, Expense, Income, Budget, BudgetCategory, 
    FinancialSummary, LoanRecord, PaymentRecord
)

class FinancialRecordSerializer(serializers.ModelSerializer):
    """Base serializer for financial records"""
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    record_type_display = serializers.CharField(source='get_record_type_display', read_only=True)
    
    class Meta:
        model = FinancialRecord
        fields = [
            'id', 'farm', 'farm_name', 'record_type', 'record_type_display',
            'amount', 'date', 'description', 'category', 'subcategory',
            'reference_number', 'payment_method', 'is_verified',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']
    
    def create(self, validated_data):
        # Set the created_by to the current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for expense records"""
    financial_record = FinancialRecordSerializer()
    
    class Meta:
        model = Expense
        fields = [
            'id', 'financial_record', 'vendor', 'invoice_number',
            'tax_amount', 'is_recurring', 'recurrence_period'
        ]
    
    def create(self, validated_data):
        financial_record_data = validated_data.pop('financial_record')
        financial_record_data['record_type'] = 'expense'
        
        # Create the financial record
        financial_record = FinancialRecord.objects.create(**financial_record_data)
        
        # Create the expense record
        expense = Expense.objects.create(financial_record=financial_record, **validated_data)
        return expense

class IncomeSerializer(serializers.ModelSerializer):
    """Serializer for income records"""
    financial_record = FinancialRecordSerializer()
    
    class Meta:
        model = Income
        fields = [
            'id', 'financial_record', 'customer', 'invoice_number',
            'tax_amount', 'is_recurring', 'recurrence_period'
        ]
    
    def create(self, validated_data):
        financial_record_data = validated_data.pop('financial_record')
        financial_record_data['record_type'] = 'income'
        
        # Create the financial record
        financial_record = FinancialRecord.objects.create(**financial_record_data)
        
        # Create the income record
        income = Income.objects.create(financial_record=financial_record, **validated_data)
        return income

class BudgetCategorySerializer(serializers.ModelSerializer):
    """Serializer for budget categories"""
    class Meta:
        model = BudgetCategory
        fields = ['id', 'name', 'description', 'parent', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for farm budgets"""
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'farm', 'farm_name', 'name', 'description', 'category', 'category_name',
            'amount', 'start_date', 'end_date', 'is_active', 'notes',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']
    
    def create(self, validated_data):
        # Set the created_by to the current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class FinancialSummarySerializer(serializers.ModelSerializer):
    """Serializer for financial summaries"""
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    
    class Meta:
        model = FinancialSummary
        fields = [
            'id', 'farm', 'farm_name', 'period', 'start_date', 'end_date',
            'total_income', 'total_expenses', 'net_profit', 'profit_margin',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class LoanRecordSerializer(serializers.ModelSerializer):
    """Serializer for loan records"""
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    
    class Meta:
        model = LoanRecord
        fields = [
            'id', 'farm', 'farm_name', 'lender', 'loan_amount', 'interest_rate',
            'start_date', 'end_date', 'payment_frequency', 'payment_amount',
            'total_payments', 'remaining_balance', 'status', 'purpose',
            'reference_number', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class PaymentRecordSerializer(serializers.ModelSerializer):
    """Serializer for loan payment records"""
    loan_reference = serializers.CharField(source='loan.reference_number', read_only=True)
    
    class Meta:
        model = PaymentRecord
        fields = [
            'id', 'loan', 'loan_reference', 'payment_date', 'amount',
            'payment_method', 'reference_number', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']