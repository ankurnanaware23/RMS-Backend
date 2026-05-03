from django.db import models
from tables.models import Table
from menu.models import Dish


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Ready', 'Ready'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    ORDER_TYPE_CHOICES = (
        ('Dine In', 'Dine In'),
        ('Takeaway', 'Takeaway'),
    )
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default='Dine In')
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} for {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.dish.name} in Order {self.order.id}"


class Earning(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='earning', null=True, blank=True)
    date = models.DateField()
    completed_at = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Earnings on {self.date}: {self.amount}"
