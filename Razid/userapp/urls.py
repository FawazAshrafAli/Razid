from django.urls import path
from .import  views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from . forms import MyPasswordResetForm,MySetPasswordForm
from django.contrib.auth import views as auth_views
from .views import toggle_wishlist,resend_otp,payment_success, payment_failure,products_by_category, products_by_subcategory



urlpatterns = [
    path('', views.home, name='home'),
    path('//<str:encrypted_name>/', views.home_with_encrypted_name, name='home_with_encrypted_name'),
    path('register/',views.register,name='register'),
    path('login/',views.user_login,name='login_user'),
    path('logout/', views.user_logout, name='logout_user'),
    # path('product-detail/<int:category_id>/', views.productdetail, name='product-detail'),
    path('product-detail/<str:encrypted_category_id>/', views.product_detail_encrypted, name='product-detail-encrypted'),
    # path('product-detail/<str:encrypted_category_id>/', views.productdetail, name='product-detail'),
    path('singleproduct/<str:encrypted_product_id>/', views.singleproduct, name='singleproduct'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/',views.show_cart,name='showcart'),
    path('pluscart/',views.plus_cart,name="plus_cart"),
    path('minuscart/',views.minus_cart,name="minus_cart"),
    path('removecart/',views.remove_cart,name="remove_cart"),

    path('wishlist/',views.show_wishlist,name='wishlist'),
    path('pluswishlist/',views.plus_wishlist,name="plus_wishlist"),
    path('minuswishlist/',views.minus_wishlist,name="minus_wishlist"),
    # path('update_wishlist/<int:product_id>/', views.update_wishlist, name='update_wishlist'),

    path('review/<str:encrypted_product_id>/',views.review,name='review'),

    path('imageupload/<int:product_pk>/', views.imageupload, name='imageupload'),

    path('checkout/',views.checkout.as_view(),name='checkout'),

    path('payment-success/', payment_success, name='payment_success'),
    path('payment-failure/', payment_failure, name='payment_failure'),

    path('paymentdone/',views.payment_done,name='paymentdone'),

    path('search/',views.search_view,name="search"),
  
   path('profile/',views.ProfileView.as_view(),name='profile'),

   path('address/',views.address,name='address'),

    path('updateAddress/<int:pk>',views.updateAddress.as_view(),name='updateAddress'),

    path('orders/',views.orders,name='orders'),

    path('shopall/',views.shopall,name='shopall'),

    # path('pluswish/<int:id>/',views.pluswish,name='pluswish'),

    # path('minuswish/<int:id>/',views.minuswish,name='minuswish'),

    path('send_otp/', views.send_otp, name='send_otp'),
    path('otp_verification/', views.otp_verification, name='otp_verification'),
    path('resend_otp/', resend_otp, name='resend_otp'),
    path('password-reset/',views.PasswordReset,name='password-reset'),
    path('password-reset-complete/',views.pwcomplete,name='password_reset_complete'),

    path('add_to_cart_wishlist/', views.add_to_cart_wishlist, name='add_to_cart_wishlist'),

    
    path('autosuggest/',views.autosuggest,name="autosuggest"),

    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/',views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/<int:product_id>/toggle/', toggle_wishlist, name='toggle_wishlist'),

    path('delete-item/<int:item_id>/',views.delete_item, name='delete_item'),

    path('pluscart2/',views.plus_cart_base,name="plus_cart2"),
    path('minuscart2/',views.minus_cart_base,name="minus_cart2"),
    path('removecart2/',views.remove_cart_base,name="remove_cart2"),

    path('cod_confirmation/',views.cod_confirmation,name="cod_confirmation"),

    path('trackorder/',views.trackorder,name='trackorder'),

    path('invoice/',views.invoice,name='invoice'),
    path('invoice/export/',views. invoice, name='export_invoice'),

    path('userprofile/',views.userprofile,name='userprofile'),

    path('add-to-cart-newarrivals/', views.add_to_cart_newarrival, name='add_to_cart_newarrivals'),

    path('add_to_cart_productdetail/',views.add_to_cart_productdetail,name='add_to_cart_productdetail'),
    path('add_to_wishlist_productdetail/',views.add_to_wishlist_productdetail,name='add_to_wishlist_productdetail'),

    path('add_to_cart_tabmen/', views.add_to_cart_tabmen, name='add_to_cart_tabmen'),
    path('add_to_wishlist_tabmen/', views.add_to_wishlist_tabmen, name='add_to_wishlist_tabmen'),

    path('add_to_cart_tabwomen/', views.add_to_cart_tabwomen, name='add_to_cart_tabwomen'),
    path('add_to_wishlist_tabwomen/', views.add_to_wishlist_tabwomen, name='add_to_wishlist_tabwomen'),
     
    path('add_to_cart_tabchild/', views.add_to_cart_tabchild, name='add_to_cart_tabchild'),
    path('add_to_wishlist_tabchild/', views.add_to_wishlist_tabchild, name='add_to_wishlist_tabchild'),

    path('add_to_cart_taball/', views.add_to_cart_taball, name='add_to_cart_taball'),
    path('add_to_wishlist_taball/', views.add_to_wishlist_taball, name='add_to_wishlist_taball'),

    path('add_to_wishlist_newarrivals/',views.add_to_wishlist_newarrivals,name='add_to_wishlist_newarrivals'),

    
    path('add_to_cart_shopall/', views.add_to_cart_shopall, name='add_to_cart_shopall'),
    path('add_to_wishlist_shopall/', views.add_to_wishlist_shopall, name='add_to_wishlist_shopall'),

    path('checkoutimage/',views.checkoutimage.as_view(),name='checkoutimage'),

    path('orderhistory/',views.orderhis,name='orderhistoryuser'),

    path('category/<int:category_id>/', views.category_products_view, name='category_products'),
    path('subcategory/<int:subcategory_id>/', views.subcategory_products_view, name='subcategory_products'),

    path('category/<int:id>/<slug:slug>/', views.products_by_category, name='category_products'),
    path('subcategory/<int:id>/<slug:slug>/', views.products_by_subcategory, name='subcategory_products'),

    path('category/<encrypted_category_id>/', products_by_category, name='category_products'),
    path('subcategory/<encrypted_subcategory_id>/', products_by_subcategory, name='subcategory_products'),

    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('terms-and-conditions/',views.terms_condition,name='terms-and-conditions'),
    path('privacy-policy/',views.privacypage,name='privacy-policy'),



    

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)