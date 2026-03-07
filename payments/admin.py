from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from .models import Payment
from orders.models import OrderItem


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "method", "amount", "confirmed_badge", "created_at", "confirm_button")
    list_filter = ("method", "confirmed", "created_at")
    search_fields = ("order__id", "reference")
    ordering = ("-created_at",)
    fields = ("order", "method", "amount", "reference", "note", "qr_image", "confirmed", "created_at", "qr_preview")
    readonly_fields = ("created_at", "qr_preview")

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("<int:pk>/confirm/", self.admin_site.admin_view(self.confirm_view), name="payments_payment_confirm"),
        ]
        return custom + urls

    def confirm_view(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
            payment.confirmed = True
            payment.save(update_fields=["confirmed"])
            order = payment.order
            if order.status == "pending":
                order.status = "confirmed"
                order.save(update_fields=["status"])
            messages.success(request, "Pago confirmado.")
        except Payment.DoesNotExist:
            messages.error(request, "Pago no encontrado.")
        return redirect(f"../../")

    def confirmed_badge(self, obj):
        color = "#16a34a" if obj.confirmed else "#b91c1c"
        label = "Sí" if obj.confirmed else "No"
        return format_html('<span style="color:{};font-weight:700">{}</span>', color, label)
    confirmed_badge.short_description = "Confirmado"

    def confirm_button(self, obj):
        if obj.confirmed:
            return format_html('<span style="color:#16a34a;font-weight:700">Confirmado</span>')
        return format_html(
            '<a class="button" style="padding:6px 10px;background:#111;color:#fff;border-radius:6px;" href="{}">Pago confirmado</a>',
            f"{obj.id}/confirm/",
        )
    confirm_button.short_description = ""

    def qr_preview(self, obj):
        if obj.method == "qr" and obj.qr_image:
            return format_html('<img src="{}" style="max-width:180px;border:1px solid #e5e7eb;border-radius:8px;">', obj.qr_image.url)
        return "—"
    qr_preview.short_description = "Código QR"
