from django.contrib import admin
from Auth.models import CustomUser, ContactList

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(ContactList)