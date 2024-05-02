import time
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.auth import (authenticate, get_user_model, login, logout,
                                 update_session_auth_hash)
import random
from django.conf import settings
import stripe
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from Auth.models import (Booking, BrokerAccount, ContactList,
                         CustomUser, Payment, Review, Properties, Testimonials)

from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


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

        print(number, password)

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
    prpocount = Properties.objects.all().count()
    testimonials = Testimonials.objects.all()[:3]
    userCount = CustomUser.objects.all().count()
    broker = BrokerAccount.objects.all()[:3]
    agentcount = BrokerAccount.objects.all().count()
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
    return render(request, 'index.html', context)


def agentDash(request):
    properties = Properties.objects.all()[:9]
    prpocount = Properties.objects.all().count()
    testimonials = Testimonials.objects.all()[:3]
    userCount = CustomUser.objects.all().count()
    broker = BrokerAccount.objects.all()[:3]
    agentcount = BrokerAccount.objects.all().count()
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
        print(name, email, subject, message)
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
    reviews = Review.objects.filter(broker=id)
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
            broker = BrokerAccount.objects.all()[:3]
            agentcount = BrokerAccount.objects.all().count()
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
            twitterLink = request.POST.get("twitterLink")
            linkedInLink = request.POST.get("linkedInLink")
            email = f"{name.lower()}{random.randint(1000, 9999)}@gmail.com"
            agent_email = remove(email)

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
                twitterLink=twitterLink,
                linkedInLink=linkedInLink
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
                    name=name,
                    intro=intro,
                    instagramLink=instagramLink,
                    facebookLink=facebookLink,
                    twitterLink=twitterLink,
                    linkedInLink=linkedInLink,
                    is_admin=False,
                    is_agent=True,
                    agentId=agent.id
                )
                return redirect('/admin-agent-management')
            except Exception as e:
                message = "Couldn't process your request!! Please try again later."
                messages.error(request, message)
                print(e)

        allAgents = BrokerAccount.objects.all()
        context = {'allAgents': allAgents}
        return render(request, 'admin/agent-management.html', context)
    else:
        messages.error(
            request, "You are not authorized to access this page.")
        return redirect('/')


def edit_agents(request, id):
    if (request.user.is_authenticated and request.user.is_admin):
        agent = get_object_or_404(BrokerAccount, id=id)
        context = {
            'agent': agent
        }
        if request.method == 'POST':
            photo = request.FILES.get("photo")
            name = request.POST.get("name")
            intro = request.POST.get("intro")
            instagramLink = request.POST.get("instagramLink")
            facebookLink = request.POST.get("facebookLink")
            twitterLink = request.POST.get("twitterLink")
            linkedInLink = request.POST.get("linkedInLink")

            if photo is None:
                photo = agent.photo

            editQuery = BrokerAccount(id=id, photo=photo, name=name, intro=intro, instagramLink=instagramLink,
                                      facebookLink=facebookLink, twitterLink=twitterLink, linkedInLink=linkedInLink)
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
            print(request.user)
            print(properties)
            for property in properties:
                print(property.name)
            context = {"properties": properties}
            return render(request, 'agent/assigned-properties.html', context)
        else:
            messages.error(
                request, "You do not have permission to access this page.")
            if request.user.is_admin:
                return redirect('/')
            else:
                return redirect('.admin-page')
    else:
        messages.error(
            request, "You must be logged in to access this page.")
        return redirect('/login')


def booking_management(request):
    bookings_sale = Booking.objects.all()
    context = {
        'bookings': bookings_sale
    }
    return render(request, 'admin/booking-management.html', context)


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
            print(image, name, description, intro)

            test_obj = Testimonials(
                image=image,
                name=name,
                description=description,
                intro=intro
            )
            print(test_obj)

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
        brokers = BrokerAccount.objects.all()
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

            broker = BrokerAccount.objects.get(pk=broker_id)

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
            print(request.POST.get("rent"))
            property_obj.type = request.POST.get("rent")
            print(property_obj.type)
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
        agent_delete = get_object_or_404(BrokerAccount, pk=id)
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
    context = {
        'bookings': user_bookings
    }
    return render(request, 'bookings.html', context)


