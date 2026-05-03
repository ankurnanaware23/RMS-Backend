from django.db import models


class Table(models.Model):
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Occupied', 'Occupied'),
        ('Booked', 'Booked'),
    )
    table_number = models.CharField(max_length=10, unique=True)
    seats = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Available')
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    booking_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.table_number

    def save(self, *args, **kwargs):
        if self.status == 'Available':
            self.customer_name = None
            self.booking_time = None
        super().save(*args, **kwargs)
