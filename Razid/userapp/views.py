from django.shortcuts import render,redirect
from adminapp.models import *
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from . models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.http import HttpResponseBadRequest
import razorpay
from django.conf import settings
from django.views import View
from django.db.models import Sum
from . forms import CustomerProfileForm
from django.urls import reverse
import random
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from cryptography.fernet import InvalidToken
import os
import hashlib
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .utils.encryption import encrypt_data,decrypt_data
from .utility import encrypt,decrypt


from .utils.encryption import encrypt_data, decrypt_data
from urllib.parse import quote, unquote


def home(request):
    encrypted_name = encrypt_data('home')
    print("Encrypted Name:", encrypted_name)  # Debugging statement
    encoded_encrypted_name = quote(encrypted_name)
    print("Encoded Encrypted Name:", encoded_encrypted_name)  # Debugging statement
    return redirect(reverse('home_with_encrypted_name', args=[encoded_encrypted_name]))

def home_with_encrypted_name(request, encrypted_name):
    decoded_encrypted_name = unquote(encrypted_name)
    print("Decoded Encrypted Name:", decoded_encrypted_name)  # Debugging statement
    decrypted_name = decrypt_data(decoded_encrypted_name)
    print("Decrypted Name:", decrypted_name)  # Debugging statement

    if decrypted_name == 'home':
        context = {}
        data = SubCategory.objects.all()
        parent_categories = Category.objects.all()
        parent_slider = BackgroundSliders.objects.all()
        child_slider = ChildSliders.objects.all()
        products = Product.objects.all()
        newarrival = Product.objects.latest('id')
        latest_products = Product.objects.order_by('-id')[:4]
        most_ordered_products = OrderPlaced.objects.order_by('-order__ordered_date')
        encrypted_subcategories = {subcategory.id: encrypt_data(str(subcategory.id)) for subcategory in data}
        totalitem = 0
        wishitem = 0
        wishlist = {}
        cart = []
        amount2 = 0
        totalamount = 0

        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
            wishitem = WishList.objects.filter(user=request.user).count()
            cart = Cart.objects.filter(user=request.user)
            amount = sum(cart_item.quantity * cart_item.product.price for cart_item in cart)
            amount2 = amount
            totalamount = amount + 40
            user = request.user
        else:
            totalitem = 0
            wishitem = 0
            user = None
            cart = []

        for product in products:
            wishlist = WishList.objects.filter(product=product, user=request.user.pk).exists()

        # Calculate total quantity count for each category
        category_quantities = {}
        for category in parent_categories:
            category_products = products.filter(categories__parent_category=category)
            category_total_quantity = category_products.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
            category_quantities[category.name] = category_total_quantity

        for product in latest_products:
            avg_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
            product.avg_rating = round(avg_rating) if avg_rating is not None else 0

        for i in most_ordered_products:
            avg_rating2 = Rating.objects.filter(product=i.product).aggregate(Avg('rating'))['rating__avg']
            i.product.avg_rating2 = round(avg_rating2) if avg_rating2 is not None else 0

        for product in products:
            avg_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
            product.avg_rating = round(avg_rating) if avg_rating is not None else 0

        amount = 0
        for p in cart:
            value = p.quantity * p.product.price
            amount = amount + value
            amount2 = amount
        totalamount = amount + 40

        for product in products:
            if product.size and product.size[0] != '':
                try:
                    size_list = json.loads(product.size[0])
                    context['sizes'] = size_list
                except json.JSONDecodeError:
                    pass

        most_ordered = (OrderPlaced.objects
                        .values('product')
                        .annotate(total_quantity=Sum('quantity'))
                        .order_by('-total_quantity')
                        .first())

        if most_ordered:
            product_id = most_ordered['product']
            product = Product.objects.get(id=product_id)
            product.total_quantity = most_ordered['total_quantity']
            product.encrypted_pro_id = encrypt(str(product.id))
            print(f"Most Ordered Product ID: {product.id}, Encrypted ID: {product.encrypted_pro_id}")  # Check this output
            context['most_ordered'] = product

        encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}
        for subcategory in data:
            subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
            print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging

        for product in products:
            product.encrypted_pro_id = encrypt(str(product.id))
            print(f"Product ID: {product.id}, Encrypted Product ID: {product.encrypted_pro_id}")
        
        product = newarrival  # Just a single product
        product.encrypted_pro_id = encrypt(str(product.id))
        print(f"Product ID: {product.id}, Encrypted Product ID: {product.encrypted_pro_id}")

        for product in latest_products:
            product.encrypted_pro_id = encrypt(str(product.id))
            print(f"Product ID: {product.id}, Encrypted Product ID: {product.encrypted_pro_id}")
        
        for product in most_ordered_products:
            product.product.encrypted_pro_id = encrypt(str(product.product.id))
            print(f"Product ID: {product.product.id}, Encrypted Product ID: {product.product.encrypted_pro_id}")
        

        
        

        context = {
            'SubCate': data,
            'Category': parent_categories,
            'parent_slider': parent_slider,
            'child_slider': child_slider,
            'products': products,
            'totalitem': totalitem,
            'wishitem': wishitem,
            'newarrival': newarrival,
            'category_quantities': category_quantities,
            'latest_products': latest_products,
            'wishlist': wishlist,
            'cart': cart,
            'amount2': amount2,
            'totalamount2': totalamount,
            'most_ordered_products': most_ordered_products,
            # 'most_ordered': product,
            'encrypted_subcategories': encrypted_subcategories,
            'encrypted_id' : subcategory.encrypted_id,
        }

        # for subcategory in data:
        #     subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
        #     print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging

        return render(request, 'index2.html', context)
    else:
        return render(request, '404.html', status=404)


def add_to_wishlist(request, product_id):
    product = Product.objects.get(pk=product_id)
    wishlist, created = WishList.objects.get_or_create(user=request.user)
    wishlist.products.add(product)
    return redirect('home')

def remove_from_wishlist(request, product_id):
    product = Product.objects.get(pk=product_id)
    wishlist = WishList.objects.get(user=request.user)
    wishlist.products.remove(product)
    return redirect('home')


def toggle_wishlist(request, product_id):
    if request.method == 'POST' and request.is_ajax():
        product = get_object_or_404(Product, pk=product_id)
        wishlist, created = WishList.objects.get_or_create(user=request.user)
        if 'active' in request.POST and request.POST['active'] == 'true':
            wishlist.products.remove(product)
            return JsonResponse({'success': True})
        else:
            wishlist.products.add(product)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})


# def pluswish(request, id):
#     products = Product.objects.get(id=id)
#     user = request.user
#     WishList.objects.create(user=user, product=products)
    
#     return redirect('home')


# def minuswish(request, id):
#     print("inside minus")
   
#     try:
#         product = Product.objects.get(id=id)
#     except Product.DoesNotExist:
#         print("Not exists")
    
#     user = request.user
#     WishList.objects.filter(user=user, product=product).delete()
    
#     return redirect('home')



def register(request):
     data = SubCategory.objects.all()
     parent_categories = Category.objects.all()
     encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}

     for subcategory in data:
            subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
            print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging

     context ={
          'SubCate':data,
          'Category' : parent_categories,
          'encrypted_subcategories': encrypted_subcategories,

          
    }
     
     if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Perform basic form validation
        if password1 != password2:
            error_message = "Passwords do not match."
            return render(request, 'register.html', {'error_message': error_message})

        # Create the user
        user = User.objects.create_user(username=name, email=email, password=password1)
        # Optionally, you can log the user in after registration
        # login(request, user)
        return redirect('login_user')  # Redirect to the login page after successful registration

     return render(request,'register.html',context)




def user_login(request):
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}

    for subcategory in data:
            subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
            print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging

    context ={
          'SubCate':data,
          'Category' : parent_categories,
          'encrypted_subcategories': encrypted_subcategories,


    }
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)  # Use auth_login instead of login
            return redirect('home')
        else:
            messages.success(request, "There is an error logging in")
            return redirect('login_user')
    else:
        return render(request, 'login.html',context)

def user_logout(request):
    logout(request)
    return redirect('login_user')
# def productdetail(request, category_id):
#     print("category_id",category_id)
#     encrypted_category_id = encrypt_data(category_id)
#     print("encrycategory_id",encrypted_category_id)

#     # encoded_encrypted_category_id = quote(encrypted_category_id)
#     # print("encodeecategory_id",encoded_encrypted_category_id)

#     return redirect(reverse('product-detail-encrypted', args=[encrypted_category_id]))

