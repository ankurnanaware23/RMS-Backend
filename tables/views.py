from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Table
from .serializers import TableSerializer


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    @action(detail=True, methods=['post'])
    def book(self, request, pk=None):
        table = self.get_object()
        if table.status != 'Available':
            return Response({'error': 'Table is not available for booking'}, status=status.HTTP_400_BAD_REQUEST)

        customer_name = request.data.get('customer_name')
        booking_time = request.data.get('booking_time')

        if not customer_name or not booking_time:
            return Response({'error': 'Customer name and booking time are required'}, status=status.HTTP_400_BAD_REQUEST)

        table.status = 'Booked'
        table.customer_name = customer_name
        table.booking_time = booking_time
        table.save()
        return Response(self.get_serializer(table).data)

    @action(detail=True, methods=['post'])
    def free(self, request, pk=None):
        table = self.get_object()
        table.status = 'Available'
        table.customer_name = None
        table.booking_time = None
        table.save()
        return Response(self.get_serializer(table).data)
