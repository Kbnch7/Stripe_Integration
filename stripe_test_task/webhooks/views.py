from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.db import transaction
import stripe

from main.models import Order, OrderItem, Cart, Item


User = get_user_model()

@csrf_exempt
def confirm_payment_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id')

        if not user_id:
            return HttpResponse(status=200)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponse(status=200)

        metadata = session.metadata
        buy_type = metadata.get('buy_type')

        total_price = session.amount_total / 100 

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                stripe_session_id=session['id'],
                total_price=total_price
            )

            if buy_type == "instant":
                item = Item.objects.get(id=metadata['item_id'])
                OrderItem.objects.create(
                    order=order,
                    item=item,
                    amount=int(metadata['quantity']),
                    price=metadata['price']
                )
            elif buy_type == "cart":
                i = 0
                while f"item_{i}_id" in metadata:
                    item = Item.objects.get(id=metadata[f"item_{i}_id"])
                    OrderItem.objects.create(
                        order=order,
                        item=item,
                        amount=int(metadata[f"item_{i}_quantity"]),
                        price=metadata[f"item_{i}_price"]
                    )
                    i += 1
                Cart.objects.filter(user=user).delete()
                

        print(f"Заказ #{order.id} создан ({buy_type})")

    return HttpResponse(status=200)