def product_detail_encrypted(request, encrypted_category_id):
    try:
        print(f"Encrypted Category ID: {encrypted_category_id}")  # Debugging

        # Decrypt the category ID
        category_id = decrypt(encrypted_category_id)
        print(f"Decrypted Category ID: {category_id}")  # Debugging

        # Query products by the decrypted category ID
        products = Product.objects.filter(categories=category_id)
        print(f"Products: {products}")  # Debugging

    except Exception as e:
        print(f"Decryption or query error: {e}")  # Debugging
        return HttpResponse("Invalid URL", status=400)


    subcategories = SubCategory.objects.all()
    for subcategory in subcategories:
        subcategory.encrypted_id = encrypt(str(subcategory.id))
    print(f"SubCategories: {subcategories}")  # Debugging

    parent_categories = Category.objects.all()
    print(f"Parent Categories: {parent_categories}")  # Debugging

    totalitem = 0
    wishitem = 0
    cart = []
    amount2 = 0
    totalamount = 0

    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()
        cart = Cart.objects.filter(user=request.user)
        print(f"Cart Items: {cart}")  # Debugging

        amount = sum(cart_item.quantity * cart_item.product.price for cart_item in cart)
        amount2 = amount
        totalamount = amount + 40
        user = request.user
    else:
        totalitem = 0
        wishitem = 0
        user = None
        cart = []

    # Sorting logic
    sort = request.GET.get('sort', 'relevance')
    if sort == 'name_asc':
        products = products.order_by('title')
    elif sort == 'name_desc':
        products = products.order_by('-title')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('id')  # Default sorting by relevance (or any other default logic)

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for product in products:
        avg_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        product.avg_rating = round(avg_rating) if avg_rating is not None else 0

    sizes = []
    for product in products:
        if product.size:
            sizes.extend(product.size)

    # Encrypting product IDs for further use
    # encrypted_products = {}
    # for product in products:
    #     encrypted_product_id = encrypt(str(product.id))
    #     encrypted_products[product.id] = encrypted_product_id
    #     print(f"Encrypted Product ID for {product.id}: {encrypted_product_id}")  # Debugging

    # print(f"Encrypted Products: {encrypted_products}")  # Debugging

    # for product in products:
    #    product.encrypted_pro_id = encrypt(str(product.id))

    for product in products:
        product.encrypted_pro_id = encrypt(str(product.id))
        print(f"Product ID: {product.id}, Encrypted Product ID: {product.encrypted_pro_id}, Slug: {product.slug}")
    
    encrypted_name = encrypt_data('home')
    encoded_encrypted_name = quote(encrypted_name)


    context = {
        'products': products,
        'SubCate': subcategories,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'page_obj': page_obj,
        'sizes': sizes,
        'sort': sort,
        'cart': cart,
        'amount2': amount2,
        'totalamount2': totalamount,
        'category_id': encrypted_category_id,
        'encoded_encrypted_name' : encoded_encrypted_name,
        # 'encrypted_products': encrypted_products,
        # 'encrypted_pro_id': product.encrypted_pro_id,
    }

    return render(request, 'productdetail.html', context)
    # except Exception as e:
    #     print(f"View rendering error: {e}")  
    #     return HttpResponse("Internal Server Error", status=500)


@require_POST
def add_to_cart_productdetail(request):
    # Extract product ID and quantity from the POST data
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        # Retrieve the product from the database
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        # If the product does not exist, return an error response
        return JsonResponse({'error': 'Product does not exist'}, status=400)

    if request.user.is_authenticated:
        # If the user is authenticated, associate the product with the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user, product=product)
    else:
        # For anonymous users, you might handle carts differently
        # For example, using session-based carts
        return JsonResponse({'error': 'Authentication required'}, status=403)

    # Update the quantity of the product in the cart
    cart.quantity += quantity
    cart.save()

    # Return a success response
    return JsonResponse({'message': 'Product added to cart successfully'})


@require_POST
def add_to_wishlist_productdetail(request):
    # Extract product ID from the POST data
    product_id = request.POST.get('product_id')

    try:
        # Retrieve the product from the database
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        # If the product does not exist, return an error response
        return JsonResponse({'error': 'Product does not exist'}, status=400)

    if request.user.is_authenticated:
        # If the user is authenticated, add the product to the user's wishlist
        wishlist, created = WishList.objects.get_or_create(user=request.user, product=product)
        if created:
            return JsonResponse({'message': 'Product added to wishlist successfully'})
        else:
            return JsonResponse({'message': 'Product is already in wishlist'})
    else:
        # For anonymous users, you might handle adding to wishlist differently
        # For example, you could prompt them to log in
        return JsonResponse({'error': 'Authentication required'}, status=403)


from django.http import Http404
def singleproduct(request, encrypted_product_id):

    
    print("inside try")

    # Decrypt the product_id
    product_id = decrypt(encrypted_product_id)
    print("product id",product_id)

    product = get_object_or_404(Product, id=product_id)

    context = {}
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    relatedproduct = Product.objects.all()
    # product = Product.objects.get(id=id,slug=slug)
    most_ordered_products = OrderPlaced.objects.order_by('-order__ordered_date')

    admin_choice = product.admin_choice
    # if product.size[0] != '':        
    #     size_list = json.loads(product.size[0])        
    #     print(size_list)
    #     context['sizes'] = size_list
    if product.size:
        context['sizes'] = product.size
    reviews = Rating.objects.filter(product=product)
    colors = [product.color1, product.color2, product.color3, product.color4]
    colors = [color.replace("('", "") for color in colors if color]
    print("lala colors",colors)

    wishlist = WishList.objects.filter(Q(product=product) & Q(user=request.user.pk))
    totalitem = 0
    wishitem = 0
    cart = []
    amount2 = 0
    totalamount = 0
    
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()
        cart = Cart.objects.filter(user=request.user)
        amount = sum(cart_item.quantity * cart_item.product.price for cart_item in cart)
        amount2 = amount
        totalamount = amount + 40
        user = request.user
        
    else:
        totalitem = 0
        wishitem = 0
        user = None
        cart = []
    


    if product:
        avg_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']

        product.avg_rating = round(avg_rating) if avg_rating is not None else 0
        print(product.avg_rating)

    for i in most_ordered_products:
        print("Most ordered product ID:", i.product.id)
        avg_rating2 = Rating.objects.filter(product=i.product).aggregate(Avg('rating'))['rating__avg']
        i.product.avg_rating2 = round(avg_rating2) if avg_rating2 is not None else 0
        print("This is rating:", i.product.avg_rating2)

    # user=request.user
    # cart=Cart.objects.filter(user=user)
    # print("the cart item is",cart)
    # amount=0
    # amount2 = 0
    # for p in cart:
    #     value = p.quantity*p.product.price
    #     amount= amount + value
    #     amount2=amount
        
    # totalamount=amount+40
    # print(totalamount)
    


    # for product in relatedproduct:
    #     print("product id : ", product.id)
    #     avg_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    #     product.avg_rating = round(avg_rating) if avg_rating is not None else 0
    #     print(product.avg_rating)

    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}
    for subcategory in data:
            subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
            print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging
    
    encrypted_product_id = encrypt(str(product.id))
    print(f"Product ID: {product.id}, Encrypted Product ID: {encrypted_product_id}")

    
    context.update({
        'wishlist' : wishlist,
        'product': product,
        'SubCate': data,
        'Category': parent_categories,
        'totalitem':totalitem,
        'wishitem':wishitem,
        'relatedproducts': relatedproduct,
        'reviews': reviews,
        'admin_choice': admin_choice,
        'colors': colors,
        'avg_rating': avg_rating,
        'most_ordered_products': most_ordered_products,
        'cart' : cart,
        'amount2' : amount2,
        'totalamount2' : totalamount,
        'product_id' : encrypted_product_id,
        'encrypted_id' : subcategory.encrypted_id,
        'encrypted_product_id': encrypted_product_id,
    

    })
    

    return render(request, 'singleproduct.html', context)
    # except Exception as e:
    #     # Handle decryption error or invalid ID
    #     return HttpResponse("Invalid URL", status=400)


def imageupload(request, product_pk):
    user_id = request.user.id
    product_id = product_pk
    if request.method == 'POST':
        print('inside')
        text = request.POST.get('your-text')
        image = request.FILES.get('upload-image')
        print('the image is',image)
        print('the image is',text)


        if text and image:
            product = get_object_or_404(Product, pk=product_id)
            ImageUpload.objects.create(
                user_id=user_id,
                product=product,
                text=text,
                image=image,
            )
            return redirect('checkoutimage')
        else:
            # Handle the error case where text or image is missing
            return render(request, 'upload_image.html', {
                'error': 'Text and image are required.',
                'product': product,
            })

    # Render the form again if not a POST request or if there was an error
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'upload_image.html', {'product': product})

@login_required(login_url='login_user')
def review(request, encrypted_product_id):
    try:
        print("Received encrypted ID:", encrypted_product_id)
        product_id = decrypt(encrypted_product_id)
        print("Decrypted product ID:", product_id)
    except Exception as e:
        print("Error during decryption:", e)
        return HttpResponse("Invalid product ID", status=400)
    user_id = request.user.id

    if request.method == 'POST':
        rating = request.POST['rating']
        comment = request.POST['your-commemt']

        product = get_object_or_404(Product, pk=product_id)

        data = Rating.objects.create(
            user_id=user_id,
            product=product,
            rating=rating,
            description=comment
        )

        print("Review saved successfully!")

        # Redirect to the singleproduct view with the encrypted product ID
        return redirect('singleproduct', encrypted_product_id=encrypted_product_id)
    
    # encrypted_product_id = encrypt(str(product.id))
    # print(f"Product ID: {product.id}, Encrypted Product ID: {encrypted_product_id}")


    context = {
        'user_id': user_id,
        'encrypted_product_id': encrypted_product_id,
    }
    return render(request, 'singleproduct.html', context)


