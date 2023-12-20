from django.shortcuts import render,redirect,get_object_or_404
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.models import User,auth
from .models import *
from product.models import *
from .forms import *
from product.views import *
from django.contrib.auth import authenticate,login
import os
import random
import kaira.settings
from django.http import JsonResponse
from django.core.serializers import serialize
  
# Create your views here.

def index(request):
    whish = False
    products_with_variants = Product.objects.prefetch_related('productvarient_set').order_by('-created')[:12]
    
    for product in products_with_variants:
        for product_varient in product.productvarient_set.all():
            product_varient.calculated_price = product_varient.price * product_varient.offer / 100
            if request.user.is_authenticated:
                Wishlist= wishlist.objects.filter(user = request.user, product_id =product_varient.id).first()
                if Wishlist:
                    product_varient.whish=True
    return render(request, 'user/index.html', {'products_with_variants': products_with_variants})


def sort(request,pid,w):
    sizes=Size.objects.all()
    category = Category.objects.all()
    subcategory = SubCategory.objects.all()
    prod= Product.objects.all()
    brand=Brand.objects.all()
    another=ProductVarient.objects.all()
    colors = ProductVarient.objects.values_list('color', flat=True).distinct()

    if w== 0:
        S_category = Category.objects.get(id=pid)
        c_prod = Product.objects.filter(category_id=S_category).first()
        product = ProductVarient.objects.filter(Product_id=c_prod)
    elif w== 1:
        S_subcategory = SubCategory.objects.get(id=pid)
        c_prod = Product.objects.filter(subcategory_id=S_subcategory).first()
        product = ProductVarient.objects.filter(Product_id= c_prod)
    else:
        b_brand = Brand.objects.get(id=pid)
        c_prod = Product.objects.filter(brand_id=b_brand).first()
        product = ProductVarient.objects.filter(Product=c_prod)
    if request.method == 'POST':
        color = request.POST['color'] 
        product = ProductVarient.objects.filter(color=color)
    for variants in product:
        product.sizes = sizes
        offer_price = round(variants.price -( variants.price *(variants.offer/100 )))if variants.offer else variants.price
        variants.offer_price = offer_price
    
    context={
             'prod': prod,
             'category':category,
             'subcategory':subcategory,
             'product':product,
             'sizes':sizes,
             'brand':brand,
             'colors':colors,
             'another':another
             }
    if request.user.is_authenticated:
        wishlist_products = wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        context.update({'wishlist_product_ids': wishlist_products})
    return render(request, 'user/shop.html', context)
    
        

        
        

        

def shop(request):
    sizes=Size.objects.all()
    category = Category.objects.all()
    subcategory = SubCategory.objects.all()
    prod = Product.objects.all()
    product = ProductVarient.objects.all()
    brand=Brand.objects.all()
    for variants in product:
        product.sizes = sizes
        offer_price = round(variants.price -( variants.price *(variants.offer/100 )))if variants.offer else variants.price
        variants.offer_price = offer_price
    
    context={
             'prod': prod,
             'category':category,
             'subcategory':subcategory,
             'product':product,
             'sizes':sizes,
             'brand':brand
             }
    if request.user.is_authenticated:
        wishlist_products = wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        context.update({'wishlist_product_ids': wishlist_products})
    return render(request, 'user/shop.html', context)
    

def register(request):
    
    if request.method == 'POST':
        # Get form data
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        

        # Check if password and confirm password match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect(register)
        
        else:

        # Generate OTP
            otp = get_random_string(length=4, allowed_chars='1234567890')
        
        # Save user details to database
            user = User.objects.create_user(username=username, password=password, email=email)
        
        # Send OTP to user email
            print(otp)
            subject = 'OTP for account verification'
            message = f'Your OTP for account verification is {otp}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email,]
            send_mail(subject, message, email_from, recipient_list)


         # Create UserProfile object for the user
            UserProfile.objects.create(user=user)
            
        # Save OTP to database
            user.profile.otp = otp
            user.profile.save()
        
        # Redirect to OTP verification page
            return redirect('verifyotp', user.id)

    return render(request, 'user/register.html')


