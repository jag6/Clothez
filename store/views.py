from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages, auth
from django.contrib.auth.models import User
import json
import datetime
from . models import *
from . forms import * 
from . options import price_options
from .utils import cookieCart, cartData, guestOrder

def index(request):
	# metadata
	title = 'Your #1 Online Store'
	description = 'Your number one stop for all of life\'s essentials.'

	# banner
	banner = Banner.objects.filter(name = 'Home Banner')

	# cart
	data = cartData(request)
	cartItems = data['cartItems']

	# products
	products = Product.objects.all()

	context = {
		'title': title,
		'description': description,
		'banner': banner,
		'cartItems': cartItems,
		'products': products, 
	}
	return render(request, 'store/index.html', context)

def search(request):
	# metadata
	title = 'Search'
	description = 'Search for the product you\'re looking for.'
	url = '/search'

	# cart
	data = cartData(request)
	cartItems = data['cartItems']

	#search info
	queryset_list = Product.objects.order_by('-name')

	if 'q' in request.GET:
		q = request.GET['q']
		if q:
			queryset_list = queryset_list.filter(name__icontains = q)
	
	# if 'price' in request.GET:
	# 	price = price.GET['price']
	# 	if price:
	# 		queryset_list = queryset_list.filter(price__lte = price)

	context = {
		'title': title,
		'description': description,
		'url': url,
		'cartItems': cartItems,
		'products': queryset_list,
		'values': request.GET,
		'price_options': price_options
	}

	return render(request, 'store/search.html', context)

def product(request, product_id):
	# metadata
	url = '/'
	css = 'product'

	# cart
	data = cartData(request)
	cartItems = data['cartItems']

	product = get_object_or_404(Product, pk = product_id)

	context = {
		'css': css,
		'url': url,
		'product': product,
		'cartItems': cartItems
	}

	return render(request, 'store/product.html', context)

def wishlist(request):
	# metadata
	title = 'Wishlist'
	description = 'View or change items in wishlist.'
	url = '/wishlist'
	css = 'cart'

	# cart
	data = cartData(request)
	cartItems = data['cartItems']

	context = {
		'title': title,
		'description': description,
		'url': url,
		'css': css,
		'cartItems': cartItems
	}

	return render(request, 'store/wishlist.html', context)

def cart(request):
	# metadata
	title = 'Shopping Cart'
	description = 'View or change items in cart.'
	url = '/cart'
	css = 'cart'

	# cart
	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {
		'title': title,
		'description': description,
		'url': url,
		'css': css,
		'items': items, 
		'order': order, 
		'cartItems': cartItems
	}
	return render(request, 'store/cart.html', context)

def checkout(request):
	# metadata
	title = 'Checkout'
	description = 'Pay with PayPal.'
	url = '/checkout'
	css = 'checkout'

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
		'url': url,
		'css': css,
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
	# redirect signed-in users
	if request.user.is_authenticated:
		return redirect('my-account')
	
	if request.method == 'GET':
		form = SignUpForm()

		# cart
		data = cartData(request)
		cartItems = data['cartItems']

		return render(request, 'user/sign-up.html', {'form': form, 'cartItems': cartItems})
	
	if request.method == 'POST':
		form = SignUpForm(request.POST)

		# cart
		data = cartData(request)
		cartItems = data['cartItems']

		if form.is_valid():
			#save new user
			user = User.objects.create_user(first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'], email=form.cleaned_data['email'], username=form.cleaned_data['username'], password=form.cleaned_data['password'])
			user.save()
			
			#save user as customer
			customer = Customer.objects.create(user=user, first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'], email=form.cleaned_data['email'], username=form.cleaned_data['username'])
			customer.save()

			messages.success(request, 'Sign-up successful. Please sign-in.')
			return redirect('sign-in')
		else:
			form.errors
			return render(request, 'user/sign-up.html', {'form': form, 'cartItems': cartItems})

def signIn(request):
	# redirect signed-in users
	if request.user.is_authenticated:
		return redirect('my-account')
	
	if request.method == 'GET':
		form = SignInForm()

		# cart
		data = cartData(request)
		cartItems = data['cartItems']

		return render(request, 'user/sign-in.html', {'form': form, 'cartItems': cartItems})
	
	if request.method == 'POST':
		form = SignInForm(request.POST)

		# cart
		data = cartData(request)
		cartItems = data['cartItems']

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
			return render(request, 'user/sign-in.html', {'form': form, 'cartItems': cartItems})

def myAccount(request):
	if not request.user.is_authenticated:
		return redirect('sign-in')
	
	# metadata
	title = 'My Account'
	description = 'View previous orders or change account information.'
	url = '/my-account'

	# cart
	data = cartData(request)
	cartItems = data['cartItems']

	context = {
		'title': title,
		'description': description,
		'url': url,
		'cartItems': cartItems
	}
		
	return render(request, 'user/my-account.html', context)

def signOut(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'Logout Successful')
        return redirect('sign-in')