@login_required
def add_to_cart(request):
    user = request.user
    encrypted_product_id = request.GET.get('prod_id')

    # Check if encrypted_product_id is provided and not empty
    if not encrypted_product_id:
        return HttpResponseBadRequest("Product ID is missing")

    try:
        # Decrypt the product_id
        product_id = decrypt(encrypted_product_id)

        # Fetch the product
        product = Product.objects.get(id=product_id)

        # Create or update the Cart object for the user and product
        Cart.objects.create(user=user, product=product)

        # Encrypt the product ID for redirection
        encrypted_product_id = encrypt(str(product.id))
        
        return redirect('singleproduct', encrypted_product_id=encrypted_product_id)
    except Product.DoesNotExist:
        return HttpResponseBadRequest("Product does not exist")
    except Exception as e:
        # Handle other potential exceptions
        return HttpResponseBadRequest(f"An error occurred: {e}")
# @login_required

def show_cart(request):
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    latest_products = Product.objects.order_by('-id')[:4]

    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}
    for subcategory in data:
        subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
        print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging

    
    totalitem = 0
    wishitem = 0
    cart = []
    gst =0
    amount = 0
    totalamount = 0
    cart_message = ""
    
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()
        cart = Cart.objects.filter(user=request.user)
        
        if cart:
            amount = sum(cart_item.quantity * cart_item.product.price for cart_item in cart)
            gst = amount * 0.10
        
            totalamount = amount + gst + 40  # Assuming shipping cost or similar
        else:
            cart_message = "Your cart is empty."
    else:
        cart_message = "You need to be logged in to view your cart."

    for product in latest_products:
        avg_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        product.avg_rating = round(avg_rating) if avg_rating is not None else 0

    context = {
        'SubCate': data,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'latest_products': latest_products,
        'cart': cart,
        'totalamount': totalamount,
        'gst': gst,
        'amount': amount,
        'cart_message': cart_message,
        'encrypted_subcategories' : encrypted_subcategories,
    }
    return render(request, 'cart2.html', context)


@login_required(login_url='login') 
def plus_cart(request):
    if request.method=="GET":
        prod_id=request.GET['prod_id']
        print("this is product id",prod_id)
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        user=request.user
        cart=Cart.objects.filter(user=user)
        amount=0
        # amount2=0
        for p in cart:
            value = p.quantity*p.product.price
            amount= amount + value
            # amount2=amount

        totalamount=amount+40
        #print(prod_id)
        data={
              'quantity':c.quantity,
              'amount':amount,
            #   'amount2': amount2,
              'totalamount':totalamount,
        }
        return JsonResponse(data)



@login_required(login_url='login_user') 
def minus_cart(request):
    if request.method=="GET":
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        user=request.user
        cart=Cart.objects.filter(user=user)
        amount=0
        # amount2=0

        for p in cart:
            value = p.quantity*p.product.price
            amount= amount + value
            # amount2=amount

        totalamount=amount+40
        #print(prod_id)
        data={
              'quantity':c.quantity,
              'amount':amount,
            #   'amount2': amount2,
              'totalamount':totalamount,
        }
        return JsonResponse(data)


# @login_required
def remove_cart(request):
    if request.method=="GET":
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        user=request.user
        cart=Cart.objects.filter(user=user)
        amount=0
        # amount2=0
        for p in cart:
            value = p.quantity * p.product.price
            amount= amount + value
            # amount2=amount
        totalamount=amount+40
       
        data={
              'quantity':c.quantity,
              'amount':amount,
            #   'amount2': amount2,
              'totalamount':totalamount,
            
        }
        return JsonResponse(data)


def show_wishlist(request):
    totalitem = 0
    wishitem = 0
    cart = []
    amount2 = 0
    totalamount = 0
    wishlist_message = ""
    encrypted_id = None
    encrypted_pro_id = None

    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()
        cart = Cart.objects.filter(user=request.user)
        amount = sum(cart_item.quantity * cart_item.product.price for cart_item in cart)
        amount2 = amount
        totalamount = amount + 40
        user = request.user
    else:
        totalitem = 0
        wishitem = 0
        user = None
        cart = []
        wishlist_message = "You need to be logged in to view your wishlist."

    products = WishList.objects.filter(user=user) if user else []
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}

    for subcategory in data:
        subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
        print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")

    if products:
        for product in products:
            product.product.encrypted_pro_id = encrypt(str(product.product.id))
            print(f"Product ID: {product.product.id}, Encrypted Product ID: {product.product.encrypted_pro_id}")
            encrypted_pro_id = product.product.encrypted_pro_id

    context = {
        'SubCate': data,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'products': products,
        'cart': cart,
        'amount2': amount2,
        'totalamount2': totalamount,
        'wishlist_message': wishlist_message,
        'encrypted_id': encrypted_subcategories.get(data[0].id) if data else None,  # Ensure at least one subcategory exists
        'encrypted_pro_id': encrypted_pro_id,
    }
    return render(request, 'wishlist.html', context)


# @login_required(login_url='login')
# def plus_wishlist(request, encrypted_product_id):
#     product_id = decrypt(encrypted_product_id)
#     product = get_object_or_404(Product, id=product_id)
#     user = request.user
#     WishList.objects.get_or_create(user=user, product=product)
    
#     encrypted_product_id = encrypt(str(product.id))
#     return redirect('singleproduct', encrypted_product_id=encrypted_product_id)


def plus_wishlist(request):
    user = request.user
    encrypted_product_id = request.GET.get('prod_id')

    # Check if encrypted_product_id is provided and not empty
    if not encrypted_product_id:
        return HttpResponseBadRequest("Product ID is missing")

    try:
        # Decrypt the product_id
        product_id = decrypt(encrypted_product_id)

        # Fetch the product
        product = Product.objects.get(id=product_id)

        # Create or update the Cart object for the user and product
        WishList.objects.create(user=user, product=product)

        # Encrypt the product ID for redirection
        encrypted_product_id = encrypt(str(product.id))
        
        return redirect('singleproduct', encrypted_product_id=encrypted_product_id)
    except Product.DoesNotExist:
        return HttpResponseBadRequest("Product does not exist")
    except Exception as e:
        # Handle other potential exceptions
        return HttpResponseBadRequest(f"An error occurred: {e}")

@login_required(login_url='login_user')
def minus_wishlist(request):
    user = request.user
    encrypted_product_id = request.GET.get('prod_id')

    # Check if encrypted_product_id is provided and not empty
    if not encrypted_product_id:
        return HttpResponseBadRequest("Product ID is missing")

    try:
        # Decrypt the product_id
        product_id = decrypt(encrypted_product_id)

        # Fetch the product
        product = Product.objects.get(id=product_id)

        # Fetch and delete the specific WishList entry
        wishlist_entry = WishList.objects.get(user=user, product=product)
        wishlist_entry.delete()

        # Encrypt the product ID for redirection
        encrypted_product_id = encrypt(str(product.id))
        
        return redirect('singleproduct', encrypted_product_id=encrypted_product_id)
    except WishList.DoesNotExist:
        return HttpResponseBadRequest("Wishlist entry does not exist")
    except Product.DoesNotExist:
        return HttpResponseBadRequest("Product does not exist")
    except Exception as e:
        # Handle other potential exceptions
        return HttpResponseBadRequest(f"An error occurred: {e}")
# class checkout(View):
#     def get(self, request):
#         # if 'paid' in request.POST:
#             totalitem = 0
#             wishitem = 0
#             if request.user.is_authenticated:
#                 totalitem = len(Cart.objects.filter(user=request.user))
#                 wishitem = len(WishList.objects.filter(user=request.user))

#             user = request.user
#             add = Customer.objects.filter(user=user)
#             cart_items = Cart.objects.filter(user=user)

#             famount = 0
#             for p in cart_items:
#                 value = p.quantity * p.product.price
#                 famount = famount + value
#             totalamount = famount + 40
#             razoramount = int(totalamount * 100)
#             client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
#             data = {"amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12"}
#             payment_response = client.order.create(data=data)
#             order_id = payment_response['id']
#             order_status = payment_response['status']
#             if order_status == 'created':
#                 payment = Payment(
#                     user=user,
#                     amount=totalamount,
#                     razorpay_order_id=order_id,
#                     razorpay_payment_status=order_status
#                 )
#                 payment.save()
     

#             return render(request, 'checkout.html', locals())

#     def post(self, request):
#         if 'cod' in request.POST:
#             # Handle Cash on Delivery logic
#             # Retrieve form data
#             user_id = request.user.id  # Assuming you have a logged-in user
#             cust_id = request.POST.get('custid')
#             tot_amount = request.POST.get('totamount')

#             # Get product IDs and quantities from the submitted form data
#             product_ids = request.POST.getlist('product_ids[]')
#             quantities = request.POST.getlist('quantities[]')

#             # Create OrderPlaced objects for each item in the cart
#             for product_id, quantity in zip(product_ids, quantities):
#                 Order.objects.create(
#                     user_id=user_id,
#                     customer_id=cust_id,
#                     product_id=product_id,
#                     quantity=quantity,
#                     payment_method='COD',
#                     amount=tot_amount,
#                 )

#             # Redirect to COD confirmation page or display success message
#             return redirect('cod_confirmation')
#         else:
#             # Handle online payment logic (Razorpay or any other payment gateway)
#             pass

#         return render(request, 'checkout.html', locals())


from django.shortcuts import redirect

# class checkout(View):
#     def get(self, request):
#         user = request.user
#         cart = Cart.objects.filter(user=user)
#         data = SubCategory.objects.all()
#         parent_categories = Category.objects.all()
#         totalitem = 0
#         wishitem = 0
#         if request.user.is_authenticated:
#             totalitem = len(Cart.objects.filter(user=request.user))
#             wishitem = len(WishList.objects.filter(user=request.user))