#OTP verification

def verify_otp(request, user_id):
    
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        otp = request.POST['otp']
        if user.profile.otp == otp:
            user.profile.is_verified = True
            user.profile.otp = ''
            user.profile.save()
            messages.success(request, 'Account has been verified')
            return redirect(index)
        else:
            messages.error(request, 'Invalid OTP')
            
            return redirect('verifyotp', user_id)
    return render(request, 'user/verify_otp.html', {'user': user})


#Resend OTP

def resend_otp(request, user_id):
    user = User.objects.get(id=user_id)

    # Generate new OTP
    otp = get_random_string(length=4, allowed_chars='1234567890')

    # Send new OTP to user email
    
    subject = 'New OTP for account verification in kaira'
    message = f'Your new OTP for account verification is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email,]
    print(otp)
    send_mail(subject, message, email_from, recipient_list)

    # Save new OTP to database
    user.profile.otp = otp
    user.profile.save()

    messages.success(request, 'New OTP has been sent to your email')
    return redirect('verifyotp', user_id)

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            otp = get_random_string(length=4, allowed_chars='1234567890')
            user.profile.otp = otp
            print(otp)
            user.profile.save()
            subject = 'OTP for password reset in kaira'
            message = f'Your OTP for password reset is {otp}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email,]
            send_mail(subject, message, email_from, recipient_list)
            return redirect('resetpass', user.id)
        else:
            messages.error(request, 'Email does not exist')
            return redirect(forgot_password)
    return render(request, 'user/forget_password.html')





def reset_password(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        otp = request.POST['otp']
        if user.profile.otp == otp:
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            if password == confirm_password:
                user.set_password(password)
                user.profile.otp = ''
                user.profile.save()
                user.save()
                messages.success(request, 'Password reset successful. Please login.')
                return render(request,'user/login.html')
            else:
                messages.error(request, 'Passwords do not match')
        else:
            messages.error(request, 'Invalid OTP')
    return render(request, 'user/reset_password.html', {'user': user})


def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "User login successful")
            request.session['username'] = username

            # check if there is a cart session
            cart = request.session.get('cart', {})
            if cart:
                for cart_item_key, cart_item in cart.items():
                    # extract product id and size from cart item key
                    product_id, size = cart_item_key.split('-')

                    # get the product variant and stock
                    product = ProductVarient.objects.get(id=product_id)
                    product_stock = Size.objects.filter(varient=product_id, size=size).first()
                    stock = product_stock.stock

                    # check if quantity is less than or equal to stock
                    quantity = cart_item['quantity']
                    if quantity <= stock:
                        cart_item, created = CartItem.objects.get_or_create(
                            product=product,
                            user=request.user,
                            size=size if request.user.is_authenticated else None,
                            is_active=True
                        )

                        if not created and not request.user.is_authenticated:
                            cart_item.quantity += int(quantity)
                            cart_item.save()

                        if cart_item.quantity < stock:
                            cart_item.quantity += 1
                            cart_item.save()

                        messages.success(request, f"{quantity} x {product.name} added to cart!")
                    else:
                        messages.error(request, f"{quantity} x {product.name} could not be added to cart: insufficient stock!")

                # clear the cart session after adding to the user's cart
                request.session['cart'] = {}

            return redirect(index)

        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'user/login.html', {})





def logout(request):  #LOGOUT REQUEST

    auth.logout(request)
    return redirect('home')


def user(request):
    if request.user.is_authenticated:

        return render(request,'user/user.html')
    else:
        return redirect('login',)


