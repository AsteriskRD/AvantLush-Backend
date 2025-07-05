This documentation provides all the necessary API endpoints and payloads for integrating Clover Hosted Checkout with the AvantLush frontend.

🔗 Base URLs
Development: http://localhost:8000
Production: https://avantlush-backend-2s6k.onrender.com

🛒 1. Create Clover Hosted Checkout Session
Endpoint
POST /api/checkout/create-session/

Copy

Apply

Description
Creates a Clover hosted checkout session and returns a checkout URL for payment processing.

Request Headers
{
  "Content-Type": "application/json",
  "Authorization": "Bearer <jwt_token>" // Optional for authenticated users
}

Copy

Apply

Request Payload
{
  "payment_method": "clover_hosted",
  "order_data": {
    "total_amount": 29.99,
    "order_number": "ORDER-20250105-001", // Optional - auto-generated if not provided
    "currency": "USD", // Optional - defaults to USD
    "customer": {
      "email": "customer@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "phoneNumber": "555-123-4567" // Optional
    },
    "redirect_urls": { // Optional - uses default if not provided
      "success": "https://yourfrontend.com/checkout/success",
      "failure": "https://yourfrontend.com/checkout/failure",
      "cancel": "https://yourfrontend.com/checkout/cancel"
    },
    "items": [ // Optional - for order tracking
      {
        "name": "Product Name",
        "price": 19.99,
        "quantity": 1,
        "description": "Product description"
      }
    ]
  }
}

Copy

Apply

Success Response (200)
{
  "is_success": true,
  "data": {
    "status": "success",
    "message": "Hosted checkout session created successfully",
    "checkout_url": "https://sandbox.dev.clover.com/checkout/b88e2368-7e98-40b1-8e21-41a143234aa1?mode=checkout",
    "session_id": "b88e2368-7e98-40b1-8e21-41a143234aa1",
    "order_id": "b88e2368-7e98-40b1-8e21-41a143234aa1",
    "integration_type": "clover_hosted_official",
    "expires_at": "2025-07-04T23:57:25.541+0000",
    "created_at": "2025-07-04T23:42:25.575+0000",
    "clover_config": {
      "environment": "SANDBOX",
      "merchantId": "X4SS3ZCHCN4S1",
      "sessionId": "b88e2368-7e98-40b1-8e21-41a143234aa1",
      "amount": 2999, // Amount in cents
      "currency": "USD",
      "redirect_urls": {
        "success": "https://yourfrontend.com/checkout/success",
        "failure": "https://yourfrontend.com/checkout/failure"
      },
      "customer": {
        "email": "customer@example.com",
        "firstName": "John",
        "lastName": "Doe",
        "phoneNumber": "555-123-4567"
      }
    }
  }
}

Copy

Apply

Error Response (400/500)
{
  "is_success": false,
  "data": {
    "status": "error",
    "message": "total_amount is required"
  }
}

Copy

Apply

🎯 2. Alternative Endpoint (Simplified)
Endpoint
POST /api/create-hosted-checkout/

Copy

Apply

Description
Simplified endpoint specifically for Clover hosted checkout creation.

Request Payload
{
  "total_amount": 29.99,
  "currency": "USD",
  "customer": {
    "email": "customer@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "phoneNumber": "555-123-4567"
  },
  "success_url": "https://yourfrontend.com/checkout/success",
  "failure_url": "https://yourfrontend.com/checkout/failure",
  "cancel_url": "https://yourfrontend.com/checkout/cancel"
}

Copy

Apply

Success Response
{
  "is_success": true,
  "data": {
    "status": "success",
    "checkout_url": "https://sandbox.dev.clover.com/checkout/session-id?mode=checkout",
    "session_id": "session-id",
    "order_id": "order-id"
  }
}

Copy

Apply

📋 3. Get Available Payment Methods
Endpoint
GET /api/checkout/payment-methods/

Copy

Apply

Description
Returns list of available payment methods including Clover.

Response
{
  "success": true,
  "payment_methods": [
    {
      "id": "clover_hosted",
      "name": "Clover Hosted Checkout",
      "description": "Secure payment processing with Clover",
      "type": "redirect",
      "enabled": true
    },
    {
      "id": "stripe",
      "name": "Credit/Debit Card",
      "description": "Pay with Visa, Mastercard, etc.",
      "type": "card",
      "enabled": true
    }
  ]
}

Copy

Apply

🔄 4. Payment Status Check
Endpoint
GET /api/checkout/clover-hosted/status/{order_id}/

Copy

Apply

Description
Check the payment status of a Clover hosted checkout session.

Response
{
  "status": "success",
  "payment_status": "completed",
  "order_id": "order-id",
  "session_id": "session-id",
  "amount": 29.99,
  "currency": "USD",
  "transaction_id": "clover-transaction-id"
}