#         user = request.user
#         add = Customer.objects.filter(user=user)
#         cart_items = Cart.objects.filter(user=user)

#         famount = 0
#         for p in cart_items:
#             value = p.quantity * p.product.price
#             famount = famount + value
#         totalamount = famount + 40
#         razoramount = int(totalamount * 100)
#         client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
#         data = {"amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12"}
#         payment_response = client.order.create(data=data)
#         order_id = payment_response['id']
#         order_status = payment_response['status']
#         if order_status == 'created':
#             payment = Payment(
#                 user=user,
#                 amount=totalamount,
#                 razorpay_order_id=order_id,
#                 razorpay_payment_status=order_status
#             )
#             payment.save()

#         context = {
#             'user': user,
#             'cart': cart,
#             'data': data,
#             'parent_categories': parent_categories,
#             'totalitem': totalitem,
#             'wishitem': wishitem,
#             'add': add,
#             'cart_items': cart_items,
#             'famount': famount,
#             'totalamount': totalamount,
#             'razoramount': razoramount,
#             'order_id': order_id,
#             'order_status': order_status
#         }

#         return render(request, 'checkout.html', context)

#     def post(self, request):
#         data = SubCategory.objects.all()
#         parent_categories = Category.objects.all()
#         if 'cod' in request.POST:
#             user = request.user
#             cust_id = request.POST.get('custid')
#             tot_amount = request.POST.get('totamount')

#             # Retrieve the selected address ID from the form data
#             address_id = request.POST.get('cust')

#             # Create a single order for all products in the cart
#             order = Order.objects.create(
#                 user=user,
#                 customer_id=cust_id,
#                 amount=tot_amount,
#                 payment_method='COD',
#                 address_id=address_id  # Save the selected address ID with the order
#             )

#             # Get product IDs and quantities from the submitted form data
#             product_ids = request.POST.getlist('product_ids[]')
#             quantities = request.POST.getlist('quantities[]')

#             # Create OrderPlaced objects for each item in the cart
#             for product_id, quantity in zip(product_ids, quantities):
#                 OrderPlaced.objects.create(
#                     order=order,
#                     product_id=product_id,
#                     quantity=quantity
#                 )

#                 Cart.objects.filter(user=user).delete()

#             # Redirect to COD confirmation page or display success message
#             return redirect('cod_confirmation')
#         else:
#             # Handle online payment logic (Razorpay or any other payment gateway)
#             pass


#         return render(request, 'checkout.html', locals())
    
class checkout(View):
    def get(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user)
        data = SubCategory.objects.all()
        parent_categories = Category.objects.all()
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(WishList.objects.filter(user=request.user))

        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)

        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.price
            famount += value
            gst = famount * 0.10
        totalamount = famount + gst + 40

        txnid = str(uuid.uuid4())
        easebuzz_url = "https://testpay.easebuzz.in/payment/initiateLink" if settings.EASEBUZZ_ENV == 'test' else "https://pay.easebuzz.in/payment/initiateLink"
        
        customer = Customer.objects.filter(user=user).first()
        phone_number = customer.mobile if customer else ''

        params = {
            'key': settings.EASEBUZZ_MERCHANT_KEY,
            'txnid': txnid,
            'amount': str(totalamount),  # Ensure amount is a string
            'firstname': user.username,
            'email': user.email,
            'phone': phone_number,
            'productinfo': "Order Payment",
            'surl': request.build_absolute_uri(reverse('payment_success')),
            'furl': request.build_absolute_uri(reverse('payment_failure')),
            'udf1': '',
            'udf2': '',
            'udf3': '',
            'udf4': '',
            'udf5': ''
        }

        # Create the hash
        hash_string = "{key}|{txnid}|{amount}|{productinfo}|{firstname}|{email}|{udf1}|{udf2}|{udf3}|{udf4}|{udf5}|{salt}".format(
            key=settings.EASEBUZZ_MERCHANT_KEY,
            txnid=txnid,
            amount=params['amount'],
            productinfo=params['productinfo'],
            firstname=params['firstname'],
            email=params['email'],
            udf1=params['udf1'],
            udf2=params['udf2'],
            udf3=params['udf3'],
            udf4=params['udf4'],
            udf5=params['udf5'],
            salt=settings.EASEBUZZ_SALT
        )
        hash_value = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()
        params['hash'] = hash_value

        # Log the parameters and hash for debugging
        print("Parameters being sent to Easebuzz:", params)
        print("Hash String:", hash_string)
        print("Generated Hash:", hash_value)

        # Save the payment details in the database
        payment = Payments(
            user=user,
            amount=totalamount,
            easebuzz_payment_status='created'
        )
        payment.save()

        context = {
            'user': user,
            'cart': cart,
            'data': data,
            'parent_categories': parent_categories,
            'totalitem': totalitem,
            'wishitem': wishitem,
            'add': add,
            'cart_items': cart_items,
            'famount': famount,
            'totalamount': totalamount,
            'easebuzz_url': easebuzz_url,
            'params': params
        }

        return render(request, 'checkout.html', context)

    def post(self, request):
        if 'cod' in request.POST:
            user = request.user
            cust_id = request.POST.get('custid')
            tot_amount = request.POST.get('totamount')
            address_id = request.POST.get('cust')

            order = Order.objects.create(
                user=user,
                customer_id=cust_id,
                amount=tot_amount,
                payment_method='COD',
                address_id=address_id
            )

            product_ids = request.POST.getlist('product_ids[]')
            quantities = request.POST.getlist('quantities[]')

            for product_id, quantity in zip(product_ids, quantities):
                OrderPlaced.objects.create(
                    order=order,
                    product_id=product_id,
                    quantity=quantity
                )

                Cart.objects.filter(user=user).delete()


                send_invoice(order, orders,  tot_amount)

            return redirect('cod_confirmation')

        return render(request, 'checkout.html', locals())
    
# views.py (continued)
def payment_success(request):
    params = request.POST
    txnid = params['txnid']
    amount = params['amount']
    status = params['status']
    hash_received = params['hash']

    hash_string = "{key}|{txnid}|{amount}|{productinfo}|{firstname}|{email}|{udf1}|{udf2}|{udf3}|{udf4}|{udf5}|{salt}".format(
        key=settings.EASEBUZZ_MERCHANT_KEY,
        txnid=txnid,
        amount=amount,
        productinfo="Order Payment",
        firstname=params['firstname'],
        email=params['email'],
        udf1='',
        udf2='',
        udf3='',
        udf4='',
        udf5='',
        salt=settings.EASEBUZZ_SALT
    )
    hash_calculated = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()

    if hash_calculated != hash_received:
        return render(request, 'cod_orderplaced.html')

    try:
        payment = Payments.objects.get(easebuzz_payment_id=txnid)
        payment.easebuzz_payment_status = 'success' if status == 'success' else 'failed'
        payment.paid = True if status == 'success' else False
        payment.save()
    except Payments.DoesNotExist:
        return render(request, 'cod_orderplaced.html')

    return render(request, 'cod_orderplaced.html')

def payment_failure(request):
    return render(request, 'cod_orderplaced.html')

    



def cod_confirmation(request):
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(WishList.objects.filter(user=request.user))

    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}

    for subcategory in data:
        subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
        print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")


    context = {
        'SubCate':data,
        'Category' : parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'encrypted_subcategories': encrypted_subcategories,
    }
    return render(request,'cod_orderplaced.html',context)


# @login_required
def payment_done(request):
    user = request.user
    # print(request.user)
    if user.is_authenticated:
        
     order_id=request.GET.get('order_id')
    payment_id=request.GET.get('payment_id')
    cust_id=request.GET.get('cust_id')
    #print("payment_done :oid=",order_id,"pid=",payment_id,"cid=",cust_id)
    user=request.user
    #return redirect("orders")
    customer=User.objects.get(id=cust_id)
    payment=Payment.objects.get(razorpay_order_id=order_id)
    payment.paid=True
    payment.razorpay_payment_id=payment_id
    payment.save()
    cart=Cart.objects.filter(user=user)
    cart.save()
    for c in cart:
        print(c)
    OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity,payment=payment).save()
    #c.delete()
    Cart.objects.filter(user=request.user).delete()
    return redirect("home")


def search_view(request):
    if request.method == 'GET':
        search_query = request.GET.get('search_query', '')
        
        # Filter products by search query
        products = Product.objects.filter(title__icontains=search_query) 

        # Filter subcategories by search query
        subcategories = SubCategory.objects.filter(name__icontains=search_query)
        
        # Filter categories by search query
        categories = Category.objects.filter(name__icontains=search_query)

        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
            wishitem = WishList.objects.filter(user=request.user).count()

        no_results_message = ""
        if not products.exists() and not subcategories.exists() and not categories.exists():
            no_results_message = "No items found matching your search."


        for product in products:
            product.encrypted_pro_id = encrypt(str(product.id))
            print(f"Product ID: {product.id}, Encrypted Product ID: {product.encrypted_pro_id}, Slug: {product.slug}")
    

        encrypted_name = encrypt_data('home')
        encoded_encrypted_name = quote(encrypted_name)


        context = {
            'SubCate': subcategories,
            'Category': categories,
            'totalitem': totalitem,
            'wishitem': wishitem,
            'product': products,
            'no_results_message': no_results_message,
            'encoded_encrypted_name' : encoded_encrypted_name,
        }

        return render(request, 'search.html', context)
    return render(request, 'index2.html')


