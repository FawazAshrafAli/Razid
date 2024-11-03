"""
URL configuration for Razid project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from userapp. views import user_login,user_logout

urlpatterns = [

    
    # path('auth/', include('djoser.urls')),
    # path('auth/',include('djoser.urls.jwt')), #for token authentication
    path('dj-admin/', admin.site.urls),
    path('admin/',include('adminapp.urls')),
    # path('api/',include('apiapp.urls')),
    path('',include('userapp.urls')),
     path('login/',user_login,name='login_user'),
    path('logout/', user_logout, name='logout_user'),
    # path('auth/',include('django.contrib.auth.urls')),
    # path('api-token-auth/',views.obtain_auth_token,name='api_token_auth'),
    # path('api-auth/',include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)