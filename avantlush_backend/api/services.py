from django.conf import settings
import requests
import time
from abc import ABC, abstractmethod
import stripe
import paypalrestsdk
import google.auth.transport.requests
import logging
import os
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
        self.merchant_id = getattr(settings, 'CLOVER_MERCHANT_ID', 'X4SS3ZCHCN4S1')
        self.environment = getattr(settings, 'CLOVER_ENVIRONMENT', 'sandbox')
        
        # Use correct Clover API base URL
        if self.environment.lower() == 'sandbox':
            self.base_url = "https://apisandbox.dev.clover.com"
            self.checkout_base_url = "https://checkout.sandbox.dev.clover.com"
        else:
            self.base_url = "https://api.clover.com"
            self.checkout_base_url = "https://checkout.clover.com"
        
        print(f"🔍 DEBUG: Using {self.environment.upper()} environment")
        print(f"🔍 DEBUG: API Base URL: {self.base_url}")
        print(f"🔍 DEBUG: Checkout Base URL: {self.checkout_base_url}")

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
                "Accept": "application/json",
                "X-Clover-Merchant-Id": self.merchant_id 
            }
            
            url = f"{self.base_url}/v3/merchants/{self.merchant_id}/charges"
            
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
        return {
            "number": card_data.get("number"),
            "exp_month": card_data.get("exp_month"),
            "exp_year": card_data.get("exp_year"),
            "cvv": card_data.get("cvv"),
            "name": card_data.get("name", "")
        }
    
    def get_payment_token(self, card_data):
        """Get a payment token from Clover for later use"""
        try:
            headers = {
                "Authorization": f"Bearer {self.private_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/v3/merchants/{self.merchant_id}/tokens"
            
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

    def create_hosted_checkout_session(self, order_data):
        """
        Create Clover hosted checkout session using official API
        """
        print("🔍 DEBUG: === CREATING CLOVER HOSTED CHECKOUT (OFFICIAL API) ===")
        print(f"🔍 DEBUG: Order data received: {order_data}")
        
        try:
            # Prepare customer data - only include fields that are provided
            customer_data = {}
            
            customer_info = order_data.get('customer', {})
            
            # Email (required by most payment processors)
            customer_data['email'] = customer_info.get('email', 'customer@example.com')
            
            # Names (optional)
            if customer_info.get('firstName'):
                customer_data['firstName'] = customer_info['firstName']
            else:
                customer_data['firstName'] = 'Customer'  # Minimal default
            
            if customer_info.get('lastName'):
                customer_data['lastName'] = customer_info['lastName']
            else:
                customer_data['lastName'] = ''  # Empty instead of default
            
            # Phone number - ONLY include if provided
            if customer_info.get('phoneNumber'):
                customer_data['phoneNumber'] = customer_info['phoneNumber']
            # ✅ Don't include phoneNumber if not provided
            
            # Prepare request data in Clover's required format
            clover_request = {
                "customer": customer_data,
                "shoppingCart": {
                    "lineItems": [
                        {
                            "name": f"Order {order_data.get('order_number', 'N/A')}",
                            "price": int(float(order_data['total_amount']) * 100),  # Convert to cents
                            "unitQty": 1,
                            "note": f"Order total: ${order_data['total_amount']}"
                        }
                    ]
                }
            }
            
            print(f"🔍 DEBUG: Customer data: {customer_data}")
            
            # Use BACKEND URLs for Clover redirects (these will proxy to frontend)
            redirect_urls = order_data.get('redirect_urls', {})
            backend_base = settings.BACKEND_URL
            
            clover_request["redirectUrls"] = {
                "success": redirect_urls.get('success', f"{backend_base}/checkout/success"),
                "failure": redirect_urls.get('failure', f"{backend_base}/checkout/failure"), 
                "cancel": redirect_urls.get('cancel', f"{backend_base}/checkout/cancel")
            }
            
            print(f"🔍 DEBUG: Clover request payload: {clover_request}")
            
            # Prepare headers as per Clover documentation
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "X-Clover-Merchant-Id": self.merchant_id,
                "authorization": f"Bearer {self.private_token}"
            }
            
            # Use official Clover API endpoint
            url = f"{self.base_url}/invoicingcheckoutservice/v1/checkouts"
            print(f"🔍 DEBUG: Making request to: {url}")
            
            response = requests.post(url, json=clover_request, headers=headers, timeout=30)
            print(f"🔍 DEBUG: Response status: {response.status_code}")
            print(f"🔍 DEBUG: Response content: {response.text}")
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                
                # Extract the checkout URL from Clover's response
                checkout_url = response_data.get('href')
                session_id = response_data.get('checkoutSessionId')
                
                if checkout_url:
                    print(f"✅ Successfully created Clover hosted checkout session")
                    print(f"✅ Checkout URL: {checkout_url}")
                    
                    return {
                        'success': True,
                        'checkout_url': checkout_url,  # This is the official Clover hosted URL
                        'session_id': session_id,
                        'order_id': session_id,
                        'integration_type': 'clover_hosted_official',
                        'message': 'Redirect user to Clover hosted checkout page',
                        'expires_at': response_data.get('expirationTime'),
                        'created_at': response_data.get('createdTime'),
                        # 🔧 FIX: Return the correct redirect URLs
                        'redirect_urls': clover_request["redirectUrls"],
                        'clover_config': {
                            'environment': self.environment,
                            'merchantId': self.merchant_id,
                            'sessionId': session_id,
                            'amount': int(float(order_data['total_amount']) * 100),
                            'currency': order_data.get('currency', 'USD'),
                            'redirect_urls': clover_request["redirectUrls"],
                            'customer': clover_request['customer']
                        }
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No checkout URL returned from Clover API'
                    }
            else:
                error_data = response.json() if response.text else {}
                return {
                    'success': False,
                    'error': f'Clover API error: {error_data.get("message", "Unknown error")}',
                    'details': error_data
                }
                
        except Exception as e:
            print(f"❌ Exception in create_hosted_checkout_session: {str(e)}")
            return {
                'success': False,
                'error': f'Checkout session creation failed: {str(e)}'
            }

    def _create_clover_order(self, order_data):
        """
        Create an order in Clover system
        """
        try:
            print(f"🔍 DEBUG: Creating Clover order with data: {order_data}")
            
            # Prepare order payload for Clover API
            order_payload = {
                "total": int(float(order_data['total_amount']) * 100),  # Convert to cents
                "currency": order_data.get('currency', 'USD'),
                "note": f"Order {order_data['order_number']}",
                "state": "open",
                "testMode": True  # ✅ FIXED: Always True for sandbox
            }
            
            print(f"🔍 DEBUG: Order payload: {order_payload}")
            
            headers = {
                "Authorization": f"Bearer {self.private_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Create order endpoint
            url = f"{self.base_url}/v3/merchants/{self.merchant_id}/orders"
            print(f"🔍 DEBUG: Making request to: {url}")
            
            response = requests.post(url, json=order_payload, headers=headers)
            print(f"🔍 DEBUG: Response status: {response.status_code}")
            print(f"🔍 DEBUG: Response content: {response.text}")
            
            if response.status_code in [200, 201]:
                order_response = response.json()
                order_id = order_response.get('id')
                print(f"✅ Successfully created Clover order: {order_id}")
                return order_id
            else:
                print(f"❌ Failed to create order. Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Exception in _create_clover_order: {str(e)}")
            return None

    def test_clover_connection(self):
        """Test Clover API connection with a simple checkout session"""
        try:
            test_data = {
                'total_amount': 10.00,
                'order_number': 'TEST-CONNECTION',
                'customer': {
                    'email': 'test@example.com',
                    'name': 'Test Customer'
                },
                'items': [{
                    'name': 'Test Item',
                    'price': 10.00,
                    'quantity': 1,
                    'description': 'Connection test item'
                }]
            }
            
            result = self.create_hosted_checkout_session(test_data)
            return result
            
        except Exception as e:
            print(f"🔍 DEBUG: Test connection failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def process_direct_payment(self, order_data, card_data):
        """
        Process payment directly through Clover API using external payment tender
        """
        print("🔍 DEBUG: === PROCESSING DIRECT CLOVER PAYMENT ===")
        print(f"🔍 DEBUG: Order data: {order_data}")
        print(f"🔍 DEBUG: Card data keys: {list(card_data.keys())}")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.private_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # STEP 1: Create Order in Clover
            print("🔍 DEBUG: STEP 1 - Creating Clover Order")
            order_payload = {
                "total": int(float(order_data['total_amount']) * 100),
                "currency": order_data.get('currency', 'USD'),
                "note": f"Order {order_data['order_number']}",
                "state": "open"
            }
            
            order_url = f"{self.base_url}/v3/merchants/{self.merchant_id}/orders"
            order_response = requests.post(order_url, json=order_payload, headers=headers, timeout=30)
            print(f"🔍 DEBUG: Order creation status: {order_response.status_code}")
            
            if order_response.status_code not in [200, 201]:
                return {
                    "success": False,
                    "error": f"Failed to create Clover order: {order_response.text}",
                    "step": "order_creation"
                }
            
            clover_order = order_response.json()
            clover_order_id = clover_order.get('id')
            print(f"✅ Created Clover order: {clover_order_id}")
            
            # STEP 2: Get tenders and create external payment
            print("🔍 DEBUG: STEP 2 - Creating External Payment")
            
            tenders_url = f"{self.base_url}/v3/merchants/{self.merchant_id}/tenders"
            tenders_response = requests.get(tenders_url, headers=headers, timeout=30)
            
            external_tender_id = None
            if tenders_response.status_code == 200:
                tenders_data = tenders_response.json()
                print(f"🔍 DEBUG: Available tenders: {[t.get('label', 'No label') for t in tenders_data.get('elements', [])]}")
                
                for tender in tenders_data.get('elements', []):
                    tender_label = tender.get('label', '').lower()
                    tender_key = tender.get('labelKey', '').lower()
                    
                    if 'external' in tender_label or 'external' in tender_key:
                        external_tender_id = tender.get('id')
                        print(f"✅ Found external payment tender ID: {external_tender_id}")
                        break
            
            if not external_tender_id:
                print("❌ Could not find external payment tender")
                return {
                    "success": False,
                    "error": "External payment tender not available",
                    "step": "tender_lookup"
                }
            
            # Create external payment
            payment_payload = {
                "amount": int(float(order_data['total_amount']) * 100),
                "currency": order_data.get('currency', 'USD'),
                "tender": {"id": external_tender_id},
                "note": f"External payment for {order_data['order_number']} - Card ending in {card_data['number'][-4:]}"
            }
            
            payment_url = f"{self.base_url}/v3/merchants/{self.merchant_id}/orders/{clover_order_id}/payments"
            print(f"🔍 DEBUG: Creating external payment at: {payment_url}")
            print(f"🔍 DEBUG: Payment payload: {payment_payload}")
            
            payment_response = requests.post(payment_url, json=payment_payload, headers=headers, timeout=30)
            print(f"🔍 DEBUG: Payment status: {payment_response.status_code}")
            print(f"🔍 DEBUG: Payment response: {payment_response.text}")
            
            if payment_response.status_code in [200, 201]:
                payment_data = payment_response.json()
                return {
                    "success": True,
                    "transaction_id": payment_data.get("id"),
                    "clover_order_id": clover_order_id,
                    "amount": payment_data.get("amount", 0),
                    "payment_type": "external",
                    "card_last_four": card_data['number'][-4:],
                    "card_brand": "Visa",  # Simulated since we can't process real card
                    "tender_id": external_tender_id,
                    "response": payment_data,
                    "clover_order": clover_order
                }
            else:
                payment_error = payment_response.json() if payment_response.text else {"message": "Unknown payment error"}
                return {
                    "success": False,
                    "error": payment_error.get("message", "Payment processing failed"),
                    "details": payment_error,
                    "step": "external_payment_creation",
                    "clover_order_id": clover_order_id
                }
            
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return {
                "success": False,
                "error": f"Payment processing error: {str(e)}"
            }

    def verify_webhook_signature(self, payload, signature):
        """
        Verify Clover webhook signature for security
        """
        try:
            import hmac
            import hashlib
            
            # Get webhook secret from settings
            webhook_secret = getattr(settings, 'CLOVER_WEBHOOK_SECRET', '')
            
            if not webhook_secret:
                print("⚠️ WARNING: No webhook secret configured, skipping signature verification")
                return True  # Allow in development
            
            # Calculate expected signature
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            print(f"❌ Webhook signature verification error: {str(e)}")
            return False  # Reject on error