def category_products_view(request, category_id):
    category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=category)

    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()

    context = {
        'category': category,
        'products': products,
        'totalitem': totalitem,
        'wishitem': wishitem,
    }

    return render(request, 'category_products.html', context)

def subcategory_products_view(request, subcategory_id):
    subcategory = SubCategory.objects.get(id=subcategory_id)
    products = Product.objects.filter(subcategory=subcategory)

    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()

    context = {
        'subcategory': subcategory,
        'products': products,
        'totalitem': totalitem,
        'wishitem': wishitem,
    }

    return render(request, 'subcategory_products.html', context)



# @method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self,request):
        form=CustomerProfileForm()
        totalitem = 0
        wishitem=0

        if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
           wishitem=len(WishList.objects.filter(user=request.user))

        data = SubCategory.objects.all()
        parent_categories = Category.objects.all()
        context = {
        'SubCate': data,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'form' : form,
    }

        return render(request,'user-profile.html',context)
    def post(self,request):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            user=request.user
            name=form.cleaned_data['name']
            locality=form.cleaned_data['locality']
            city=form.cleaned_data['city']
            mobile=form.cleaned_data['mobile']
            state=form.cleaned_data['state']
            zipcode=form.cleaned_data['zipcode']


            reg=Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,"Congratulations ! Profile saved successfully")
        else:
            messages.success(request,"Invalid input data")

        return render(request,'user-profile.html',locals())
            

# @login_required        
def address(request):
    add = Customer.objects.filter(user=request.user)
    totalitem = 0
    wishitem = 0

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user)) 
        wishitem = len(WishList.objects.filter(user=request.user))

    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    context = {
        'SubCate': data,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'add' : add,
    }

    return render(request, 'address.html', context)


# @method_decorator(login_required,name='dispatch')
class updateAddress(View):
    def get(self,request,pk):
        add=Customer.objects.get(pk=pk)
        form=CustomerProfileForm(instance=add)
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
           totalitem = len(Cart.objects.filter(user=request.user))
           wishitem=len(WishList.objects.filter(user=request.user))

        data = SubCategory.objects.all()
        parent_categories = Category.objects.all()
        
        
        context = {
            'SubCate': data,
            'Category': parent_categories,
            'totalitem': totalitem,
            'wishitem': wishitem,
            'form': form,
     }

    

        return render(request,'updateaddress.html',context)

    def post(self,request,pk):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            add=Customer.objects.get(pk=pk)
            add.name=form.cleaned_data['name']
            add.locality=form.cleaned_data['locality']
            add.city=form.cleaned_data['city']
            add.mobile=form.cleaned_data['mobile']
            add.state=form.cleaned_data['state']
            add.zipcode=form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Congratulations! Profile Updated Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
            
        return redirect("address")


# @login_required
def orders(request):
    totalitem = 0
    wishitem = 0
    order_placed = []

    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()   
        
    order_placed = OrderPlaced.objects.filter(user=request.user)
    
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
         

    context = {
        'totalitem': totalitem,
        'wishitem': wishitem,
        'order_placed': order_placed,
        'SubCate': data,
        'Category': parent_categories,
    }
    return render(request, 'order.html', context)




from django.db.models import Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def shopall(request):
    print("inside  shop all")
    products = Product.objects.all()

    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()

    totalitem = 0
    wishitem = 0
    wishlist = {}
    cart = []
    amount2 = 0
    totalamount = 0
    
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()
        cart = Cart.objects.filter(user=request.user)
        amount = sum(cart_item.quantity * cart_item.product.price for cart_item in cart)
        amount2 = amount
        totalamount = amount + 40
        user = request.user
        
    else:
        totalitem = 0
        wishitem = 0
        user = None
        cart = [] 

    for product in products:
        print("product id : ", product.id)
        avg_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']

        product.avg_rating = round(avg_rating) if avg_rating is not None else 0
        print(product.avg_rating)
   
    # Paginate the products
    paginator = Paginator(products, 10)  # Show 12 products per page
    page_number = request.GET.get('page')
    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)


    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}
    for subcategory in data:
        subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
        print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging

    for product in products:
        product.encrypted_pro_id = encrypt(str(product.id))
        print(f"Product ID: {product.id}, Encrypted Product ID: {product.encrypted_pro_id}, Slug: {product.slug}")
    

    encrypted_name = encrypt_data('home')
    encoded_encrypted_name = quote(encrypted_name)


    context = {
        'products': products,
        'SubCate': data,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'cart': cart,
        'amount2': amount2,
        'totalamount2': totalamount,
        'encrypted_subcategories' : encrypted_subcategories,
        'encoded_encrypted_name': encoded_encrypted_name,
        

    }
    return render(request, 'shopall.html', context)




# @login_required
def send_otp_email(user_email):
    
    otp = str(random.randint(100000, 999999))
    send_mail(
       'Password Reset OTP',
        f'Your OTP for password reset is: {otp}',
        'your_email@example.com',  
        [user_email],
        fail_silently=False,
    )
    return otp

# View for sending OTP
# @login_required
# def send_otp(request):
#     data = SubCategory.objects.all()
#     parent_categories = Category.objects.all()
#     totalitem = Cart.objects.filter(user=request.user).count()
#     wishitem = WishList.objects.filter(user=request.user).count() 


#     if request.method == 'POST':
#         user_email = request.POST.get('email')
        
#         if user_email:
#             otp = send_otp_email(user_email)
#             request.session['otp'] = otp  
#             return redirect('otp_verification')  
#         else:
#             messages.error(request, 'Please enter a valid email address.')

    
    

#     context = {
        
#         'SubCate': data,
#         'Category': parent_categories,
#         'totalitem': totalitem,
#         'wishitem': wishitem,
#     }

#     return render(request, 'send_otp.html',context) 


def send_otp(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        
        if user_email:
            # Generate OTP
            otp = generate_otp()

            # Send OTP to the provided email address
            send_mail(
                'Your OTP',
                f'Your OTP is: {otp}',
                'sender@example.com',  # Update with your email address
                [user_email],
                fail_silently=False,
            )

            # Store OTP in session
            request.session['otp'] = otp  

            # Redirect to OTP verification page
            return redirect('otp_verification')  
        else:
            messages.error(request, 'Please enter a valid email address.')
    
    # If not a POST request or email is not provided, render the send OTP page
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()

    totalitem = 0
    wishitem = 0

    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()

    else:
        totalitem = 0
        wishitem = 0
    
    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}

    for subcategory in data:
            subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
            print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging


    context = {
        'SubCate': data,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'encrypted_subcategories' : encrypted_subcategories,
        'encrypted_id' : subcategory.encrypted_id,

    }

    return render(request, 'send_otp.html', context)

def generate_otp():
    # Generate a 6-digit OTP
    return ''.join(random.choices('0123456789', k=6))



@csrf_exempt
def resend_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_email = data.get('email')

        if user_email:
            try:
                # Generate new OTP
                new_otp = generate_otp()

                # Send new OTP to the provided email address
                send_mail(
                    'Your New OTP',
                    f'Your new OTP is: {new_otp}',
                    'sender@example.com',  # Replace with your email address
                    [user_email],
                    fail_silently=False,
                )

                # Update session with the new OTP
                request.session['otp'] = new_otp  

                # Return a success response
                return JsonResponse({'success': True})
            except Exception as e:
                # Return an error response if email sending fails
                return JsonResponse({'error': str(e)}, status=500)
        else:
            # Return an error response if email is not provided
            return JsonResponse({'error': 'Please provide a valid email address.'}, status=400)
    else:
        # Return a method not allowed response if request method is not POST
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)
    
# View for OTP verification
#@login_required
def otp_verification(request):
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        
        # Check if OTP has expired
        if 'otp_generated_time' in request.session:
            print('lalalalal')
            otp_generated_time = request.session['otp_generated_time']
            if timezone.now() > otp_generated_time + timedelta(seconds=60):
                request.session.flush()
                messages.error(request, 'OTP has expired. Please request a new one.')
                # return redirect('send_otp')

        if entered_otp == stored_otp:
            return render(request, 'password-reset.html')  
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    # Calculate the remaining time for OTP expiration
    remaining_time = 0
    if 'otp_generated_time' in request.session:
        otp_generated_time = request.session['otp_generated_time']
        remaining_time = max(0, 60 - (timezone.now() - otp_generated_time).total_seconds())

    totalitem = 0
    wishitem = 0

    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()

    else:
        totalitem = 0
        wishitem = 0

    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}

    for subcategory in data:
            subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
            print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging


    context = {
        'SubCate': data,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'remaining_time': remaining_time,  
        'encrypted_subcategories' : encrypted_subcategories,
        'encrypted_id' : subcategory.encrypted_id,

    }

    return render(request, 'otp_verification.html', context)

# #@login_required
# def password_reset(request):
#     if request.method == 'POST':
#         user=request.user
#         # Reset the user's password and clear the OTP session
#         new_password = request.POST.get('new_password')
#         # Set the new password for the user
#         # You can use Django's built-in password reset functionality or your custom logic
#         # For example, using Django's built-in functionality:
#         user.set_password(new_password)
#         user.save()
        
#         del request.session['otp']  # Clear the stored OTP from the session
#         messages.success(request, 'Password reset successful. You can now log in with your new password.')
#         return redirect('password_reset_complete')  

