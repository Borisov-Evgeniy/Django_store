from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate, get_user
from django.db import IntegrityError
from .models import Product
from django.contrib.auth.models import User

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'shop/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('signup')
            except IntegrityError:
                return render(request, 'shop/signupuser.html',
                              {'form': UserCreationForm(),
                               'error': 'Такое имя пользователя уже существует! Попробуйте другое'})
        else:
            return render(request, 'shop/signupuser.html',
                          {'form': UserCreationForm(),
                           'error': 'Пароли не совпали'})


def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('signup')

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'shop/login.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'],
                            password=request.POST['password'])
        if user is None:
            return render(request, 'shop/login.html',
                          {'form': AuthenticationForm(),
                           'error': 'Неверные данные для входа'})
        else:
            login(request, user)
            return redirect('signup')


@login_required(login_url='login')
def index(request):
    products = Product.objects.all()
    return render(request, 'shop/index.html', {'products': products})


@user_passes_test(lambda user: user.is_superuser)
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        product.delete()
        return redirect('home')
    return render(request, 'shop/delete_product.html', {'product': product})


@user_passes_test(lambda user: user.is_superuser)
@user_passes_test(lambda user: user.is_superuser)
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')

        if not name:
            return render(request, 'shop/edit_product.html',
                          {'product': product, 'error': 'Название обязательно для заполнения'})

        product.name = name
        product.description = description
        product.price = price
        product.save()
        return redirect('home')

    return render(request, 'shop/edit_product.html', {'product': product})


@user_passes_test(lambda user: user.is_superuser)
@login_required(login_url='login')
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        price = request.POST.get('price', '')

        if 'image' in request.FILES:
            image = request.FILES['image']
        else:
            image = None

        if not name:
            return render(request, 'shop/add_product.html', {'error': 'Name is required'})

        if not description:
            return render(request, 'shop/add_product.html', {'error': 'Description is required'})

        if not price:
            return render(request, 'shop/add_product.html', {'error': 'Price is required'})

        try:
            price = float(price)
        except ValueError:
            return render(request, 'shop/add_product.html', {'error': 'Price must be a valid number'})

        user = get_user(request)
        product = Product(name=name, description=description, price=price, image=image, added_by=user)
        product.save()
        return redirect('home')

    return render(request, 'shop/add_product.html')