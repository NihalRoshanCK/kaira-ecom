from product.models import *
from user.models import *
from user.models import *
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
import random,datetime
from django.shortcuts import render







# def subtotal(items):
#     cart_items = []
#     total = 0
#     for cart_item in items:
#         product = get_object_or_404(ProductVarient, id=cart_item.product_id)
#         quantity = cart_item.quantity
#         price = round(product.price-(product.price* (product.offer/100))) * quantity
#         size=Size.objects.get(varient_id=product.id)
#         cart_items.append({'product':product,'quantity':quantity,'price':price}) 
#         if size.stock == 0:
#             pass
#         else:
#             total += price   
#     context = { 'cart_items': cart_items, 'total': total }
#     return context


def subtotal(current_user):
    cart_items = []
    total = 0
    grandtotal=0
    shiping=500
    discount_display=0
    state = ['Kerala', 'AndraPradesh', 'Karnataka', 'Tamilnadu']
    city = ['Kannur','Kozhikkode','Ernakulam','Thiruvananthapuram','Banglore','Hubli','Hydrabad','Coimbator','Madurai']
    address=Address.objects.filter(user=current_user)
    items = CartItem.objects.filter(user_id=current_user.id).order_by('id')
    # where get addres (its alredy get in views here it add on context)
    address=address
    # where getting the price 
    for cart_item in items:
        product = get_object_or_404(ProductVarient, id=cart_item.product_id)
        quantity = cart_item.quantity
        price = product.price* quantity
        offer=(product.price-(product.price * (product.offer/100))) * quantity
        discount = price-offer
        discount_display+=discount
        size=Size.objects.get(varient_id=product.id,size=cart_item.size )
        cart_items.append({'product':product,'quantity':quantity,'price':price}) 
        # where get the total
        if size.stock == 0:
            pass
        else:
            total += price-discount
    if total < 20000:
        grandtotal= total+ shiping
    else:
        grandtotal=total
    context = { 'cart_items': cart_items, 'total': total , 'grandtotal':grandtotal,'discount_display':discount_display , 'address':address ,'city':city ,'state':state}
    return context

def coupon_check(coupon_code,current_user,grand_total):
    amountToBePaid =0
    msg=''
    coupon_discount = 0
    coupon = ''
    extra_discount = False
    coupon = ''
    try:
        coupon = Coupon.objects.get(code = coupon_code)
        coupon_discount = 0
    
        if (coupon.active):
            try:
                
                instance = UserCoupon.objects.get(user=current_user, coupon=coupon)
               
            except ObjectDoesNotExist:
          
                instance = None
            
            if(instance):
                
                pass
            else:
                
                instance = UserCoupon.objects.create(user = current_user ,coupon = coupon)
            if(not instance.used):
                if float(grand_total) >= float(instance.coupon.min_value):
                    coupon_discount = ((float(grand_total) * float(instance.coupon.discount))/100)
                    amountToBePaid = float(grand_total) - coupon_discount
                    amountToBePaid = format(amountToBePaid, '.2f')
                    coupon_discount = format(coupon_discount, '.2f')
                    msg = 'Coupon Applied successfully'
                    extra_discount=True
                    
                else:
                    msg='This coupon is only applicable for orders more than ₹'+ str(instance.coupon.min_value)+ '\- only!'
            else:
                msg = 'Coupon is already used'
        else:
            msg="Coupon is not Active!"
    except:
        msg="Invalid Coupon Code!"
        
    
    check={
        'coupon':coupon,'coupon_discount':coupon_discount,'extra_discount':extra_discount,'amountToBePaid':amountToBePaid
        }
    return check



def createorder(newAddress_id,current_user,mode,discount_Display,price,couponCode,total,couponDiscount,razorpay_order_id):
        address = Address.objects.get(id = newAddress_id)
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr,mt,dt)
        current_date = d.strftime("%Y%m%d")
        rand = str(random.randint(1111111,9999999))
        order_number = current_date + rand
        cash = 0
        newPayment = Payment()
        newOrder =Order()
        grand_total = calculateCartTotal(current_user,cash)
        if  mode == "cod":
            print("cod")
            newPayment.order_id =order_number
            newPayment.payment_method = "Cash On Delevery"
            newPayment.customer = current_user
            newPayment.amount_paid = price
            newPayment.save()
            newOrder.order_number=order_number
            newOrder.user=current_user
            newOrder.address = address
            newOrder.order_discount=float(discount_Display)+float(couponDiscount)
            newOrder.order_total = float(total)+float(discount_Display)+float(couponDiscount)
            newOrder.paid_amount = price
            if float(total)<20000:
                newOrder.is_shipping=True
            newOrder.is_ordered = True
            newOrder.payment = newPayment
            newOrder.used_coupon = couponCode
            newOrder.save()
            newOrder.order_number =order_number
            newOrderItems = CartItem.objects.filter(user=current_user)
            for item in newOrderItems:
                OrderProduct.objects.create(
                    order = newOrder,
                    customer=current_user,
                    product=item.product,
                    product_price=item.product.price,
                    quantity=item.quantity,
                    ordered=True
                )
                #TO DECRESE THE QUANTITY OF PRODUCT FROM CART
                variant = ProductVarient.objects.filter(id=item.product_id).first()
                s= item.size
                orderproduct = Size.objects.filter(varient = variant, size=s).first()
                if orderproduct.stock - item.quantity >= 0:
                    orderproduct.stock -= item.quantity
                    orderproduct.save()
            try:
                coupon = Coupon.objects.filter(code=couponCode).first()
                user_coupon = UserCoupon.objects.filter(user=current_user, coupon=coupon).first()
                user_coupon.used=True
                user_coupon.order=newOrder
                user_coupon.save()
            except:
                pass
            cart=CartItem.objects.filter(user=current_user)
            cart.delete()
            return newOrder.order_number
                # messages.success(request,  f"{orderproduct.stock} only left in cart.")
        else:
            print("razorpay")
            newPayment.razorpay_order_id = razorpay_order_id  
            newPayment.payment_method = 'Razorpay'
            newPayment.customer=current_user
            newPayment.amount_paid=price
            newPayment.order_id =order_number
            newPayment.save()
            newOrder.user=current_user
            newOrder.order_number=order_number
            newOrder.address = address
            newOrder.order_discount=float(discount_Display)+float(couponDiscount)
            newOrder.order_total = float(total)+float(discount_Display)+float(couponDiscount)
            newOrder.paid_amount = price 
            newOrder.payment = newPayment
            if float(total)<20000:
                newOrder.is_shipping=True
            newOrder.save()
            return

def calculateCartTotal(current_user,cash):
   cart_items   = CartItem.objects.filter(user=current_user)
   if not cart_items:
       pass
    #   return redirect('product_management:productlist',0)
   else:
    #   grand_total=0
      for cart_item in cart_items:
         cash  += (cart_item.product.price * cart_item.quantity)
        #  tax = (5 * total) / 100
        #  grand_total = tax + total
   return cash