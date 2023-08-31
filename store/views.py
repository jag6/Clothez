from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
# from django.contrib.postgres.search import SearchQuery
import json
import datetime
from . models import *
from . forms import * 
from . options import price_options
from .utils import cartData, guestOrder

def index(request):
	# metadata
	title = 'Your #1 Online Store'
	description = 'Your number one stop for all of life\'s essentials.'

	# banner
	banner = Banner.objects.get(name = 'Home Banner')

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
	# search_options = Product.objects.distinct('category', 'type', 'gender')
	queryset_list = Product.objects.order_by('-name')

	if 'q' in request.GET:
		q = request.GET['q']
		if q:
			queryset_list = queryset_list.filter(name__icontains = q ) | \
							queryset_list.filter(gender__istartswith = q)
			# description__icontains = q, category__icontains = q, type__icontains = q, gender__icontains = q, 
	
	# if 'price' in request.GET:
	# 	price = price.GET['price']
	# 	if price:
	# 		queryset_list = queryset_list.filter(price__lte = price)

	context = {
		'title': title,
		'description': description,
		'url': url,
		'cart_items': cart_items,
		# 'search_options': search_options,
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