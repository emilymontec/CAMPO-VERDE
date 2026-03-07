from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class LowStockFilter(admin.SimpleListFilter):
    title = "Stock bajo"
    parameter_name = "low_stock"

    def lookups(self, request, model_admin):
        return (("1", "Solo stock bajo"),)

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(stock__lte=admin.models.F("min_stock"))
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "min_stock", "low_stock_badge", "available")
    list_filter = ("available", "category", LowStockFilter)
    search_fields = ("name", "category__name")
    list_editable = ("price", "stock", "min_stock", "available")

    def low_stock_badge(self, obj):
        if getattr(obj, "low_stock", False):
            return format_html('<span style="color:#b91c1c;font-weight:700">BAJO</span>')
        return format_html('<span style="color:#16a34a;font-weight:700">OK</span>')
    low_stock_badge.short_description = "Alerta"
