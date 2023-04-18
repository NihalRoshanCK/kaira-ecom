from django.shortcuts import render ,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from .utils import subtotal , coupon_check,createorder
from user.models import *
from .models import *
from product.views import *
from user.views import *
from django.contrib import messages
from django.contrib.auth.models import User
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import kaira.settings
from django.http import HttpResponseBadRequest
# Create your views here.


def addcart(request, product_id):
    if request.method=='GET':
        size=request.GET.get('size')
        quantity=request.GET.get('quantity')
        product = ProductVarient.objects.get(id=product_id)
        productstock= Size.objects.filter(varient=product_id,size=size).first()
        stock=productstock.stock
        if request.user.is_authenticated:
            print(stock)
            if quantity is None:
                quantity = 1
            cart_item, created = CartItem.objects.get_or_create(product=product,user=request.user , size=size if request.user.is_authenticated else None,is_active=True)
            if not created and not request.user.is_authenticated:
                cart_item.quantity += int(quantity)
                cart_item.save()
            if cart_item.quantity<stock:
                print(cart_item.quantity)
                cart_item.quantity += 1
                cart_item.save()
                return redirect('singleproduct',product_id)
        else:
            cart = request.session.get('cart', {})
            cart_item_key = f"{product_id}-{size}"
            if cart_item_key in cart:
            #     cart_item = cart[cart_item_key]
            #     cart_item['quantity'] += 1
                messages.success(request, f"{quantity} x {product.name} Log in for access more Quantity ")
            else:
                cart[cart_item_key] = {
                    'quantity': 1,
                    'size': size,
                }
                messages.success(request, f"{quantity} x {product.name} added to cart! (session)")
            request.session['cart'] = cart
            # return redirect('singleproduct', product_id)
            return redirect('singleproduct', product_id)

def viewcart(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:
        cart = request.session.get('cart', {})
        cart_items = []
        for key, value in cart.items():
            product_id, size = key.split('-')
            product = ProductVarient.objects.get(id=product_id)
            cart_item = {
                'product': product,
                'size': size,
                'quantity': value['quantity']
            }
            cart_items.append(cart_item)

    total = 0
    discount = 0
    for item in cart_items:
        if request.user.is_authenticated:
            product_price=item.product.price
            offer=item.product.offer
            quantity=item.quantity
        else:
            product_price = item['product'].price
            offer = item['product'].offer
            quantity = item['quantity']
        price_after_discount = product_price - (product_price * offer/100)
        total += price_after_discount * quantity
        discount += product_price * quantity - (price_after_discount * quantity)
        discount=round(discount,2)

    context = {'cart_items': cart_items, 'total': total, 'discount': discount}
    return render(request, 'product/cart.html', context)


# def viewcart(request):
#     if request.user.is_authenticated:
#         cart_items = CartItem.objects.filter(user=request.user, is_active=True)
#         total=0
#         discount=0
#         for item in cart_items:
#             total+=(item.product.price - (item.product.price * item.product.offer/100))* item.quantity
#             discount+=(item.product.price-((item.product.price - (item.product.price * item.product.offer/100))* item.quantity))
#             discount=round(discount, 2)
#         context = {'cart_items': cart_items,'total':total,'discount':discount}
#     else:
#         cart = request.session.get('cart', {})
#         cart_items = []
#         for key, value in cart.items():
#             product_id, size = key.split('-')
#             product = ProductVarient.objects.get(id=product_id)
#             productstock = Size.objects.filter(varient=product_id, size=size).first()
#             stock = productstock.stock
#             cart_item = {
#                 'product': product,
#                 'size': size,
#                 'quantity': value['quantity'],
#                 'stock': stock,
#             }
#             cart_items.append(cart_item)
#         context = {'cart_items': cart_items}
#     return render(request, 'product/cart.html', context)

def remove_cart(request, product_id ,size):
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product_id=product_id, size    =size, user=request.user, is_active=True)  
        cart_item.delete()
        messages.success(request, f"{cart_item.product.name} removed from cart!")
        return redirect(viewcart)
    else:
        cart = request.session.get('cart', {})
        try:
            product_id_str = str(product_id)
            for key, value in cart.items():
                if key.startswith(product_id_str):
                    size = key.split('-')[1]
                    product = ProductVarient.objects.get(id=product_id)
                    productstock = Size.objects.filter(varient=product_id, size=size).first()
                    stock = productstock.stock
                    del cart[key]
                    request.session['cart'] = cart
                    messages.success(request, f"{product.name} ({size}) removed from cart!")
                    break
            else:
                raise KeyError
        except KeyError:
            messages.error(request, "The selected item does not exist in your cart.")
        return redirect(viewcart)
    
