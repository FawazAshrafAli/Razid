from rest_framework import serializers
from adminapp .models import Product,Category
from apiapp . models import *
from django.contrib.auth.models import User



class  ProductSerializer(serializers.ModelSerializer):
    class Meta:
       model = Product
       fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password']


    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'])
        user.set_password(validated_data['password'])  
        user.save()
        return user



class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields =  "__all__"

    
    def __init__(self, *args, **kwargs):
        super(ProductDetailSerializer,self).__init__(*args, **kwargs)
        # self.Meta.depth = 1





class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields =  ['id','user','mobile']
    

    def __init__(self, *args, **kwargs):
        super(CustomerSerializer,self).__init__(*args, **kwargs)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'




class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'






class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['rating','description']



    

    
    def __init__(self, *args, **kwargs):
        super(RatingSerializer,self).__init__(*args, **kwargs)
    def create(self, validated_data):
        product_id = self.context["product_id"]
        user_id = self.context["user_id"]
        rating = Rating.objects.create(product_id = product_id, user_id=user_id, **self.validated_data)
        return rating
    


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favour
        fields = '__all__'

    def __init__(self,*args, **kwargs):
        super(WishlistSerializer,self).__init__(*args, **kwargs)

    
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['user'] = UserSerializer(instance.user).data
    #     response['product'] = ProductSerializer(instance.product).data



class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = '__all__'