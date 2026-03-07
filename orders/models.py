from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from products.models import Product

class ShippingZone(models.Model):
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Zona de Envío"
        verbose_name_plural = "Zonas de Envío"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (${self.cost})"


class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('preparing', 'En preparación'),
        ('sent', 'Enviado'),
        ('delivered', 'Entregado'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    delivery_method = models.CharField(
        max_length=20,
        choices=[
            ('delivery', 'Domicilio'),
            ('pickup', 'Recoger')
        ]
    )

    address = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"Pedido {self.id}"


class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.IntegerField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price
