import time
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.auth import (authenticate, get_user_model, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
import random
from django.conf import settings
import stripe
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from Auth.models import (Booking, BrokerAccount, ContactList,
                         CustomUser, Payment, Review, Properties, SellingProperties, Testimonials)

from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import secrets
import string
from django.core.mail import send_mail

import requests


def initiate_payment(user_id, property, price, property_id, date, note):
    url = "https://a.khalti.com/api/v2/epayment/initiate/"

    payload = json.dumps({
        "return_url": f"http://localhost:8000/payment_successful?user_id={user_id}",
        "website_url": "http://localhost:8000/",
        "amount": price,
        "purchase_order_id": property_id,
        "purchase_order_name": "Property rent",
        "customer_info": {
            "name": "Realstate",
            "email": "test@khalti.com",
            "phone": "9800000001",
        },
        "merchant_property_id": property_id,
        "merchant_date": date,
        "merchant_note": note
    })
    headers = {
        'Authorization': 'key 37ac1d14b13a48d2b2a153a4046b1c32',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        response_data = response.json()

        if response_data.get('payment_url'):
            return {"url": response_data.get('payment_url'), "success": True}
        else:
            return {"success": False, "message": "Failed to get payment URL."}

    except requests.RequestException as e:
        return {"success": False, "message": str(e)}


def user_login(request):
    if request.user.is_authenticated:
        messages.error(request, 'You are already logged in.')
        if request.user.is_admin:
            return redirect('/admin-page')
        else:
            return redirect('/')

    if request.method == 'POST':
        number = request.POST.get('number')
        password = request.POST.get('password')

        # print(number, password)

        user = authenticate(request, username=number, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')

            if user.is_admin:
                return redirect('admin-page')
            elif user.is_agent:
                return redirect('/')
            else:
                return redirect('/')
        else:
            messages.error(request, 'Invalid login credentials.')

    return render(request, 'login.html')


def register(request):
    if request.user.is_authenticated:
        messages.error(request, 'You are already logged in.')
        if request.user.is_admin:
            return redirect('/admin-page')
        return redirect('/')

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        number = request.POST['number']
        password = request.POST['password']

        isUser = CustomUser.objects.filter(number=number).exists()
        isEmail = CustomUser.objects.filter(email=email).exists()

        if (isUser):
            messages.error(request, 'User already exists.')
            return redirect('register')
        if (isEmail):
            messages.error(request, 'Email already exists.')
            return redirect('register')

        User = get_user_model()

        user = User.objects.create_user(
            username=number, email=email, password=password)
        user.name = name
        user.number = number
        user.save()

        messages.success(
            request, 'Registration successful. You can now log in.')
        return redirect('login')

    return render(request, 'register.html')


def dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            messages.error(
                request, "You do not have permission to access this page.")
            return redirect('admin-page')
    properties = Properties.objects.filter(type="Sale", is_archived=False)[:9]
    propertiesrent = Properties.objects.filter(
        type="Rent", is_archived=False)[:9]
    prpocount = Properties.objects.all().count()
    testimonials = Testimonials.objects.all()[:3]
    userCount = CustomUser.objects.all().count()
    broker = CustomUser.objects.filter(is_agent=True)[:3]
    agentcount = CustomUser.objects.filter(is_agent=True).count()
    boughtprpo = Booking.objects.all().count()

    location = ''
    searchDetails = None
    if request.method == 'POST':
        location = request.POST['location']
        searchDetails = Properties.objects.filter(location__contains=location)
    context = {
        'properties': properties,
        "propertiesrent": propertiesrent,
        'testimonials': testimonials,
        'broker': broker,
        'location': location,
        'searchDetails': searchDetails,
        "prpocount": prpocount,
        "userCount": userCount,
        "agentcount": agentcount,
        "boughtprpo": boughtprpo
    }
    return render(request, 'index.html', context)


def agentDash(request):
    properties = Properties.objects.all()[:9]
    prpocount = Properties.objects.all().count()
    testimonials = Testimonials.objects.all()[:3]
    userCount = CustomUser.objects.all().count()
    broker = CustomUser.objects.filter(is_agent=True)[:3]
    agentcount = CustomUser.objects.filter(is_agent=True).count()
    boughtprpo = Booking.objects.all().count()

    location = ''
    searchDetails = None
    if request.method == 'POST':
        location = request.POST['location']
        searchDetails = Properties.objects.filter(location__contains=location)
    context = {
        'properties': properties,
        'testimonials': testimonials,
        'broker': broker,
        'location': location,
        'searchDetails': searchDetails,
        "prpocount": prpocount,
        "userCount": userCount,
        "agentcount": agentcount,
        "boughtprpo": boughtprpo
    }
    return render(request, 'agent/agent_dashboard.html', context)


def contact(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            messages.error(
                request, "You do not have permission to access this page.")
            return redirect('admin-page')

    if request.method == 'POST':
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        query = ContactList(name=name, email=email,
                            subject=subject, message=message)
        # print(name, email, subject, message)
        try:
            query.save()
            message = "Received your message!! We will contact you shortly."
            messages.success(request, message)
            return redirect('/contact')
        except Exception as e:
            message = "Couldn't process your request!! Please try again later."
            messages.error(request, message)
            print(e)
    return render(request, 'contact.html')


def singleProperty(request, id):
    if request.user.is_authenticated:
        if request.user.is_admin:
            messages.error(
                request, "You do not have permission to access this page.")
            return redirect('admin-page')
    details = get_object_or_404(Properties, id=id)
    brokerId = details.broker_id
    reviews = Review.objects.filter(broker=brokerId)
    return render(request, 'property-single.html', {'details': details, 'reviews': reviews})


def services(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            messages.error(
                request, "You do not have permission to access this page.")
            return redirect('admin-page')
    testimonials = Testimonials.objects.all()[:6]
    return render(request, 'services.html', {'testimonials': testimonials})


def calculate_land_area(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            messages.error(
                request, "You do not have permission to access this page.")
            return redirect('admin-page')
    testimonials = Testimonials.objects.all()[:6]
    return render(request, 'calculator.html',)


def properties(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            messages.error(
                request, "You do not have permission to access this page.")
            return redirect('admin-page')
    properties = Properties.objects.filter(type="Rent", is_archived=False)
    # featuredProperties = Properties.objects.all()[:9]
    context = {
        'properties': properties,
        # 'featuredProperties': featuredProperties,
    }
    return render(request, 'properties.html', context)


def about(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            messages.error(
                request, "You do not have permission to access this page.")
            return redirect('admin-page')
    testimonials = Testimonials.objects.all()[:3]
    context = {
        'testimonials': testimonials
    }

    return render(request, 'about.html', context)


def adminPage(request):
    if (request.user.is_authenticated):
        if request.user.is_admin:
            properties = Properties.objects.all()[:9]
            prpocount = Properties.objects.all().count()
            testimonials = Testimonials.objects.all()[:3]
            userCount = CustomUser.objects.all().count()
            broker = CustomUser.objects.filter(is_agent=True)[:3]
            agentcount = CustomUser.objects.filter(is_agent=True).count()
            boughtprpo = Booking.objects.all().count()
            seven_days_ago = datetime.now() - timedelta(days=7)
            user_count_last_7_days = CustomUser.objects.filter(
                created_at=seven_days_ago).count()

            # Get active users based on login activities in the last 7 days
            # active_users = CustomUser.objects.filter(last_login=seven_days_ago).distinct()
            # active_user_count = active_users.count()
            active_user_count = CustomUser.objects.filter(
                is_active=True).count()

            context = {
                'properties': properties,
                'testimonials': testimonials,
                'broker': broker,
                "prpocount": prpocount,
                "userCount": userCount,
                "agentcount": agentcount,
                "boughtprpo": boughtprpo,
                "active_user_count": active_user_count,
                "user_count_last_7_days": user_count_last_7_days
            }

            return render(request, 'admin/admin-panel.html', context)
    else:
        messages.error(
            request, "You do not have permission to access this page.")
        return redirect('dashboard')


def csrf_failure_view(request, reason=""):
    return render(request, 'csrf_failure.html', {'reason': reason})


def remove(string):
    return string.replace(" ", "")


def enquiryProperty(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            allEnquiries = ContactList.objects.all()
            context = {
                'allEnquiries': allEnquiries
            }
            return render(request, 'admin/enquiry-management.html', context)
        else:
            messages.error(
                request, "You do not have permission to access this page.")
            return redirect('/')


def agentManagement(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            photo = request.FILES.get("photo")
            name = request.POST.get("name")
            number = request.POST.get("number")
            intro = request.POST.get("intro")
            instagramLink = request.POST.get("instagramLink")
            facebookLink = request.POST.get("facebookLink")
            email = f"{name.lower()}{random.randint(1000, 9999)}@gmail.com"
            agent_email = remove(email)
            print(photo)

            agent_password = "password123"

            if BrokerAccount.objects.filter(number=number).exists():
                messages.error(request, "Number already exists")
                return redirect('/admin-agent-management')

            agent = BrokerAccount.objects.create(
                photo=photo,
                name=name,
                number=number,
                intro=intro,
                instagramLink=instagramLink,
                facebookLink=facebookLink,
            )
            message = "Agent added successfully!!"
            messages.success(request, message)

            User = get_user_model()
            try:
                if User.objects.filter(number=number).exists():
                    messages.error(request,
                                   "User already exists")

                new_user = User.objects.create_user(
                    username=number,
                    number=number,
                    email=agent_email,
                    password=agent_password,
                    image=photo,
                    name=name,
                    intro=intro,
                    instagramLink=instagramLink,
                    facebookLink=facebookLink,
                    is_admin=False,
                    is_agent=True,
                    agentId=agent.id
                )
                print(new_user)
                return redirect('/admin-agent-management')
            except Exception as e:
                message = "Couldn't process your request!! Please try again later."
                messages.error(request, message)
                print(e)

        allAgents = CustomUser.objects.filter(is_agent=True)
        context = {'allAgents': allAgents}
        return render(request, 'admin/agent-management.html', context)
    else:
        messages.error(
            request, "You are not authorized to access this page.")
        return redirect('/')


def edit_agents(request, id):
    if (request.user.is_authenticated and request.user.is_admin):
        agent = get_object_or_404(CustomUser, id=id)
        context = {
            'agent': agent
        }
        if request.method == 'POST':
            photo = request.FILES.get("photo")
            name = request.POST.get("name")
            intro = request.POST.get("intro")
            instagramLink = request.POST.get("instagramLink")
            facebookLink = request.POST.get("facebookLink")

            if photo is None:
                photo = agent.photo

            editQuery = CustomUser(id=id, photo=photo, name=name, intro=intro, instagramLink=instagramLink,
                                   facebookLink=facebookLink)
            editQuery.save()
            messages.success(request, "Agent Edited Successfully !!!")

            return redirect("/admin-agent-management")

        return render(request, 'admin/agent-edit.html', context)
    else:
        messages.error(
            request, "You do not have permission to access this page.")
        return redirect('dashboard')


def edit_testimonial(request, id):
    if (request.user.is_authenticated and request.user.is_admin):
        details = get_object_or_404(Testimonials, id=id)

        if request.method == 'POST':
            image = request.FILES.get("image")
            name = request.POST.get("name")
            intro = request.POST.get("intro")
            description = request.POST.get("description")

            try:
                if image is None:
                    image = details.image

                editQuery = Testimonials(
                    id=id, image=image, name=name, intro=intro, description=description)
                editQuery.save()
                message = "Testimonial edited successfully"
                messages.success(request, message)
                return redirect('/admin-testimonial')
            except Exception as e:
                message = "Couldn't edit property. Please try again later."
                messages.error(request, message)
                print(e)

        return render(request, 'admin/testimonial-edit.html', {'testi': details})
    else:
        messages.error(
            request, "You do not have permission to access this page.")
        return redirect('dashboard')


def assignedToagent(request):
    if request.user.is_authenticated:
        if request.user.is_agent:
            properties = Properties.objects.filter(
                broker_id=request.user.agentId)
            # print(request.user)
            # print(properties)
            # for property in properties:
            # print(property.name)
            context = {"properties": properties}
            return render(request, 'agent/assigned-properties.html', context)
        else:
            messages.error(
                request, "You do not have permission to access this page.")
            if request.user.is_admin:
                return redirect('/')
            else:
                return redirect('admin-page')
    else:
        messages.error(
            request, "You must be logged in to access this page.")
        return redirect('/login')


def booking_management(request):
    if (request.user.is_authenticated and request.user.is_admin):

        bookings_sale = Booking.objects.all()
        context = {
            'bookings': bookings_sale
        }
        return render(request, 'admin/booking-management.html', context)
    else:
        messages.error(
            request, "You do not have permission to access this page.")
        return redirect('dashboard')


def rent_management(request):
    bookings_sale = Booking.objects.all()
    context = {
        'bookings': bookings_sale
    }
    return render(request, 'admin/rental-management.html', context)


def admin_testimonial(request):
    if (request.user.is_authenticated and request.user.is_admin):
        testimonials = Testimonials.objects.all()
        context = {
            'testimonials': testimonials,
        }
        if request.method == 'POST':
            image = request.FILES.get("image")
            name = request.POST.get("name")
            description = request.POST.get("description")
            intro = request.POST.get("intro")
            # print(image, name, description, intro)

            test_obj = Testimonials(
                image=image,
                name=name,
                description=description,
                intro=intro
            )
            # print(test_obj)

            try:
                test_obj.save()
                message = "Testimonial added successfully"
                messages.success(request, message)
                return redirect('/admin-testimonial')
            except Exception as e:
                message = "Couldn't add Testimonial. Please try again later."
                messages.error(request, message)
                print(e)

        return render(request, 'admin/admin-testimonial.html', context)
    else:
        messages.error(
            request, "You do not have permission to access this page.")
        return redirect('dashboard')


def adminProperty(request):
    if (request.user.is_authenticated and request.user.is_admin):
        brokers = CustomUser.objects.filter(is_agent=True)
        properties = Properties.objects.all()
        context = {
            'properties': properties,
            'brokers': brokers,
        }

        if request.method == 'POST':
            image = request.FILES.get("image")
            imageTwo = request.FILES.get("imageTwo")
            imageThree = request.FILES.get("imageThree")
            broker_id = request.POST.get("broker")
            type = request.POST.get("rent")
            name = request.POST.get("name")
            location = request.POST.get("location")
            beds = request.POST.get("beds")
            baths = request.POST.get("baths")
            price = request.POST.get("price")
            description = request.POST.get("description")
            latitude = request.POST.get("latitude")
            longitude = request.POST.get("longitude")

            broker = CustomUser.objects.get(pk=broker_id)

            property_obj = Properties(
                image=image,
                imageTwo=imageTwo,
                imageThree=imageThree,
                broker=broker,
                type=type,
                name=name,
                location=location,
                beds=beds,
                baths=baths,
                price=price,
                description=description,
                latitude=latitude,
                longitude=longitude
            )

            try:
                property_obj.save()
                message = "Property added successfully"
                messages.success(request, message)
                return redirect('/admin-property-management')
            except Exception as e:
                message = "Couldn't add property. Please try again later."
                messages.error(request, message)
                print(e)

        return render(request, 'admin/property-management.html', context)
    else:
        messages.error(
            request, "You do not have permission to access this page.")
        return redirect('dashboard')


def adminSellerProperty(request):
    if (request.user.is_authenticated and request.user.is_admin):
        properties = SellingProperties.objects.all()
        context = {
            'properties': properties,
        }

        return render(request, 'admin/admin-seller-property.html', context)
    else:
        messages.error(
            request, "You do not have permission to access this page.")
        return redirect('dashboard')


def adminSaveSellerProperty(request, property_id):
    if (request.user.is_authenticated and request.user.is_admin):
        details = get_object_or_404(SellingProperties, id=property_id)

        properties = Properties.objects.all()
        brokers = CustomUser.objects.filter(is_agent=True)
        context = {
            'properties': properties,
            'brokers': brokers,
            'details': details
        }

        if request.method == 'POST':
            image = details.image
            imageTwo = details.imageTwo
            imageThree = details.imageThree
            broker_id = request.POST.get("broker")
            type = request.POST.get("rent")
            name = request.POST.get("name")
            location = request.POST.get("location")
            beds = request.POST.get("beds")
            baths = request.POST.get("baths")
            price = request.POST.get("price")
            description = request.POST.get("description")
            latitude = request.POST.get("latitude")
            longitude = request.POST.get("longitude")

            broker = CustomUser.objects.get(pk=broker_id)

            property_obj = Properties(
                image=image,
                imageTwo=imageTwo,
                imageThree=imageThree,
                broker=broker,
                type=type,
                name=name,
                location=location,
                beds=beds,
                baths=baths,
                price=price,
                description=description,
                latitude=latitude,
                longitude=longitude
            )

            try:
                property_obj.save()
                property_objd = get_object_or_404(
                    SellingProperties, pk=property_id)
                property_objd.delete()
                message = "Property added successfully"
                messages.success(request, message)
                return redirect('/admin-property-management')
            except Exception as e:
                message = "Couldn't add property. Please try again later."
                messages.error(request, message)
                print(e)

        return render(request, 'admin/add-seller-property.html', context)
    else:
        messages.error(
            request, "You do not have permission to access this page.")
        return redirect('dashboard')


def editProperty(request, property_id):
    if (request.user.is_authenticated and request.user.is_admin):
        details = get_object_or_404(Properties, id=property_id)

        if request.method == 'POST':
            property_obj = Properties.objects.get(pk=property_id)

            if 'image' in request.FILES:
                property_obj.image = request.FILES.get("image")
            if 'imageTwo' in request.FILES:
                property_obj.imageTwo = request.FILES.get("imageTwo")
            if 'imageThree' in request.FILES:
                property_obj.imageThree = request.FILES.get("imageThree")

            property_obj.name = request.POST.get("name")
            # print(request.POST.get("rent"))
            property_obj.type = request.POST.get("rent")
            # print(property_obj.type)
            property_obj.location = request.POST.get("location")
            property_obj.beds = request.POST.get("beds")
            property_obj.baths = request.POST.get("baths")
            property_obj.price = request.POST.get("price")
            property_obj.description = request.POST.get("description")
            property_obj.latitude = request.POST.get("latitude")
            property_obj.longitude = request.POST.get("longitude")

            try:
                # Save the updated property
                property_obj.save()

                message = "Property edited successfully"
                messages.success(request, message)
                return redirect('/admin-property-management')
            except Exception as e:
                message = "Couldn't edit property. Please try again later."
                messages.error(request, message)
                print(e)

        return render(request, 'admin/edit-property.html', {'details': details})
    else:
        messages.error(
            request, "You do not have permission to access this page.")
        return redirect('dashboard')


def deleteProperty(request, property_id):
    if (request.user.is_authenticated and request.user.is_admin):
        property_obj = get_object_or_404(Properties, pk=property_id)
        property_obj.delete()
        message = "Property deleted successfully"
        messages.success(request, message)
        return redirect('/admin-property-management')
    else:
        messages.error(
            request, "You do not have permission to access this page.")
        return redirect('dashboard')


def delete_agent(request, id):
    if (request.user.is_authenticated and request.user.is_admin):
        agent_delete = get_object_or_404(CustomUser, id=id)
        agent_delete.delete()
        message = "Agent deleted successfully"
        messages.success(request, message)
        return redirect('/admin-agent-management')
    else:
        messages.error(
            request, "You do not have permission to access this page.")
        return redirect('dashboard')


def user_delete_booking(request, id):
    booking_delete = get_object_or_404(Booking, pk=id)
    booking_delete.delete()
    message = "Booking deleted successfully"
    messages.success(request, message)
    return redirect('/bookinglist')


def admin_delete_booking(request, id):
    if (request.user.is_authenticated and request.user.is_admin):
        booking_delete = get_object_or_404(Booking, pk=id)
        booking_delete.delete()
        message = "Booking deleted successfully"
        messages.success(request, message)
        return redirect('/admin-teams-management')
    else:
        messages.error(
            request, "You do not have permission to access this page.")
        return redirect('dashboard')


def admin_delete_test(request, id):
    if (request.user.is_authenticated and request.user.is_admin):
        delete_test = get_object_or_404(Testimonials, pk=id)
        delete_test.delete()
        message = "Testimonial deleted successfully"
        messages.success(request, message)
        return redirect('/admin-testimonial')
    else:
        messages.error(
            request, "You do not have permission to access this page.")
        return redirect('dashboard')


def bookinglist(request):
    user = request.user.id
    user_bookings = Booking.objects.filter(user=user)
    for bk in user_bookings:
        print(bk.property.type)

    context = {
        'bookings': user_bookings
    }
    return render(request, 'bookings.html', context)


stripe.api_key = 'sk_test_51P1lOZ06ho0W5mPfHhr4drqVtm8P1AwXs4vaJc5fuG5lJdCiZSPWusgTNVFBIVqpTOHXCX2zUAJe3rF4RBlcIPUY00kiP8S4oq'


def booking(request):
    if request.method == 'POST':
        property_id = request.POST.get('property')
        property_type = request.POST.get('property_type')
        # print(property_id, property_type)
        date = request.POST.get('date')
        note = request.POST.get('note')

        if request.user.is_authenticated:
            property_instance = get_object_or_404(
                Properties, id=property_id)

            if (Booking.objects.filter(date=date).exists()):
                message = "This property has been booked for this date"
                messages.error(request, message)
                return redirect('/singleproperty/' + str(property_id))
            if (property_type == 'Sale'):
                property_instance = get_object_or_404(
                    Properties, id=property_id)

                booking = Booking(
                    user=request.user, property=property_instance, date=date, note=note, isPaid=False)
                booking.status = 'Confirmed'
                booking.save()

                message = "Booking added successfully!!"
                messages.success(request, message)
                return redirect('bookinglist')

            else:
                request.session['property'] = property_id
                request.session['date'] = date
                request.session['note'] = note
                user_id = request.user.id

                print("\nuser_id\n", user_id)

                try:
                    property_instance = get_object_or_404(
                        Properties, id=property_id)

                    price = int(property_instance.price) * 100
                    # print(price)

                    initiate_data = initiate_payment(
                        user_id, property_instance, price, property_id, date, note)
                    if initiate_data.get('success'):
                        return redirect(initiate_data.get('url'))
                    else:
                        messages.error(
                            request, "Couldn't process your request!! Please try again later.")
                        return redirect('/booking')
                except Exception as e:
                    messages.error(
                        request, "Couldn't process your request!! Please try again later.")
                    print(e)
                    return redirect('/booking')
    return render(request, 'booking_page.html')


def payment_successful(request):
    data = request.GET
    user = request.user
    # print("\ndata\n", data)
    # print("\nuser\n", user)

    if data.get('status') == "Completed":
        try:
            property_id = data.get("property_id")
            date = data.get("date")
            note = data.get("note")
            txn_id = data.get("tidx")

            # Ensure the user is authenticated and is a valid instance of CustomUser
            if user.is_authenticated:
                user_payment = Payment.objects.create(
                    user=user,
                    payment_bool=True,
                    txnId=txn_id
                )
                user_payment.save()

                property_instance = get_object_or_404(
                    Properties, id=property_id)

                booking = Booking.objects.create(
                    user=user,
                    property=property_instance,
                    date=date,
                    note=note,
                    isPaid=True,
                    status='Confirmed'
                )
                booking.save()

                property_instance.is_archived = True
                property_instance.save()

                messages.success(
                    request, "Payment successful. Your booking is confirmed.")
                return redirect('/bookinglist')
            else:
                messages.error(request, "User not authenticated.")
                return redirect('login')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('/')

    messages.error(request, "Payment not completed.")
    return redirect('/')


def payment_cancelled(request):
    return render(request, 'index.html')


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
    time.sleep(10)
    payload = request.body
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, settings.STRIPE_WEBHOOK_SECRECT_TEST
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id', None)
        time.sleep(15)
        user_payment = Payment.objects.get(stripe_checkout_id=session_id)
        line_items = stripe.checkout.Session.list_line_items(
            session_id, limit=1)
        user_payment.payment_bool = True
        user_payment.save()
        return HttpResponse(status=200)


def user_logout(request):
    logout(request)
    return redirect('/login')


def profile(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            name = request.POST.get('name')
            email = request.POST.get('email')
            number = request.POST.get('number')
            user.name = name
            user.email = email
            user.number = number
            if request.FILES.get("image"):
                user.image = request.FILES.get("image")
            user.save()
            messages.success(
                request, "Your Profile has been updated successfully")
            return redirect('/profile_page')
        else:
            messages.error(request, "Something went wrong")
            return redirect('/login')

    if request.user.is_authenticated:
        user = request.user
        image = user.image
        name = user.name
        email = user.email
        number = user.number
        context = {
            'image': image,
            'name': name,
            'email': email,
            'number': number
        }
        return render(request, 'profile.html', context)
    return render(request, 'profile.html')


def sellProperty(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            name = request.POST.get('name')
            location = request.POST.get('location')
            beds = request.POST.get('beds')
            baths = request.POST.get('baths')
            price = request.POST.get('price')
            description = request.POST.get('description')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            image = request.FILES.get('image')
            imageTwo = request.FILES.get('imageTwo')
            imageThree = request.FILES.get('imageThree')

            property = SellingProperties(
                name=name,
                location=location,
                beds=beds,
                baths=baths,
                price=price,
                description=description,
                latitude=latitude,
                longitude=longitude,
                image=image,
                imageTwo=imageTwo,
                imageThree=imageThree,
            )
            property.save()
            messages.success(
                request, 'Property sent to admin for verification.')
            return redirect('/')
        else:
            messages.error(request, 'You must log in first.')
            return redirect('/login')

    return render(request, 'sell_property.html')


def changepassword(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not request.user.check_password(current_password):
                return render(request, 'changepassword.html', {'error_message': 'Current password is incorrect'})

            if new_password != confirm_password:
                return render(request, 'changepassword.html', {'error_message': 'New password and confirm password do not match'})

            # Set the new password for the user
            request.user.set_password(new_password)
            request.user.save()

            # Update session to prevent user from being logged out due to password change
            update_session_auth_hash(request, request.user)

            return redirect('/profile_page')

    return render(request, 'changepassword.html')


def review_agent(request, broker_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            property_id = request.POST.get('property_id')
            property = get_object_or_404(Properties, id=property_id)
            print("\n review Agenenaljgsglk \n", broker_id)
            if Booking.objects.filter(user=request.user, property_id=property_id, status='Confirmed').exists():
                rating = request.POST.get('rating')
                comment = request.POST.get('comment')

                if Review.objects.filter(user=request.user, broker=broker_id).exists():
                    messages.error(
                        request, 'You have already submitted a review for this broker.')
                else:
                    review = Review(
                        broker_id=broker_id, user=request.user, rating=rating, comment=comment)
                    review.save()
                    messages.success(request, 'Review submitted successfully.')
                    print("\n review Agenenaljgsglk \n", review)
            else:
                messages.error(request, 'You must book this property first.')
        else:
            messages.error(request, 'You must log in first.')
            return redirect('/login')

        return redirect('/singleproperty/' + str(property_id))
    else:
        property = Properties.objects.get(id=property_id)
        return render(request, 'property.html', {'property': property})


def error_view(request, exception=None):
    error_message = str(exception) if exception else "An error occurred."
    return render(request, 'error.html', {'error_message': error_message}, status=404)


def properties_booked(request, id):
    if request.user.is_authenticated:
        if request.user.is_agent:
            details = get_object_or_404(Properties, id=id)
            # print(details.id)
            bookings = Booking.objects.filter(property_id=details.id)
            return render(request, 'agent/agent-single-property.html', {'details': details, "bookings": bookings})
        else:
            messages.error(
                request, "You do not have permission to access this page.")
            if request.user.is_admin:
                return redirect('admin-page')
            else:
                return redirect('/')
    else:
        return redirect('/login')


@csrf_exempt
def update_is_archived(request, property_id):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)
            is_archived = request_data.get('is_archived', False)
            property = get_object_or_404(Properties, id=property_id)
            property.is_archived = is_archived
            property.save()
            return JsonResponse({'success': True, 'is_archived': property.is_archived})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


def forgotpassword(request):
    if request.method == 'POST':
        reset_email = request.POST.get('resetemail')
        try:
            user = CustomUser.objects.get(email=reset_email)
        except CustomUser.DoesNotExist:
            user = None

        if user:
            random_password = ''.join(secrets.choice(
                string.ascii_letters + string.digits + string.punctuation) for _ in range(12))
            user.set_password(random_password)
            user.save()

            message = f'Your new password: {random_password}'
            send_mail(
                'Password Reset',
                message,
                'avicekbhatta.321@gmail.com',
                [reset_email],
                fail_silently=False
            )
            messages.success(
                request, 'Password reset successful. Check your email for the new password.')
            return redirect('login')
        else:
            return render(request, 'forgotpassword.html', {'error': True})

    return render(request, 'forgotpassword.html')
