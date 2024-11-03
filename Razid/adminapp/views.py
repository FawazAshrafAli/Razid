from django.shortcuts import render, redirect
from .models import *
from django.views import View
from django.http import JsonResponse
from userapp . models import Rating,User,OrderPlaced,Order,ImageUpload,Contact
from django.shortcuts import render, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from .forms import ImageUploadForm
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg
from django.core.files.base import ContentFile
import base64
from django.urls import reverse
from django.http import Http404
from .utils import encrypt
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
import random
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.db import IntegrityError
from django.db.models import Sum
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
import datetime
import calendar





# from .utils import encode_url, decode_url 

# Create your views here.
def adminlogin(request):
    print("inside function")
    if request.method == 'POST':
        print("inside POST request")

        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            admin_user = AdminUser.objects.get(username=username,password=password)
            
            # Check if the provided password matches the hashed password
            if admin_user is not None:
                
                return redirect('adminhome')
            else:
                messages.error(request, "Authentication failed.")
                return redirect('login_admin')

        except AdminUser.DoesNotExist:
            messages.error(request, "Authentication failed.")
            return redirect('login_admin')
    
    return render(request, 'login_admin.html')

@login_required(login_url='login_admin')
def home(request):
    orders = Order.objects.all()
    today = timezone.now().date()
    daily_order_count = Order.objects.filter(ordered_date__date=today).count()
    daily_visitors_count = User.objects.filter(last_login__date=today).count()
    daily_signups_count = User.objects.filter(date_joined__date=today).count()
    daily_revenue = Order.objects.filter(ordered_date__date=today).aggregate(total=Sum('amount'))['total'] or 0
    order_placed = OrderPlaced.objects.all()
    now = timezone.now()
    current_month_start = now.replace(day=1)
    previous_month_end = current_month_start - timedelta(days=1)
    previous_month_start = previous_month_end.replace(day=1)



    last_six_customers = User.objects.annotate(
        order_count=Count('order'),
        total_spent=Sum('order__amount')
    ).order_by('-date_joined')[:6]

    top_three_products = Product.objects.annotate(
        order_count=Count('orderitems')
    ).order_by('-order_count')[:3]

    admin_user = None
    if request.user.is_authenticated and request.user.is_superuser:
        admin_user = request.user
        print(admin_user)  
    
    for i in orders:
      print(f"Order ID from orders: {i.id} ({type(i.id)})")

    for j in order_placed:
        print(f"Order ID from order_placed: {j.order_id} ({type(j.order_id)})")

    sold_items = (
        OrderPlaced.objects
        .values('product__title')  
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:10]  
    )
    
    now = timezone.now()
    current_month_start = now.replace(day=1)

    # Get the start of the previous month
    previous_month_end = current_month_start - timedelta(days=1)
    previous_month_start = previous_month_end.replace(day=1)

    # Get the top 10 sold items in the current month
    sold_items = (
        OrderPlaced.objects
        .filter(order__ordered_date__gte=current_month_start)
        .values('product__title')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:10]
    )

    # Get the sales for the same products in the previous month
    previous_sold_items = (
        OrderPlaced.objects
        .filter(order__ordered_date__range=(previous_month_start, previous_month_end))
        .values('product__title')
        .annotate(previous_quantity=Sum('quantity'))
    )

    # Convert previous_sold_items to a dictionary for easy lookup
    previous_sales_dict = {item['product__title']: item['previous_quantity'] for item in previous_sold_items}

    # Calculate the percentage change
    for item in sold_items:
        product_title = item['product__title']
        current_sales = item['total_quantity']
        previous_sales = previous_sales_dict.get(product_title, 0)  # Default to 0 if not found

        if previous_sales:
            item['percentage_change'] = ((current_sales - previous_sales) / previous_sales) * 100
        else:
            item['percentage_change'] = 0

    today = datetime.date.today()
    current_month = today.month
    current_year = today.year

    
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    signup_counts = [0] * days_in_month

    
    signups = User.objects.filter(date_joined__year=current_year, date_joined__month=current_month)

   
    for signup in signups:
        day = signup.date_joined.day
        if 1 <= day <= days_in_month: 
            signup_counts[day - 1] += 1  

    
    today = datetime.date.today()
     
    # Prepare labels and empty lists for active and inactive users
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    active_users = []
    inactive_users = []

    for day in last_7_days:
        # Calculate active users: Assume users who have logged in during the day are active
        active_count = User.objects.filter(last_login__date=day).count()
        active_users.append(active_count)

        # Calculate inactive users: Users who have not logged in that day
        inactive_count = User.objects.filter(last_login__date__lt=day).count()
        inactive_users.append(inactive_count)

    
    completed_orders = Order.objects.filter(status='Delivered').count()
    unpaid_orders = Order.objects.filter(status='Processing').count()
    returned_orders = Order.objects.filter(status='Shipped').count()
    pending_orders = Order.objects.filter(status='Pending').count()
    canceled_orders = Order.objects.filter(status='Order Placed').count()
    # broken_orders = Order.objects.filter(status='broken').count()
    

    

    context = {
        'orders': orders,
        'order_placed' : order_placed,
        'daily_order_count': daily_order_count,
        'daily_visitors_count': daily_visitors_count,
        'daily_signups_count': daily_signups_count,
        'daily_revenue': daily_revenue,
        'admin_user': admin_user,  
        'last_six_customers': last_six_customers,
        'top_three_products': top_three_products,
        'sold_items': sold_items,
        'signup_data': signup_counts,
        'labels': [day.strftime('%d %b') for day in last_7_days],
        'active_users': active_users,
        'inactive_users': inactive_users,
        'completed_orders': completed_orders,
        'unpaid_orders': unpaid_orders,
        'returned_orders': returned_orders,
        'pending_orders': pending_orders,
        'canceled_orders': canceled_orders,
        # 'broken_orders': broken_orders,
       
        
    }
    return render(request, 'home.html', context)

