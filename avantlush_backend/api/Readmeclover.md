# Clover Hosted Checkout Integration Documentation

This documentation provides all the necessary API endpoints and payloads for integrating Clover Hosted Checkout with the AvantLush frontend.

## 🔗 Base URLs
- **Development**: `http://localhost:8000`
- **Production**: `https://avantlush-backend-2s6k.onrender.com`

## 🔐 Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

---

## 🛒 1. Create Clover Hosted Checkout Session (Authenticated)

### Endpoint
```
POST /api/create-hosted-checkout/
```

### Description
Creates a Clover hosted checkout session for authenticated users. This endpoint creates an order in the database first, then generates a Clover checkout URL.

### Authentication
**Required**: JWT token in Authorization header

### Request Headers
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer <jwt_token>"
}
```

### Request Payload
```json
{
  "total_amount": 29.99,
  "currency": "USD",
  "shipping_cost": 4.99,
  "shipping_address": {
    "street_address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "country": "US",
    "zip_code": "10001"
  }
}
```

### Success Response (200)
```json
{
  "is_success": true,
  "data": {
    "status": "success",
    "message": "Order created for user@example.com",
    "order_id": 88,
    "order_number": "ORD-20250105-001",
    "checkout_url": "https://sandbox.dev.clover.com/checkout/4de24107-dd60-4f50-b474-37e049a61b40?mode=checkout",
    "session_id": "4de24107-dd60-4f50-b474-37e049a61b40",
    "total_amount": 29.99,
    "user_email": "user@example.com",
    "instructions": "Visit checkout_url to complete payment"
  }
}
```

### Error Response (401 - Unauthorized)
```json
{
  "is_success": false,
  "data": {
    "status": "error",
    "message": "Authentication required. Please login first.",
    "code": "AUTH_REQUIRED"
  }
}
```

### Error Response (400 - Bad Request)
```json
{
  "is_success": false,
  "data": {
    "status": "error",
    "message": "total_amount is required"
  }
}
```

---

## 🧪 2. Create Clover Hosted Checkout Session (Test - No Auth)


### Endpoint
```
POST /api/create-hosted-checkout-test/
```

### Description
**Development/Testing Only**: Creates a Clover hosted checkout session without authentication using a test user.

### Authentication
**Not Required**: Uses test user automatically

### Request Headers
```json
{
  "Content-Type": "application/json"
}
```

### Request Payload
```json
{
  "total_amount": 29.99,
  "currency": "USD",
  "shipping_cost": 4.99
}
```

### Success Response (200)
```json
{
  "is_success": true,
  "data": {
    "status": "success",
    "message": "Test order created for test-checkout@example.com",
    "order_id": 88,
    "order_number": "ORD-20250105-001",
    "checkout_url": "https://sandbox.dev.clover.com/checkout/4de24107-dd60-4f50-b474-37e049a61b40?mode=checkout",
    "session_id": "4de24107-dd60-4f50-b474-37e049a61b40",
    "total_amount": 29.99,
    "user_email": "test-checkout@example.com",
    "instructions": "Visit checkout_url to complete payment"
  }
}
```

---

## 🔄 3. Alternative Checkout Session Creation

### Endpoint
```
POST /api/checkout/create-session/
```

### Description
Alternative endpoint that supports multiple payment methods including Clover hosted checkout.

### Request Headers
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer <jwt_token>"
}
```

### Request Payload
```json
{
  "payment_method": "clover_hosted",
  "order_data": {
    "total_amount": 29.99,
    "currency": "USD",
    "customer": {
      "email": "customer@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "phoneNumber": "555-123-4567"
    },
    "redirect_urls": {
      "success": "https://yourfrontend.com/checkout/success",
      "failure": "https://yourfrontend.com/checkout/failure",
      "cancel": "https://yourfrontend.com/checkout/cancel"
    }
  }
}
```

---

## 📋 4. Get Available Payment Methods

### Endpoint
```
GET /api/checkout/payment-methods/
```

### Description
Returns list of available payment methods including Clover.

### Authentication
**Not Required**

### Response
```json
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
```

---

## 🔄 5. Payment Status Check

### Endpoint
```
GET /api/orders/<order_id>/payment-status/
```

### Description
Check the payment status of a Clover hosted checkout session.

### Authentication
**Required**: JWT token

### Response
```json
{
  "status": "success",
  "payment_status": "completed",
  "order_id": 88,
  "order_number": "ORD-20250105-001",
  "session_id": "4de24107-dd60-4f50-b474-37e049a61b40",
  "amount": 29.99,
  "currency": "USD",
  "transaction_id": "clover-transaction-id"
}
```

