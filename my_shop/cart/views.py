from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from shop.models import Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        user = request.user

        # Получите или создайте объект Cart для пользователя
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Попробуйте найти существующий CartItem для данного продукта и корзины
        cart_item, created = CartItem.objects.get_or_create(product=product, user=user)

        if not created:
            # Если CartItem уже существует, увеличьте его количество на 1
            cart_item.quantity += 1
            cart_item.update_subtotal()
            cart_item.save()
        else:
            # Если CartItem только что создан, установите его количество на 1
            cart_item.quantity = 1
            cart_item.update_subtotal()
            cart_item.save()

        # Обновите общую сумму корзины и сохраните ее
        cart.total += Decimal(str(product.price))
        cart.save()

        messages.success(request, 'Товар успешно добавлен в корзину.')
        return redirect('cart:cart')



@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart = cart_item.cart
    product = cart_item.product

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.update_subtotal()
        cart.total -= product.price
        cart.save()
    else:
        cart_item.delete()

    return redirect('cart:cart')

@login_required
def update_cart(request):
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')
        quantity = int(request.POST.get('quantity'))
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        cart = cart_item.cart
        product = cart_item.product

        # Обновите количество товара в корзине
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.update_subtotal()
            cart.total += (quantity - cart_item.quantity) * product.price
            cart_item.save()
            cart.save()
        else:
            cart_item.delete()

    return redirect('cart:cart')


@login_required
def view_cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = CartItem.objects.filter(cart=cart)

    context = {
        'cart_items': cart_items,
        'cart': cart,
    }

    return render(request, 'cart/cart.html', context)