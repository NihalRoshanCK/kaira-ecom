from django.shortcuts import render,redirect,get_object_or_404 
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth.models import User,auth
from django.contrib.auth.decorators import login_required,user_passes_test
from user.models import *
from product.models import *
from .form import CouponForm
from django.core.paginator import Paginator
from django.db.models import Q,Sum,F
import razorpay
from django.conf import settings
import kaira.settings
from datetime import datetime
from django.core.mail import send_mail


# Create your views here.

def adminlogin(request):
    if request.user.is_superuser:
        return redirect('admindashboard')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect(admindashboard)
        else:
            messages.error(request, "Username or password mismatch")
    return render(request, 'adminpanel/admin_login.html')

# @user_passes_test(lambda u:u.is_superuser,login_url='adminlogin')
# def admindash(request):
#     return render(request, 'adminpanel/admin_dash.html')

def adminlogout(request):
    auth.logout(request)
    if 'username' in request.session:
            request.session.flush()
    return redirect(adminlogin)

def add_Category(request):
    if request.method == "POST":
        name = request.POST['name']
        if Category.objects.filter(name__iexact=name.lower().replace(' ', '')).exists():
            messages.error(request,'category already exist')

        else:
            Category.objects.create(name=name)
            messages.success(request,'category created successfully')
            return redirect(view_Category)

    return render (request,'adminpanel/addcategory.html',locals())



def view_Category(request):
    category = Category.objects.all()
    return render (request,'adminpanel/viewcategory.html',locals())

def editcategory(request, pid):
    category = Category.objects.get(id=pid)
    if request.method == 'POST':
        name = request.POST['name']
        if Category.objects.filter(name__iexact=name.lower().replace(' ', '')).exists():
            messages.info(request,"Category already exists")  
        else:
            category.name = name
            category.save()
            messages.success(request,'category edited successfully')
            return redirect(view_Category)
    return render(request, 'adminpanel/editcategory.html', locals())

def deletecategory(request, pid):
    category = Category.objects.get(id=pid)
    category.delete()
    messages.success(request,'category deleted successfully')
    return redirect(view_Category)



def add_Subcategory(request):
    category = Category.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        main_category_id = request.POST['maincategory']
        main_category = Category.objects.get(id=main_category_id)
        if SubCategory.objects.filter(name__iexact=name.lower().replace(' ', '')).exists():
            messages.error(request,'subcategory already exist')
        else:
            SubCategory.objects.create(main_category=main_category,name=name)
            messages.success(request,'Sub category created successfully')
            return redirect(view_Subcategory)
    return render (request,'adminpanel/addsubcategory.html',locals())

def view_Subcategory(request):
    sub_category = SubCategory.objects.all()
    return render (request,'adminpanel/viewsubcategory.html',locals())

def view_Brand(request):
    brand = Brand.objects.all()
    return render (request,'adminpanel/viewbrands.html',locals())

def add_Brand(request):
    if request.method == "POST":
        name = request.POST['name']
        if Brand.objects.filter(name__iexact=name.lower().replace(' ', '')).exists():
            messages.error(request,'brand already exist')

        else:
            Brand.objects.create(name=name)
            messages.success(request,'brand created successfully')
            return redirect(view_Brand)

    return render (request,'adminpanel/addbrand.html',locals())

# def view_Color(request):
#     color = Color.objects.all()
#     return render (request,'adminpanel/viewcolor.html',locals())


def add_Product(request):
    brand=Brand.objects.all()
    sub_category = SubCategory.objects.all()
    category = Category.objects.all()
    if request.method == 'POST':
        name = request.POST['name']
        brand= request.POST['brand']
        sub_category=request.POST['sub_category']
        category = request.POST['categories']
        desc = request.POST['desc']
        category_id = Category.objects.get(id=category)
        # color_id = Color.objects.get(id=color)
        brand_id = Brand.objects.get(id=brand)
        sub_category_id = SubCategory.objects.get(id=sub_category)
        product = Product.objects.create( name = name  ,subcategory = sub_category_id , brand = brand_id ,  category = category_id , description = desc )
        product.save()
        messages.success(request, "Product Added")
        return redirect(view_Product)
    return render (request,'adminpanel/addproduct.html',locals())

