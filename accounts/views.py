from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.hashers import make_password

from  store.models import *
from . forms import * 
from .tokens import account_activation_token

def signUp(request):
	# redirect signed-in users
	if request.user.is_authenticated:
		return redirect('my-account')
	
	# metadata
	title = 'Create a New Account'
	description = 'Sign up and save today!'
	url = '/sign-up'

	if request.method == 'GET':
		form = SignUpForm()

		context = {
			'form': form,  
			'title': title,
			'description': description,
			'url': url
		}
		return render(request, 'accounts/sign-up.html', context)
	
	if request.method == 'POST':
		form = SignUpForm(request.POST)

		context = {
			'form': form,  
			'title': title,
			'description': description,
			'url': url
		}

		if form.is_valid():
			# save new user
			user = User.objects.create_user(first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'], email=form.cleaned_data['email'], username=form.cleaned_data['username'], password=form.cleaned_data['password'])
			user.is_active = False
			user.save()

			# send confirm sign-up email
			user_email = form.cleaned_data['email']
			subject = 'Activate Your User Account - Clothez'
			message = render_to_string('accounts/email-templates/activate-account.html', {
				'user': user,
				'domain': get_current_site(request).domain,
				'uid': urlsafe_base64_encode(force_bytes(user.pk)),
				'token': account_activation_token.make_token(user),
				'protocol': 'https' if request.is_secure() else 'http'
			})
			email = EmailMessage(subject, message, to=[user_email])
			if email.send():
				messages.success(request, 'Please click on the link in your email to complete the sign-up process.')
			else:
				messages.error(request, f'Problem sending confirmation email to {user_email}, check if you typed it correctly.')
			return redirect('index')
		else:
			form.errors
			return render(request, 'accounts/sign-up.html', context)

def activateAccount(request, uidb64, token):
	# check for user
	User = get_user_model()
	try:
		uid = force_str(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None

	# complete user sign-up
	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.save()
		# save user as customer
		customer = Customer.objects.create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email, username=user.username)
		customer.save()

		messages.success(request, 'Your sign-up has been successfully completed. Please sign-in.')
		return redirect('sign-in')
	else:
		messages.error(request, 'Activation link invalid!')
		return redirect('index')

def signIn(request):
	# redirect signed-in users
	if request.user.is_authenticated:
		return redirect('my-account')
	
	# metadata
	title = 'Welcome Back'
	description = 'Sign in and do what you came to do.'
	url = '/sign-in'
	
	if request.method == 'GET':
		form = SignInForm()

		context = {
			'form': form,  
			'title': title,
			'description': description,
			'url': url
		}
		return render(request, 'accounts/sign-in.html', context)
	
	if request.method == 'POST':
		form = SignInForm(request.POST)

		context = {
			'form': form,  
			'title': title,
			'description': description,
			'url': url
		}

		if form.is_valid():
			user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
			if user is None:
				messages.error(request, 'Invalid credentials, please try again')
				return render(request, 'accounts/sign-in.html', context)  
			else:
				auth.login(request, user)
				return redirect('my-account')
		else:
			form.errors
			return render(request, 'accounts/sign-in.html', context)

def myAccount(request):
	if not request.user.is_authenticated:
		return redirect('sign-in')
	
	# orders
	orders = Order.objects.order_by('-date_ordered').filter(customer=request.user.customer)

	# metadata
	title = 'My Account'
	description = 'View previous orders or change account information.'
	url = '/my-account'

	if request.method == 'GET':
		form = ChangePasswordForm()

		context = {
			'form': form,  
			'orders': orders,
			'title': title,
			'description': description,
			'url': url
		}
		return render(request, 'accounts/my-account.html', context)
	
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)

		context = {
			'form': form,  
			'orders': orders,
			'title': title,
			'description': description,
			'url': url
		}

		if form.is_valid():
			# update user
			password = make_password(form.cleaned_data['password'], hasher='default')
			User.objects.filter(username=request.user.username).update(password=password)

			messages.success(request, 'Password successfully updated.')
			return redirect('my-account')
		else:
			form.errors
			return render(request, 'accounts/my-account.html', context)
		
def myOrder(request, order_id):
	# order info
	order = get_object_or_404(Order, pk=order_id)

	if request.user != order.customer.user:
		return redirect('my-account')
	
	# metadata
	title = 'Order' + ' ' + str(order_id)
	description = 'View your order details.'
	url = '/my-account/order'

	context = {
		'order': order,
		'title': title,
		'description': description,
		'url': url
	}

	return render(request, 'accounts/my-order.html', context)

def forgotPassword(request):
	# metadata
	title = 'Forgot Your Password?'
	description = 'Enter in your email in order to reset your password.'
	url = '/forgot-password'

	if request.method == 'GET':
		form = ForgotPasswordForm()

		context = {
			'form': form, 
			'title': title,
			'description': description,
			'url': url
		}
		return render(request, 'accounts/forgot-password.html', context)

	if request.method == 'POST':
		form = ForgotPasswordForm(request.POST)

		context = {
			'form': form, 
			'title': title,
			'description': description,
			'url': url
		}

		if form.is_valid():
			email = form.cleaned_data['email']
			user = User.objects.filter(email=email).first()
			if user:
				# send reset password email
				subject = 'Reset Your Password - Clothez'
				message = render_to_string('accounts/email-templates/reset-password.html', {
					'user': user,
					'domain': get_current_site(request).domain,
					'uid': urlsafe_base64_encode(force_bytes(user.pk)),
					'token': account_activation_token.make_token(user),
					'protocol': 'https' if request.is_secure() else 'http'
				})
				email = EmailMessage(subject, message, to=[user.email])
				if email.send():
					messages.success(request, 'Email has been sent. Please check your inbox.')
				else:
					messages.error(request, 'Problem sending email. Please try again.')
				return redirect('check-email')
			else:
				messages.error(request, 'Invalid email, please try again')
				return render(request, 'accounts/forgot-password.html', context)
		else:
			form.errors
			return render(request, 'accounts/forgot-password.html', context)
		
def checkEmail(request):
	# metadata
	title = 'Check Your Email'
	description = 'Check your email in order to proceed with the reset password process.'
	url = '/check-email'

	context = {
		'title': title,
		'description': description,
		'url': url
	}
	return render(request, 'accounts/check-email.html', context)
		
def resetPassword(request, uidb64, token):
	# metadata
	title = 'Reset Password'
	description = 'Enter in a new password then proceed to the sign-in page.'
	url = '/reset-password'

	# check for user
	User = get_user_model()
	try:
		uid = force_str(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	
	if user is not None and account_activation_token.check_token(user, token):
		if request.method == 'GET':
			form = ChangePasswordForm()

			context = {
				'form': form,
				'title': title,
				'description': description,
				'url': url
			}
			return render(request, 'accounts/reset-password.html', context)
		
		if request.method == 'POST':
			form = ChangePasswordForm(request.POST)
			if form.is_valid():
				# update user
				password = make_password(form.cleaned_data['password'], hasher='default')
				User.objects.filter(username=user.username).update(password=password)

				messages.success(request, 'Password successfully updated.')
				return redirect('sign-in')
			else:
				form.errors
				return render(request, 'accounts/my-account.html', context)
	else:
		messages.error(request, 'Link has expired')
		return redirect('index')

	messages.error(request, 'Something went wrong')
	return redirect('index')

def signOut(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'Sign-out Successful')
        return redirect('sign-in')