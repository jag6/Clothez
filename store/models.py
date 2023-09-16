from django.db import models
from django.db.models import Avg
from django.contrib import admin
from django.contrib.auth.models import User

class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	first_name = models.CharField(max_length=20, null=True)
	last_name = models.CharField(max_length=20, null=True)
	username = models.CharField(max_length=20, null=True)
	email = models.CharField(max_length=20, null=True)

	@property
	def name(self):
		name = self.first_name + ' ' + self.last_name
		return name
	
	def __str__(self):
		return self.name

class Product(models.Model):
	name = models.CharField(max_length=20, null=True)
	description = models.TextField(null=True)
	category = models.CharField(max_length=20, null=True)
	type = models.CharField(max_length=20, null=True)
	gender = models.CharField(max_length=20, null=True)
	price = models.FloatField()
	digital = models.BooleanField(default=False,null=True, blank=True)
	image = models.ImageField(upload_to='products/', null=True)
	count_in_stock = models.IntegerField(null=True, blank=True)
	is_published = models.BooleanField(default=True)
	created_at = models.DateTimeField(null=True, auto_now_add=True)

	def __str__(self):
		return self.name
	
	@property
	def imageURL(self):
		try:
			url = self.image.url
		except:
			url = ''
		return url
	
	@property
	def rating(self):
		review = Review.objects.filter(product=self).aggregate(avg_rating=Avg('rating'))
		avg = 0
		if review["avg_rating"] is not None:
			avg = float(review["avg_rating"])
		return avg
	
	@property
	def num_reviews(self):
		return Review.objects.filter(product=self).count()

	
class Review(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
	rating = models.IntegerField(default=0)
	comment = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.customer.name

class Order(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)
	is_shipped = models.BooleanField(default=False)

	def __str__(self):
		return str(self.id)
		
	@property
	def shipping(self):
		shipping = False
		order_items = self.orderitem_set.all()
		for i in order_items:
			if i.product.digital == False:
				shipping = True
		return shipping

	@property
	def get_cart_total(self):
		order_items = self.orderitem_set.all()
		total = sum([item.get_total for item in order_items])
		return total 

	@property
	def get_cart_items(self):
		order_items = self.orderitem_set.all()
		total = sum([item.quantity for item in order_items])
		return total
	
	@property
	def my_order_items(self):
		return OrderItem.objects.filter(order=self.id)

class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
	order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
	quantity = models.IntegerField(default=1)
 
	def __str__(self):
		return self.product.name

	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total

class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=20, null=False)
	state = models.CharField(max_length=20, null=False)
	zipcode = models.CharField(max_length=20, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address
	

class Banner(models.Model):
	name = image_description = models.CharField(max_length=20, null=True)
	text = models.CharField(max_length=200, null=True)
	image = models.ImageField(upload_to='banners/', null=True)
	image_description = models.CharField(max_length=100, null=True)

	def __str__(self):
		return self.name