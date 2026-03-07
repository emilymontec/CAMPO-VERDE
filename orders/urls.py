from django.urls import path
from .views import cart_view, add_to_cart, remove_from_cart, quick_buy_product, set_shipping_options

urlpatterns = [
    path('carrito/', cart_view, name='cart_view'),
    path('carrito/agregar/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('carrito/quitar/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('comprar/rapido/<int:product_id>/', quick_buy_product, name='quick_buy_product'),
    path('carrito/envio/', set_shipping_options, name='set_shipping_options'),
]
