from io import BytesIO
from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order
from xhtml2pdf import pisa

@shared_task
def payment_completed(order_id):
    """
    Task to send an e-mail notification with the invoice when an order is
    successfully created.
    """
    order = Order.objects.get(id=order_id)
    
    # Create invoice e-mail
    subject = f'My Shop - Invoice no. {order.id}'
    message = 'Please find attached the invoice for your recent purchase.'
    email = EmailMessage(subject, message, 'admin@myshop.com', [order.email])
    
    # Generate PDF
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    
    # Create PDF from HTML
    pisa_status = pisa.CreatePDF(html, dest=out)
    if pisa_status.err:
        raise Exception("Error generating PDF")
    
    # Attach PDF file
    email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
    
    # Send e-mail
    email.send()