def categorypage(request):
    if request.method == 'POST':
        
        # if 'text' in request.POST:
            name = request.POST['text']
            slug = request.POST['slug']
            sort_description = request.POST['sortdescription']
            full_description =  request.POST['fulldescription']
            product_tags = request.POST['group_tag']
            data = Category()
            data.name = name
            data.slug=slug
            data.full_detail = full_description
            data.sort_description = sort_description
            data.product_tag = product_tags
            data.save()

    cate = Category.objects.all()
    sub = SubCategory.objects.all()
    

    product_counts = {}
    for subcategory in sub:
        product_counts[subcategory.id] = Product.objects.filter(categories=subcategory).count()
        print(product_counts)

    
    

    context={
        'cate':cate,
        'subcate' : sub,
        'product_counts': product_counts,
      
    }
    return render(request, 'category.html',context)


    

def subcategory(request):
    parentCategory = Category.objects.all()
    sub = SubCategory.objects.all()

    if request.method=='POST':
        name = request.POST['text']
        slug = request.POST['slug']
        sort_description = request.POST['sortdescription']
        full_description =  request.POST['fulldescription']
        product_tags = request.POST['group_tag']
        id=request.POST['parent-category']
        image= request.FILES['image1']

        id = Category.objects.filter(id = id).first()
        data = SubCategory()
        data.name = name
        data.slug=slug
        data.full_detail = full_description
        data.sort_description = sort_description
        data.product_tag = product_tags
        data.parent_category = id
        data.image = image
        data.save()

    subcategories_with_counts = []

    for subcategory in sub:
        product_count = Product.objects.filter(categories=subcategory).count()
        subcategories_with_counts.append({
            'subcategory': subcategory,
            'product_count': product_count
        })
       
    
    


    context = {

        'parentCategory': parentCategory,
        'subcategory' : sub,
        'subcategories_with_counts': subcategories_with_counts,
      

       

    }

    
    return render(request, 'sub_category.html', context)