---

## 📦 6. Get User Orders

### Endpoint
```
GET /api/orders/
```

### Description
Get all orders for the authenticated user.

### Authentication
**Required**: JWT token

### Response
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 88,
      "order_number": "ORD-20250105-001",
      "status": "PENDING",
      "payment_status": "PENDING",
      "total": "29.99",
      "created_at": "2025-01-05T10:30:00Z",
      "clover_session_id": "4de24107-dd60-4f50-b474-37e049a61b40"
    }
  ]
}
```

---

## 🎨 Frontend Integration Examples

### React/JavaScript Example (Authenticated)

```javascript
// 1. Login and get JWT token
const loginUser = async (email, password) => {
  const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  if (data.access_token) {
    localStorage.setItem('jwt_token', data.access_token);
    return data.access_token;
  }
  throw new Error('Login failed');
};

// 2. Create Clover checkout session
const createCloverCheckout = async (orderData) => {
  const token = localStorage.getItem('jwt_token');
  
  if (!token) {
    throw new Error('Please login first');
  }
  
  try {
    const response = await fetch('/api/create-hosted-checkout/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        total_amount: orderData.total,
        currency: 'USD',
        shipping_cost: orderData.shipping || 4.99,
        shipping_address: {
          street_address: orderData.address.street,
          city: orderData.address.city,
          state: orderData.address.state,
          country: orderData.address.country || 'US',
          zip_code: orderData.address.zip
        }
      })
    });

    const result = await response.json();
    
    if (result.is_success) {
      // Store order info for later reference
      localStorage.setItem('current_order_id', result.data.order_id);
      
      // Redirect user to Clover hosted checkout
      window.location.href = result.data.checkout_url;
    } else {
      throw new Error(result.data.message);
    }
  } catch (error) {
    console.error('Checkout creation failed:', error);
    throw error;
  }
};

// 3. Usage example
const handleCheckout = async () => {
  try {
    const orderData = {
      total: 29.99,
      shipping: 4.99,
      address: {
        street: '123 Main St',
        city: 'New York',
        state: 'NY',
        zip: '10001'
      }
    };
    
    await createCloverCheckout(orderData);
  } catch (error) {
    alert(`Checkout failed: ${error.message}`);
  }
};
```

### React Component Example

```jsx
import React, { useState } from 'react';

const CloverCheckout = ({ orderTotal, shippingAddress, onSuccess, onError }) => {
  const [loading, setLoading] = useState(false);

  const handlePayment = async () => {
    setLoading(true);
    
    try {
      const token = localStorage.getItem('jwt_token');
      
      if (!token) {
        throw new Error('Please login to continue');
      }

      const response = await fetch('/api/create-hosted-checkout/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          total_amount: orderTotal,
          currency: 'USD',
          shipping_cost: 4.99,
          shipping_address: shippingAddress
        })
      });

      const result = await response.json();
      
      if (result.is_success) {
        // Store order info
        localStorage.setItem('current_order_id', result.data.order_id);
        localStorage.setItem('current_order_number', result.data.order_number);
        
        // Redirect to Clover checkout
        window.location.href = result.data.checkout_url;
      } else {
        throw new Error(result.data.message);
      }
    } catch (error) {
      onError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="clover-checkout">
      <button 
        onClick={handlePayment}
        disabled={loading}
        className="checkout-button"
      >
        {loading ? 'Creating checkout...' : `Pay $${orderTotal} with Clover`}
      </button>
    </div>
  );
};

export default CloverCheckout;
```

---

## 🔄 Frontend Redirect Handling

### Success Page Component

```jsx
import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

const CheckoutSuccess = () => {
  const [searchParams] = useSearchParams();
  const [orderData, setOrderData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const verifyPayment = async () => {
      try {
        const orderId = localStorage.getItem('current_order_id');
        const token = localStorage.getItem('jwt_token');
        
        if (orderId && token) {
          const response = await fetch(`/api/orders/${orderId}/payment-status/`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          const data = await response.json();
          setOrderData(data);
        }
      } catch (error) {
        console.error('Error verifying payment:', error);
      } finally {
        setLoading(false);
      }
    };

    verifyPayment();
  }, []);

  if (loading) {
    return <div>Verifying payment...</div>;
  }

  return (
    <div className="success-page">
      <h1>🎉 Payment Successful!</h1>
      <p>Thank you for your purchase!</p>
      
      {orderData && (
        <div className="order-details">
          <p><strong>Order ID:</strong> {orderData.order_id}</p>
          <p><strong>Order Number:</strong> {orderData.order_number}</p>
          <p><strong>Amount:</strong> ${orderData.amount}</p>
          <p><strong>Status:</strong> {orderData.payment_status}</p>
        </div>
      )}
      
      <button onClick={() => window.location.href = '/'}>
        Continue Shopping
      </button>
    </div>
  );
};