def user_update(request):
    user_profile = UserProfile.objects.get(user=request.user)
    user_form = UserForm(instance=request.user)
    profile_form = UserProfileForm(instance=user_profile)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)  # don't save the profile yet
            if 'image' in request.FILES:
                print('ureka!!')
                profile.image = request.FILES['image']
            user_profile = profile.save()  # now save the profile
            messages.info(request, 'Updated Successfully')
            return redirect('user')
    return render(request,'user/user_update.html',{'user_form': user_form,'profile_form': profile_form})

def singleproduct(request, slug):
    whish = False
    prod = ProductVarient.objects.get(id=slug)
    product = Product.objects.get(id=prod.Product.id)
    offer= round(prod.price -( prod.price *(prod.offer/100 )))
    images = ProductImage.objects.filter(varient_id=slug)
    size = Size.objects.filter(varient_id=slug)
    color= ProductVarient.objects.filter(Product=product)
    if request.user.is_authenticated:
        Wishlist= wishlist.objects.filter(user = request.user, product_id = prod.id).first()
        if Wishlist:
            whish = True 
    print(whish)    
    print(slug)
    return render(request, 'user/singleproduct.html', locals())

def singleproductmodeal(request, slug):
    whish = True
    prod = ProductVarient.objects.get(id=slug)
    product = Product.objects.get(id=prod.Product.id)
    offer= round(prod.price -( prod.price *(prod.offer/100 )))
    images = ProductImage.objects.filter(varient_id=slug)
    size = Size.objects.filter(varient_id=slug)
    color= ProductVarient.objects.filter(Product=product)
    if request.user.is_authenticated:
        Wishlist= wishlist.objects.filter(user = request.user, product_id = prod.id).first()
        if Wishlist is  None:
            whish = False 
    size_list = list(size.values())
    print(whish)    
    print(slug)
    data = {
        'size_data': size_list  ,
    }
    print(size_list)
    return JsonResponse(data,safe=False)


def search(request):
    keyword = request.GET.get('keyword')
    print(keyword)
    products = Product.objects.filter(Q(description_icontains=keyword) | Q(name_icontains=keyword)).order_by('created')
    # paginator = Paginator(products, 2)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)
    allcategory = Category.objects.all() 
    context = {
        'categories': Category.objects.all(),
        'product': products,
        'keyword' : keyword,
        'allcategory' : allcategory,
        # 'page_obj': page_obj
        
        
    }
    return render(request, 'user/shop.html', context)




def address_book(request):
    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        selected_addresses = request.POST.getlist('selected_addresses')
        Address.objects.filter(id__in=selected_addresses).delete()
        return redirect(address_book)
    return render(request, 'user/adressbook.html', {'addresses': addresses})    




def add_address(request,w):
    state = ['Kerala', 'AndraPradesh', 'Karnataka', 'Tamilnadu']
    city = ['Kannur','Kozhikkode','Ernakulam','Thiruvananthapuram','Banglore','Hubli','Hydrabad','Coimbator','Madurai']
    if request.method == 'POST':
        address = Address(
            user=request.user,
            firstname=request.POST['firstname'],
            lastname=request.POST['lastname'],
            phone=request.POST['phone'],
            email=request.POST['email'],
            address_line_1=request.POST['address_line_1'],
            address_line_2=request.POST.get('address_line_2', ''),
            city=request.POST['city'],
            state=request.POST['state'],
            pincode=request.POST['pincode']
        )
        addresses = Address.objects.filter(user=request.user)
        if not addresses.exists():
            address.is_default=True
        address.save()

        # set default address
        if request.POST.get('default', '') == 'on':
            # set all other addresses as non-default
            Address.objects.filter(user=request.user).exclude(id=address.id).update(is_default=False)
            address.is_default = True
            address.save()
        if w==0:
            return redirect('address_book')
        else:
            return redirect('checkout')
    else:
        context = {
            'state': state,
            'city': city,
        }
    return render(request, 'user/addadress.html', context)

