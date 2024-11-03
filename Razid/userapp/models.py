from django.db import models
from django.contrib.auth.models import User
from adminapp .models import Product
from .utility import generate_order_id
from django.utils.crypto import get_random_string
import uuid
from django.utils import timezone
import random
from datetime import timedelta
from django.dispatch import receiver
from django.db.models.signals import pre_save


# Create your models here.


STATE_CHOICES=(
    ("Andhra Pradesh","Andhra Pradesh"),
    ("Arunachal Pradesh ","Arunachal Pradesh "),
    ("Assam","Assam"),
    ("Bihar","Bihar"),("Chhattisgarh","Chhattisgarh"),
    ("Goa","Goa"),
    ("Gujarat","Gujarat"),
    ("Haryana","Haryana"),
    ("Himachal Pradesh","Himachal Pradesh"),
    ("Jammu and Kashmir ","Jammu and Kashmir "),
    ("Jharkhand","Jharkhand"),
    ("Karnataka","Karnataka"),
    ("Kerala","Kerala"),
    ("Madhya Pradesh","Madhya Pradesh"),
    ("Maharashtra","Maharashtra"),
    ("Manipur","Manipur"),
    ("Meghalaya","Meghalaya"),
    ("Mizoram","Mizoram"),
    ("Nagaland","Nagaland"),
    ("Odisha","Odisha"),
    ("Punjab","Punjab"),
    ("Rajasthan","Rajasthan"),
    ("Sikkim","Sikkim"),
    ("Tamil Nadu","Tamil Nadu"),
    ("Telangana","Telangana"),
    ("Tripura","Tripura"),
    ("Uttar Pradesh","Uttar Pradesh"),
    ("Uttarakhand","Uttarakhand"),
    ("West Bengal","West Bengal"),
    ("Andaman and Nicobar Islands","Andaman and Nicobar Islands"),
    ("Chandigarh","Chandigarh"),
    ("Dadra and Nagar Haveli","Dadra and Nagar Haveli"),
    ("Daman and Diu","Daman and Diu"),
    ("Lakshadweep","Lakshadweep"),
    ("National Capital Territory of Delhi","National Capital Territory of Delhi"),
    ("Puducherry","Puducherry")


)



class Customer(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='customers')
    name=models.CharField(max_length=200)
    email1=models.EmailField(null=True,blank=True)
    email2=models.EmailField(null=True,blank=True)
    image1=models.ImageField(null=True,blank=True,upload_to="customer-images/")
    image2=models.ImageField(null=True,blank=True,upload_to="customer-images/")
    address1=models.TextField(null=True)
    address2=models.TextField(null=True)
    address3=models.TextField(null=True)
    locality=models.CharField(max_length=200,null=True)
    city=models.CharField(max_length=50,null=True)
    mobile=models.IntegerField(default=0)
    mobile2=models.IntegerField(default=0,null=True)
    zipcode=models.IntegerField(null=True)
    state=models.CharField(choices=STATE_CHOICES,max_length=100,null=True)
    def __str__(self):
        return self.name





class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveBigIntegerField(default=1)




class WishList(models.Model):
   user=models.ForeignKey(User,on_delete=models.CASCADE)
   product = models.ForeignKey(Product,on_delete=models.CASCADE)





