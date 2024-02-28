# from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from Auth.models import BrokerAccount, ContactList, Properties, Testimonials


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
    return render(request, 'admin/enquiry-management.html')

def agentManagement(request):
    return render(request, 'admin/agent-management.html')

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
