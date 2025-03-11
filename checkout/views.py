from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
import stripe
from django.conf import settings
from decimal import Decimal
class CheckoutViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['GET'])
    def payment_methods(self, request):
        """Return available payment methods"""
        return Response({
            'methods': [
                {
                    'id': 'visa',
                    'name': 'Visa',
                    'enabled': True
                },
                {
                    'id': 'mastercard',
                    'name': 'Mastercard',
                    'enabled': True
                },
                {
                    'id': 'stripe',
                    'name': 'Stripe',
                    'enabled': True
                },
                {
                    'id': 'paypal',
                    'name': 'PayPal',
                    'enabled': True
                },
                {
                    'id': 'google_pay',
                    'name': 'Google Pay',
                    'enabled': True
                }
            ]
        })

    @action(detail=False, methods=['POST'])
    def validate_promocode(self, request):
        """Validate promocode and return discount amount"""
        promocode = request.data.get('promocode')
        subtotal = Decimal(request.data.get('subtotal', '0'))

        try:
            discount = self._calculate_discount(promocode, subtotal)
            return Response({
                'valid': True,
                'discount_percentage': 20,  # Example fixed percentage
                'discount_amount': discount
            })
        except ValueError as e:
            return Response({
                'valid': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def process(self, request):
        """Process checkout"""
        try:
            with transaction.atomic():
                # Get cart and items
                cart = Cart.objects.get(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart).select_related('product')
                
                if not cart_items.exists():
                    return Response({
                        'status': 'error',
                        'message': 'Cart is empty'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validate address
                address_id = request.data.get('address_id')
                try:
                    shipping_address = Address.objects.get(
                        id=address_id,
                        user=request.user
                    )
                except Address.DoesNotExist:
                    return Response({
                        'status': 'error',
                        'message': 'Invalid shipping address'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Calculate totals
                subtotal = Decimal('0.00')
                shipping_cost = Decimal('3.00')
                
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=shipping_address.street_address,
                    shipping_city=shipping_address.city,
                    shipping_state=shipping_address.state,
                    shipping_country=shipping_address.country,
                    shipping_zip=shipping_address.zip_code,
                    shipping_cost=shipping_cost,
                    status='PENDING'
                )

                # Process order items
                for cart_item in cart_items:
                    if cart_item.quantity > cart_item.product.stock_quantity:
                        raise ValueError(f'Insufficient stock for {cart_item.product.name}')
                    
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )
                    
                    cart_item.product.stock_quantity -= cart_item.quantity
                    cart_item.product.save()
                    
                    subtotal += cart_item.product.price * cart_item.quantity

                # Apply discount
                discount_code = request.data.get('discount_code')
                discount_amount = Decimal('0.00')
                if discount_code:
                    discount_amount = self._calculate_discount(discount_code, subtotal)

                # Update order totals
                order.subtotal = subtotal
                order.discount = discount_amount
                order.total = subtotal - discount_amount + shipping_cost
                order.save()

                # Clear cart
                cart_items.delete()

                return Response({
                    'status': 'success',
                    'message': 'Order created successfully',
                    'order_id': order.id,
                    'total': order.total
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def process_payment(self, request):
        """Process payment for an order"""
        payment_method = request.data.get('payment_method')
        payment_data = request.data.get('payment_data')
        order_id = request.data.get('order_id')
        save_card = request.data.get('save_card', False)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
            
            payment_service = self._get_payment_service(payment_method)
            if not payment_service:
                return Response({
                    'status': 'error',
                    'message': 'Invalid payment method'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            result = payment_service.process_payment(order, payment_data)
            
            if result['success']:
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total,
                    payment_method=payment_method,
                    transaction_id=result['transaction_id'],
                    status='COMPLETED',
                    gateway_response=result['response'],
                    save_card=save_card
                )
                
                if payment_data.get('card_details'):
                    payment.card_last_four = payment_data['card_details'].get('last4')
                    payment.card_brand = payment_data['card_details'].get('brand')
                    payment.card_expiry = payment_data['card_details'].get('exp_date')
                    payment.save()
                
                order.status = 'PAID'
                order.save()
                
                return Response({
                    'status': 'success',
                    'payment_id': payment.id
                })
            
            return Response({
                'status': 'error',
                'message': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Order.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)

    def _get_payment_service(self, payment_method):
        """Get appropriate payment service based on payment method"""
        services = {
            'STRIPE': StripePaymentService(),
            'PAYPAL': PayPalPaymentService(),
            'GOOGLE_PAY': GooglePayService(),
            'VISA': StripePaymentService(),
            'MASTERCARD': StripePaymentService(),
        }
        return services.get(payment_method.upper())

    def _calculate_discount(self, promocode, subtotal):
        """Calculate discount amount based on promocode"""
        # Implement your discount logic here
        if not promocode:
            return Decimal('0.00')
            
        # Example: 20% discount
        return subtotal * Decimal('0.20')

    @action(detail=False, methods=['GET'])
    def get_client_secret(self, request):
        """Get Stripe client secret for frontend payment flow"""
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.create(
                amount=int(float(request.GET.get('amount')) * 100),
                currency='usd'
            )
            return Response({'client_secret': intent.client_secret})
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)