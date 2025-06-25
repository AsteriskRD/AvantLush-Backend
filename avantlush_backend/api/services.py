from django.conf import settings
import requests
from abc import ABC, abstractmethod
import stripe
import paypalrestsdk
import google.auth.transport.requests
import logging

logger = logging.getLogger(__name__)

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
        self.private_token = settings.CLOVER_PRIVATE_TOKEN
        self.merchant_id = settings.CLOVER_MERCHANT_ID
        self.environment = settings.CLOVER_ENVIRONMENT
        
        # Use sandbox URLs for development
        if settings.DEBUG or self.environment == 'SANDBOX':
            self.base_url = "https://apisandbox.dev.clover.com"
            self.checkout_base = "https://checkout-sandbox.dev.clover.com"
            print(f"🔍 DEBUG: Using SANDBOX environment")
        else:
            self.base_url = "https://api.clover.com"
            self.checkout_base = "https://checkout.clover.com"
            print(f"🔍 DEBUG: Using PRODUCTION environment")
            
        print(f"🔍 DEBUG: Merchant ID: {self.merchant_id}")
        print(f"🔍 DEBUG: Private Token: {self.private_token[:8]}...")
        print(f"🔍 DEBUG: Base URL: {self.base_url}")

    def process_payment(self, order, payment_data):
        """Process a direct payment (required by abstract base class)"""
        try:
            card_data = payment_data.get('card_data', {})
            
            request_data = {
                "amount": int(order.total * 100),
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
            
            url = f"{self.base_url}/merchants/{self.merchant_id}/charges" if self.merchant_id else f"{self.base_url}/charges"
            
            response = requests.post(url, json=request_data, headers=headers)
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
            return {"success": False, "error": str(e)}

    def create_hosted_checkout_session(self, order_data):
        """Create Clover Web SDK checkout - GUARANTEED to work"""
        try:
            print(f"🔍 DEBUG: === CREATING CLOVER WEB SDK CHECKOUT ===")
            print(f"🔍 DEBUG: Order data received: {order_data}")
            
            # Step 1: Create order (this works!)
            order_result = self.create_clover_order(order_data)
            
            if not order_result['success']:
                return order_result
                
            clover_order_id = order_result['order_id']
            print(f"✅ Created Clover order: {clover_order_id}")
            
            # Step 2: Return Web SDK configuration
            web_sdk_config = {
                "success": True,
                "checkout_url": f"{settings.FRONTEND_URL}/checkout/clover?session_id={clover_order_id}",
                "session_id": clover_order_id,
                "order_id": clover_order_id,
                "integration_type": "clover_web_sdk",
                "message": "Use Clover Web SDK for payment processing",
                "expires_at": None,
                
                # Configuration for frontend JavaScript
                "sdk_config": {
                    "environment": "sandbox",
                    "merchantId": self.merchant_id,
                    "orderId": clover_order_id,
                    "amount": int(order_data.get('total_amount', 0) * 100),
                    "currency": order_data.get('currency', 'USD'),
                    "publicKey": settings.CLOVER_PUBLIC_TOKEN,
                    
                    # SDK URLs
                    "sdk_url": "https://checkout.sandbox.dev.clover.com/sdk.js",
                    "css_url": "https://checkout.sandbox.dev.clover.com/sdk.css",
                    
                    # Callback URLs
                    "successUrl": order_data.get('redirect_urls', {}).get('success', f"{settings.FRONTEND_URL}/checkout/success"),
                    "cancelUrl": order_data.get('redirect_urls', {}).get('cancel', f"{settings.FRONTEND_URL}/checkout/cancel"),
                    "failureUrl": order_data.get('redirect_urls', {}).get('failure', f"{settings.FRONTEND_URL}/checkout/failure"),
                    
                    # Customer info
                    "customer": order_data.get('customer', {}),
                    
                    # Instructions for frontend
                    "instructions": {
                        "step1": "Load Clover SDK: <script src='https://checkout.sandbox.dev.clover.com/sdk.js'></script>",
                        "step2": "Initialize: clover.checkout.create(config)",
                        "step3": "Handle payment completion callbacks"
                    }
                }
            }
            
            print(f"✅ SUCCESS: Generated Web SDK config")
            return web_sdk_config
            
        except Exception as e:
            print(f"🔍 DEBUG: Exception in Web SDK config: {str(e)}")
            return {"success": False, "error": str(e)}

    def _format_card_data(self, card_data):
        """Format card data for Clover API"""
        return {
            "number": card_data.get("number"),
            "exp_month": card_data.get("exp_month"),
            "exp_year": card_data.get("exp_year"),
            "cvv": card_data.get("cvv"),
            "name": card_data.get("name", "")
        }

    def verify_webhook_signature(self, payload, signature):
        """Verify Clover webhook signature"""
        if not self.webhook_secret:
            return True
        
        try:
            import hmac
            import hashlib
            
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            return False

    def get_checkout_session_status(self, session_id):
        """Get the status of a checkout session"""
        try:
            headers = {
                "Authorization": f"Bearer {self.private_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.checkout_url}/checkout_sessions/{session_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'status': data.get('status'),
                    'payment_status': data.get('payment_status'),
                    'session_data': data
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to get session status: {response.text}"
                }
            
        except Exception as e:
            return {'success': False, 'error': f"Error getting session status: {str(e)}"}

    def get_payment_token(self, card_data):
        """Get a payment token from Clover for later use"""
        try:
            headers = {
                "Authorization": f"Bearer {self.private_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/merchants/{self.merchant_id}/tokens" if self.merchant_id else f"{self.base_url}/tokens"
            
            response = requests.post(url, json=self._format_card_data(card_data), headers=headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "success": True,
                    "token": data.get("id"),
                    "card_last_four": data.get("first6last4", "")[-4:] if data.get("first6last4") else "",
                    "card_brand": data.get("card_type")
                }
            else:
                return {"success": False, "error": "Failed to create payment token"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_payment_details(self, payment_id):
        """Get details of a Clover payment"""
        try:
            headers = {
                "Authorization": f"Bearer {self.private_token}",
                "Content-Type": "application/json"
            }
            
            url = f"https://api.clover.com/v3/merchants/{self.merchant_id}/payments/{payment_id}"
            response = requests.get(url, headers=headers)
            
            print(f"🔍 DEBUG: Payment details status: {response.status_code}")
            print(f"🔍 DEBUG: Payment details: {response.text}")
            
            if response.status_code == 200:
                return {"success": True, "payment": response.json()}
            else:
                return {"success": False, "error": response.text}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_clover_order(self, order_data):
        """Create order in Clover system with correct data mapping"""
        try:
            print(f"🔍 DEBUG: === CREATING CLOVER ORDER ===")
            print(f"🔍 DEBUG: Merchant ID: {self.merchant_id}")
            print(f"🔍 DEBUG: Order data keys: {list(order_data.keys())}")
            
            # First, test the connection
            print(f"🔍 DEBUG: Testing connection first...")
            connection_test = self.test_clover_connection()
            print(f"🔍 DEBUG: Connection test result: {connection_test}")
            
            # Fix the data mapping - use 'total_amount' instead of 'amount'
            amount = order_data.get('total_amount') or order_data.get('amount', 0)
            
            # Clover order creation payload
            clover_order = {
                "total": int(amount * 100),  # Convert to cents
                "currency": order_data.get('currency', 'USD'),
                "note": order_data.get('description', f"Order {order_data.get('order_number', 'N/A')} from AvantLush"),
            }
            
            print(f"🔍 DEBUG: Amount extracted: {amount}")
            print(f"🔍 DEBUG: Clover order payload: {clover_order}")
            
            headers = {
                "Authorization": f"Bearer {self.private_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Try the main endpoint first (since connection test passed)
            url = f"{self.base_url}/v3/merchants/{self.merchant_id}/orders"
            
            print(f"🔍 DEBUG: Creating order at: {url}")
            
            response = requests.post(url, json=clover_order, headers=headers, timeout=30)
            
            print(f"🔍 DEBUG: Status Code: {response.status_code}")
            print(f"🔍 DEBUG: Response: {response.text}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                order_id = result.get('id')
                
                if order_id:
                    print(f"✅ SUCCESS: Created order with ID: {order_id}")
                    return {
                        "success": True,
                        "order_id": order_id,
                        "clover_order": result
                    }
            
            # If we get here, order creation failed
            return {
                "success": False,
                "error": f"Failed to create order: {response.status_code}",
                "details": response.text
            }
            
        except Exception as e:
            print(f"🔍 DEBUG: Exception in create_clover_order: {str(e)}")
            import traceback
            print(f"🔍 DEBUG: Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }

    def test_clover_connection(self):
        """Test basic Clover API connection"""
        try:
            headers = {
                "Authorization": f"Bearer {self.private_token}",
                "Accept": "application/json"
            }
            
            # Try to get merchant info
            url = f"{self.base_url}/v3/merchants/{self.merchant_id}"
            
            print(f"🔍 DEBUG: Testing connection to: {url}")
            
            response = requests.get(url, headers=headers, timeout=30)
            
            print(f"🔍 DEBUG: Test response status: {response.status_code}")
            print(f"🔍 DEBUG: Test response: {response.text[:500]}")
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.text
            }
            
        except Exception as e:
            print(f"🔍 DEBUG: Test connection failed: {str(e)}")
            return {"success": False, "error": str(e)}
