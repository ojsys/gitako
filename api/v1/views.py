from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root providing links to all main endpoints
    """
    return Response({
        'accounts': reverse('user-list', request=request, format=format),
        'farms': reverse('farm-list', request=request, format=format),
        'fields': reverse('field-list', request=request, format=format),
        'crops': reverse('crop-list', request=request, format=format),
        'marketplace': {
            'products': reverse('product-list', request=request, format=format),
            'inputs': reverse('input-list', request=request, format=format),
            'produce': reverse('produce-list', request=request, format=format),
            'orders': reverse('order-list', request=request, format=format),
        },
        'activities': reverse('activity-list', request=request, format=format),
        'inventory': {
            'inputs': reverse('input-inventory-list', request=request, format=format),
            'produce': reverse('produce-inventory-list', request=request, format=format),
        },
        'financials': {
            'records': reverse('financial-record-list', request=request, format=format),
            'expenses': reverse('expense-list', request=request, format=format),
            'income': reverse('income-list', request=request, format=format),
            'budgets': reverse('budget-list', request=request, format=format),
        },
        'recommendations': reverse('recommendation-list', request=request, format=format),
    })