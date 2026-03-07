from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem

ACTIVE_STATUSES = {"confirmed", "preparing", "sent", "delivered"}


@receiver(post_save, sender=OrderItem)
def reduce_stock_on_create(sender, instance, created, **kwargs):
    order = instance.order
    if order.status in ACTIVE_STATUSES and created:
        product = instance.product
        product.stock = max(0, int(product.stock) - int(instance.quantity))
        product.save(update_fields=["stock"])


@receiver(post_delete, sender=OrderItem)
def restore_stock_on_delete(sender, instance, **kwargs):
    order = instance.order
    if order.status in ACTIVE_STATUSES:
        product = instance.product
        product.stock = int(product.stock) + int(instance.quantity)
        product.save(update_fields=["stock"])