#     return render(request, 'password_reset.html')  


    
def PasswordReset(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            user = request.user
            if user.is_authenticated:
                # If user is authenticated, update their password
                user.set_password(new_password)
                user.save()
                
                # Clear the stored OTP from the session if it exists
                if 'otp' in request.session:
                    del request.session['otp']
                    
                # messages.success(request, 'Password reset successful. You can now log in with your new password.')
                return redirect('login_user')
            else:
                # If user is not authenticated, get their username or email
                username_or_email = request.POST.get('username_or_email')
                user = None
                try:
                    # Check if the username or email provided exists in the database
                    user = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
                except User.DoesNotExist:
                    messages.error(request, 'User not found.')
                if user:
                    # Set the new password for the user and save
                    user.set_password(new_password)
                    user.save()
                    
                    # Clear the stored OTP from the session if it exists
                    if 'otp' in request.session:
                        del request.session['otp']
                    
                    # messages.success(request, 'Password reset successful. You can now log in with your new password.')
                    return redirect('login_user')
                else:
                    messages.error(request, 'User not found.')
        else:
            messages.error(request, 'Passwords do not match.')
    
    return render(request, 'password-reset.html')



def pwcomplete(request):
    return render(request,"password_reset_complete.html")



# def autosuggest(request):
#     print("autosuggest",request.GET)
#     query_original = request.GET.get('term')
#     queryset = Product.objects.filter(title__icontains=query_original) 
#     mylist = []
#     mylist += [x.title for x in queryset]
#     return JsonResponse(mylist, safe=False)
def autosuggest(request):
    print("autosuggest", request.GET)
    query_original = request.GET.get('term')
    
    # Query products, categories, and subcategories
    product_queryset = Product.objects.filter(title__icontains=query_original)
    category_queryset = Category.objects.filter(name__icontains=query_original)
    subcategory_queryset = SubCategory.objects.filter(name__icontains=query_original)
    
    
    
    # Create a list of suggestions
    suggestions = []
    suggestions += [{'label': x.title, 'type': 'product', 'id': encrypt(str(x.id))} for x in product_queryset]
    suggestions += [{'label': x.name, 'type': 'category', 'id': encrypt(str(x.id))} for x in category_queryset]
    suggestions += [{'label': x.name, 'type': 'subcategory', 'id': encrypt(str(x.id))} for x in subcategory_queryset]

    return JsonResponse(suggestions, safe=False)

def products_by_category(request, encrypted_category_id):
    category_id = decrypt(encrypted_category_id)
    categories = get_object_or_404(Category, id=category_id)
    subcategories = SubCategory.objects.filter(parent_category=categories)
    products = Product.objects.filter(categories__in=subcategories)
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    for product in products:
        product.encrypted_pro_id = encrypt(str(product.id))
        print(f"Product ID: {product.id}, Encrypted Product ID: {product.encrypted_pro_id}")

    encrypted_name = encrypt_data('home')
    encoded_encrypted_name = quote(encrypted_name)

    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()


    # Sorting logic
    sort = request.GET.get('sort', 'relevance')
    if sort == 'name_asc':
        products = products.order_by('title')
    elif sort == 'name_desc':
        products = products.order_by('-title')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('id')  # Default sorting by relevance (or any other default logic)

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for product in products:
        avg_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        product.avg_rating = round(avg_rating) if avg_rating is not None else 0

    sizes = []
    for product in products:
        if product.size:
            sizes.extend(product.size)

    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}
    for subcategory in data:
        subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
        print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging



    
    context = {
        'SubCate': data,
        'Category': parent_categories,
        'page_obj': page_obj,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'products': products,
        'subcategory': categories,
        'encoded_encrypted_name' : encoded_encrypted_name,
        # 'encrypted_pro_id' : product.encrypted_pro_id,
        'encrypted_subcategories' :encrypted_subcategories,
        'encrypted_id' : subcategory.encrypted_id,

    }
    return render(request, 'category_products.html',context)

def products_by_subcategory(request, encrypted_subcategory_id):
    subcategory_id = decrypt(encrypted_subcategory_id)
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
    products = Product.objects.filter(categories=subcategory)
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()


    # Sorting logic
    sort = request.GET.get('sort', 'relevance')
    if sort == 'name_asc':
        products = products.order_by('title')
    elif sort == 'name_desc':
        products = products.order_by('-title')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('id')  # Default sorting by relevance (or any other default logic)

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for product in products:
        avg_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        product.avg_rating = round(avg_rating) if avg_rating is not None else 0

    sizes = []
    for product in products:
        if product.size:
            sizes.extend(product.size)

    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}
    for subcategory in data:
        subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
        print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")
        

    for product in products:
        product.encrypted_pro_id = encrypt(str(product.id))
        print(f"Product ID: {product.id}, Encrypted Product ID: {product.encrypted_pro_id}")

    encrypted_name = encrypt_data('home')
    encoded_encrypted_name = quote(encrypted_name)



    
    context = {
        'SubCate': data,
        'Category': parent_categories,
        'page_obj': page_obj,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'products': products,
        'subcategory': subcategory,
        'encoded_encrypted_name' : encoded_encrypted_name,
        # 'encrypted_pro_id' : product.encrypted_pro_id,
        'encrypted_subcategories' :encrypted_subcategories,
        'encrypted_id' : subcategory.encrypted_id,

    }
    return render(request, 'subcategory_products.html',context)




def delete_item(request, item_id):
    if request.method == 'POST':
        
        try:
            item = WishList.objects.get(id=item_id)
            item.delete()
        except WishList.DoesNotExist:
            # Handle the case where the item doesn't exist
            pass
    
        return redirect('wishlist')  
    return render(request, 'wishlist.html')




@login_required(login_url='login') 
def add_to_cart_wishlist(request):
    user = request.user
    print("lalala",user)
    product_id = request.GET.get('prod_id')
    print(product_id)
    # Check if product_id is provided and not empty
    if not product_id:
        return HttpResponseBadRequest("Product ID is missing")

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return HttpResponseBadRequest("Product does not exist")

    # Create a Cart object for the user and product
    Cart(user=user, product=product).save()

    return redirect(reverse('wishlist'))




# # @login_required
# def show_cart(request):
#     user=request.user
#     cart=Cart.objects.filter(user=user)
#     amount=0
#     for p in cart:
#         value = p.quantity*p.product.price
#         amount= amount + value
#         amount2=amount
        
#     totalamount=amount+40
#     totalitem = 0
#     wishitem = 0
#     if request.user.is_authenticated:
#         totalitem = len(Cart.objects.filter(user=request.user))
#         wishitem=len(WishList.objects.filter(user=request.user))
    
#     context = {
#         'totalitem':totalitem,
#         'wishitem':wishitem,
#     }
#     return render(request,'index2.html',locals())




@login_required(login_url='login') 
def plus_cart_base(request):
    if request.method=="GET":
        prod_id=request.GET['prod_id']
        print("this is product id",prod_id)
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        user=request.user
        cart=Cart.objects.filter(user=user)
        amount2=0
        # amount2=0
        for p in cart:
            value = p.quantity*p.product.price
            amount2= amount2 + value
            # amount2=amount

        totalamount2=amount2+40
        #print(prod_id)
        data={
              'quantity':c.quantity,
              'amount':amount2,
            #   'amount2': amount2,
              'totalamount2':totalamount2,
        }
        return JsonResponse(data)



@login_required(login_url='login') 
def minus_cart_base(request):
    if request.method=="GET":
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        user=request.user
        cart=Cart.objects.filter(user=user)
        amount2=0
        # amount2=0

        for p in cart:
            value = p.quantity*p.product.price
            amount2= amount2 + value
            # amount2=amount

        totalamount2=amount2+40
        #print(prod_id)
        data={
              'quantity':c.quantity,
              'amount2':amount2,
            #   'amount2': amount2,
              'totalamount2':totalamount2,
        }
        return JsonResponse(data)


# @login_required
def remove_cart_base(request):
    if request.method=="GET":
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        user=request.user
        cart=Cart.objects.filter(user=user)
        amount=0
        # amount2=0
        for p in cart:
            value = p.quantity * p.product.price
            amount= amount + value
            # amount2=amount
        totalamount=amount+40
       
        data={
              'quantity':c.quantity,
              'amount':amount,
            #   'amount2': amount2,
              'totalamount':totalamount,
            
        }
        return JsonResponse(data)

@login_required(login_url='login_user') 
def trackorder(request):
    orders = Order.objects.filter(user=request.user)
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    totalitem = Cart.objects.filter(user=request.user).count()
    wishitem = WishList.objects.filter(user=request.user).count()

    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}
    for subcategory in data:
        subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
        print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")
        

    # for product in products:
    #     product.encrypted_pro_id = encrypt(str(product.id))
    #     print(f"Product ID: {product.id}, Encrypted Product ID: {product.encrypted_pro_id}")

    encrypted_name = encrypt_data('home')
    encoded_encrypted_name = quote(encrypted_name)

    context = {
        
        'SubCate': data,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'orders': orders,
        'encrypted_subcategories' :encrypted_subcategories,
        'encrypted_id' : subcategory.encrypted_id,
        'encoded_encrypted_name' :encoded_encrypted_name,

    }

    return render(request, 'track_order.html', context)


