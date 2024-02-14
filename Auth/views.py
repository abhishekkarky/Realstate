# from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.shortcuts import get_object_or_404, redirect, render

from Auth.models import ContactList, Properties, Testimonials, BrokerAccount


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

def adminProperty(request):
    return render(request, 'admin/property-management.html')

def enquiryProperty(request):
    return render(request, 'admin/enquiry-management.html')
def agentManagement(request):
    return render(request, 'admin/agent-management.html')
def teamsManagement(request):
    return render(request, 'admin/teams-management.html')
