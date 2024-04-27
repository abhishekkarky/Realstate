from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    image = models.ImageField(upload_to='media/', default='/static/images/realstate-logo.png')
    name = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    number = models.CharField(max_length=20, unique = True)
    password = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    is_agent = models.BooleanField(default=False)
    agentId = models.IntegerField(default=0)
    intro = models.CharField(max_length = 50, null = False)
    instagramLink = models.CharField(max_length = 1000, blank=True, null = False )
    facebookLink = models.CharField(max_length = 1000, blank=True, null = False)
    twitterLink = models.CharField(max_length = 1000, blank=True, null = False )
    linkedInLink = models.CharField(max_length = 1000, blank=True, null = False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'number'

    groups = models.ManyToManyField('auth.Group', related_name='customuser_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='customuser_user_permissions', blank=True)

    def __str__(self):
        return self.number
    

class ContactList(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    subject = models.CharField(max_length=12, default = 'subject')
    message = models.TextField()

class BrokerAccount(models.Model):
    photo = models.ImageField(upload_to='media/', default='/static/images/img_1.jpg')
    name = models.CharField(max_length = 20)
    intro = models.CharField(max_length = 50)
    number = models.CharField(max_length=20, unique = True)
    instagramLink = models.CharField(max_length = 1000, default='https://instagram.com')
    facebookLink = models.CharField(max_length = 1000, default='https://facebook.com')
    twitterLink = models.CharField(max_length = 1000, default = 'https://twitter.com')
    linkedInLink = models.CharField(max_length = 1000, default='https://linkedin.com')


class Properties(models.Model):
    image = models.ImageField(upload_to='media/', default='/static/images/img_1.jpg')
    imageTwo = models.ImageField(upload_to='media/', default='/static/images/img_1.jpg')
    imageThree = models.ImageField(upload_to='media/', default='/static/images/img_1.jpg')
    broker = models.ForeignKey(BrokerAccount, on_delete=models.CASCADE)
    name = models.CharField(max_length = 20)
    location = models.CharField(max_length = 50)
    beds = models.CharField(max_length = 10)
    baths = models.CharField(max_length = 10)
    price = models.CharField(max_length = 30)
    description = models.CharField(max_length = 1000)
    latitude = models.FloatField(default=27.707)
    longitude = models.FloatField(default=85.34238)
    is_archived= models.BooleanField(default=False)

class Testimonials(models.Model):
    image = models.ImageField(upload_to='media/', default='/static/images/img_1.jpg')
    intro = models.CharField(max_length = 100)
    name = models.CharField(max_length = 100)
    description = models.CharField(max_length = 1000)

class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    property = models.ForeignKey(Properties, on_delete=models.CASCADE)
    date = models.DateField()
    note = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Pending')

class Review(models.Model):
    broker = models.ForeignKey(BrokerAccount,on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.property.name}"