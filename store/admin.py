from django.contrib import admin
from django.db.models import Avg
from django.urls import path
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.core.mail import send_mail
from eCommerce.settings import EMAIL_HOST_USER
from . models import *

admin.site.register(ShippingAddress)
admin.site.register(Banner)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    search_fields = ('last_name__startswith',)
    list_display = ('name', 'username', 'email', 'order_count')
    
    def order_count(self, obj):
	    return Order.objects.filter(customer=obj).count()

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'category', 'type', 'rating', 'review_count')
    list_filter = ('gender', 'category', 'type')

    def rating(self, obj):
        review = Review.objects.filter(product=obj).aggregate(avg_rating=Avg('rating'))
        avg = 0
        if review['avg_rating'] is not None:
            avg = float(review['avg_rating'])
        return avg
    
    def review_count(self, obj):
	    return Review.objects.filter(product=obj).count()

class OrderItemInline(admin.TabularInline):
    model = OrderItem

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            extra = obj.orderitem_set.count()
        return extra

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'is_shipped', 'order_total', 'order_shipped_btn')
    actions = ['order_shipped']
        
    def order_total(self, obj):
        order_items = obj.orderitem_set.all()
        total = sum([item.get_total for item in order_items])
        return total 
    
    def order_shipped_btn(self, obj):
        return format_html('<a href="mailto:{}">SEND</a>', obj.customer.email)
    
    order_shipped_btn.short_description = 'Order Shipped'
    order_shipped_btn.allow_tags = True

    def order_shipped(self, request, queryset):
        for obj in queryset.select_related('customer'):
            customer_email = obj.customer.email
            if request.method == 'POST':
                if obj.is_shipped == False:
                    obj.is_shipped = True
                    obj.save()
                send_mail(
                    'Order Shipped - Clothez',
                    'Your order has been shipped. Please expect it within the next 3-5 days. Thank you for your business.',
                    EMAIL_HOST_USER,
                    [customer_email],
                    fail_silently=False
                )
                return HttpResponseRedirect('/admin/store/order')

    order_shipped.short_description = 'Send Order Shipped Email'