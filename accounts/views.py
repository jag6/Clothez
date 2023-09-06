from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from  store.models import *
from . forms import * 
from store.utils import cartData

def signUp(request):
	# redirect signed-in users
	if request.user.is_authenticated:
		return redirect('my-account')
	
	if request.method == 'GET':
		form = SignUpForm()

		# cart
		data = cartData(request)
		cart_items = data['cart_items']

		return render(request, 'accounts/sign-up.html', {'form': form, 'cart_items': cart_items})
	
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
			return render(request, 'accounts/sign-up.html', {'form': form, 'cart_items': cart_items})

def signIn(request):
	# redirect signed-in users
	if request.user.is_authenticated:
		return redirect('my-account')
	
	if request.method == 'GET':
		form = SignInForm()

		# cart
		data = cartData(request)
		cart_items = data['cart_items']

		return render(request, 'accounts/sign-in.html', {'form': form, 'cart_items': cart_items})
	
	if request.method == 'POST':
		form = SignInForm(request.POST)

		# cart
		data = cartData(request)
		cart_items = data['cart_items']

		if form.is_valid():
			user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
			if user is None:
				messages.error(request, 'Invalid credentials, please try again')
				return render(request, 'accounts/sign-in.html')  
			else:
				auth.login(request, user)
				return redirect('my-account')
		else:
			form.errors
			return render(request, 'accounts/sign-in.html', {'form': form, 'cart_items': cart_items})

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
		
		return render(request, 'accounts/my-account.html', {'form': form, 'cart_items': cart_items, 'orders': orders})
	
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
			return render(request, 'accounts/my-account.html', {'form': form, 'cart_items': cart_items, 'orders': orders})

def signOut(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'Sign-out Successful')
        return redirect('sign-in')