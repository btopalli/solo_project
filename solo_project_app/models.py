from django.db import models
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime
from dateutil.relativedelta import relativedelta

class City(models.Model):
    city_name = models.CharField(max_length=45)

class UserManager(models.Manager):
    def registration_validator(self, post_data):
        errors = {}

        if len(post_data['first_name']) < 2:
            errors['first_name'] = "First name must be at least 2 characters"

        if len(post_data['last_name']) < 2:
            errors['last_name'] = "Last name must be at least 2 characters"

        if len(post_data['email']) > 0:
            try:
                validate_email(post_data['email'])
                user = User.objects.filter(email = post_data['email'])
                if (user):
                    errors['email'] = "This email address is already used"
            except ValidationError:
                errors['email'] = "Please enter a valid email address"
        else:
            errors['email'] = "Please enter your email address"

            
        if len(post_data['password']) < 8:
            errors['password'] = "Password must be at least 8 characters"

        if len(post_data['password2']) < 8:
            errors['password2'] = "Password 2 must be at least 8 characters"

        if post_data['password'] != post_data['password2']:
            errors['password'] = "Passwords must match!"


        if len(post_data['contact_number']) < 8:
            errors['contact_number'] = "Contact number must be at least 8 characters"

        if post_data['city_id'] == "0":
            errors['city_id'] = "You must select a city"

        return errors

    def login_validator(self, post_data):
        errors = {}
        try:
            validate_email(post_data['email'])
            user = User.objects.filter(email = post_data['email'])
            if (not user):
                errors['email'] = "There is not user with this email"
        except ValidationError:
            errors['email'] = "Please enter a valid email address"
            
        if len(post_data['password']) < 8:
            errors['password'] = "Password must be at least 8 characters"

        return errors

class User(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.EmailField(max_length=45)
    password = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20, default="")
    city = models.ForeignKey(City, related_name="user_from", on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    objects = UserManager()

class AdManager(models.Manager):
    def ad_validator(self, post_data):
        errors = {}

        if len(post_data['title']) < 10:
            errors['title'] = "A title must consist of at least 10 characters"

        if len(post_data['description']) < 30:
            errors['description'] = "A description must consist of at least 30 characters"

        year, month, day = map(int, post_data['end_date'].split('-'))
        end_date = datetime.date(year, month, day).strftime('%Y-%m-%d')

        present = datetime.date.today().strftime('%Y-%m-%d')

        if (end_date <= present):
            errors['end_date'] = "End date must greater than present date"

        return errors

class Category(models.Model):
    name = models.CharField(max_length=255)

class Ad(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='%Y/%m/%d/', blank=True)
    user = models.ForeignKey(User, related_name="posted_by", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name="ads_in_category", on_delete=models.CASCADE)
    users_who_liked = models.ManyToManyField(User, related_name="favorited_ads")
    end_date = models.DateField(default=timezone.now)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    objects = AdManager()



    