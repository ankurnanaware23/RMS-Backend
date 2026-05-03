from django.contrib import admin
from .models import Order, OrderItem, Earning


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'table', 'status', 'order_type', 'total_amount', 'created_at')
    list_filter = ()
    search_fields = ('customer_name',)
    inlines = [OrderItemInline]

    def has_change_permission(self, request, obj=None):
        if obj and obj.status in ('Completed', 'Cancelled'):
            return False
        return super().has_change_permission(request, obj=obj)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in ('Completed', 'Cancelled'):
            return [field.name for field in obj._meta.fields]
        return super().get_readonly_fields(request, obj=obj)

    def has_delete_permission(self, request, obj=None):
        return False


class OrderStatusFilter(admin.SimpleListFilter):
    title = 'Order Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('Pending', 'On Going'),
            ('Completed', 'Completed'),
            ('Cancelled', 'Cancelled'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value in ('Pending', 'Completed', 'Cancelled'):
            return queryset.filter(status=value)
        return queryset


OrderAdmin.list_filter = (OrderStatusFilter,)




@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'date', 'completed_at', 'amount')
    list_filter = ('date',)
    search_fields = ('order__id',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
