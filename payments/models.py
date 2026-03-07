from django.db import models

# Create your models here.
from orders.models import Order


class Payment(models.Model):

    PAYMENT_METHODS = [
        ('transfer', 'Transferencia'),
        ('qr', 'QR'),
        ('key', 'Llaves'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reference = models.CharField(max_length=120, blank=True)
    note = models.TextField(blank=True)
    qr_image = models.ImageField(upload_to="payments/qr/", blank=True, null=True)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago pedido {self.order.id}"