def changepassword(request):
    if request.method == 'POST':
        oldpass = request.POST['currentpassword']
        newpass = request.POST['newpassword']
        confirm_newpass = request.POST['confirmpassword']
        user = authenticate(username=request.user.username, password=oldpass)
        if user:
            if newpass == confirm_newpass:
                user.set_password(newpass)
                user.save()
                messages.success(request, "Password Changed")
                return redirect(loginpage)
            else:
                messages.success(request, "Password not matching")
                return redirect(changepassword)
        else:
            messages.success(request, "Invalid Password")
            return redirect(changepassword)
        
    return render(request, 'user/userchangepassword.html')


def myorders(request):
    orders = Order.objects.filter(user=request.user).order_by('id').reverse()
    return render(request, 'user/userorder.html', {'orders': orders})

def cancelOrder(request):
    if request.method == 'POST':
            id = request.POST.get('id')

    client = razorpay.Client(auth=(kaira.settings.API_KEY, kaira.settings.RAZORPAY_SECRET_KEY))
    try:
        order = Order.objects.get(id=id,user=request.user)
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        order = None
    
    if order is None:
        # Render an error message if the order does not exist
        messages.warning(request,'The order you are trying to cancel does not exist.')
        return redirect(myorders)
    
    payment=order.payment
    msg=''
    
    if (payment.payment_method == 'Paid by Razorpay'):
        payment_id = payment.payment_id
        amount = payment.amount_paid
        amount= amount*100
        try :
            captured_amount = client.payment.capture(payment_id,amount)
        except BadRequestError as e:
            # Handle a BadRequestError from Razorpay
            captured_amount = None
            messages.warning(request,'The payment has not been captured.Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!')
            return redirect(myorders)
        #   except ServerError as e:
              # Handle a ServerError from Razorpay
        #   captured_amount = None
            # msg = "Server error occurred while capturing the payment."

        if captured_amount is not None and captured_amount['status'] == 'captured' :
            refund_data = {
                "payment_id": payment_id,
                "amount": amount,  # amount to be refunded in paise
                "currency": "INR",
            }
            
            refund = client.payment.refund(payment_id, refund_data)
            #  except BadRequestError as e:
            #      # Handle a BadRequestError from Razorpay
            #      refund = None
            #      msg = "Bad request error occurred while processing the refund."
            #  except ServerError as e:
            #      # Handle a ServerError from Razorpay
            #      refund = None
            #      msg = "Server error occurred while processing the refund."
            print(refund)
            
            if refund is not None:
                current_user=request.user
                order.refund_completed = True
                order.status = 'Cancelled'
                payment = order.payment
                payment.refund_id = refund['id']
                payment.save()
                order.save()
                messages.success(request,'Your order has been successfully cancelled and amount has been refunded!')
                mess=f'Hai\t{current_user.username},\nYour order has been canceled, Money will be refunded with in 1 hour\nThanks!'
                try:
                    send_mail(
                            "Order Cancelled",
                            mess,
                            settings.EMAIL_HOST_USER,
                            [current_user.email],
                            fail_silently = False
                        )
                except Exception as e:
                    # Handle an exception while sending email
                    msg += "\nError occurred while sending an email notification."
            else :
                messages.warning(request,'Your order is not cancelled because the refund could not be completed now. Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!')
                pass
        else :
            if(payment.paid):
                order.refund_completed = True
                order.status = 'Cancelled'
                messages.success(request,'YOUR ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
                order.save()
            else:
                order.status = 'Cancelled'
                order.save()
                messages.success(request,'Your payment has not been recieved yet. But the order has been cancelled.!')
    else :
        order.status = 'Cancelled'
        messages.success(request,'YOUR ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
        order.save()
    return redirect(myorders)

def viewOrder(request, id):
    order =Order.objects.filter(id=id,user=request.user).first()
    orderitems = OrderProduct.objects.filter(order=order)
    payment=Payment.objects.get(order_id=order.order_number)

    context={
        'order': order,
        'orderitems':orderitems,
        'payment':payment
    }
    return render(request,'user/orderdetials.html',context)