export default CheckoutSuccess;
```

---

## 🧪 Testing Information

### Test Card Numbers (Clover Sandbox)
- **Visa**: `4005 5192 0000 0004`
- **Mastercard**: `5555 5555 5555 4444`
- **Discover**: `6011 3610 0000 6668`
- **Expiry**: Any future date (e.g., `12/25`)
- **CVV**: Any 3-digit number (e.g., `123`)
- **ZIP**: Any 5-digit number (e.g., `12345`)

### Environment URLs
- **Sandbox**: `https://sandbox.dev.clover.com/checkout/`
- **Production**: `https://checkout.clover.com/`

### Test Endpoints
Use the test endpoint for development without authentication:
```bash
curl -X POST https://avantlush-backend-2s6k.onrender.com/api/create-hosted-checkout-test/ \
  -H "Content-Type: application/json" \
  -d '{"total_amount": 29.99, "currency": "USD", "shipping_cost": 4.99}'
```

---

## 🔒 Security Notes

- **HTTPS Required**: All redirect URLs must use HTTPS in production
- **JWT Authentication**: Most endpoints require valid JWT tokens
- **CORS**: Backend is configured to accept requests from your frontend domain
- **Webhook Security**: Payment confirmations are handled via secure webhooks
- **Token Expiration**: JWT tokens expire after 60 minutes - handle refresh tokens
- **Environment Variables**: Never expose API keys in frontend code

---

## 🚨 Error Handling

### Common Error Responses

#### Authentication Errors
```json
{
  "is_success": false,
  "data": {
    "status": "error",
    "message": "Authentication required. Please login first.",
    "code": "AUTH_REQUIRED"
  }
}
```

#### Validation Errors
```json
{
  "is_success": false,
  "data": {
    "status": "error",
    "message": "total_amount is required"
  }
}
```

#### Server Errors
```json
{
  "is_success": false,
  "data": {
    "status": "error",
    "message": "Order creation failed: Database connection error"
  }
}
```

### Frontend Error Handling Example

```javascript
const handleCheckoutError = (error) => {
  if (error.message.includes('Authentication required')) {
    // Redirect to login
    window.location.href = '/login';
  } else if (error.message.includes('total_amount is required')) {
    // Show validation error
    showNotification('Please enter a valid amount', 'error');
  } else {
    // Generic error
    showNotification('Checkout failed. Please try again.', 'error');
  }
};

// Usage in checkout function
try {
  await createCloverCheckout(orderData);
} catch (error) {
  handleCheckoutError(error);
}
```

---

## 🔄 Webhook Handling

### Webhook Endpoint
```
POST /api/webhooks/clover-hosted/
```

### Description
Clover sends payment status updates to this endpoint. Your frontend doesn't need to call this directly - it's for backend processing only.

### Webhook Events
- Payment completed
- Payment failed
- Payment cancelled

### Order Status Updates
After webhook processing, order status will be updated:
- `PENDING` → `PROCESSING` (payment successful)
- `PENDING` → `FAILED` (payment failed)
- `PENDING` → `CANCELLED` (payment cancelled)

---

## 📱 Mobile Considerations

### Responsive Design
Clover checkout pages are mobile-responsive, but ensure your redirect URLs work on mobile devices.

### Deep Links
For mobile apps, configure proper deep link handling for success/failure URLs:

```javascript
// Example for React Native
const handleDeepLink = (url) => {
  if (url.includes('/checkout/success')) {
    // Handle success
    navigation.navigate('OrderSuccess');
  } else if (url.includes('/checkout/failure')) {
    // Handle failure
    navigation.navigate('OrderFailure');
  }
};
```

---

## 🚀 Production Deployment Checklist

### Backend Configuration
- [ ] Switch `CLOVER_ENVIRONMENT` to `PRODUCTION`
- [ ] Update `CLOVER_PRIVATE_TOKEN` with production token
- [ ] Update `CLOVER_MERCHANT_ID` with production merchant ID
- [ ] Configure production webhook URLs
- [ ] Enable HTTPS redirect (`SECURE_SSL_REDIRECT = True`)

