from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mass_mail
from eCommerce.settings import EMAIL_HOST_USER
import json
import datetime
from . models import *
from . forms import * 
from . options import *
from . utils import *

def index(request):
	# metadata
	title = 'Your #1 Online Store'
	description = 'Your number one stop for all of life\'s essentials.'

	# banner
	banner = Banner.objects.get(name = 'Home Banner')

	# products
	latest_products = Product.objects.order_by('created_at').filter(is_published=True)[:6]
	mens_products = Product.objects.order_by('category', 'name').filter(gender='Men\'s', is_published=True)
	womens_products = Product.objects.order_by('category', 'name').filter(gender='Women\'s', is_published=True)
	unisex_products = Product.objects.order_by('category', 'name').filter(gender='Unisex', is_published=True)

	context = {
		'title': title,
		'description': description,
		'banner': banner,
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

	#search info
	queryset_list = Product.objects.order_by('category', 'name').filter(is_published=True)

	if 'q' in request.GET:
		q = request.GET['q']
		if q:
			queryset_list = queryset_list.filter(gender__iexact = q) | \
							queryset_list.filter(name__icontains = q ) | \
							queryset_list.filter(category__icontains = q) | \
							queryset_list.filter(type__icontains = q)
	
	# keyword
	if 'keyword' in request.GET:
		keyword = request.GET['keyword']
		if keyword:
			queryset_list = queryset_list.filter(name__icontains = keyword)

	# category
	if 'category' in request.GET:
		category = request.GET['category']
		if category:
			queryset_list = queryset_list.filter(category__icontains = category)

	# gender
	if 'gender' in request.GET:
		gender = request.GET['gender']
		if gender:
			queryset_list = queryset_list.filter(gender__iexact = gender)
	
	# price
	if 'price' in request.GET:
		price = request.GET['price']
		if price:
			queryset_list = queryset_list.filter(price__lte = price)

	context = {
		'title': title,
		'description': description,
		'url': url,
		'products': queryset_list,
		'values': request.GET,
		'category_options': category_options,
		'gender_options': gender_options,
		'price_options': price_options
	}
	return render(request, 'store/search.html', context)

def product(request, product_id):
	# metadata
	css = 'product'

	# product info
	product = get_object_or_404(Product, pk=product_id)

	# reviews
	reviews = Review.objects.filter(product=product).order_by('-created_at')

	if request.method == 'GET':
		if request.user.is_authenticated:
			# check for product as order item in customer order
			order_item = OrderItem.objects.filter(order__customer=request.user.customer, product=product).first()

			# check if user already submitted review
			left_review = Review.objects.filter(customer=request.user.customer, product=product).first()

			form = ReviewForm()

			context = {
				'form': form, 
				'css': css, 
				'product': product, 
				'order_item': order_item, 
				'left_review': left_review, 
				'reviews': reviews
			}
			return render(request, 'store/product.html', context)
		else:
			context = {
				'css': css,
				'product': product,
				'reviews': reviews
			}
			return render(request, 'store/product.html', context)
	
	if request.method == 'POST':
		if request.user.is_authenticated:
			# check for product as order item in customer order
			order_item = OrderItem.objects.filter(order__customer=request.user.customer, product=product).first()

			# check if user already submitted review
			left_review = Review.objects.filter(customer=request.user.customer, product=product).first()

			form = ReviewForm(request.POST)

			context = {
				'form': form, 
				'css': css, 
				'product': product, 
				'order_item': order_item, 
				'left_review': left_review, 
				'reviews': reviews
			}

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

	# cart
	data = cartData(request)
	if not data['cart_items']:
		return redirect('/')
	
	cart_items = data['cart_items']
	order = data['order']
	items = data['items']

	# pre-fill shipping address
	if(request.user.is_authenticated and ShippingAddress.objects.filter(customer=request.user.customer).first()):
		shipping = ShippingAddress.objects.filter(customer=request.user.customer).first()
		address = shipping.address
		city = shipping.city
		state = shipping.state
		zipcode = shipping.zipcode

		context = {
			'title': title,
			'description': description,
			'url': url,
			'css': css,
			'cart_items': cart_items,
			'order': order, 
			'items': items,
			'address': address,
			'city': city,
			'state': state,
			'zipcode': zipcode
		}
	else:
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
			first_name = data['customer']['first_name']
			last_name = data['customer']['last_name']
			email = data['customer']['email']

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

		total = float(data['order']['total'])
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

		# send email to customer and store owner
		owner_url = 'https://clothezrfw.online/admin/store/order/'
		owner_message = (
			'New Order - Clothez',
			'Go to your admin panel ' + owner_url + ' and ship when ready.',
			EMAIL_HOST_USER,
			[EMAIL_HOST_USER],
		)
		if request.user.is_authenticated:
			customer_email = request.user.customer.email
			customer_url = 'https://clothezrfw.online/my-account'
			customer_message = (
				'New Order - Clothez',
				'Thank you for your order. Your item will be shipping shortly. Please check out your order details at your store account page. ' + customer_url,
				EMAIL_HOST_USER,
				[customer_email],
			)
			send_mass_mail((customer_message, owner_message), fail_silently=False)
		else:
			customer_email =  data['form']['email']
			guest_message = (
				'New Order - Clothez',
				'Thank you for your order. Your item will be shipping shortly.',
				EMAIL_HOST_USER,
				[customer_email],
			)
			send_mass_mail((guest_message, owner_message), fail_silently=False)

		return JsonResponse('Payment submitted..', safe=False)