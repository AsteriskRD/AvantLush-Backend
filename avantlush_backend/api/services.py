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
        self.merchant_id = getattr(settings, 'CLOVER_MERCHANT_ID', None)
        self.base_url = "https://api.clover.com/v3"
        self.sandbox_url = "https://sandbox.dev.clover.com/v3"  # For testing
        self.api_url = self.sandbox_url if settings.DEBUG else self.base_url

    def process_payment(self, order, payment_data):
        try:
            # Extract card data from payment_data
            card_data = payment_data.get('card_data', {})
            
            # Format request data for Clover API
            request_data = {
                "amount": int(order.total * 100),  # Convert to cents
                "currency": "USD",
                "source": self._format_card_data(card_data),
                "external_reference_id": str(order.id),
                "description": f"Order #{order.id} payment"
            }
            
            headers = {
                "Authorization": f"Bearer {self.private_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # If we have a merchant ID, include it in the URL
            url = f"{self.api_url}/merchants/{self.merchant_id}/charges" if self.merchant_id else f"{self.api_url}/charges"
            
            response = requests.post(
                url,
                json=request_data,
                headers=headers
            )
            
            response_data = response.json()
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "transaction_id": response_data.get("id"),
                    "response": response_data
                }
            else:
                return {
                    "success": False,
                    "error": response_data.get("message", "Payment processing failed"),
                    "details": response_data
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _format_card_data(self, card_data):
        """Format card data for Clover API"""
        # Clover expects card data in a specific format
        return {
            "number": card_data.get("number"),
            "exp_month": card_data.get("exp_month"),
            "exp_year": card_data.get("exp_year"),
            "cvv": card_data.get("cvv"),
            "name": card_data.get("name", "")  # Cardholder name (optional)
        }
    
    def get_payment_token(self, card_data):
        """
        Get a payment token from Clover for later use
        This is useful for saving cards for future payments
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.private_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.api_url}/merchants/{self.merchant_id}/tokens" if self.merchant_id else f"{self.api_url}/tokens"
            
            response = requests.post(
                url,
                json=self._format_card_data(card_data),
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "success": True,
                    "token": data.get("id"),
                    "card_last_four": data.get("first6last4", "")[-4:] if data.get("first6last4") else "",
                    "card_brand": data.get("card_type")
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create payment token"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }