# """
# URL configuration for Razid project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.0/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """

# from django.urls import path,include
# from django.conf import settings
# from django.conf.urls.static import static
# # from .  import views 
# # from apiapp.views import RegisterUser
# from rest_framework.authtoken import views
# from apiapp.views import *
# from rest_framework_nested import routers
# from . import views


# router = routers.DefaultRouter()

# router.register("products", views.ProductViewSet)
# router.register("post",views.PostImage)

# product_router = routers.NestedDefaultRouter(router, "products", lookup='product')
# product_router.register("ratings", views.RatingViewSet, basename = "rating")


urlpatterns = [
    # path("api-viewset-products/", include(router.urls)),
    # path("api-viewset-products/", include(product_router.urls)),

    






    # path('api-auth/',include('rest_framework.urls')),

    # # path('api-token-auth/',views.obtain_auth_token),

    # path('register/', RegisterUser.as_view(), name='register'),
    # path('login/', CustomLoginView.as_view(), name='login'),

    # # path('userlist/',UserList.as_view(),name='userlist'),

    # # path('list_products/',ListProductsGenerics.as_view(),name="list_products"),

    # # path('products_detail/<int:pk>/',ProductsDetailGenerics.as_view(),name="products_detail"),

    # path('customerlist/',CustomerListGenerics.as_view(),name="customerlist"),

    # path('customerdtailgen/<int:pk>/',CustomerDetailGenerics.as_view(),name= "custumerdetail") ,

    # path('categorylist/',CategoryList.as_view(),name= 'categorylist' ),

    # path('categorydetail/<int:pk>/',CategoryDetail.as_view(),name= 'categorydetail' ),

    # # path('api/token/', ObtainAuthTokenView.as_view(), name='api_token_auth'),

    # path('wishlist/',Wishlist.as_view(),name='wishlist'),

    # # path('postimage/',PostImage.as_view(),name='postimage'),


]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)