@login_required(login_url='login_user')
def invoice(request):
    user = request.user

    # Retrieve the latest order for the user, if any
    try:
        order = Order.objects.filter(user=user).latest('ordered_date')
    except Order.DoesNotExist:
        order = None

    # Retrieve all order items
    orders = OrderPlaced.objects.all()

    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    totalitem = Cart.objects.filter(user=user).count()
    wishitem = WishList.objects.filter(user=user).count()

    subtotal = 0
    if order:
        # Iterate through each order item and calculate the subtotal
        for order_item in orders:
            if order_item.order_id == order.id:
                subtotal += order_item.quantity * order_item.product.price

    # Calculate total amount including taxes or other charges
    totalamount = subtotal + 352

    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}
    for subcategory in data:
        subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
        print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging


    context = {
        'order': order,
        'orders': orders,
        'subtotal': subtotal,
        'totalamount': totalamount,
        'SubCate': data,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'encrypted_subcategories' :encrypted_subcategories,
        'encrypted_id' : subcategory.encrypted_id,

    }

    # Check if export request
    if 'export' in request.GET and order:
        # Generate PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
        
        # Create PDF document
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        
        # Create PDF table
        data = [['Product', 'Quantity', 'Price']]
        for order_item in orders:
            if order_item.order_id == order.id:
                data.append([order_item.product.title, order_item.quantity, order_item.product.price])
        table = Table(data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(table)
        
        # Build PDF document
        doc.build(elements)
        return response

    return render(request, 'invoice.html', context)


@login_required(login_url='login_user')
def userprofile(request):
    # Retrieve the Customer object for the current user
    registered_user = User.objects.all()
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()

    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}
    for subcategory in data:
        subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
        print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging

    
    # Define default background image URL
    default_background_image = "{% static '/images/banner/8.jpg' %}"

    customer = None
    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user).first()

    if request.method == 'POST':
        # Retrieve data from the form
        image1 = request.POST.get('image1')
        image2 = request.POST.get('image2')
        name = request.POST.get('name')
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        address3 = request.POST.get('address3')
        email1 = request.POST.get('email1')
        email2 = request.POST.get('email2')
        phone1 = request.POST.get('phone1')
        phone2 = request.POST.get('phone2')

        if customer:
            # Update only the fields that were submitted in the form
            if name:
                customer.name = name
            if address1:
                customer.address1 = address1
            if address2:
                customer.address2 = address2
            if address3:
                customer.address3 = address3
            if email1:
                customer.email1 = email1
            if email2:
                customer.email2 = email2
            if phone1:
                customer.mobile = phone1
            if phone2:
                customer.mobile2 = phone2
            if image1:
                customer.image1 = image1
            if image2:
                customer.image2 = image2
            customer.save()
            messages.success(request, "Congratulations! Profile updated successfully.")
        else:
            # Create a new Customer object and save it
            customer = Customer(
                user=request.user,
                name=name,
                address1=address1,
                address2=address2,
                address3=address3,
                email1=email1,
                email2=email2,
                mobile2=phone2,
                mobile=phone1,
                image1=image1,
                image2=image2,
            )
            customer.save()
            messages.success(request, "Congratulations! Profile created successfully.")

        # If customer has an image, get its URL
        background_image_url = customer.image1.url if customer and customer.image1 else default_background_image

    else:
        # If it's a GET request, just set default background image URL
        background_image_url = default_background_image

    totalitem = 0
    wishitem = 0
    customer = {}

    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()
        customer = Customer.objects.filter(user=request.user).first()


    else:
        totalitem = 0
        wishitem = 0

    context = {
        'customer': customer,
        'background_image_url': background_image_url,
        'SubCate': data,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'registered_user' : registered_user,
        'encrypted_subcategories' : encrypted_subcategories,
        
    }

    
    # Render the form with existing user details
    return render(request, 'userprofile2.html', context)


@login_required(login_url='login_user') 
def add_to_cart_newarrival(request):
    user = request.user
    product_id = request.GET.get('prod_id')

    # Check if product_id is provided and not empty
    if not product_id:
        return HttpResponseBadRequest("Product ID is missing")

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return HttpResponseBadRequest("Product does not exist")

    # Check if the product is already in the user's cart
    try:
        cart_item = Cart.objects.get(user=user, product=product)
        # If the item is already in the cart, add a message
        messages.info(request, 'Item already exists in the cart.')
    except Cart.DoesNotExist:
        # If the item is not in the cart, create a new Cart object for the user and product
        Cart(user=user, product=product).save()
        # Add a success message indicating that the item was successfully added to the cart
        messages.success(request, 'Item added to cart.')

    # Redirect back to the home page
    return redirect(reverse('home'))


@login_required(login_url='login_user') 
def add_to_cart_tabmen(request):
    # Extract product ID and quantity from the POST data
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        # Retrieve the product from the database
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        # If the product does not exist, return an error response
        return JsonResponse({'error': 'Product does not exist'}, status=400)

    if request.user.is_authenticated:
        # If the user is authenticated, associate the product with the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user, product=product)
    else:
        # For anonymous users, you might handle carts differently
        # For example, using session-based carts
        return JsonResponse({'error': 'Authentication required'}, status=403)

    # Update the quantity of the product in the cart
    cart.quantity += quantity
    cart.save()

    # Return a success response
    return JsonResponse({'message': 'Product added to cart successfully'})


@login_required(login_url='login_user') 
def add_to_wishlist_tabmen(request):
    # Extract product ID from the POST data
    product_id = request.POST.get('product_id')

    try:
        # Retrieve the product from the database
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        # If the product does not exist, return an error response
        return JsonResponse({'error': 'Product does not exist'}, status=400)

    if request.user.is_authenticated:
        # If the user is authenticated, add the product to the user's wishlist
        wishlist, created = WishList.objects.get_or_create(user=request.user, product=product)
        if created:
            return JsonResponse({'message': 'Product added to wishlist successfully'})
        else:
            return JsonResponse({'message': 'Product is already in wishlist'})
    else:
        # For anonymous users, you might handle adding to wishlist differently
        # For example, you could prompt them to log in
        return JsonResponse({'error': 'Authentication required'}, status=403)




@login_required(login_url='login_user') 
def add_to_cart_tabwomen(request):
    # Extract product ID and quantity from the POST data
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        # Retrieve the product from the database
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        # If the product does not exist, return an error response
        return JsonResponse({'error': 'Product does not exist'}, status=400)

    if request.user.is_authenticated:
        # If the user is authenticated, associate the product with the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user, product=product)
    else:
        # For anonymous users, you might handle carts differently
        # For example, using session-based carts
        return JsonResponse({'error': 'Authentication required'}, status=403)

    # Update the quantity of the product in the cart
    cart.quantity += quantity
    cart.save()

    # Return a success response
    return JsonResponse({'message': 'Product added to cart successfully'})


@login_required(login_url='login_user') 
def add_to_wishlist_tabwomen(request):
    # Extract product ID from the POST data
    product_id = request.POST.get('product_id')

    try:
        # Retrieve the product from the database
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        # If the product does not exist, return an error response
        return JsonResponse({'error': 'Product does not exist'}, status=400)

    if request.user.is_authenticated:
        # If the user is authenticated, add the product to the user's wishlist
        wishlist, created = WishList.objects.get_or_create(user=request.user, product=product)
        if created:
            return JsonResponse({'message': 'Product added to wishlist successfully'})
        else:
            return JsonResponse({'message': 'Product is already in wishlist'})
    else:
        # For anonymous users, you might handle adding to wishlist differently
        # For example, you could prompt them to log in
        return JsonResponse({'error': 'Authentication required'}, status=403)







@login_required(login_url='login_user') 
def add_to_cart_tabchild(request):
    # Extract product ID and quantity from the POST data
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        # Retrieve the product from the database
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        # If the product does not exist, return an error response
        return JsonResponse({'error': 'Product does not exist'}, status=400)

    if request.user.is_authenticated:
        # If the user is authenticated, associate the product with the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user, product=product)
    else:
        # For anonymous users, you might handle carts differently
        # For example, using session-based carts
        return JsonResponse({'error': 'Authentication required'}, status=403)

    # Update the quantity of the product in the cart
    cart.quantity += quantity
    cart.save()

    # Return a success response
    return JsonResponse({'message': 'Product added to cart successfully'})



@login_required(login_url='login_user') 
def add_to_wishlist_tabchild(request):
    # Extract product ID from the POST data
    product_id = request.POST.get('product_id')

    try:
        # Retrieve the product from the database
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        # If the product does not exist, return an error response
        return JsonResponse({'error': 'Product does not exist'}, status=400)

    if request.user.is_authenticated:
        # If the user is authenticated, add the product to the user's wishlist
        wishlist, created = WishList.objects.get_or_create(user=request.user, product=product)
        if created:
            return JsonResponse({'message': 'Product added to wishlist successfully'})
        else:
            return JsonResponse({'message': 'Product is already in wishlist'})
    else:
        # For anonymous users, you might handle adding to wishlist differently
        # For example, you could prompt them to log in
        return JsonResponse({'error': 'Authentication required'}, status=403)





@login_required(login_url='login_user') 
def add_to_cart_taball(request):
    # Extract product ID and quantity from the POST data
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        # Retrieve the product from the database
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        # If the product does not exist, return an error response
        return JsonResponse({'error': 'Product does not exist'}, status=400)

    if request.user.is_authenticated:
        # If the user is authenticated, associate the product with the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user, product=product)
    else:
        # For anonymous users, you might handle carts differently
        # For example, using session-based carts
        return JsonResponse({'error': 'Authentication required'}, status=403)

    # Update the quantity of the product in the cart
    cart.quantity += quantity
    cart.save()

    # Return a success response
    return JsonResponse({'message': 'Product added to cart successfully'})