Copy

Apply

🎨 Frontend Integration Examples
React/JavaScript Example
// Create Clover checkout session
const createCloverCheckout = async (orderData) => {
  try {
    const response = await fetch('/api/checkout/create-session/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userToken}` // If user is authenticated
      },
      body: JSON.stringify({
        payment_method: 'clover_hosted',
        order_data: {
          total_amount: orderData.total,
          customer: {
            email: orderData.customerEmail,
            firstName: orderData.firstName,
            lastName: orderData.lastName,
            phoneNumber: orderData.phone
          },
          redirect_urls: {
            success: `${window.location.origin}/checkout/success`,
            failure: `${window.location.origin}/checkout/failure`,
            cancel: `${window.location.origin}/checkout/cancel`
          }
        }
      })
    });

    const result = await response.json();
    
    if (result.is_success) {
      // Redirect user to Clover hosted checkout
      window.location.href = result.data.checkout_url;
    } else {
      console.error('Checkout creation failed:', result.data.message);
    }
  } catch (error) {
    console.error('Error creating checkout:', error);
  }
};

// Usage
const handleCloverPayment = () => {
  const orderData = {
    total: 29.99,
    customerEmail: 'customer@example.com',
    firstName: 'John',
    lastName: 'Doe',
    phone: '555-123-4567'
  };
  
  createCloverCheckout(orderData);
};

Copy

Apply

React Component Example
import React, { useState } from 'react';

const CloverCheckout = ({ orderTotal, customerInfo }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePayment = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/checkout/create-session/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          payment_method: 'clover_hosted',
          order_data: {
            total_amount: orderTotal,
            customer: customerInfo,
            redirect_urls: {
              success: `${window.location.origin}/checkout/success`,
              failure: `${window.location.origin}/checkout/failure`,
              cancel: `${window.location.origin}/checkout/cancel`
            }
          }
        })
      });

      const result = await response.json();
      
      if (result.is_success) {
        // Redirect to Clover hosted checkout
        window.location.href = result.data.checkout_url;
      } else {
        setError(result.data.message);
      }
    } catch (err) {
      setError('Payment initialization failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="clover-checkout">
      <button 
        onClick={handlePayment}
        disabled={loading}
        className="pay-button"
      >
        {loading ? 'Processing...' : `Pay $${orderTotal} with Clover`}
      </button>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
    </div>
  );
};

export default CloverCheckout;

Copy

Apply

🔄 Frontend Redirect Handling
Success Page Component
import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

const CheckoutSuccess = () => {
  const [searchParams] = useSearchParams();
  const [paymentData, setPaymentData] = useState(null);
  
  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    const orderId = searchParams.get('order_id');
    
    if (sessionId) {
      // Optionally verify payment status with backend
      verifyPayment(sessionId, orderId);
    }
  }, [searchParams]);

  const verifyPayment = async (sessionId, orderId) => {
    try {
      const response = await fetch(`/api/checkout/clover-hosted/status/${orderId}/`);
      const data = await response.json();
      setPaymentData(data);
    } catch (error) {
      console.error('Error verifying payment:', error);
    }
  };

  return (
    <div className="success-page">
      <h1>🎉 Payment Successful!</h1>
      <p>Thank you for your purchase!</p>
      {paymentData && (
        <div>
          <p>Order ID: {paymentData.order_id}</p>
          <p>Amount: ${paymentData.amount}</p>
        </div>
      )}
      <button onClick={() => window.location.href = '/'}>
        Continue Shopping
      </button>
    </div>
  );
};

Copy

Apply

🧪 Testing Information
Test Card Numbers
Visa: 4005 5192 0000 0004
Mastercard: 5555 5555 5555 4444
Discover: 6011 3610 0000 6668

Expiry: Any future date (e.g., 12/25)
CVV: Any 3-digit number (e.g., 123)
ZIP: Any 5-digit number (e.g., 12345)

Copy

Apply

Environment URLs
Sandbox: https://sandbox.dev.clover.com/checkout/
Production: https://checkout.clover.com/

Copy

Apply

🔒 Security Notes
HTTPS Required: All redirect URLs must use HTTPS in production
CORS: Backend is configured to accept requests from your frontend domain
Authentication: User authentication is optional but recommended for order tracking
Webhook Verification: Payment confirmations are handled via secure webhooks
🚨 Error Handling
Common Error Codes
{
  "is_success": false,
  "data": {
    "status": "error",
    "message": "total_amount is required"
  }
}

Copy

Apply

Possible Error Messages:

"total_amount is required"
"Invalid payment method"
"Failed to create Clover order"
"Customer email is required"
"Checkout session creation failed"