def additem(request,product_id,product_size):
    if request.user.is_authenticated :
        product = get_object_or_404(ProductVarient, id=product_id)
        item=CartItem.objects.get(user_id=request.user.id, product=product,size=product_size)
        productstock= Size.objects.get(varient=product_id,size=product_size)
        stock=productstock.stock
        item.quantity = item.quantity + 1
        if (stock>=item.quantity):
            item.save()
            return redirect(viewcart)
        else:
            messages.warning(request,"Product Out Of Stock...! Can't be added to cart")
            return redirect(viewcart)

    else:
        messages.warning(request, "Please log in to add items to cart.")
        return redirect(loginpage)
    
    
def removecartitem(request,product_id,product_size):
    
    product = get_object_or_404(ProductVarient, id=product_id)
    cart_items = CartItem.objects.filter(user_id=request.user.id, product=product, size=product_size)
    for cart_item in cart_items:
        if cart_item.quantity == 1:
            cart_item.delete()  # remove the item from the cart if the quantity is 1
        else:
            cart_item.quantity -= 1
            cart_item.save()  # decrement the quantity by 1
    return redirect(viewcart)


def viewwishlist(request):
    if request.user.is_authenticated:
        witems=wishlist.objects.filter(user_id=request.user.id)
        context={
            'witems':witems,
        }
        return render(request,'product/wishlist.html',context)
    return render (request,'user/login.html')
    


def add_to_wishlist(request,product_id ,w):
    if request.user.is_authenticated:
        product = ProductVarient.objects.get(id=product_id)
        if wishlist.objects.filter(product=product,user_id=request.user.id).exists():
            messages.info(request, "Product already exist in wishlist")
            return redirect('shop')
            
        else:
            wishlist.objects.create(product=product,user_id=request.user.id)
            messages.success(request,"Product added to wishlist")
            return redirect('shop')
        
    else:
        match w:
            case 1:
                return redirect('singleproduct','product_id')
            case _:
                return redirect('shop')
        messages.warning(request, "Please log in to add items to wishlist.")
        return render (request,'user/login.html')

def remove_from_wishlist(request,product_id,w):
    wishItem=wishlist.objects.get(product_id=product_id,user_id=request.user.id)
    wishItem.delete()
    match w:
        case 0:
            return redirect(viewwishlist)
        case 1:
            return redirect('singleproduct','product_id')
        case 2:
            return redirect('shop')
    
def checkout(request):
    if request.user.is_authenticated:
        current_user=request.user
        context=subtotal(current_user)
        if ('couponCode' in request.POST):
            grand_total = request.POST.get('grand_total')    
            coupon_code = request.POST.get('couponCode')
            check= coupon_check(coupon_code,current_user,grand_total)
            context.update(check)
        return render(request,'product/checkout.html',context)
    messages.warning(request, "Please log in to use checkout.")
    return redirect('login')

razorpay_client = razorpay.Client(auth=(kaira.settings.API_KEY, kaira.settings.RAZORPAY_SECRET_KEY))


