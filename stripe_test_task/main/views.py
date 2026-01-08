from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
import stripe

from .models import Item, Cart


def get_item_view(request, pk):
    item = get_object_or_404(Item, id=pk)
    context = {
        "item": item,
        "public_key": settings.STRIPE_PUBLIC_KEY
    }
    return render(request, "main/item_detail.html", context)

@login_required
def buy_item_view(request, pk):
    item = get_object_or_404(Item, id=pk)
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": item.name,
                        "description": item.description,
                    },
                    "unit_amount": item.price * 100,
                },
                "quantity": 1,
            }
        ],
        success_url=settings.SUCCESS_PURCHASE_URL,
        cancel_url=settings.CANCEL_PURCHASE_URL,
        client_reference_id=str(request.user.id),
        metadata={
            "buy_type": "instant",
            "item_id": str(item.id),
            "quantity": "1",
            "price": str(item.price),
        }
    )
    return JsonResponse({"session_id": session.id})

def home(request):
    items = Item.objects.all()
    context = {"items": items}
    return render(request, 'main/home.html', context)

@login_required
def remove_item_view(request, pk):
    item = get_object_or_404(Item, id=pk)
    cart_item_to_delete = Cart.objects.get(user=request.user, item=item)
    cart_item_to_delete.delete()
    return redirect('cart')

@login_required
def add_to_cart_view(request, pk):
    item = get_object_or_404(Item, id=pk)
    cart_item = Cart.objects.filter(
        user=request.user,
        item=item
    )
    if cart_item.exists():
        cart_item = cart_item.first()
        cart_item.amount += 1
        cart_item.save()
    else:
        Cart.objects.create(
            user=request.user,
            item=item,
            amount=1
        )
    return redirect('cart')

@login_required
def decrease_item_in_cart(request, pk):
    item = get_object_or_404(Item, id=pk)
    cart_item = get_object_or_404(Cart, user=request.user, item=item)
    if cart_item.amount == 1:
        cart_item.delete()
    else:
        cart_item.amount -= 1
        cart_item.save()
    return redirect('cart')

@login_required
def show_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum([cart_item.item.price * cart_item.amount for cart_item in cart_items])
    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "public_key": settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'main/cart.html', context)

@login_required
def show_orders(request):
    orders = request.user.orders.all().order_by('-paid_at')
    return render(request, 'main/orders.html', {'orders': orders})

@login_required
def make_order(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    line_items = []
    metadata_items = {}
    
    for i, cart_item in enumerate(cart_items):
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": cart_item.item.name,
                    "description": cart_item.item.description or "",
                },
                "unit_amount": int(cart_item.item.price * 100),
            },
            "quantity": cart_item.amount,
        })
        
        metadata_items[f"item_{i}_id"] = str(cart_item.item.id)
        metadata_items[f"item_{i}_quantity"] = str(cart_item.amount)
        metadata_items[f"item_{i}_price"] = str(cart_item.item.price)
    
    metadata_items["buy_type"] = "cart"

    promocode = request.GET.get('promo', '').strip()

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        success_url=settings.SUCCESS_PURCHASE_URL,
        cancel_url=settings.CANCEL_PURCHASE_URL,
        client_reference_id=str(request.user.id),
        metadata=metadata_items,
        allow_promotion_codes=True
        # discounts=[{"promotion_code": promocode}]
    )
    
    return JsonResponse({"session_id": session.id})
