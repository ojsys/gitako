from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Sum
from .models import (
    Transaction, Expense, Income, Budget, BudgetItem, 
    FinancialReport
)
from .serializers import (
    TransactionSerializer, ExpenseSerializer, IncomeSerializer,
    BudgetSerializer, BudgetItemSerializer, FinancialReportSerializer
)
from api.permissions import IsFarmOwner

class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for Transaction model"""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farm', 'transaction_type', 'date', 'payment_method']
    search_fields = ['description', 'reference_number']
    ordering_fields = ['date', 'amount', 'created_at']
    
    def get_queryset(self):
        """
        This view returns a list of all transactions
        for the currently authenticated user.
        """
        return Transaction.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a transaction"""
        serializer.save(user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get a summary of transactions",
        manual_parameters=[
            openapi.Parameter('farm', openapi.IN_QUERY, description="Farm ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={200: openapi.Response(
            description="Transaction summary",
            examples={
                "application/json": {
                    "total_income": 5000.00,
                    "total_expenses": 3000.00,
                    "net_profit": 2000.00,
                    "profit_margin": 40.0
                }
            }
        )}
    )
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get a summary of transactions"""
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
        income_total = queryset.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
        expense_total = queryset.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0
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
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['transaction__farm', 'category', 'crop_cycle']
    search_fields = ['transaction__description', 'vendor_name']
    ordering_fields = ['transaction__date', 'transaction__amount']
    
    def get_queryset(self):
        """
        This view returns a list of all expenses
        for the currently authenticated user.
        """
        return Expense.objects.filter(transaction__user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get expenses by category",
        responses={200: ExpenseSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get expenses grouped by category"""
        category = request.query_params.get('category')
        if not category:
            return Response(
                {"error": "Category parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        expenses = self.get_queryset().filter(category=category)
        serializer = self.get_serializer(expenses, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Get expenses by crop cycle",
        responses={200: ExpenseSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_crop_cycle(self, request):
        """Get expenses for a specific crop cycle"""
        crop_cycle_id = request.query_params.get('crop_cycle_id')
        if not crop_cycle_id:
            return Response(
                {"error": "crop_cycle_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        expenses = self.get_queryset().filter(crop_cycle_id=crop_cycle_id)
        serializer = self.get_serializer(expenses, many=True)
        return Response(serializer.data)

class IncomeViewSet(viewsets.ModelViewSet):
    """ViewSet for Income model"""
    serializer_class = IncomeSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['transaction__farm', 'source', 'crop_cycle']
    search_fields = ['transaction__description', 'buyer_name']
    ordering_fields = ['transaction__date', 'transaction__amount']
    
    def get_queryset(self):
        """
        This view returns a list of all income records
        for the currently authenticated user.
        """
        return Income.objects.filter(transaction__user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get income by source",
        responses={200: IncomeSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_source(self, request):
        """Get income grouped by source"""
        source = request.query_params.get('source')
        if not source:
            return Response(
                {"error": "Source parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        income = self.get_queryset().filter(source=source)
        serializer = self.get_serializer(income, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Get income by crop cycle",
        responses={200: IncomeSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_crop_cycle(self, request):
        """Get income for a specific crop cycle"""
        crop_cycle_id = request.query_params.get('crop_cycle_id')
        if not crop_cycle_id:
            return Response(
                {"error": "crop_cycle_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        income = self.get_queryset().filter(crop_cycle_id=crop_cycle_id)
        serializer = self.get_serializer(income, many=True)
        return Response(serializer.data)

class BudgetItemViewSet(viewsets.ModelViewSet):
    """ViewSet for BudgetItem model"""
    serializer_class = BudgetItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['budget', 'item_type', 'category']
    search_fields = ['description']
    ordering_fields = ['amount']
    
    def get_queryset(self):
        """
        This view returns a list of all budget items
        for budgets owned by the currently authenticated user.
        """
        return BudgetItem.objects.filter(budget__user=self.request.user)

class BudgetViewSet(viewsets.ModelViewSet):
    """ViewSet for Budget model"""
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farm', 'status', 'start_date', 'end_date']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'end_date', 'total_planned_income', 'total_planned_expenses', 'created_at']
    
    def get_queryset(self):
        """
        This view returns a list of all budgets
        for the currently authenticated user.
        """
        return Budget.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a budget"""
        serializer.save(user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Get budget performance metrics",
        responses={200: openapi.Response(
            description="Budget performance metrics",
            examples={
                "application/json": {
                    "planned_income": 10000.00,
                    "planned_expenses": 7000.00,
                    "planned_profit": 3000.00,
                    "actual_income": 9500.00,
                    "actual_expenses": 6800.00,
                    "actual_profit": 2700.00,
                    "income_variance": -500.00,
                    "expense_variance": 200.00,
                    "profit_variance": -300.00
                }
            }
        )}
    )
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get budget performance metrics"""
        budget = self.get_object()
        
        # Calculate variances
        income_variance = budget.actual_income - budget.total_planned_income
        expense_variance = budget.total_planned_expenses - budget.actual_expenses
        profit_variance = budget.actual_profit - budget.planned_profit
        
        return Response({
            'planned_income': budget.total_planned_income,
            'planned_expenses': budget.total_planned_expenses,
            'planned_profit': budget.planned_profit,
            'actual_income': budget.actual_income,
            'actual_expenses': budget.actual_expenses,
            'actual_profit': budget.actual_profit,
            'income_variance': income_variance,
            'expense_variance': expense_variance,
            'profit_variance': profit_variance
        })
    
    @swagger_auto_schema(
        operation_description="Get budget items",
        responses={200: BudgetItemSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get all items for a specific budget"""
        budget = self.get_object()
        items = BudgetItem.objects.filter(budget=budget)
        serializer = BudgetItemSerializer(items, many=True)
        return Response(serializer.data)

class FinancialReportViewSet(viewsets.ModelViewSet):
    """ViewSet for FinancialReport model"""
    serializer_class = FinancialReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farm', 'report_type', 'start_date', 'end_date']
    search_fields = ['title']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    
    def get_queryset(self):
        """
        This view returns a list of all financial reports
        for the currently authenticated user.
        """
        return FinancialReport.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a report"""
        serializer.save(user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Generate a new financial report",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['report_type', 'start_date', 'end_date', 'farm'],
            properties={
                'report_type': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['income_statement', 'expense_report', 'profit_loss', 
                          'budget_comparison', 'crop_profitability'],
                    description='Type of report to generate'
                ),
                'title': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Report title'
                ),
                'start_date': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    description='Start date for the report period'
                ),
                'end_date': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    description='End date for the report period'
                ),
                'farm': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Farm ID (optional)'
                )
            }
        ),
        responses={201: FinancialReportSerializer}
    )
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new financial report"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Generate report data based on type
        report_type = serializer.validated_data.get('report_type')
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')
        farm = serializer.validated_data.get('farm')
        
        # Generate report data (this would be more complex in a real application)
        report_data = self._generate_report_data(report_type, start_date, end_date, farm)
        
        # Save the report with the generated data
        serializer.save(user=request.user, report_data=report_data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def _generate_report_data(self, report_type, start_date, end_date, farm):
        """Helper method to generate report data based on type"""
        # This would be more complex in a real application
        # For now, we'll return a simple structure based on the report type
        
        if report_type == 'income_statement':
            # Get all income transactions for the period
            income_transactions = Transaction.objects.filter(
                user=self.request.user,
                farm=farm,
                transaction_type='income',
                date__gte=start_date,
                date__lte=end_date
            )
            
            # Group by source
            income_by_source = {}
            for transaction in income_transactions:
                income = Income.objects.get(transaction=transaction)
                source = income.get_source_display()
                if source not in income_by_source:
                    income_by_source[source] = 0
                income_by_source[source] += transaction.amount
            
            return {
                'report_type': 'Income Statement',
                'period': f"{start_date} to {end_date}",
                'income_by_source': income_by_source,
                'total_income': sum(income_by_source.values())
            }
            
        elif report_type == 'expense_report':
            # Get all expense transactions for the period
            expense_transactions = Transaction.objects.filter(
                user=self.request.user,
                farm=farm,
                transaction_type='expense',
                date__gte=start_date,
                date__lte=end_date
            )
            
            # Group by category
            expenses_by_category = {}
            for transaction in expense_transactions:
                expense = Expense.objects.get(transaction=transaction)
                category = expense.get_category_display()
                if category not in expenses_by_category:
                    expenses_by_category[category] = 0
                expenses_by_category[category] += transaction.amount
            
            return {
                'report_type': 'Expense Report',
                'period': f"{start_date} to {end_date}",
                'expenses_by_category': expenses_by_category,
                'total_expenses': sum(expenses_by_category.values())
            }
            
        elif report_type == 'profit_loss':
            # Calculate income
            income_total = Transaction.objects.filter(
                user=self.request.user,
                farm=farm,
                transaction_type='income',
                date__gte=start_date,
                date__lte=end_date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Calculate expenses
            expense_total = Transaction.objects.filter(
                user=self.request.user,
                farm=farm,
                transaction_type='expense',
                date__gte=start_date,
                date__lte=end_date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Calculate profit/loss
            net_profit = income_total - expense_total
            
            return {
                'report_type': 'Profit & Loss Statement',
                'period': f"{start_date} to {end_date}",
                'total_income': income_total,
                'total_expenses': expense_total,
                'net_profit': net_profit,
                'is_profitable': net_profit > 0
            }
            
        # Add other report types as needed
        
        return {'report_type': report_type, 'message': 'Report data not implemented'}
