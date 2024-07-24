import braintree
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from orders.models import Order
from django.shortcuts import render
from .tasks import payment_completed


def payment_done(request):
    """View to handle successful payment."""
    return render(request, 'payment/done.html')

def payment_canceled(request):
    """View to handle canceled or failed payment."""
    return render(request, 'payment/canceled.html')

# Instantiate Braintree payment gateway
gateway = braintree.BraintreeGateway(settings.BRAINTREE_CONF)

def payment_process(request):
    # Retrieve the order ID from the session
    order_id = request.session.get('order_id')
    
    # Get the order object or return a 404 error if not found
    order = get_object_or_404(Order, id=order_id)
    
    # Calculate the total cost of the order
    total_cost = order.get_total_cost()
    
    if request.method == 'POST':
        # Retrieve the payment nonce
        nonce = request.POST.get('payment_method_nonce', None)
        
        # Create and submit the transaction to Braintree
        result = gateway.transaction.sale({
            'amount': f'{total_cost:.2f}',
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })
        
        if result.is_success:
            # Mark the order as paid
            order.paid = True
            # Store the unique transaction ID
            order.braintree_id = result.transaction.id
            order.save()
            payment_completed.delay(order.id)
            # Redirect to the payment success page
            return redirect('payment:done')
        else:
            # Redirect to the payment canceled page if the transaction failed
            return redirect('payment:canceled')
    else:
        # Generate a client token for the payment form
        client_token = gateway.client_token.generate()
        return render(request, 'payment/process.html', {
            'order': order,
            'client_token': client_token
        })
    
    
