from django.db import models
# from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.contrib.auth.models import User
from adminapp . models import Product
# Create your models here.

class CustomUser(models.Model):
    username = models.ForeignKey(User,on_delete = models.CASCADE)
    password = models.CharField(max_length=40)

    class Meta:
        db_table = "user"

    def  __str__(self):
        return self.username


class Customer(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    mobile = models.PositiveBigIntegerField(unique=True)

    def  __str__(self):
        return self.user.username


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_time = models.DateTimeField()

    def  __str__(self):
        return self.customer


class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)  

    def  __str__(self):
        return self.product.title







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

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='rating')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user}'s {self.get_rating_display()} rating for {self.product}"





class Favour(models.Model):
   user=models.ForeignKey(User,on_delete=models.CASCADE)
   product = models.ForeignKey(Product,on_delete=models.CASCADE)


def upload_path(instance,filename):
    return '/'.join(['image', str(instance.text), filename])



class PostImage(models.Model):
    text = models.TextField(max_length=1000)
    image = models.ImageField(upload_to=upload_path)



# class UserAccountManager(BaseUserManager):
#     def create_user(self, email,name,password=None):
#         if not email:
#             raise ValueError('Users must have an email address')
        
#         email=self.normalize_email(email)
#         user=self.model(email=email,name=name)

#         user.set_password(password)
#         user.save()

#         return user






# class UserAccount(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(max_length=255, unique=True)
#     name = models.CharField(max_length=255)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)


#     objects = UserAccountManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['name']

#     def get_full_name(self):
#         return self.name

#     def get_short_name(self):
#         return self.name
    

#     def __str__(self):
#         return self.email
    
