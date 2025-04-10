from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from .models import (
    FinancialRecord, Expense, Income, Budget, BudgetCategory, 
    FinancialSummary, LoanRecord, PaymentRecord
)
from .serializers import (
    FinancialRecordSerializer, ExpenseSerializer, IncomeSerializer,
    BudgetSerializer, BudgetCategorySerializer, FinancialSummarySerializer,
    LoanRecordSerializer, PaymentRecordSerializer
)

class IsFarmOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow farm owners to edit financial records.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the farm owner
        if hasattr(obj, 'farm'):
            return obj.farm.owner == request.user
        elif hasattr(obj, 'financial_record'):
            return obj.financial_record.farm.owner == request.user
        elif hasattr(obj, 'loan'):
            return obj.loan.farm.owner == request.user
        
        return False

class FinancialRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for FinancialRecord model"""
    serializer_class = FinancialRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farm', 'record_type', 'category', 'date', 'is_verified']
    search_fields = ['description', 'reference_number']
    ordering_fields = ['date', 'amount', 'created_at']
    
    def get_queryset(self):
        """
        This view should return a list of all financial records
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return FinancialRecord.objects.filter(farm__owner=user)
    
    @action(detail=False, methods=['get'])
    def expenses(self, request):
        """Get all expense records"""
        queryset = self.get_queryset().filter(record_type='expense')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def income(self, request):
        """Get all income records"""
        queryset = self.get_queryset().filter(record_type='income')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get a summary of financial records"""
        farm_id = request.query_params.get('farm')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Calculate totals
        income_total = queryset.filter(record_type='income').aggregate(total=Sum('amount'))['total'] or 0
        expense_total = queryset.filter(record_type='expense').aggregate(total=Sum('amount'))['total'] or 0
        net_profit = income_total - expense_total
        
        # Calculate profit margin
        profit_margin = 0
        if income_total > 0:
            profit_margin = (net_profit / income_total) * 100
        
        return Response({
            'total_income': income_total,
            'total_expenses': expense_total,
            'net_profit': net_profit,
            'profit_margin': profit_margin
        })

class ExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet for Expense model"""
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['financial_record__farm', 'vendor', 'is_recurring']
    search_fields = ['financial_record__description', 'invoice_number', 'vendor']
    ordering_fields = ['financial_record__date', 'financial_record__amount']
    
    def get_queryset(self):
        """
        This view should return a list of all expenses
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return Expense.objects.filter(financial_record__farm__owner=user)

class IncomeViewSet(viewsets.ModelViewSet):
    """ViewSet for Income model"""
    serializer_class = IncomeSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['financial_record__farm', 'customer', 'is_recurring']
    search_fields = ['financial_record__description', 'invoice_number', 'customer']
    ordering_fields = ['financial_record__date', 'financial_record__amount']
    
    def get_queryset(self):
        """
        This view should return a list of all income records
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return Income.objects.filter(financial_record__farm__owner=user)

class BudgetCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for BudgetCategory model"""
    queryset = BudgetCategory.objects.all()
    serializer_class = BudgetCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

class BudgetViewSet(viewsets.ModelViewSet):
    """ViewSet for Budget model"""
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farm', 'category', 'is_active']
    search_fields = ['name', 'description', 'notes']
    ordering_fields = ['start_date', 'end_date', 'amount', 'created_at']
    
    def get_queryset(self):
        """
        This view should return a list of all budgets
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return Budget.objects.filter(farm__owner=user)
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get budget performance metrics"""
        budget = self.get_object()
        
        # Get actual expenses for this budget category
        actual_expenses = FinancialRecord.objects.filter(
            farm=budget.farm,
            record_type='expense',
            category=budget.category,
            date__gte=budget.start_date,
            date__lte=budget.end_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate metrics
        remaining = budget.amount - actual_expenses
        utilization_percentage = (actual_expenses / budget.amount) * 100 if budget.amount > 0 else 0
        
        return Response({
            'budget_amount': budget.amount,
            'actual_expenses': actual_expenses,
            'remaining': remaining,
            'utilization_percentage': utilization_percentage
        })

class FinancialSummaryViewSet(viewsets.ModelViewSet):
    """ViewSet for FinancialSummary model"""
    serializer_class = FinancialSummarySerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farm', 'period']
    search_fields = ['period']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    
    def get_queryset(self):
        """
        This view should return a list of all financial summaries
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return FinancialSummary.objects.filter(farm__owner=user)

class LoanRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for LoanRecord model"""
    serializer_class = LoanRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farm', 'lender', 'status']
    search_fields = ['lender', 'purpose', 'reference_number', 'notes']
    ordering_fields = ['start_date', 'end_date', 'loan_amount', 'created_at']
    
    def get_queryset(self):
        """
        This view should return a list of all loan records
        for farms owned by the currently authenticated user.
        """
        user = self.request.user
        return LoanRecord.objects.filter(farm__owner=user)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get all payments for a specific loan"""
        loan = self.get_object()
        payments = PaymentRecord.objects.filter(loan=loan)
        serializer = PaymentRecordSerializer(payments, many=True)
        return Response(serializer.data)

class PaymentRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for PaymentRecord model"""
    serializer_class = PaymentRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['loan', 'payment_method']
    search_fields = ['reference_number', 'notes']
    ordering_fields = ['payment_date', 'amount', 'created_at']
    
    def get_queryset(self):
        """
        This view should return a list of all payment records
        for loans associated with farms owned by the currently authenticated user.
        """
        user = self.request.user
        return PaymentRecord.objects.filter(loan__farm__owner=user)