### Frontend Configuration
- [ ] Update API base URL to production
- [ ] Configure production redirect URLs
- [ ] Test authentication flow
- [ ] Test checkout flow end-to-end
- [ ] Implement proper error handling
- [ ] Add loading states and user feedback

### Testing Checklist
- [ ] Test with real credit cards (small amounts)
- [ ] Verify webhook callbacks work
- [ ] Test order status updates
- [ ] Test authentication expiration handling
- [ ] Test mobile responsiveness
- [ ] Test error scenarios

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Authentication required" Error
**Problem**: JWT token missing or expired
**Solution**: 
```javascript
// Check token expiration
const token = localStorage.getItem('jwt_token');
if (!token) {
  // Redirect to login
  window.location.href = '/login';
}

// Validate token
const response = await fetch('/api/auth/validate-token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ token })
});
```

#### 2. "total_amount is required" Error
**Problem**: Missing or invalid amount in request
**Solution**:
```javascript
// Validate amount before sending
const amount = parseFloat(orderData.total);
if (!amount || amount <= 0) {
  throw new Error('Invalid order amount');
}
```

#### 3. Checkout URL Not Opening
**Problem**: Popup blockers or invalid URL
**Solution**:
```javascript
// Use window.location instead of window.open
window.location.href = checkoutUrl;

// Or handle popup blockers
const popup = window.open(checkoutUrl, '_blank');
if (!popup) {
  alert('Please allow popups for this site');
}
```

#### 4. Orders Not Showing After Payment
**Problem**: Webhook delay or processing issue
**Solution**:
```javascript
// Poll for order status updates
const pollOrderStatus = async (orderId) => {
  const maxAttempts = 10;
  let attempts = 0;
  
  while (attempts < maxAttempts) {
    const response = await fetch(`/api/orders/${orderId}/payment-status/`);
    const data = await response.json();
    
    if (data.payment_status === 'completed') {
      return data;
    }
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    attempts++;
  }
  
  throw new Error('Payment status check timeout');
};
```

---

## 📞 Support

### Development Support
- **Backend API**: Check server logs for detailed error messages
- **Frontend Integration**: Use browser developer tools to inspect network requests
- **Clover Issues**: Check Clover Developer Dashboard for transaction logs

### Useful Endpoints for Debugging
```bash
# Check if backend is running
GET /api/products/

# Validate JWT token
POST /api/auth/validate-token/
Body: {"token": "your-jwt-token"}

# Test checkout without auth
POST /api/create-hosted-checkout-test/
Body: {"total_amount": 10.99}

# Check user orders
GET /api/orders/
Headers: {"Authorization": "Bearer your-jwt-token"}
```

### Log Monitoring
Monitor these logs for issues:
- Django server logs for backend errors
- Browser console for frontend errors
- Clover Dashboard for payment processing issues

---

## 📈 Analytics and Monitoring

### Order Tracking
Track these metrics in your frontend:
- Checkout initiation rate
- Checkout completion rate
- Payment success rate
- Average order value

### Example Analytics Implementation
```javascript
// Track checkout initiation
const trackCheckoutStart = (orderData) => {
  analytics.track('Checkout Started', {
    order_value: orderData.total,
    payment_method: 'clover_hosted',
    user_id: getCurrentUserId()
  });
};

// Track checkout completion
const trackCheckoutComplete = (orderData) => {
  analytics.track('Order Completed', {
    order_id: orderData.order_id,
    order_value: orderData.total_amount,
    payment_method: 'clover_hosted'
  });
};
```

---

## 🎯 Next Steps

1. **Implement Authentication**: Set up user login/registration flow
2. **Add Cart Management**: Implement shopping cart functionality
3. **Order Management**: Build order history and tracking pages
4. **Payment Methods**: Add additional payment options if needed
5. **Testing**: Thoroughly test all payment scenarios
6. **Production**: Deploy and configure production environment

---

## 📋 API Reference Summary

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/create-hosted-checkout/` | POST | ✅ Yes | Create authenticated checkout |
| `/api/create-hosted-checkout-test/` | POST | ❌ No | Create test checkout |
| `/api/checkout/create-session/` | POST | ✅ Yes | Alternative checkout creation |
| `/api/checkout/payment-methods/` | GET | ❌ No | Get payment methods |
| `/api/orders/` | GET | ✅ Yes | Get user orders |
| `/api/orders/{id}/payment-status/` | GET | ✅ Yes | Check payment status |
| `/api/auth/login/` | POST | ❌ No | User login |
| `/api/auth/validate-token/` | POST | ❌ No | Validate JWT token |

---

*Last updated: January 2025*
*For technical support, contact the backend development team.*
