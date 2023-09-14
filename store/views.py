from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from eCommerce.settings import EMAIL_HOST_USER
# from django.contrib.postgres.search import SearchQuery
import json
import datetime
from . models import *
from . forms import * 
from . options import price_options
from . utils import *

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
	latest_products = Product.objects.order_by('created_at').filter(is_published=True)[:6]
	mens_products = Product.objects.order_by('category', 'name').filter(gender='Men\'s', is_published=True)
	womens_products = Product.objects.order_by('category', 'name').filter(gender='Women\'s', is_published=True)
	unisex_products = Product.objects.order_by('category', 'name').filter(gender='Unisex', is_published=True)

	context = {
		'title': title,
		'description': description,
		'banner': banner,
		'cart_items': cart_items,
		'latest_products': latest_products, 
		'mens_products': mens_products,
		'womens_products': womens_products,
		'unisex_products': unisex_products
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
	queryset_list = Product.objects.order_by('category', 'name').filter(is_published=True)

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
	if request.method == 'GET':
		# metadata
		css = 'product'

		# cart
		data = cartData(request)
		cart_items = data['cart_items']

		# product info
		product = get_object_or_404(Product, pk=product_id)

		# reviews
		reviews = Review.objects.filter(product=product).order_by('-created_at')


		if request.user.is_authenticated:
			# check for product as order item in customer order
			orders = Order.objects.filter(customer=request.user.customer).first()
			order_item = OrderItem.objects.filter(order=orders, product=product).first()

			# check if user already submitted review
			left_review = Review.objects.filter(customer=request.user.customer, product=product).first()

			# form
			form = ReviewForm()

			context = {
				'form': form, 
				'css': css, 
				'cart_items': cart_items, 
				'product': product, 
				'order_item': order_item, 
				'left_review': left_review, 
				'reviews': reviews
			}

			return render(request, 'store/product.html', context)
		else:
			context = {
				'css': css,
				'cart_items': cart_items,
				'product': product,
				'reviews': reviews
			}
			return render(request, 'store/product.html', context)
	
	if request.method == 'POST':
		# metadata
		css = 'product'

		# cart
		data = cartData(request)
		cart_items = data['cart_items']

		# product info
		product = get_object_or_404(Product, pk=product_id)

		# reviews
		reviews = Review.objects.filter(product=product).order_by('-created_at')

		if request.user.is_authenticated:
			# check for product as order item in customer order
			orders = Order.objects.filter(customer=request.user.customer).first()
			order_item = OrderItem.objects.filter(order=orders, product=product).first()

			# check if user already submitted review
			left_review = Review.objects.filter(customer=request.user.customer, product=product).first()

			# form
			form = ReviewForm(request.POST)

			context = {
				'form': form, 
				'css': css, 
				'cart_items': cart_items, 
				'product': product, 
				'order_item': order_item, 
				'left_review': left_review, 
				'reviews': reviews
			}

			# product info
			product = get_object_or_404(Product, pk = product_id)

			if form.is_valid():
				# save new review
				review = Review.objects.create(customer=request.user.customer, product=product, rating=form.cleaned_data['rating'], comment=form.cleaned_data['comment'])
				review.save()

				messages.success(request, 'Thank you for your review!')
				return redirect('product', product_id=product_id)
			else:
				form.errors
				return render(request, 'store/product.html', context)


def wishlist(request):
	# metadata
	title = 'Wishlist'
	description = 'View or change items in wishlist.'
	url = '/wishlist'
	css = 'cart'

	# cart
	cart_data = cartData(request)
	cart_items = cart_data['cart_items']

	# wishlist
	wishlist_data = wishlistData(request)
	wishlist_items = wishlist_data['wishlist_items']
	order = wishlist_data['order']
	items = wishlist_data['items']

	context = {
		'title': title,
		'description': description,
		'url': url,
		'css': css,
		'cart_items': cart_items,
		'wishlist_items': wishlist_items,
		'order': order,
		'items': items
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
		

def processOrder(request):
	if request.method == 'POST':
		transaction_id = datetime.datetime.now().timestamp()
		data = json.loads(request.body)

		if request.user.is_authenticated:
			cookie_data = cookieCart(request)
			items = cookie_data['items']

			customer = request.user.customer
			order = Order.objects.create(customer=customer, complete=False)

			for item in items:
				product = Product.objects.get(id=item['id'])
				order_item = OrderItem.objects.create(
					product=product,
					order=order,
					quantity=(item['quantity'] if item['quantity'] > 0 else -1*item['quantity'])
				)
		else:
			first_name = data['form']['first_name']
			last_name = data['form']['last_name']
			email = data['form']['email']

			cookie_data = cookieCart(request)
			items = cookie_data['items']

			customer, created = Customer.objects.get_or_create(first_name=first_name, last_name=last_name, email=email)
			customer.save()

			order = Order.objects.create(customer=customer, complete=False)

			for item in items:
				product = Product.objects.get(id=item['id'])
				order_item = OrderItem.objects.create(
					product=product,
					order=order,
					quantity=(item['quantity'] if item['quantity'] > 0 else -1*item['quantity'])
				)

		total = float(data['form']['total'])
		if total == order.get_cart_total:
			order.complete = True

		if order.shipping == True:
			ShippingAddress.objects.create(
				customer=customer,
				order=order,
				address=data['shipping']['address'],
				city=data['shipping']['city'],
				state=data['shipping']['state'],
				zipcode=data['shipping']['zipcode'],
			)

		order.transaction_id = transaction_id
		order.save()

		# send email to customer
		if request.user.is_authenticated:
			customer_email = request.user.customer.email
			customer_url = 'https://clothezrfw.online/my-account'
			send_mail(
				'New Order - Clothez',
				'Thank you for your order. Your item will be shipping shortly. Please check out your order details at your store account page. ' + customer_url,
				EMAIL_HOST_USER,
				[customer_email],
				fail_silently=False
			)
		else:
			customer_email =  data['form']['email']
			send_mail(
				'New Order - Clothez',
				'Thank you for your order. Your item will be shipping shortly.',
				EMAIL_HOST_USER,
				[customer_email],
				fail_silently=False
			)

		# send email to store owner
		owner_url = 'https://clothezrfw.online/admin/store/order/'
		send_mail(
			'New Order - Clothez',
			'Go to your admin panel ' + owner_url + ' and ship when ready.',
			EMAIL_HOST_USER,
			[EMAIL_HOST_USER],
			fail_silently=False
		)

		return JsonResponse('Payment submitted..', safe=False)