@login_required(login_url='login_user') 
def add_to_wishlist_taball(request):
    # Extract product ID from the POST data
    product_id = request.POST.get('product_id')

    try:
        # Retrieve the product from the database
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        # If the product does not exist, return an error response
        return JsonResponse({'error': 'Product does not exist'}, status=400)

    if request.user.is_authenticated:
        # If the user is authenticated, add the product to the user's wishlist
        wishlist, created = WishList.objects.get_or_create(user=request.user, product=product)
        if created:
            return JsonResponse({'message': 'Product added to wishlist successfully'})
        else:
            return JsonResponse({'message': 'Product is already in wishlist'})
    else:
        # For anonymous users, you might handle adding to wishlist differently
        # For example, you could prompt them to log in
        return JsonResponse({'error': 'Authentication required'}, status=403)


@login_required(login_url='login_user') 
def add_to_wishlist_newarrivals(request):
    product_id = request.POST.get('product_id')

    if not product_id:
        return JsonResponse({'error': 'No product ID provided'}, status=400)

    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product does not exist'}, status=400)

    wishlist, created = WishList.objects.get_or_create(user=request.user, product=product)
    if created:
        return JsonResponse({'message': 'Product added to wishlist successfully'})
    else:
        return JsonResponse({'message': 'Product is already in wishlist'})



@login_required(login_url='login_user') 
def add_to_cart_shopall(request):
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')

    if not product_id:
        print("No product ID provided")  # Debug: Check if product ID is missing
        return JsonResponse({'error': 'No product ID provided'}, status=400)

    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product does not exist'}, status=400)

    # Assuming you have a Cart model and user is authenticated
    cart, created = Cart.objects.get_or_create(user=request.user, product=product, defaults={'quantity': quantity})
    if not created:
        cart.quantity += int(quantity)
        cart.save()

    return JsonResponse({'message': 'Product added to cart successfully'})




@login_required(login_url='login_user') 
def add_to_wishlist_shopall(request):
    product_id = request.POST.get('product_id')

    if not product_id:
        print("No product ID provided")  # Debug: Check if product ID is missing
        return JsonResponse({'error': 'No product ID provided'}, status=400)

    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product does not exist'}, status=400)

    wishlist, created = WishList.objects.get_or_create(user=request.user, product=product)
    if created:
        return JsonResponse({'message': 'Product added to wishlist successfully'})
    else:
        return JsonResponse({'message': 'Product is already in wishlist'})
    

from urllib.parse import urlparse

class checkoutimage(View):
    def get(self, request):
        data = SubCategory.objects.all()
        parent_categories = Category.objects.all()
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(WishList.objects.filter(user=request.user))

        user = request.user
        add = Customer.objects.filter(user=user)
        imageupload = ImageUpload.objects.filter(user=user).order_by('-ordered_date').first()

        famount = 0
        totalamount = 0
        if imageupload:
            value = imageupload.quantity * imageupload.product.price
            famount = famount + value
            print(imageupload.product.price)
            print(imageupload.quantity)  # Corrected to print quantity

        totalamount = famount + 40

        encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}
        for subcategory in data:
            subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
            print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")

        context = {
            'user': user,
            'totalitem': totalitem,
            'wishitem': wishitem,
            'add': add,
            'imageupload': imageupload,
            'totalamount': totalamount,
            'famount': famount,
            'SubCate': data,
            'Category': parent_categories,
            'encrypted_subcategories':encrypted_subcategories,
        }

        return render(request, 'checkoutimage.html', context)

    
    

    def post(self, request):
        user = request.user
        cust_id = request.POST.get('custid')
        tot_amount = request.POST.get('totamount')
        address_id = request.POST.get('cust')
        text = request.POST.get('text')
        image_url = request.POST.get('image_url')
        print(image_url)

        if text and image_url:
            # Parse the image URL to get the file name
            image_path = urlparse(image_url).path
            image_filename = os.path.basename(image_path)

            # Check if an entry exists with the same user and image URL
            image_upload = ImageUpload.objects.filter(user=user, image=image_filename).first()

            if image_upload:
                # Update the existing entry
                image_upload.text = text
                image_upload.customer_id = cust_id
                image_upload.amount = tot_amount
                image_upload.payment_method = 'COD'
                image_upload.address_id = address_id
                image_upload.save()

                send_invoice(image_upload,orders,  tot_amount)
                Cart.objects.filter(user=user).delete()
                # Redirect to COD confirmation page or display success message
                return redirect('cod_confirmation')
            else:
                # Handle the case where no matching entry is found
                return HttpResponse("Image not found in the database.")

        # Handle the case where text or image URL is missing
        return HttpResponse("Text and image URL are required.")


def orderhis(request):
    orders = Order.objects.filter(user=request.user)
    orderplaced = OrderPlaced.objects.all()
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    totalitem = Cart.objects.filter(user=request.user).count()
    wishitem = WishList.objects.filter(user=request.user).count()

    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}
    for subcategory in data:
        subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
        print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging

    

    context = {
        
        'SubCate': data,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'orders': orders,
        'orderplaced' : orderplaced,
        'encrypted_subcategories' : encrypted_subcategories,
        'encrypted_id': subcategory.encrypted_id,
    }
    return render(request,'orderhistory.html',context)


from django.core.mail import EmailMultiAlternatives
import logging
# Configure logging
logger = logging.getLogger(__name__)

def send_invoice(order, orders, total_amount):
    try:
        print("inside the email invoice")
        # Convert total_amount to a float if it's a string
        total_amount = float(total_amount)
        subtotal = total_amount - 40  # Assuming 40 is a fixed extra cost

        subject = 'Your Invoice'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [order.user.email]

        context = {
            'order': order,
            'orders': orders,
            'totalamount': total_amount,
            'subtotal': subtotal
        }

        html_content = render_to_string('invoice_email.html', context)

        logger.info(f'Sending email to {to_email} with subject "{subject}"')

        email = EmailMultiAlternatives(subject, '', from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send()

        logger.info('Invoice email sent successfully.')
    except Exception as e:
        logger.error(f'Error sending invoice email: {e}')

import smtplib

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('w3digitalagency21@gmail.com', 'yedx kflb ujyk lncf')
    server.quit()
    print('SMTP connection successful')
except Exception as e:
    print(f'Error connecting to SMTP server: {e}')



def about(request):
    datas = StaticPage.objects.filter(page='about').first()
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()

    
    encrypted_name = encrypt_data('home')
    encoded_encrypted_name = quote(encrypted_name)

    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}
    for subcategory in data:
        subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
        print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging




    context={
        'SubCate': data,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'data':datas,
        'encrypted_subcategories' :encrypted_subcategories,
        'encrypted_id' : subcategory.encrypted_id,
        'encoded_encrypted_name' : encoded_encrypted_name,
    }
    return render(request, 'about.html',context)


def contact(request):
    print("Contact view called")
    print(f"Request method: {request.method}")

    if request.method == 'POST':
        try:
            print("Inside POST request")
            firstname = request.POST.get('firstname')
            lastname  = request.POST.get('lastname')
            email = request.POST.get('email')
            phone = request.POST.get('phonenumber')
            comments = request.POST.get('address')

            # Save to database
            datas = Contact(
                First_name=firstname,
                Last_name=lastname,
                Email=email,
                phn=phone,
                comments=comments
            )
            datas.save()
            print("Data saved successfully")

            return render(request, 'contact.html', {'success': True})

        except Exception as e:
            print(f"An error occurred: {e}")
            return render(request, 'contact.html', {'error': str(e)})

    return render(request, 'contact.html')



def terms_condition(request):
    datas = StaticPage.objects.filter(page='terms and conditions').first()
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()

    
    encrypted_name = encrypt_data('home')
    encoded_encrypted_name = quote(encrypted_name)

    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}
    for subcategory in data:
        subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
        print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging




    context={
        'SubCate': data,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'data':datas,
        'encrypted_subcategories' :encrypted_subcategories,
        'encrypted_id' : subcategory.encrypted_id,
        'encoded_encrypted_name' : encoded_encrypted_name,
    }
    return render(request, 'terms_and_condition.html',context)


def privacypage(request):
    datas = StaticPage.objects.filter(page='privay policy').first()
    data = SubCategory.objects.all()
    parent_categories = Category.objects.all()
    
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = WishList.objects.filter(user=request.user).count()

    
    encrypted_name = encrypt_data('home')
    encoded_encrypted_name = quote(encrypted_name)

    encrypted_subcategories = {subcategory.id: encrypt(str(subcategory.id)) for subcategory in data}
    for subcategory in data:
        subcategory.encrypted_id = encrypted_subcategories[subcategory.id]
        print(f"Subcategory ID: {subcategory.id}, Encrypted ID: {subcategory.encrypted_id}")  # Debugging




    context={
        'SubCate': data,
        'Category': parent_categories,
        'totalitem': totalitem,
        'wishitem': wishitem,
        'data':datas,
        'encrypted_subcategories' :encrypted_subcategories,
        'encrypted_id' : subcategory.encrypted_id,
        'encoded_encrypted_name' : encoded_encrypted_name,
    }
    return render(request,'privacy_policy.html',context)