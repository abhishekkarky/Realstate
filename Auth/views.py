from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from Auth.models import (Booking, BrokerAccount, ContactList, CustomUser,
                         Properties, Testimonials)

def user_login(request):
    if request.method == 'POST':
        number = request.POST['number']
        password = request.POST['password']

        user = authenticate(request, username=number, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('/')
        else:
            messages.error(request, 'Invalid login credentials.')

    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        number = request.POST['number']
        password = request.POST['password']           

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

# @login_required


def dashboard(request):
    properties = Properties.objects.all()[:9]
    testimonials = Testimonials.objects.all()[:3]
    broker = BrokerAccount.objects.all()[:3]
    context = {
        'properties': properties,
        'testimonials': testimonials,
        'broker': broker
    }
    return render(request, 'index.html', context)

# @login_required


def contact(request):
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

# @login_required


def singleProperty(request, id):
    details = get_object_or_404(Properties, id=id)
    return render(request, 'property-single.html', {'details': details})

# @login_required


def services(request):
    testimonials = Testimonials.objects.all()[:6]
    return render(request, 'services.html', {'testimonials': testimonials})

# @login_required


def properties(request):
    properties = Properties.objects.all()
    featuredProperties = Properties.objects.all()[:9]
    context = {
        'properties': properties,
        'featuredProperties': featuredProperties,
    }
    return render(request, 'properties.html', context)

# @login_required

def about(request):
    return render(request, 'about.html')

def adminPage(request):
    return render(request, 'admin/admin-panel.html')

def enquiryProperty(request):
    allEnquiries = ContactList.objects.all()
    context = {
        'allEnquiries': allEnquiries
    }
    return render(request, 'admin/enquiry-management.html', context)


def agentManagement(request):
    if request.method == 'POST':
        photo = request.FILES.get("photo")
        name = request.POST.get("name")
        intro = request.POST.get("intro")
        instagramLink = request.POST.get("instagramLink")
        facebookLink = request.POST.get("facebookLink")
        twitterLink = request.POST.get("twitterLink")
        linkedInLink = request.POST.get("linkedInLink")
        query = BrokerAccount(photo=photo , name=name, intro=intro, instagramLink=instagramLink,facebookLink=facebookLink, twitterLink=twitterLink, linkedInLink=linkedInLink)   
        print(photo, name, intro, instagramLink, facebookLink, twitterLink, linkedInLink)
        try:
            query.save()
            message = "Agent added successfully!!"
            messages.success(request, message)
            return redirect('/admin-agent-management')
        except Exception as e:
            message = "Couldn't process your request!! Please try again later."
            messages.error(request, message)
            print(e)
            
           
    allAgents = BrokerAccount.objects.all()
    context = {
        'allAgents': allAgents
    }
            
    return render(request, 'admin/agent-management.html',context)

    
def edit_agents(request,id):
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

        editQuery = BrokerAccount(id=id, photo=photo, name=name, intro=intro, instagramLink=instagramLink,facebookLink=facebookLink, twitterLink=twitterLink, linkedInLink=linkedInLink)
        editQuery.save()
        messages.success(request, "Agent Edited Successfully !!!")

        return redirect("admin-agent-management")


    return render(request, 'admin/agent-edit.html', context)

def teamsManagement(request):
    return render(request, 'admin/teams-management.html')

def adminProperty(request):
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
        name = request.POST.get("name")
        location = request.POST.get("location")
        beds = request.POST.get("beds")
        baths = request.POST.get("baths")
        price = request.POST.get("price")
        description = request.POST.get("description")
        
        broker = BrokerAccount.objects.get(pk=broker_id)

        property_obj = Properties(
            image=image,
            imageTwo=imageTwo,
            imageThree=imageThree,
            broker=broker,
            name=name,
            location=location,
            beds=beds,
            baths=baths,
            price=price,
            description=description
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

def editProperty(request, property_id):
    details = get_object_or_404(Properties, id=property_id)
    
    if request.method == 'POST':
        # Retrieve existing property instance
        property_obj = Properties.objects.get(pk=property_id)
        
        # Update fields with new values
        property_obj.image = request.FILES.get("image")
        property_obj.imageTwo = request.FILES.get("imageTwo")
        property_obj.imageThree = request.FILES.get("imageThree")
        property_obj.name = request.POST.get("name")
        property_obj.location = request.POST.get("location")
        property_obj.beds = request.POST.get("beds")
        property_obj.baths = request.POST.get("baths")
        property_obj.price = request.POST.get("price")
        property_obj.description = request.POST.get("description")
        
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


def deleteProperty(request, property_id):
    property_obj = get_object_or_404(Properties, pk=property_id)
    property_obj.delete()
    message = "Property deleted successfully"
    messages.success(request, message)
    return redirect('/admin-property-management') 


def delete_agent(request, id):
    agent_delete = get_object_or_404(BrokerAccount, pk=id)
    agent_delete.delete()
    message = "Agent deleted successfully"
    messages.success(request, message)
    return redirect('/admin-agent-management') 

def bookinglist(request):
    return render(request, 'bookings.html')

@login_required
def booking(request):
    if request.method == 'POST':
        # Fetching property details from the request
        property_id = request.POST.get('property')
        date = request.POST.get('date')
        note = request.POST.get('note')

        print(property_id, date, note)
        

        try:
            # Check if the user is authenticated
            if request.user.is_authenticated:
                # Retrieving the Property instance using the property_id
                property_instance = get_object_or_404(Properties, id=property_id)
                
                # Creating a Booking instance with the fetched Property instance and the user
                booking = Booking(user=request.user, property=property_instance, date=date, note=note)
                booking.save()
                
                message = "Booking added successfully!!"
                messages.success(request, message)
                return redirect('/properties')
            else:
                message = "User is not authenticated"
                messages.error(request, message)
                return redirect('/login')  # Redirecting to login page if user is not authenticated
        except Exception as e:
            message = "Couldn't process your request!! Please try again later."
            messages.error(request, message)
            print(e)
            return redirect('/booking')  # Redirecting to booking page in case of error
    else:
        # Render the booking_page.html template if the request method is not POST
        return render(request, 'booking_page.html')
    
    