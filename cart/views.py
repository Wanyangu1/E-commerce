from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm

@require_POST
def cart_add(request, product_id):
    """
    Add a product to the cart and redirect to the cart detail page.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
    
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    """
    Remove a product from the cart and redirect to the cart detail page.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    # Prepare a list of items with their update forms
    cart_items = []
    for item in cart:
        # Attach a form for each cart item
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
        cart_items.append(item)
    
    return render(request, 'cart/detail.html', {'cart': cart_items})