def view_varient(request):
    varient=ProductVarient.objects.all().order_by('id')
    image=ProductImage.objects.all()
    context={
        'varient':varient,
        'image':image,
    }
    return render (request,"adminpanel/viewvarient.html",context)
def view_Product(request):
    product = Product.objects.all().order_by('id')
    
    context = {
        'product' : product,
    }
    return render (request,'adminpanel/viewproduct.html',context)

def add_varients(request):
    color= ['White','Black','Green','Red','Yellow','Blue','Brown','Orange']
    product=Product.objects.all()
    if request.method == 'POST':
        name = request.POST['name']
        color=request.POST['color']
        product=request.POST['product']
        price=request.POST['price']
        offer=request.POST['offer']
        images = request.FILES.getlist('image')
        hoverimage = request.FILES.get('hover_image')
        # size=request.POST['size']
        # stock=request.POST['stock']
        product_id = Product.objects.get(id=product)
        varient = ProductVarient.objects.create( name = name  , color = color ,  Product = product_id , price = price, offer = offer )
        varient.save()
        for image in images :
            ProductImage.objects.create( varient = varient , images = image,hover_images = hoverimage)
        messages.success(request, "Product Added")
        Size.objects.create(varient=varient,size=size,stock=stock)
    return render (request,'adminpanel/addproductvarient.html',locals())   
        

def edit_Subcategory(request,pid):
    subcategory=SubCategory.objects.get(id=pid)
    category=Category.objects.all()
    if request.method=='POST':
        sub = request.POST['sub']
        main=request.POST['main']
        if SubCategory.objects.filter(name__iexact=sub.lower().replace(' ', '')).exists():
            messages.info(request,"SubCategory already exists") 
        else:
            subcategory.name=sub
            subcategory.main_category=main
            subcategory.save()
            messages.success(request,'SubCategory edited successfully')
            return redirect('view_Subcategory')
    return render (request,'adminpanel/editsubcategory.html',locals())

def edit_brand(request,pid):
    brand=Brand.objects.get(id=pid)
    if request.method=="POST":
        name=request.POST['name']
        if Brand.objects.filter(name__iexact=name.lower().replace(' ', '')).exists():
            messages.info(request,"Brand already exists")
        else:
            brand.name=name
            brand.save()
            messages.success(request,'Brand edited successfully')
            return redirect('view_Brand')
    return render (request,'adminpanel/editbrand.html',locals())

def edit_product(request,pid):
    product=Product.objects.get(id=pid)
    category=Category.objects.all()
    subcategor=SubCategory.objects.all()
    brand=Brand.objects.all()
    if request.method=="POST":
        name=request.POST["name"]
        catogory=request.POST["catogory"]
        subcatogory=request.POST["subcatogory"]
        brand=request.POST["brand"]
        description=request.POST["desc"]
        if Brand.objects.filter(name__iexact=name.lower().replace(' ', '')).exists():
            messages.info(request,"Product name already exists")
        else:
            product.name=name
            product.category=catogory
            product.subcategory=subcatogory
            prodect.brand=brand
            product.description=description
            product.save()
            messages.success(request,'Product edited successfully') 
            return redirect('view_Brand')
    return render(request,"adminpanel/editproduct.html",locals())


def edit_varient(request,pid):
    varient=ProductVarient.objects.get(id=pid)
    prodsize=Size.objects.filter(varient=varient)
    product=Product.objects.all()
    prodimage=ProductImage.objects.filter(varient=varient)
    colors=['White','Black','Green','Red','Yellow','Blue','Brown','Orange']
    sizes=['XS','S','M','L','XL','XXL','XXXL','7','8','9','10','11','12','28','30','32','34','36','38','40','42','UNI']
    if request.method == "POST":
        try:
            name=request.POST["name"]
            if ProductVarient.objects.filter(name__iexact=name.lower().replace(' ', '')).exists():
                messages.success(request,'Varient name  already existing')
            else:
                varient.name=name
        except:
            varient.name=varient.name
        try:
            color=request.POST["color"]
            varient.color=color
        except:
            varient.color=varient.color
        try:
            prod=request.POST["product"]
            varient.Product=prod
        except:
            varient.Product=varient.Product
        try:
            price=request.POST["price"]
            varient.price=price
        except:
            varient.Price=varient.Price
        try:
            offer=request.POST["offer"]
            varient.offer=offer
        except:
            varient.offer=varient.offer
        varient.save()

        try:
            l=prodsize.count()
            for i in range(l):
                siz=request.POST['size']
                stock=request.POST['stock']
                update=Size.objects.get(pk=siz)
                update.stock=stock
                update.save()
        except:
            pass
        try:
            images = request.FILES.getlist('image')
            hoverimage = request.FILES.get('hover_image')
            # remove the old instances of ProductImage related to the ProductVarient
            if images and hoverimage is not None:
                ProductImage.objects.filter(varient=varient).delete()
            for image in images :
                ProductImage.objects.create(varient=varient, images=image, hover_images=hoverimage)
                messages.success(request, "Varient images updated successfully.")
        except:
            pass
        return redirect('view_varient')
        
    return render(request,"adminpanel/editvarient.html",locals())

def delete_category(request,pid):
    try:
        Category.objects.get(id=pid).delete()
        messages.warning(request,'Category Deleted')
    except:
        messages.warning(request,'some thing wrong happend')
    return redirect('view_Category')

def delete_subcategory(request,pid):
    try:    
        SubCategory.objects.get(id=pid).delete()
        messages.warning(request,'Subcategory Deleted')
    except:
        messages.warning(request,'some thing wrong happend')
        return redirect(view_Subcategory)
def delete_brand(request,pid):
    try:
        Brand.objects.get(id=pid).delete()
        messages.warning(request,'brand Deleted')
    except:
        messages.warning(request,'some thing wrong happend')
    return redirect('view_Brand')

def delete_product(request,pid):
    try:
        Product.objects.get(id=pid).delete()
        messages.warning(request,'Product Deleted')
    except:
        messages.warning(request,'some thing wrong happend')
    return redirect('view_Product')

def delete_varient(request,pid):
    try:
        ProductVarient.objects.get(id=pid).delete()
        messages.warning(request,'Varient Deleted')
    except:
        messages.warning(request,'some thing wrong happend')
    return redirect('view_varient')

def view_coupon(request):
    coupon=Coupon.objects.all()
    return render(request,"adminpanel/viewcoupon.html",locals())

def add_coupons(request):
    coupon_form = CouponForm(instance=request.user)
    if request.method == 'POST':
        coupon_form= CouponForm(request.POST)
        if coupon_form.is_valid():
            coupon_form.save()
            return redirect('view_coupon')
    else:
        form = CouponForm()
    return render(request, 'adminpanel/addcoupon.html', {'coupon_form': coupon_form})

def edit_coupon(request, pid):
    coupon = Coupon.objects.get(id=pid)
    coupon_form = CouponForm(instance=request.user)
    if request.method == "POST":
        coupon_form = CouponForm(request.POST,instance=coupon)
        if coupon_form.is_valid():
            coupon_form.save()
            messages.success(request, "Coupon Updated")
            return redirect('view_coupon')
    else:
        coupon_form = CouponForm(instance=coupon)
        messages.error(request, "fill all fields")

    return render(request, 'adminpanel/editcoupon.html', {'coupon_form': coupon_form, 'coupon': coupon})

def delete_coupon(request, pid):
    try:
        Coupon.objects.get(id=pid).delete()
        messages.success(request, "Coupon Deleted")
    except:
        messages.warning(request,'some thing wrong happend')
        
    return redirect('view_coupon')

def manage_user(request):
    user = User.objects.all().order_by('id')[1:]
    return render(request, 'adminpanel/manageuser.html', {'user': user })

def block_user(request, id):
    user = get_object_or_404(User, id=id)
    if user.is_active:
        user.is_active = False
        messages.success(request, "user has been blocked.")
    else:
        user.is_active = True
        messages.success(request, "user has been unblocked.")
    user.save()
    return redirect('manage_user')


def manage_order(request):
    orders=Order.objects.all().order_by('-id')
    paginator = Paginator(orders, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    # return render(request, 'manageorder.html', locals())
    return render(request, 'adminpanel/manageorder.html', locals())

def update_order(request, id):
    if request.method == 'POST':
        order = Order.objects.get(id=id)
        status = request.POST['status']
        if status is not None:
            order.status = status
            order.save()
        if status  == "Delivered":
            try:
                payment = Payment.objects.get(payment_id = order.order_number, status = False)
                print(payment)
                if payment.payment_method == 'Cash on Delivery':
                    payment.paid = True
                    payment.save()
            except:
                pass
    return redirect('manage_order')

def admincancelOrder(request, id):
    
    
    razorpay_client = razorpay.Client(auth=(kaira.settings.API_KEY, kaira.settings.RAZORPAY_SECRET_KEY))
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        order = None
    
    if order is None:
        # Render an error message if the order does not exist
        messages.warning(request,'The order you are trying to cancel does not exist.')
        return redirect(manage_order)
    
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
            messages.warning(request,'The payment has not been captured,We cant Refund the money')
            return redirect(manage_order)
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
                messages.success(request,'The order has been successfully cancelled and amount has been refunded!')
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
                messages.warning(request,'The order is not cancelled because the refund could not be completed now. Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!')
                pass
        else :
            if(payment.paid):
                order.refund_completed = True
                order.status = 'Cancelled'
                messages.success(request,'THE ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
                order.save()
            else:
                order.status = 'Cancelled'
                order.save()
                messages.success(request,'The payment has not been recieved yet. But the order has been cancelled.!')
    else :
        order.status = 'Cancelled'
        messages.success(request,'THE ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
        order.save()
    return redirect(manage_order)

@user_passes_test(lambda u:u.is_superuser,login_url='adminlogin')
def admindashboard(request):
    if request.user.is_authenticated:
        today_sales = Payment.objects.filter(created_at=datetime.today(), paid=True).aggregate(Sum('amount_paid'))['amount_paid__sum']
        # Total sales and revenue
        orders_count = Order.objects.filter(status__in=['Order Confirmed', 'Shipped', 'Out for delivery']).count()
        total_sales = Payment.objects.filter(paid=True).aggregate(Sum('amount_paid'))['amount_paid__sum']
        total_revenue = OrderProduct.objects.filter(order__status='Delivered').annotate(total_price=F('product_price') * F('quantity')).aggregate(Sum('total_price'))['total_price__sum']
        # Render the template with the data
        if today_sales is not None:
            today_sales = round(today_sales,2)
        if total_sales is not None:
            total_sales = round(total_sales,2)
        if total_revenue is not None:
            total_revenue = round(total_revenue,2)
        cod_sum = Payment.objects.filter(payment_method='Cash On Delevery' ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        cod_sum = round(cod_sum,2)
   
        razorpay_sum = Payment.objects.filter(payment_method='Razorpay').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        razorpay_sum = round(razorpay_sum, 2)
        allcategory = Category.objects.all()
        context = {
                'orders_count': orders_count,
                'today_sales': today_sales,
                'total_sales': total_sales,
                'total_revenue': total_revenue,
                'razorpay_sum':razorpay_sum,
                'cod_sum':cod_sum,
                'allcategory':allcategory,
            }
            
        return render(request, 'adminpanel/admin_dash.html',context)
    else: 
        return redirect('adminlogin')