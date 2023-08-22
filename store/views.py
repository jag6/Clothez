from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import json
import datetime
from .models import *
from .forms import * 
from .utils import cookieCart, cartData, guestOrder

def store(request):
	# metadata
	title = 'Your #1 Online Store'
	description = 'Your number one stop for all of life\'s essentials.'

	# banner
	banner = Banner.objects.filter(name = 'Home Banner')

	# cart
	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	# products
	products = Product.objects.all()

	context = {
		'title': title,
		'description': description,
		'banner': banner,
		'cartItems': cartItems,
		'products': products, 
	}
	return render(request, 'store/store.html', context)

def search(request):
	return render(request, 'store/search.html')

def wishList(request):
	return render(request, 'store/wishlist.html')

def cart(request):
	# metadata
	title = 'Shopping Cart'
	description = 'View or change items in cart.'

	# cart
	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {
		'title': title,
		'description': description,
		'items': items, 
		'order': order, 
		'cartItems': cartItems
	}
	return render(request, 'store/cart.html', context)

def checkout(request):
	# metadata
	title = 'Checkout'
	description = 'Pay with PayPal.'

	#cart
	data = cartData(request)
	if not data['cartItems']:
		return redirect('/')
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {
		'title': title,
		'description': description,
		'items': items, 
		'order': order, 
		'cartItems': cartItems
	}
	return render(request, 'store/checkout.html', context)
		

def updateItem(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		productId = data['productId']
		action = data['action']
		print('Action:', action)
		print('Product:', productId)

		customer = request.user.customer
		product = Product.objects.get(id=productId)
		order, created = Order.objects.get_or_create(customer=customer, complete=False)

		orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

		if action == 'add':
			orderItem.quantity = (orderItem.quantity + 1)
		elif action == 'remove':
			orderItem.quantity = (orderItem.quantity - 1)

		orderItem.save()

		if orderItem.quantity <= 0:
			orderItem.delete()

		return JsonResponse('Item was added', safe=False)

def processOrder(request):
	if request.method == 'POST':
		transaction_id = datetime.datetime.now().timestamp()
		data = json.loads(request.body)

		if request.user.is_authenticated:
			customer = request.user.customer
			order, created = Order.objects.get_or_create(customer=customer, complete=False)
		else:
			customer, order = guestOrder(request, data)

		total = float(data['form']['total'])
		order.transaction_id = transaction_id

		if total == order.get_cart_total:
			order.complete = True
		order.save()

		if order.shipping == True:
			ShippingAddress.objects.create(
				customer=customer,
				order=order,
				address=data['shipping']['address'],
				city=data['shipping']['city'],
				state=data['shipping']['state'],
				zipcode=data['shipping']['zipcode'],
			)

		return JsonResponse('Payment submitted..', safe=False)
	
def signUp(request):
	if request.method == 'GET':
		form = SignUpForm()

		return render(request, 'user/sign-up.html', {'form': form})
	
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = User.objects.create_user(first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'], email=form.cleaned_data['email'], username=form.cleaned_data['username'], password=form.cleaned_data['password'])
			user.save()
			messages.success(request, 'Sign-up successful. Please sign-in.')
			return redirect('sign-in')
		else:
			form.errors
			return render(request, 'user/sign-up.html', {'form': form})

def signIn(request):
	if request.method == 'GET':
		form = SignInForm()
		return render(request, 'user/sign-in.html', {'form': form})
	
	if request.method == 'POST':
		form = SignInForm(request.POST)
		if form.is_valid():
			user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
			if user is None:
				messages.error(request, 'Invalid credentials, please try again')
				return render(request, 'accounts/login.html')  
			else:
				auth.login(request, user)
				return redirect('my-account')
		else:
			form.errors
			return render(request, 'user/sign-in.html', {'form': form})

@login_required
def myAccount(request):
	return render(request, 'user/my-account.html')

def signOut(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'Logout Successful')
        return redirect('sign-in')