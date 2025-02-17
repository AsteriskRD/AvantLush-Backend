from django.conf import settings
import requests
from abc import ABC, abstractmethod
import stripe
import paypalrestsdk
import google.auth.transport.requests

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox" if settings.DEBUG else "live",  # sandbox or live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

class BasePaymentService(ABC):
    @abstractmethod
    def process_payment(self, order, payment_data):
        pass

class StripePaymentService(BasePaymentService):
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def process_payment(self, order, payment_data):
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),
                currency='usd',
                payment_method=payment_data['payment_method_id'],
                confirm=True
            )
            return {
                'success': True,
                'transaction_id': payment_intent.id,
                'response': payment_intent
            }
        except stripe.error.StripeError as e:
            return {'success': False, 'error': str(e)}

class PayPalPaymentService(BasePaymentService):
    def process_payment(self, order, payment_data):
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "http://localhost:8000/payment/execute",  # Update with your actual URLs
                "cancel_url": "http://localhost:8000/payment/cancel"
            },
            "transactions": [{
                "amount": {
                    "total": str(order.total),
                    "currency": "USD"
                },
                "description": f"Order #{order.id}"
            }]
        })

        if payment.create():
            return {
                'success': True,
                'transaction_id': payment.id,
                'response': payment.to_dict()
            }
        return {
            'success': False, 
            'error': payment.error if hasattr(payment, 'error') else 'Payment creation failed'
        }

    def execute_payment(self, payment_id, payer_id):
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            return {
                'success': True,
                'transaction_id': payment.id,
                'response': payment.to_dict()
            }
        return {
            'success': False,
            'error': payment.error if hasattr(payment, 'error') else 'Payment execution failed'
        }

class CloverPaymentService(BasePaymentService):
    def __init__(self):
        self.public_token = settings.CLOVER_PUBLIC_TOKEN
        self.private_token = settings.CLOVER_PRIVATE_TOKEN
        self.base_url = "https://api.clover.com/v3"

    def process_payment(self, order, payment_data):
        try:
            # Create payment on Clover
            payment_data = {
                "amount": int(order.total * 100),  # Convert to cents
                "currency": "USD",
                "source": payment_data.get('card_data'),
                "external_reference": str(order.id)
            }
            
            headers = {
                "Authorization": f"Bearer {self.private_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                f"{self.base_url}/charges",
                json=payment_data,
                headers=headers
            )
            
            response_data = response.json()
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "transaction_id": response_data["id"],
                    "response": response_data
                }
            else:
                return {
                    "success": False,
                    "error": response_data.get("message", "Payment processing failed")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }