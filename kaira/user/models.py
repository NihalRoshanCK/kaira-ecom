from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Create your models here.

STATE_CHOICES = (
    ('Kerala','Kerala'),
    ('Tamilnadu','Tamilnadu'),
    ('Karnataka','Karnataka'),
    ('AndraPradesh','AndraPradesh')
)
DIST_CHOICES = {
    ('Kannur','Kannur'),
    ('Kozhikkode','Kozhikkode'),
    ('Ernakulam','Ernakulam'),
    ('Thiruvananthapuram','Thiruvananthapuram'),
    ('Banglore','Banglore'),
    ('Hubli','Hubli'),
    ('Hydrabad','Hydrabad'),
    ('Coimbator','Coimbator'),
    ('Madurai','Madurai'),
}

COLOR_CHOICES = (
    ('White','White'),
    ('Black','Black'),
    ('Green','Green'),
    ('Red','Red'),
    ('Yellow','Yellow'),
    ('Blue','Blue'),
    ('Brown','Brown'),
    ('Orange','Orange'),
)

SIZE_CHOICES = (
    ('XS','XS'),
    ('S','S'),
    ('M','M'),
    ('L','L'),
    ('XL','XL'),
    ('XXL','XXL'),
    ('XXXL','XXXL'),
    ('7','7'),
    ('8','8'),
    ('9','9'),
    ('10','10'),
    ('11','11'),
    ('12','12'),
    ('28','28'),
    ('30','30'),
    ('32','32'),
    ('34','34'),
    ('36','36'),
    ('38','38'),    
    ('40','40'),
    ('42','42'),
    ('UNI','UNI'),
)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    mobile_regex = RegexValidator(regex=r'^\d+$', message="Mobile number should only contain digits")
    mobile = models.CharField(validators=[mobile_regex], max_length=10, null=True,blank=True)
    address = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='user', null=True, blank=True)
    district = models.CharField(choices=DIST_CHOICES,max_length=20, null=True, blank=True)
    state = models.CharField(choices=STATE_CHOICES,max_length=20, null=True,blank=True)
    pincode_regex = RegexValidator(regex=r'^\d+$', message="Pincode should only contain digits")
    pincode = models.PositiveIntegerField(null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    main_category= models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    description = models.TextField()
    updated = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductVarient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color=models.CharField(choices=COLOR_CHOICES,max_length=50)
    Product= models.ForeignKey(Product,on_delete=models.CASCADE)
    price = models.PositiveBigIntegerField(null=True)
    offer=models.PositiveIntegerField(null=True)
    
    
    def __str__(self):
        return self.name
    
    
class Size(models.Model):
    varient= models.ForeignKey(ProductVarient,on_delete=models.CASCADE)
    size = models.CharField(choices=SIZE_CHOICES,max_length=10, null= True)
    stock=models.PositiveIntegerField(null=True,blank=True)
    
    def __str__(self):
        return self.varient.name

class ProductImage(models.Model):
    varient= models.ForeignKey(ProductVarient, on_delete=models.CASCADE, null=True)
    images = models.ImageField(upload_to='media',null=True)
    hover_images = models.ImageField(upload_to='media',null=True)

    def __str__(self):
        
        return self.varient.name

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=100,null=True)
    lastname = models.CharField(max_length=100,null=True)
    email = models.EmailField(max_length=200)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    phone_regex = RegexValidator(regex=r'^\d+$', message="Mobile number should only contain digits")
    phone = models.CharField(validators=[phone_regex], max_length=10, null=True)
    city = models.CharField(choices=DIST_CHOICES,max_length=255)
    state = models.CharField(choices=STATE_CHOICES,max_length=255)
    pincode_regex = RegexValidator(regex=r'^\d+$', message="Pincode should only contain digits")
    pincode = models.PositiveIntegerField(null=True,blank=True)
    is_default = models.BooleanField(default=False)
    
    

    def __str__(self):
        return self.user.username