from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils.http import urlencode
from decimal import Decimal
from products.models import Product
from .models import ShippingZone

def _get_cart(session):
    return session.setdefault("cart", {})

def _save_session(request):
    request.session.modified = True

def _cart_items(cart):
    items = []
    total = Decimal("0")
    for pid, qty in cart.items():
        p = Product.objects.filter(id=int(pid), available=True).first()
        if not p:
            continue
        quantity = int(qty)
        subtotal = Decimal(p.price) * quantity
        total += subtotal
        items.append({"product": p, "quantity": quantity, "subtotal": subtotal})
    return items, total

def _shipping_cost(total, shipping_opts=None):
    free_threshold = getattr(settings, "FREE_SHIPPING_OVER", 100000)
    default_shipping = getattr(settings, "DEFAULT_SHIPPING_COST", 10000)
    shipping_opts = shipping_opts or {}
    method = shipping_opts.get("method", "delivery")
    if method == "pickup":
        return Decimal("0")
    zone_id = shipping_opts.get("zone_id")
    if zone_id:
        try:
            zone = ShippingZone.objects.get(id=int(zone_id), active=True)
            zone_cost = Decimal(zone.cost)
        except (ShippingZone.DoesNotExist, ValueError):
            zone_cost = Decimal(default_shipping)
    else:
        zone_cost = Decimal(default_shipping)
    if total >= Decimal(free_threshold):
        return Decimal("0")
    return zone_cost

def _discount_amount(total):
    percent = getattr(settings, "DISCOUNT_PERCENT", 0)
    if not percent:
        return Decimal("0")
    return (Decimal(total) * Decimal(percent) / Decimal("100")).quantize(Decimal("1."))

def cart_view(request):
    cart = _get_cart(request.session)
    items, total = _cart_items(cart)
    discount = _discount_amount(total)
    shipping_opts = request.session.get("shipping", {"method": "delivery"})
    shipping = _shipping_cost(total - discount, shipping_opts)
    grand_total = total - discount + shipping
    wa_number = getattr(settings, "WHATSAPP_NUMBER", "")
    wa_text = "Pedido CAMPOVERDE:\n"
    for i in items:
        wa_text += f"- {i['quantity']} x {i['product'].name} = ${i['subtotal']}\n"
    wa_text += f"Subtotal: ${total}\n"
    if discount > 0:
        wa_text += f"Descuento: -${discount}\n"
    wa_text += f"Envío ({shipping_opts.get('method', 'delivery')}): ${shipping}\n"
    wa_text += f"Total: ${grand_total}\n"
    wa_link = f"https://wa.me/{wa_number}?{urlencode({'text': wa_text})}" if wa_number else ""
    zones = ShippingZone.objects.filter(active=True).order_by("name")
    ctx = {
        "items": items,
        "total": total,
        "discount": discount,
        "shipping": shipping,
        "grand_total": grand_total,
        "wa_link": wa_link,
        "zones": zones,
        "shipping_opts": shipping_opts,
    }
    return render(request, "orders/cart.html", ctx)

@require_POST
def add_to_cart(request, product_id):
    qty = int(request.POST.get("qty", "1"))
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = _get_cart(request.session)
    current = int(cart.get(str(product_id), 0))
    cart[str(product_id)] = current + max(1, qty)
    _save_session(request)
    return redirect("cart_view")

def remove_from_cart(request, product_id):
    cart = _get_cart(request.session)
    cart.pop(str(product_id), None)
    _save_session(request)
    return redirect("cart_view")

def quick_buy_product(request, product_id):
    p = get_object_or_404(Product, id=product_id, available=True)
    wa_number = getattr(settings, "WHATSAPP_NUMBER", "")
    text = f"Hola, quiero comprar 1 x {p.name} por ${p.price}"
    link = f"https://wa.me/{wa_number}?{urlencode({'text': text})}" if wa_number else "/"
    return redirect(link)

@require_POST
def set_shipping_options(request):
    method = request.POST.get("method", "delivery")
    zone_id = request.POST.get("zone_id")
    address = request.POST.get("address", "")
    request.session["shipping"] = {"method": method, "zone_id": zone_id, "address": address}
    _save_session(request)
    return redirect("cart_view")

# Create your views here.