def productsAdd(request):
    print("inside productsAdd view")
    
    data = SubCategory.objects.all()
    
    if request.method == 'POST':
        print("inside POST request")
        
        # Safely retrieve files from request.FILES
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')
        image5 = request.FILES.get('image5')
        image6 = request.FILES.get('image6')

        # Retrieve other form data
        product_name = request.POST.get('product_name', '')
        categories_id = request.POST.get('categories', '')
        availability = request.POST.get('availability', '')
        price = request.POST.get('price', '')
        description = request.POST.get('description', '')
        tags = request.POST.get('group_tag', '')
        quantity = request.POST.get('quantity', '')
        full_detail = request.POST.get('fulldetail', '')
        slug = request.POST.get('slug', '')
        custom_size = request.POST.get('customsize', '')
        admin_choice = request.POST.get('admin_choice', '')
        color1 = request.POST.get('color1', '')
        color2 = request.POST.get('color2', '')
        color3 = request.POST.get('color3', '')
        color4 = request.POST.get('color4', '')
        additional_colors = request.POST.getlist('additionalColor')
        selected_sizes = request.POST.getlist('size')

        # Retrieve cropped image data
        cropped_image_data = request.POST.get('cropped_image_data', '')
        
        # Decode base64 data and save it as a file
        format, imgstr = cropped_image_data.split(';base64,') 
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'cropped_image.{ext}')

        categories = SubCategory.objects.get(id=categories_id)

        # Create a new product instance
        product_details = Product(
            product_image=data,
            product_image1=image1,
            product_image2=image2,
            product_image3=image3,
            product_image4=image4,
            product_image5=image5,
            product_image6=image6,
            title=product_name,
            categories=categories,
            availability=availability,
            admin_choice=admin_choice,
            price=price,
            description=description,
            product_tag=tags,
            quantity=quantity,
            full_detail=full_detail,
            slug=slug,
            color1=color1,
            color2=color2,
            color3=color3,
            color4=color4,
            colors=additional_colors,
            custom_size=custom_size,
            size=selected_sizes,
        )

        product_details.save()

        return redirect(productsAdd)
    
    context = {
        'subcategory': data,
        'stock_availability': ['IN STOCK', 'OUT OF STOCK'],
    }

    return render(request, 'productadd2.html', context)


def Productlist(request):
    products = Product.objects.all()
    paginator = Paginator(products, 10)  # Show 10 products per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Encrypt product IDs
    for product in page_obj:
        product.encrypted_id = encrypt(str(product.id))

    context = {
        'ProductsDisplay': page_obj,
        'page_obj': page_obj,
    }

    return render(request, 'productlist.html', context)

def Productgrid(request):
    products = Product.objects.all()
    paginator = Paginator(products, 12)  # Show 12 products per page or adjust as needed

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'productgrid.html', {'page_obj': page_obj})


def Backgroundslider(request):
    if request.method == 'POST':
        product_image = request.FILES['image']
        heading1 =  request.POST['head1']
        heading2 =  request.POST['head2']
        description = request.POST['description']

        data = BackgroundSliders()
        data.image =  product_image
        data.heading1 = heading1
        data.heading2 = heading2
        data.description = description
        data.save()
    return render(request,'addparentslider.html')



def Childslider(request):
    if request.method == 'POST':
        name = request.POST['name']
        product_image = request.FILES['image']
        data = ChildSliders()
        data.name = name
        data.image =  product_image
        data.save()
    return render(request,'addchildsider.html')

def Review(request):
    reviews = Rating.objects.all()

    # Step 1: Calculate average rating for each product
    avg_ratings = Rating.objects.values('product').annotate(avg_rating=Avg('rating'))
    avg_ratings_dict = {item['product']: round(item['avg_rating']) if item['avg_rating'] is not None else 0 for item in avg_ratings}

    # Step 2: Assign average rating to each review
    for review in reviews:
        review.avg_rating = avg_ratings_dict.get(review.product_id, 0)
        print("this is rating :", review.avg_rating)

    # Step 3: Paginate the reviews
    paginator = Paginator(reviews, 5)  # Show 5 reviews per page or adjust as needed
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'reviews.html', {'page_obj': page_obj})


def upload_and_crop(request):
    form = ImageUploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return JsonResponse({'message': 'works'})
    context = {'form': form}
    return render(request, 'imagecrop.html', context)


def userlist(request):
    data=User.objects.all()
    return render(request, "users-list.html",{ 'data': data })

