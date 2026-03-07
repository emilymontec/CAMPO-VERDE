from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, ShippingZone
from payments.models import Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "quantity", "price", "subtotal_display")
    readonly_fields = ("subtotal_display",)

    def subtotal_display(self, obj):
        try:
            return f"${obj.subtotal()}"
        except Exception:
            return "-"
    subtotal_display.short_description = "Subtotal"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "created_at", "total_display", "status_timeline")
    list_filter = ("status", "created_at", "customer")
    search_fields = ("id", "customer__username", "customer__email")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]
    
    def get_inlines(self, request, obj=None):
        class PaymentInline(admin.TabularInline):
            model = Payment
            extra = 0
            fields = ("method", "amount", "reference", "confirmed")
        return [OrderItemInline, PaymentInline]

    ORDER_FLOW = ["pending", "confirmed", "preparing", "sent", "delivered"]
    LABELS = {
        "pending": "Pendiente",
        "confirmed": "Confirmado",
        "preparing": "En preparación",
        "sent": "Enviado",
        "delivered": "Entregado",
    }

    def total_display(self, obj):
        return f"${obj.total}"
    total_display.short_description = "Total"

    def status_timeline(self, obj):
        current = obj.status
        try:
            idx = self.ORDER_FLOW.index(current)
        except ValueError:
            idx = 0

        items = []
        for i, key in enumerate(self.ORDER_FLOW):
            active = i <= idx
            color = "#111827" if active else "#d1d5db"
            label = self.LABELS.get(key, key.title())
            items.append(
                f"""
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:10px;height:10px;border-radius:50%;background:{color};"></div>
                    <span style="font-size:11px;color:{color};white-space:nowrap;">{label}</span>
                </div>
                """
            )
        return format_html(
            '<div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;">{}</div>',
            format_html("".join(items)),
        )

    status_timeline.short_description = "Estado"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price", "subtotal_display")
    search_fields = ("order__id", "product__name")
    list_filter = ("order__status",)

    def subtotal_display(self, obj):
        try:
            return f"${obj.subtotal()}"
        except Exception:
            return "-"
    subtotal_display.short_description = "Subtotal"


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "cost", "active", "notes")
    list_editable = ("cost", "active")
    search_fields = ("name", "notes")
    ordering = ("name",)
