from django.shortcuts import render
from store.utils import cartData
from . models import *

def about(request):
    # metadata
    title = 'About Us'
    description = 'Learn about us and our business.'
    url= '/about'

    # cart
    data = cartData(request)
    cart_items = data['cart_items']

    # content
    content = PageContent.objects.get(name = 'About')

    context = {
        'title': title,
        'description': description,
        'url': url,
        'cart_items': cart_items,
        'content': content
    }

    return render(request, 'pages/about.html', context)

def contact(request):
    # metadata
    title = 'Contact'
    description = 'Drop us a line.'
    url= '/contact'

    # cart
    data = cartData(request)
    cart_items = data['cart_items']

    # content
    content = PageContent.objects.get(name = 'Contact')

    context = {
        'title': title,
        'description': description,
        'url': url,
        'cart_items': cart_items,
        'content': content
    }

    return render(request, 'pages/contact.html', context)

def privacyPolicy(request):
    # metadata
    title = 'Privacy Policy'
    description = 'Drop us a line.'
    url= '/privacy-policy'

    # cart
    data = cartData(request)
    cart_items = data['cart_items']

    # content
    content = PageContent.objects.get(name = 'Privacy Policy')

    context = {
        'title': title,
        'description': description,
        'url': url,
        'cart_items': cart_items,
        'content': content
    }

    return render(request, 'pages/privacy-policy.html', context)