def neworder(request):
    order_placed_list = OrderPlaced.objects.all().order_by('-id')
    order_list = Order.objects.all().order_by('-id')



    # paginator_order_placed = Paginator(order_placed_list, 10)  # Show 10 OrderPlaced per page
    # paginator_orders = Paginator(order_list, 10)  # Show 10 Orders per page

    # page_number_order_placed = request.GET.get('page_order_placed')
    # page_number_orders = request.GET.get('page_orders')

    # page_obj_order_placed = paginator_order_placed.get_page(page_number_order_placed)
    # page_obj_orders = paginator_orders.get_page(page_number_orders)
    
    context = {
        # 'page_obj_order_placed': page_obj_order_placed,
        # 'page_obj_orders': page_obj_orders,
        'orders' : order_placed_list,
        'ordered_list' : order_list,
    }

    return render(request, "new_order.html", context)

def neworderimage(request):
    order_placed_list = ImageUpload.objects.all()
    paginator = Paginator(order_placed_list, 10)  # Show 10 orders per page.
    
    page_number = request.GET.get('page_order_placed')
    page_obj_order_placed = paginator.get_page(page_number)
    
    context = {
        'page_obj_order_placed': page_obj_order_placed,
    }

    return render(request, "imageorders.html", context)

@csrf_exempt
@require_POST
def update_order_status_two(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        delivery_date = request.POST.get('delivery_date')

        print("Order ID:", order_id)
        print("New Status:", new_status)
        print("Delivery Date:", delivery_date)

        try:
            order = ImageUpload.objects.get(id=order_id)
            order.status = new_status
            order.delivery_expected_date = delivery_date
            order.save()
            return JsonResponse({'success': True})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})



import logging
logger = logging.getLogger(__name__)

def update_order_status(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        delivery_date = request.POST.get('delivery_date')  # Extract delivery date from POST data

        try:
            order = Order.objects.get(order_id=order_id)
            order.status = new_status
            order.delivery_expected_date = delivery_date  # Update delivery date
            order.save()
            return JsonResponse({'success': True})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})

def order_detail(request):
    detail = Order.objects.latest('id')
    details = OrderPlaced.objects.all()

    context={
          'detail': detail,
          'details': details,


    }
    return render(request, 'order_detail.html',context)



def orderhistory(request):
    data = Order.objects.all()
    imageupload = ImageUpload.objects.all()
    context = {
        'data': data,
        'imageupload': imageupload
    }
    return render(request, 'order_history.html', context)

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Product
from .utils import decrypt

def ProductDetail(request, encrypted_pk):
    try:
        pk = decrypt(encrypted_pk)
        latest_product = get_object_or_404(Product, pk=pk)
    except Exception as e:
        return HttpResponse("Invalid URL", status=400)

    return render(request, 'productdetailadmin.html', {'latest_product': latest_product})