stripe.api_key = 'sk_test_51P1lOZ06ho0W5mPfHhr4drqVtm8P1AwXs4vaJc5fuG5lJdCiZSPWusgTNVFBIVqpTOHXCX2zUAJe3rF4RBlcIPUY00kiP8S4oq'


def booking(request):
    if request.method == 'POST':
        property_id = request.POST.get('property')
        date = request.POST.get('date')
        note = request.POST.get('note')

        if request.user.is_authenticated:
            property_instance = get_object_or_404(
                Properties, id=property_id)

            if (Booking.objects.filter(date=date).exists()):
                message = "This property has been booked for this date"
                messages.error(request, message)
                return redirect('/singleproperty/' + str(property_id))

            request.session['property'] = property_id
            request.session['date'] = date
            request.session['note'] = note

            try:
                property_instance = get_object_or_404(Properties, id=property_id)
                price = stripe.Price.create(
                    unit_amount=property_instance.price,
                    currency='usd',
                    product='prod_PrXMqQakxRxCcx',
                    recurring=None,
                )

                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[
                        {
                            'price': price.id,
                            'quantity': 1
                        }
                    ],
                    mode='payment',
                    customer_creation='always',
                    success_url='http://127.0.0.1:8000/payment_successful?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url='http://127.0.0.1:8000/payment_cancelled?session_id={CHECKOUT_SESSION_ID}',
                )
                return redirect(checkout_session.url, code=303)
            except Exception as e:
                messages.error(
                    request, "Couldn't process your request!! Please try again later.")
                print(e)
                return redirect('/booking')
    return render(request, 'booking_page.html')

        #     booking = Booking(
        #         user=request.user, property=property_instance, date=date, note=note)
        #     booking.status = 'Confirmed'
        #     booking.save()

        #     message = "Booking added successfully!!"
        #     messages.success(request, message)
        #     return redirect('/properties')
        # else:
        #     message = "User is not authenticated"
        #     messages.error(request, message)
        #     return redirect('/login')


def payment_successful(request):
    checkout_session_id = request.GET.get('session_id', None)
    print(request.session.get('property'))
    property_id = request.session.get('property')
    date = request.session.get('date')
    note = request.session.get('note')

    try:
        session = stripe.checkout.Session.retrieve(checkout_session_id)
        customer = stripe.Customer.retrieve(session.customer)
        with transaction.atomic():
            user_payment = Payment.objects.create(
                user=request.user,
                payment_bool=True,
                stripe_checkout_id=checkout_session_id
            )
            user_payment.save()

            property_instance = get_object_or_404(Properties, id=property_id)
            print(property_instance)
            booking = Booking.objects.create(
                user=request.user,
                property=property_instance,
                date=date,
                note=note,
                isPaid=True
            )
            booking.save()
    except Exception as e:
        print(e)
        messages.error(
            request, "Payment unsuccessful. Please try again later.")
        return redirect('/bookinglist')

    messages.success(request, "Payment successful. Your booking is confirmed.")
    return redirect('/bookinglist')


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


def review_agent(request, property_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            property = Properties.objects.get(id=property_id)
            agentId = property.broker_id
            print(agentId)
            if Booking.objects.filter(user=request.user, property_id=property_id, status='Confirmed').exists():
                rating = request.POST.get('rating')
                comment = request.POST.get('comment')

                if Review.objects.filter(user=request.user, broker=agentId).exists():
                    messages.error(
                        request, 'You have already submitted a review for this broker.')
                else:
                    review = Review(
                        broker_id=agentId, user=request.user, rating=rating, comment=comment)
                    review.save()
                    messages.success(request, 'Review submitted successfully.')
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
            print(details.id)
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
