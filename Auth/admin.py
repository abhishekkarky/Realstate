from django.contrib import admin
from Auth.models import CustomUser, ContactList, Properties, BrokerAccount

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(ContactList)
admin.site.register(Properties)
admin.site.register(BrokerAccount)