def product_edit_view(request, encrypted_product_id):
    try:
        # Decrypt the product_id
        product_id = decrypt(encrypted_product_id)
        product = get_object_or_404(Product, id=product_id)
    except Exception as e:
        # Handle decryption error or invalid ID
        return HttpResponse("Invalid URL", status=400)

    data = SubCategory.objects.all()

    if request.method == 'POST':
        try:
            print("inside POST request")
            
            # Safely retrieve files from request.FILES
            image1 = request.FILES.get('image1')
            image2 = request.FILES.get('image2')
            image3 = request.FILES.get('image3')
            image4 = request.FILES.get('image4')
            image5 = request.FILES.get('image5')
            image6 = request.FILES.get('image6')

            # Retrieve other form data
            product_name = request.POST.get('product_name', '')
            categories_id = request.POST.get('categories', '')
            availability = request.POST.get('availability', '')
            price = request.POST.get('price', '')
            description = request.POST.get('description', '')
            tags = request.POST.get('group_tag', '')
            quantity = request.POST.get('quantity', '')
            full_detail = request.POST.get('fulldetail', '')
            slug = request.POST.get('slug', '')
            custom_size = request.POST.get('customsize', '')
            admin_choice = request.POST.get('admin_choice', '')
            color1 = request.POST.get('color1', '')
            color2 = request.POST.get('color2', '')
            color3 = request.POST.get('color3', '')
            color4 = request.POST.get('color4', '')
            additional_colors = request.POST.getlist('additionalColor')
            selected_sizes = request.POST.getlist('size')

            # Retrieve cropped image data
            cropped_image_data = request.POST.get('cropped_image_data', '')
            
            # Decode base64 data and save it as a file
            if cropped_image_data:
                format, imgstr = cropped_image_data.split(';base64,') 
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f'cropped_image.{ext}')

            categories = SubCategory.objects.get(id=categories_id)

            

            if product_name:
                product.title = product_name
            if data:
                product.product_image = data
            if image1:
                product.product_image1 = image1
            if image2:
                product.product_image2 = image2
            if image3:
                product.product_image3 = image3
            if image4:
                product.product_image4 = image4
            if image5:
                product.product_image5 = image5
            if image6:
                product.product_image6 = image6
            if categories:
                product.categories = categories
            if availability:
                product.availability = availability
            if admin_choice:
                product.admin_choice = admin_choice
            if price:
                product.price = price
            if description:
                product.description = description
            if tags:
                product.product_tag = tags
            if quantity:
                product.quantity = quantity
            if full_detail:
                product.full_detail = full_detail
            if slug:
                product.slug = slug
            if color1:
                product.color1 = color1
            if color2:
                product.color2 = color2
            if color3:
                product.color3 = color3
            if color4:
                product.color4 = color4
            if additional_colors:
                product.colors = additional_colors
            if custom_size:
                product.custom_size = custom_size
            if selected_sizes:
                product.size = selected_sizes
            

            product.save()
            messages.success(request, 'Product updated successfully')
            return redirect('product_edit', encrypted_product_id=encrypted_product_id)

        except Exception as e:
            messages.error(request, "An error occurred while updating the product")
            return redirect('product_edit', encrypted_product_id=encrypted_product_id)
        

            

    context = {
        'subcategory': data,
        'product': product,
        'stock_availability': ['IN STOCK', 'OUT OF STOCK'],
        'product_id': encrypted_product_id,  # Pass the encrypted product ID to the template
        'selected_sizes': product.size if product.size else []
    }

    return render(request, 'productadd3.html', context)



def delete_item_list(request, encrypted_item_id):
    try:
        item_id = decrypt(encrypted_item_id)
        item = Product.objects.get(id=item_id)
        item.delete()
    except Exception as e:
        # Handle decryption error or item does not exist
        pass
    
    return redirect('productlist')


def delete_item_review(request, item_id):
    if request.method == 'POST':
        
        try:
            item = Rating.objects.get(id=item_id)
            item.delete()
        except Rating.DoesNotExist:
            # Handle the case where the item doesn't exist
            pass
    
        return redirect(Review)  
    return render(request, 'review.html')



def delete_item_grid(request, item_id):
    if request.method == 'POST':
        
        try:
            item = Product.objects.get(id=item_id)
            item.delete()
        except Product.DoesNotExist:
            # Handle the case where the item doesn't exist
            pass
    
        return redirect(Productgrid)  
    return render(request, 'productgrid.html')


def delete_item_sub(request, item_id):
    if request.method == 'POST':
        
        try:
            item = SubCategory.objects.get(id=item_id)
            item.delete()
        except SubCategory.DoesNotExist:
            # Handle the case where the item doesn't exist
            pass
    
        return redirect(subcategory)  
    return render(request, 'sub_category.html')



def delete_item_cate(request, item_id):
    if request.method == 'POST':
        
        try:
            item = Category.objects.get(id=item_id)
            item.delete()
        except Category.DoesNotExist:
            # Handle the case where the item doesn't exist
            pass
    
        return redirect(subcategory)  
    return render(request, 'category.html')


import logging

logger = logging.getLogger(__name__)

