from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('search', views.search, name="search"),
    path('<int:product_id>', views.product, name="product"),
    path('wishlist', views.wishlist, name="wishlist"),
    path('cart', views.cart, name="cart"),
    path('checkout', views.checkout, name="checkout"),
    # api
    path('update_item', views.updateItem, name="update_item"),
    path('process_order', views.processOrder, name="process_order"),
    # user
    path('sign-up', views.signUp, name="sign-up"),
    path('sign-in', views.signIn, name="sign-in"),
    path('my-account', views.myAccount, name="my-account"),
    path('sign-out', views.signOut, name="sign-out")
]
