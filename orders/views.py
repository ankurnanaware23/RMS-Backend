from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderItem, Earning
from .serializers import OrderSerializer, OrderItemSerializer, EarningSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        if order.table:
            order.table.status = 'Occupied'
            order.table.save()


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class EarningViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Earning.objects.all()
    serializer_class = EarningSerializer

    @action(detail=False, methods=['get'], url_path='performance')
    def performance(self, request):
        today = timezone.now().date()

        revenue = Order.objects.filter(created_at__date=today).aggregate(total=Sum('total_amount'))['total'] or 0
        total_customers = Order.objects.filter(created_at__date=today).values('customer_name').distinct().count()
        event_count = Order.objects.filter(created_at__date=today).count()
        sales_details = Order.objects.filter(created_at__date__gte=today - timezone.timedelta(days=30))             .values('created_at__date')             .annotate(daily_total=Sum('total_amount'))             .order_by('created_at__date')

        today_earning = revenue
        in_progress_orders = Order.objects.filter(status='In Progress').count()
        total_dishes_ordered = OrderItem.objects.filter(order__created_at__date=today).aggregate(total=Sum('quantity'))['total'] or 0
        active_orders = Order.objects.filter(status__in=['Pending', 'In Progress']).count()

        recent_orders = OrderSerializer(Order.objects.order_by('-created_at')[:5], many=True).data

        popular_dishes = OrderItem.objects.values('dish__name')             .annotate(count=Count('id'))             .order_by('-count')[:5]

        return Response({
            'overall_performance': {
                'revenue': revenue,
                'total_customer': total_customers,
                'event_count': event_count,
            },
            'sales_details': sales_details,
            'todays_performance': {
                'today_earning': today_earning,
                'in_progress': in_progress_orders,
                'total_customer': total_customers,
                'total_dishes': total_dishes_ordered,
                'active_orders': active_orders,
            },
            'recent_orders': recent_orders,
            'popular_dishes': popular_dishes,
        })
