from rest_framework import serializers
from .models import (
    Transaction, Income, Expense, Budget, BudgetItem, FinancialReport
)

class TransactionSerializer(serializers.ModelSerializer):
    """Base serializer for financial transactions"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'user_name', 'farm', 'farm_name', 'transaction_type', 
            'transaction_type_display', 'amount', 'description', 'date',
            'payment_method', 'reference_number', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class IncomeSerializer(serializers.ModelSerializer):
    """Serializer for income records"""
    transaction = TransactionSerializer()
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    crop_cycle_name = serializers.CharField(source='crop_cycle.crop.name', read_only=True)
    
    class Meta:
        model = Income
        fields = [
            'transaction', 'source', 'source_display', 'crop_cycle', 'crop_cycle_name',
            'quantity', 'unit', 'price_per_unit', 'buyer_name', 'buyer_contact'
        ]
    
    def create(self, validated_data):
        transaction_data = validated_data.pop('transaction')
        transaction_data['transaction_type'] = 'income'
        transaction_data['user'] = self.context['request'].user
        
        # Create the transaction
        transaction = Transaction.objects.create(**transaction_data)
        
        # Create the income record
        income = Income.objects.create(transaction=transaction, **validated_data)
        return income
    
    def update(self, instance, validated_data):
        transaction_data = validated_data.pop('transaction', None)
        if transaction_data:
            for attr, value in transaction_data.items():
                setattr(instance.transaction, attr, value)
            instance.transaction.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for expense records"""
    transaction = TransactionSerializer()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    crop_cycle_name = serializers.CharField(source='crop_cycle.crop.name', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'transaction', 'category', 'category_display', 'crop_cycle', 'crop_cycle_name',
            'quantity', 'unit', 'price_per_unit', 'vendor_name', 'vendor_contact'
        ]
    
    def create(self, validated_data):
        transaction_data = validated_data.pop('transaction')
        transaction_data['transaction_type'] = 'expense'
        transaction_data['user'] = self.context['request'].user
        
        # Create the transaction
        transaction = Transaction.objects.create(**transaction_data)
        
        # Create the expense record
        expense = Expense.objects.create(transaction=transaction, **validated_data)
        return expense
    
    def update(self, instance, validated_data):
        transaction_data = validated_data.pop('transaction', None)
        if transaction_data:
            for attr, value in transaction_data.items():
                setattr(instance.transaction, attr, value)
            instance.transaction.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class BudgetItemSerializer(serializers.ModelSerializer):
    """Serializer for budget items"""
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)
    
    class Meta:
        model = BudgetItem
        fields = [
            'id', 'budget', 'item_type', 'item_type_display', 'category', 
            'description', 'amount', 'quantity', 'unit', 'price_per_unit'
        ]

class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for farm budgets"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = BudgetItemSerializer(many=True, read_only=True)
    planned_profit = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    actual_income = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    actual_expenses = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    actual_profit = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'user', 'user_name', 'farm', 'farm_name', 'title', 'description',
            'start_date', 'end_date', 'total_planned_income', 'total_planned_expenses',
            'planned_profit', 'actual_income', 'actual_expenses', 'actual_profit',
            'status', 'status_display', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'planned_profit', 
                           'actual_income', 'actual_expenses', 'actual_profit']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class FinancialReportSerializer(serializers.ModelSerializer):
    """Serializer for financial reports"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    report_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialReport
        fields = [
            'id', 'user', 'user_name', 'farm', 'farm_name', 'title',
            'start_date', 'end_date', 'report_type', 'report_type_display',
            'report_data', 'report_file', 'created_at'
        ]
        read_only_fields = ['created_at', 'report_file']
    
    def get_report_type_display(self, obj):
        return dict(obj.REPORT_TYPE_CHOICES).get(obj.report_type, obj.report_type)
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)