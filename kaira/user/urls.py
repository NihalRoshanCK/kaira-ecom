from django.urls import path
from .views import *


urlpatterns = [
    path('',index, name='home'),
    # path('signin/', views.signin, name='signin'),
    path('shop',shop, name='shop'),
    path('sort/<int:pid>/<int:w>/',sort, name='sort'),
    path('register/',register, name='register'),
    path('verifyotp/<int:user_id>/',verify_otp, name='verifyotp'),
    path('resend-otp/<int:user_id>/',resend_otp, name='resend_otp'),
    path('forgotpass/',forgot_password, name='forgotpass'),
    path('resetpass/<int:user_id>/',reset_password, name='resetpass'),
    path('userupdate/',user_update, name='user_update'),
    path('login/',user_login,name="login"),
    path('logout/',logout, name='logout'),
    path('user/',user, name='user'),
    path('singleproduct/<slug:slug>/', singleproduct, name='singleproduct'),
    path('singleproductmodeal/<slug:slug>/', singleproductmodeal, name='singleproductmodeal'),
    path('changepassword/',changepassword, name='changepassword'),
    path('add_address/<int:w>',add_address, name='add_address'),
    path('address_book/',address_book, name='address_book'),
    path('myorder/', myorders, name="myorders"),
    path('cancelOrder/',cancelOrder, name='cancelOrder'),
    path('vieworder/<int:id>/',viewOrder, name='vieworder'),
    
    
]