class Payment(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    amount=models.FloatField()
    razorpay_order_id=models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_status=models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_id=models.CharField(max_length=100,blank=True,null=True)
    paid=models.BooleanField(default=False)


class Payments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    easebuzz_payment_status = models.CharField(max_length=100, blank=True, null=True)
    easebuzz_payment_id = models.CharField(max_length=100, blank=True, null=True)
    paid = models.BooleanField(default=False)



class Order(models.Model):
    order_id = models.CharField(max_length=20, unique=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    address_id =  models.TextField(null=True)
    ordered_date = models.DateTimeField(auto_now_add=True, null=True)
    amount = models.FloatField(null=True)
    status = models.CharField(max_length=50, default='Order Placed')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, default="", null=True)
    payment_method = models.CharField(max_length=20)
    delivery_expected_date = models.DateField(null=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate alphanumeric order ID using UUID version 4
            self.order_id = self.generate_order_id()

        if not self.ordered_date:
            self.ordered_date = timezone.now()  # Set ordered_date if not already set

        # Set delivery expected date as 7 days from ordered date
        if not self.delivery_expected_date:
            self.delivery_expected_date = self.ordered_date + timedelta(days=7)

        super().save(*args, **kwargs)

    def generate_order_id(self):
        return uuid.uuid4().hex[:10]




class OrderPlaced(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    quantity = models.PositiveIntegerField(default=1,null=True)

    def save(self, *args, **kwargs):
        if not self.order_id:  # Check if this is the first product in the order
            order = Order.objects.create(
                user=self.user,
                customer=self.customer,
                amount=self.amount,
                status=self.status,
                payment=self.payment,
                payment_method=self.payment_method
            )
            self.order = order  
            self.order_id = order.order_id  

        super().save(*args, **kwargs)




#     last_order_timestamp = None  # Variable to store the timestamp of the last generated order ID

# def generate_order_id():
#     global last_order_timestamp
    
#     # Get the current timestamp
#     current_timestamp = timezone.now().strftime('%Y%m%d%H%M%S')

#     # Check if the current order is placed within the same second as the last one
#     if last_order_timestamp == current_timestamp:
#         # If so, return the same order ID as the last one
#         return last_order_id
    
#     # Generate a unique order ID
#     unique_id = uuid.uuid4().hex[:6]  
#     order_id = f'{current_timestamp}-{unique_id}'
    
#     # Update the last order timestamp and ID
#     last_order_timestamp = current_timestamp
#     last_order_id = order_id
    
#     return order_id


class Rating(models.Model):
    ONE_STAR = 1
    TWO_STARS = 2
    THREE_STARS = 3
    FOUR_STARS = 4
    FIVE_STARS = 5

    RATING_CHOICES = [
        (ONE_STAR, '1 star'),
        (TWO_STARS, '2 stars'),
        (THREE_STARS, '3 stars'),
        (FOUR_STARS, '4 stars'),
        (FIVE_STARS, '5 stars'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_ratings')
    description = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def save(self, *args, **kwargs):
        if not self.pk:  # If the instance is being created (not updated)
            user_id = kwargs.pop('user_id', None)
            product_id = kwargs.pop('product_id', None)

            # Ensure both user_id and product_id are provided
            if user_id is not None and product_id is not None:
                self.user_id = user_id
                self.product_id = product_id

        super().save(*args, **kwargs)



class ImageUpload(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_imageupload',null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_imageuplaod',null=True)
    text = models.TextField(max_length=1000)
    image =  models.ImageField(upload_to="user-images/")
    order_id = models.CharField(max_length=20, unique=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    address_id =  models.TextField(null=True)
    ordered_date = models.DateTimeField(auto_now_add=True, null=True)
    amount = models.FloatField(null=True)
    payment_method = models.CharField(max_length=20,null=True)
    status = models.CharField(max_length=50, default='Order Placed')
    delivery_expected_date = models.DateField(null=True)
    quantity = models.PositiveIntegerField(default=1,null=True)



   
    

    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate alphanumeric order ID using UUID version 4
            self.order_id = self.generate_order_id()

        if not self.ordered_date:
            self.ordered_date = timezone.now()  # Set ordered_date if not already set

        # Set delivery expected date as 7 days from ordered date
        if not self.delivery_expected_date:
            self.delivery_expected_date = self.ordered_date + timedelta(days=7)

        if self.image:
            # Replace forward slashes with backslashes in the image path
            self.image = self.image.name.replace('/', '\\')

        super().save(*args, **kwargs)


    def generate_order_id(self):
        return uuid.uuid4().hex[:10]

    

class Contact(models.Model):

   First_name = models.CharField(max_length=100)
   Last_name = models.CharField(max_length=100)
   Email = models.EmailField()
   phn = models.IntegerField(default=0)
   comments = models.TextField(max_length=1000)
   created_at = models.DateTimeField(auto_now_add=True,null=True)

   def __str__(self):
    return self.name