from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login  # Rename the login function

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            return redirect('dashboard')  

        else:
            return render(request, 'login.html', {'error': 'Invalid login credentials'})

    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']

        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()

        user = authenticate(request, username=email, password=password)
        auth_login(request, user)  

        return redirect('login')  

    return render(request, 'register.html')


def dashboard(request):
    return render(request, 'index.html')

def contact(request):
    return render(request, 'contact.html')

def singleProperty(request):
    return render(request, 'property-single.html')

def services(request):
    return render(request, 'services.html')

def properties(request):
    return render(request, 'properties.html')
def about(request):
    return render(request, 'about.html')
