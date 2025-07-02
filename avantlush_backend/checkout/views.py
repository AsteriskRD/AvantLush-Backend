@api_view(['POST'])
def create_checkout_session(request):
    """Create checkout session - Simple endpoint"""
    try:
        data = request.data
        payment_method = data.get('payment_method')
        order_data = data.get('order_data', {})
        
        if payment_method != 'clover_hosted':
            return Response({
                "success": False,
                "error": "Only Clover Hosted checkout is currently supported"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate required fields
        required_fields = ['total_amount', 'order_number']
        for field in required_fields:
            if field not in order_data:
                return Response({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare order data for Clover with proper redirect URLs
        clover_order_data = {
            'total_amount': float(order_data['total_amount']),
            'order_number': order_data['order_number'],
            'order_id': order_data.get('order_id', order_data['order_number']),
            'currency': order_data.get('currency', 'USD'),
            'customer': order_data.get('customer', {}),
            'items': order_data.get('items', []),
            'redirect_urls': order_data.get('redirect_urls', {
                'success': f"{settings.FRONTEND_URL}/checkout/success",
                'failure': f"{settings.FRONTEND_URL}/checkout/failure", 
                'cancel': f"{settings.FRONTEND_URL}/checkout/cancel"
            })
        }
        
        # Create Clover checkout session
        clover_service = CloverPaymentService()
        result = clover_service.create_hosted_checkout_session(clover_order_data)
        
        if result['success']:
            return Response(result)  # Return complete result
        else:
            logger.error(f"Clover checkout session creation failed: {result['error']}")
            return Response({
                "success": False,
                "error": result['error']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return Response({
            "success": False,
            "error": "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)