def confirmation(request):
    # try:
    current_user=request.user
    cart_items=CartItem.objects.filter(user=request.user)
    newAddress_id = request.POST.get('selected_addresses')
    if request.method == "POST":
        if newAddress_id is None:
         return redirect('checkout')
        total = request.POST["total"]
        try:
            price=float(request.POST["amountToBePaid"])
        except:
            price= float(request.POST["grand_total"])
        try:
            couponCode=request.POST["couponCode"]
            couponDiscount=float(request.POST["couponDiscount"])
        except:
            couponDiscount=0
        try:
            discount_Display=float(request.POST["discount_Display"])
        except:
            couponDiscount=0
        mode =request.POST["mode"]
        if mode == 'Razorpay':
            amount =price*100 
            currency = 'INR'
            # Create a Razorpay Order
            
            razorpay_order = razorpay_client.order.create(dict(amount=amount,currency=currency,payment_capture='0'))
            # order id of newly created order.
            razorpay_order_id = razorpay_order['id']
            print(razorpay_order_id,"*********************************************")
            createorder(newAddress_id,current_user,mode,discount_Display,price,couponCode,total,couponDiscount,razorpay_order_id)
            callback_url = '/product/paymenthandler/'
            # we need to pass these details to frontend.
            context = {}
            context['razorpay_order_id'] = razorpay_order_id
            context['razorpay_merchant_key'] = settings.API_KEY
            context['razorpay_amount'] = amount
            context['currency'] = currency
            context['callback_url'] = callback_url
            context['cart_items'] = cart_items
            context['couponDiscount'] = couponDiscount
            # context['addressSelected'] = addressSelected
            context['couponCode'] = couponCode
            context['price'] = price
            context['total'] = total

            return render(request, 'product/confirmation.html', context=context)
            
        else:
            a=0
            neworder=createorder(newAddress_id,current_user,mode,discount_Display,price,couponCode,total,couponDiscount,a)
            
            return redirect ('invoice',neworder)

def invoice(request,order):
    conform_order = Order.objects.get(user=request.user,order_number=order)
    orderitem = OrderProduct.objects.filter(customer=request.user,order=conform_order)
    payment=Payment.objects.get(order_id=conform_order.order_number)
    total=0
    for i in orderitem:
        total +=i.product_price
    context={
            'conform_order':conform_order,
            'orderitem':orderitem,
            'payment':payment,
            'total':total
            }
    return render(request, 'product/invoice.html', context=context)
   

 
@csrf_exempt
def paymenthandler(request):
    # only accept POST request.
    if request.method == "POST":
        try:
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            # verify the payment signature.
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            payment.payment_id = payment_id
            payment.save()
            order=Order.objects.get(order_number=payment.order_id)
            newOrderItems = CartItem.objects.filter(user=request.user)
            print(order.order_number)
            try:
                coupon = Coupon.objects.filter(code=order.used_coupon).first()
            except:
                pass
            # print(coupon.code)
            
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is not None:
                amount =int(payment.amount_paid*100)  # Rs. 200
                try:
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount) 
                    order.is_ordered=True
                    order.save()
                    payment.paid=True
                    payment.save()
                    try:
                        user_coupon = UserCoupon.objects.filter(user=request.user, coupon=coupon).first()
                        user_coupon.used=True
                        user_coupon.order=Order
                        user_coupon.save()
                    except:
                        pass
                    for item in newOrderItems:
                        OrderProduct.objects.create(
                            order = order,
                            customer=request.user,
                            product=item.product,
                            product_price=item.product.price,
                            quantity=item.quantity,
                            ordered=True
                        )
                        variant = ProductVarient.objects.filter(id=item.product_id).first()
                        s= item.size
                        orderproduct = Size.objects.filter(varient = variant, size=s).first()
                        if orderproduct.stock - item.quantity >= 0:
                            orderproduct.stock -= item.quantity
                            orderproduct.save()
                    cart=CartItem.objects.filter(user=request.user)
                    cart.delete()
                    # render success page on successful caputre of payment
                    return redirect ('invoice', order)
                except:
                    order.delete()
                    payment.save()
                    # if there is an error while capturing payment.
                    return render(request, 'paymentfail.html')
            else:
                
                # if signature verification fails.
                return render(request, 'product/invoice.html')
        except:
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
        
       # if other than POST request is made.
        return HttpResponseBadRequest()

