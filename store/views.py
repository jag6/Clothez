from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
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
	cart_items = data['cart_items']

	# products
	products = Product.objects.all()

	context = {
		'title': title,
		'description': description,
		'banner': banner,
		'cart_items': cart_items,
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
	cart_items = data['cart_items']

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
		'cart_items': cart_items,
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
	cart_items = data['cart_items']

	product = get_object_or_404(Product, pk = product_id)

	context = {
		'css': css,
		'url': url,
		'product': product,
		'cart_items': cart_items
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
	cart_items = data['cart_items']

	context = {
		'title': title,
		'description': description,
		'url': url,
		'css': css,
		'cart_items': cart_items
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
	cart_items = data['cart_items']
	order = data['order']
	items = data['items']

	context = {
		'title': title,
		'description': description,
		'url': url,
		'css': css,
		'cart_items': cart_items,
		'order': order, 
		'items': items
	}
	return render(request, 'store/cart.html', context)

def checkout(request):
	# metadata
	title = 'Checkout'
	description = 'Pay with PayPal.'
	url = '/checkout'
	css = 'cart'

	#cart
	data = cartData(request)
	if not data['cart_items']:
		return redirect('/')
	
	cart_items = data['cart_items']
	order = data['order']
	items = data['items']

	context = {
		'title': title,
		'description': description,
		'url': url,
		'css': css,
		'cart_items': cart_items,
		'order': order, 
		'items': items
	}
	return render(request, 'store/checkout.html', context)
		

def updateItem(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		product_id = data['product_id']
		action = data['action']
		print('Action:', action)
		print('Product:', product_id)

		customer = request.user.customer
		product = Product.objects.get(id=product_id)
		order, created = Order.objects.get_or_create(customer=customer, complete=False)

		order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

		if action == 'add':
			order_item.quantity = (order_item.quantity + 1)
		elif action == 'remove':
			order_item.quantity = (order_item.quantity - 1)

		order_item.save()

		if order_item.quantity <= 0:
			order_item.delete()

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
		cart_items = data['cart_items']

		return render(request, 'user/sign-up.html', {'form': form, 'cart_items': cart_items})
	
	if request.method == 'POST':
		form = SignUpForm(request.POST)

		# cart
		data = cartData(request)
		cart_items = data['cart_items']

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
			return render(request, 'user/sign-up.html', {'form': form, 'cart_items': cart_items})

def signIn(request):
	# redirect signed-in users
	if request.user.is_authenticated:
		return redirect('my-account')
	
	if request.method == 'GET':
		form = SignInForm()

		# cart
		data = cartData(request)
		cart_items = data['cart_items']

		return render(request, 'user/sign-in.html', {'form': form, 'cart_items': cart_items})
	
	if request.method == 'POST':
		form = SignInForm(request.POST)

		# cart
		data = cartData(request)
		cart_items = data['cart_items']

		if form.is_valid():
			user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
			if user is None:
				messages.error(request, 'Invalid credentials, please try again')
				return render(request, 'user/sign-in.html')  
			else:
				auth.login(request, user)
				return redirect('my-account')
		else:
			form.errors
			return render(request, 'user/sign-in.html', {'form': form, 'cart_items': cart_items})

def myAccount(request):
	if not request.user.is_authenticated:
		return redirect('sign-in')
	
	if request.method == 'GET':
		form = ChangePasswordForm()

		# cart
		data = cartData(request)
		cart_items = data['cart_items']

		#orders
		orders = Order.objects.order_by('-date_ordered').filter(customer=request.user.customer)
		
		return render(request, 'user/my-account.html', {'form': form, 'cart_items': cart_items, 'orders': orders})
	
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)

		# cart
		data = cartData(request)
		cart_items = data['cart_items']

		#orders
		orders = Order.objects.order_by('-date_ordered').filter(customer=request.user.customer)

		if form.is_valid():
			#update user
			password = make_password(form.cleaned_data['password'], hasher='default')
			User.objects.filter(username=request.user.username).update(password=password)

			messages.success(request, 'Password successfully updated.')
			return redirect('my-account')
		else:
			form.errors
			return render(request, 'user/my-account.html', {'form': form, 'cart_items': cart_items, 'orders': orders})

def signOut(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'Sign-out Successful')
        return redirect('sign-in')