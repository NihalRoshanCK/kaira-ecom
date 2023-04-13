from django.urls import path
from .views import *



urlpatterns = [
    
    path('cart',viewcart, name='cart'),
    path('addProduct/<int:product_id>/',addcart, name='addcart'),
    path('additem/<int:product_id>/<str:product_size>/',additem, name='additem'),
    path('removecart/<int:product_id>/<str:size>/',remove_cart, name='removecart'),
    path('addwishlist/<int:product_id>/<int:w>',add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/',viewwishlist, name='wishlist'),
    path('removecartitem/<int:product_id>/<str:product_size>/',removecartitem,name='removecartitem'),
    path('removewishlist/<int:product_id>/<int:w>',remove_from_wishlist,name='remove_from_wishlist'),
    path('confirmation/',confirmation, name='confirmation'),
    path('checkout/',checkout,name='checkout'),
    path('paymenthandler/',paymenthandler, name='paymenthandler'),
    path('invoice/<int:order>',invoice,name='invoice')
    # path('razorpay_payment/',razorpay_payment, name='razorpay_payment'),
    
    
]