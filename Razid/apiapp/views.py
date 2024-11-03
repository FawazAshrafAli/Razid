from adminapp .models import Product
from rest_framework.views import APIView
from adminapp .models import Product,SubCategory
from apiapp. models import Favour
# from django.contrib.auth.models import User

from rest_framework.response import Response
from .serializers import *
from rest_framework import generics,permissions
# from rest_framework.decorators import api_view
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.views import Request
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from django.contrib.auth.views import LoginView




# Create your views here.

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]



class RegisterUser(APIView):
    def get(self, request):
        serializer = UserSerializer(data=request.data)
        print(serializer)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = request.user
        serializer = UserSerializer(user)
        data = {
            'token': response.data['key'],
            'user': serializer.data
        }
        return Response(data)

        






# class ListProductsGenerics(generics.ListCreateAPIView):
#     # authentication_classes = [TokenAuthentication]
#     # permission_classes = [IsAuthenticated]
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
    

# class ProductsDetailGenerics(generics.RetrieveUpdateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
    


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]


    # @action(detail=True, methods=['GET'])
    # def reviews(self, request, pk=None):
    #     product = self.get_object()
    #     reviews = Rating.objects.filter(product=product)
    #     serializer = RatingSerializer(reviews, many=True)
    #     return Response(serializer.data)

    # @action(detail=True, methods=['POST'])
    # def add_review(self, request, pk=None):
    #     product = self.get_object()
    #     serializer = RatingSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(product=product, user=request.user)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CustomerListGenerics(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    

class CustomerDetailGenerics(generics.RetrieveUpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    


# class CategoryList(generics.ListCreateAPIView):
#     queryset = SubCategory.objects.all()
#     serializer_class = CategorySerializer
    

class CategoryList(generics.ListCreateAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        # Retrieve the category parameter from the request's query parameters
        category_param = self.request.query_params.get('category', None)

        # If category parameter is provided, filter the queryset
        if category_param:
            queryset = SubCategory.objects.filter(category=category_param)
        else:
            queryset = SubCategory.objects.all()

        return queryset




class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = CategoryDetailSerializer
    







class RatingViewSet(ModelViewSet):
    # queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Rating.objects.filter(product_id = self.kwargs['product_pk'])
    
    def get_serializer_context(self):
        user_id = self.request.user.id
        product_id = self.kwargs["product_pk"]
        return {"user_id": user_id, "product_id": product_id}
    def perform_create(self, serializer):
        # Ensure 'product_id' is set before saving
        serializer.save(product_id=self.kwargs['product_pk'])
        


class Wishlist(generics.ListCreateAPIView):
    queryset = Favour.objects.all()
    serializer_class = WishlistSerializer



# class PostImage(generics.ListCreateAPIView):
#     queryset = PostImage.objects.all()
#     serializer_class = PostImageSerializer
    

class PostImage(viewsets.ModelViewSet):
    queryset = PostImage.objects.all()
    serializer_class = PostImageSerializer


    def post(self,request,*args,**kwargs):
        text = request.data['text']
        image = request.data['image']
        PostImage.objects.create(text=text,image=image)
        return Response({"message":"Posted Successfully!"},status=200)