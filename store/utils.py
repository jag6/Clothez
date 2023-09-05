import json
from . models import *

def cookieCart(request):
	try:
		cart = json.loads(request.COOKIES['cart'])
	except:
		cart = {}
		print('CART:', cart)

	items = []
	order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
	cart_items = order['get_cart_items']

	for i in cart:
		try:	
			if cart[i]['quantity'] > 0: 
				cart_items += cart[i]['quantity']

				product = Product.objects.get(id=i)
				total = (product.price * cart[i]['quantity'])

				order['get_cart_total'] += total
				order['get_cart_items'] += cart[i]['quantity']

				item = {
                    'id': product.id,
                    'product': {'id': product.id,'name': product.name, 'price': product.price, 'imageURL': product.imageURL}, 
                    'quantity': cart[i]['quantity'],
                    'digital': product.digital,
                    'get_total': total,
				}
				items.append(item)

				if product.digital == False:
					order['shipping'] = True
		except:
			pass
			
	return {'cart_items': cart_items ,'order': order, 'items': items}

def cartData(request):
	cookie_data = cookieCart(request)
	cart_items = cookie_data['cart_items']
	order = cookie_data['order']
	items = cookie_data['items']

	return {'cart_items': cart_items,'order': order, 'items': items}

def cookieWishlist(request):
	try:
		wishlist = json.loads(request.COOKIES['wishlist'])
	except:
		wishlist = {}
		print('wishlist:', wishlist)

	items = []
	order = {'get_wishlist_total': 0, 'get_wishlist_items': 0, 'shipping': False}
	wishlist_items = order['get_wishlist_items']

	for i in wishlist:
		try:	
			if wishlist[i]['quantity'] > 0: 
				wishlist_items += wishlist[i]['quantity']

				product = Product.objects.get(id=i)
				total = (product.price * wishlist[i]['quantity'])

				order['get_wishlist_total'] += total
				order['get_wishlist_items'] += wishlist[i]['quantity']

				item = {
                    'id': product.id,
                    'product': {'id': product.id,'name': product.name, 'price': product.price, 
                    'imageURL': product.imageURL}, 
                    'quantity': wishlist[i]['quantity'],
                    'digital': product.digital,
                    'get_total': total,
				}
				items.append(item)

				if product.digital == False:
					order['shipping'] = True
		except:
			pass
			
	return {'wishlist_items': wishlist_items ,'order': order, 'items': items}

def wishlistData(request):
	cookie_data = cookieWishlist(request)
	wishlist_items = cookie_data['wishlist_items']
	order = cookie_data['order']
	items = cookie_data['items']

	return {'wishlist_items': wishlist_items, 'order': order, 'items': items}