def sendotp(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        
        if user_email:
            try:
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
                return redirect('otpverify')  
            except Exception as e:
                logger.error(f"Error sending OTP email: {e}")
                messages.error(request, 'There was an error sending the OTP. Please try again later.')
        else:
            messages.error(request, 'Please enter a valid email address.')
    
    # If not a POST request or email is not provided, render the send OTP page
    return render(request, 'sendotp.html')

def generate_otp():
    # Generate a 6-digit OTP
    return ''.join(random.choices('0123456789', k=6))

def otpverify(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        
        # Check if OTP has expired
        if 'otp_generated_time' in request.session:
            otp_generated_time = request.session['otp_generated_time']
            if timezone.now() > otp_generated_time + timedelta(seconds=60):
                request.session.flush()
                messages.error(request, 'OTP has expired. Please request a new one.')
                # return redirect('send_otp')

        if entered_otp == stored_otp:
            return render(request, 'resetpassword.html')  
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

        # Calculate the remaining time for OTP expiration
        remaining_time = 0
        if 'otp_generated_time' in request.session:
            otp_generated_time = request.session['otp_generated_time']
            remaining_time = max(0, 60 - (timezone.now() - otp_generated_time).total_seconds())

   
    return render(request,'otpverify.html')


def resetpw(request):
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
                return redirect('login_admin')
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
                    return redirect('login_admin')
                else:
                    messages.error(request, 'User not found.')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request,'resetpassword.html')

from django.views.decorators.http import require_http_methods

# @login_required
@require_http_methods(["GET"])
def list_static_pages(request):
    static_pages = StaticPage.objects.all()
    return render(request, 'static_page_list.html', {'static_pages': static_pages})

# @login_required
@require_http_methods(["GET", "POST"])
def edit_static_page(request, page):
    static_page = get_object_or_404(StaticPage, page=page)
    if request.method == 'POST':
        static_page.content = request.POST.get('content')
        static_page.save()
        return redirect(reverse('static_page_list'))

    return render(request, 'edit_static_page.html', {'page': static_page})


# @login_required
@require_http_methods(["GET", "POST"])
def create_static_page(request):
    if request.method == 'POST':
        page_type = request.POST.get('page')
        content = request.POST.get('content')

        try:
            static_page = StaticPage.objects.create(page=page_type, content=content)
            return redirect(reverse('static_page_list'))
        except IntegrityError:
            error_message = f"The page '{page_type}' already exists."
            return render(request, 'create_static_page.html', {'error_message': error_message, 'page_type': page_type, 'content': content})

    return render(request, 'create_static_page.html')


def search_view_admin(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')

        if query:
            try:
                order = get_object_or_404(Order, order_id=query)
                order_placed = OrderPlaced.objects.filter(order=order)
                
                context = {
                    'detail': order,
                    'details': order_placed,
                }
                return render(request, 'orderdetail2.html', context)
            
            except Order.DoesNotExist:
                context = {
                    'error_message': 'Order not found.',
                }
                return render(request, 'order_detail.html', context)

    return render(request, 'order_detail.html')


def user_logout_admin(request):
    logout(request)
    return redirect('login_admin')




def admin_inquiries(request):
    inquiries = Contact.objects.all().order_by('-created_at')
    context = {
        'inquiries': inquiries,
    }
    return render(request, 'admin_inquiries.html', context)

import plotly.express as px

def sales_report(request):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    # Aggregate sales data
    daily_sales = Order.objects.filter(ordered_date__date=today).values('ordered_date__hour').annotate(total=Sum('amount')).order_by('ordered_date__hour')
    monthly_sales = Order.objects.filter(ordered_date__date__gte=start_of_month).values('ordered_date__day').annotate(total=Sum('amount')).order_by('ordered_date__day')
    yearly_sales = Order.objects.filter(ordered_date__date__gte=start_of_year).values('ordered_date__month').annotate(total=Sum('amount')).order_by('ordered_date__month')

    # Preparing Plotly graphs
    daily_fig = px.bar(
        x=[f"{hour['ordered_date__hour']}:00" for hour in daily_sales],
        y=[hour['total'] for hour in daily_sales],
        labels={'x': 'Hour of the Day', 'y': 'Total Sales'},
        title='Daily Sales'
    )
    
    monthly_fig = px.bar(
        x=[f"Day {day['ordered_date__day']}" for day in monthly_sales],
        y=[day['total'] for day in monthly_sales],
        labels={'x': 'Day of the Month', 'y': 'Total Sales'},
        title='Monthly Sales'
    )
    
    yearly_fig = px.bar(
        x=[f"Month {month['ordered_date__month']}" for month in yearly_sales],
        y=[month['total'] for month in yearly_sales],
        labels={'x': 'Month of the Year', 'y': 'Total Sales'},
        title='Yearly Sales'
    )

    context = {
        'daily_plot': daily_fig.to_html(),
        'monthly_plot': monthly_fig.to_html(),
        'yearly_plot': yearly_fig.to_html(),
    }

    return render(request, 'home.html', context)
