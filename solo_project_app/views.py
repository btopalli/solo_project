from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from solo_project_app.models import User
from solo_project_app.models import Ad
from solo_project_app.models import City
from solo_project_app.models import Category
import bcrypt
import datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models import Q


def index(request):
    category_id = int(request.GET.get('category_id', 0))
    if category_id > 0:
        ads = Ad.objects.filter(category_id=category_id).order_by('-created_at')
    else: 
        ads = Ad.objects.order_by('-created_at')

    categories = Category.objects.all()
    
    context = {
        'ads': ads,
        'categories' : categories,
        'category_id' : category_id
    }
    return render(request, 'index.html', context)


def dashboard(request):
    if 'userid' not in  request.session:
        return redirect(index)

    user = User.objects.get(pk=request.session['userid'])

    ads = user.posted_by.order_by('-created_at')
    favorited_ads = user.favorited_ads.all();
    
    context = {
        'user': user,
        'ads': ads,
        'favorited_ads' : favorited_ads
    }
    return render(request, 'dashboard.html', context)

def search(request):
    search_term = request.GET['search_term']
    ads = Ad.objects.filter(Q(title__contains=search_term) | Q(description__contains=search_term)).order_by('-created_at')

    
    context = {
        'ads': ads,
    }
    return render(request, 'search_results.html', context)

def favorite(request, id):
    if 'userid' not in request.session:
        return JsonResponse({'success':0})
    
    ad = Ad.objects.get(pk=id)
    user = User.objects.get(pk=request.session['userid'])
    ad.users_who_liked.add(user)
    return JsonResponse({'success' : 1})

def unfavorite(request, id):
    if 'userid' not in request.session:
        return JsonResponse({'success':0})

    ad = Ad.objects.get(pk=id)
    user = User.objects.get(pk=request.session['userid'])
    ad.users_who_liked.remove(user)
    return JsonResponse({'success' : 1})

def login_form(request):
    return render(request, 'login_form.html')

def ad_view(request, id):
    ad = Ad.objects.get(pk=id)
    ad.views = ad.views + 1
    ad.save()

    if 'userid' in  request.session:
        user = User.objects.get(pk=request.session['userid'])
    else:
        user = None

    context = {
        'ad' : ad,
        'user' : user
    }
    return render(request, 'ad_view.html', context)

def login(request):
    errors = User.objects.login_validator(request.POST)
    if len(errors) > 0:
        for k, v in errors.items():
            messages.error(request, v)
        return redirect(login_form)

    user = User.objects.filter(email=request.POST['email'])
    if user:
        logged_user = user[0]
        if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
            request.session['userid'] = logged_user.id
            request.session['loggedIn'] = True
            request.session['first_name'] = logged_user.first_name
            return redirect(dashboard)

    return redirect(dashboard)

def registration_form(request):
    cities = City.objects.all()
    context = {
        'cities': cities,
    }
    return render(request, 'registration_form.html', context)


def registration(request):
    errors = User.objects.registration_validator(request.POST)
    if len(errors) > 0:
        for k, v in errors.items():
            messages.error(request, v)

        request.session['first_name'] = request.POST['first_name']
        request.session['last_name'] = request.POST['last_name']
        request.session['email'] = request.POST['email']
        return redirect(registration_form)

    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    email = request.POST['email']
    password = request.POST['password']
    contact_number = request.POST['contact_number']
    city = City.objects.get(pk=request.POST['city_id'])
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    user = User()
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.password = pw_hash
    user.contact_number = contact_number
    user.city = city
    user.save()

    request.session['userid'] = user.id
    request.session['first_name'] = first_name
    request.session['loggedIn'] = True
    request.session['last_name'] = ""
    request.session['email'] = ""
    return redirect(dashboard)


def logout(request):
    request.session.flush()
    return redirect(index)    


def ad_form(request):
    categories = Category.objects.all()

    context = {
        'ad_id' : 0,
        'categories' : categories
    }
    return render(request, 'ad_form.html', context)    


def ad_create(request):
    errors = Ad.objects.ad_validator(request.POST)
    if len(errors) > 0:
        for k, v in errors.items():
            messages.error(request, v)

        request.session['title'] = request.POST['title']
        request.session['description'] = request.POST['description']
        request.session['end_date'] = request.POST['end_date']
        return redirect(ad_form)

    id = request.POST['ad_id']
    title = request.POST['title']
    description = request.POST['description']
    end_date = request.POST['end_date']
    category = Category.objects.get(pk=request.POST['category_id'])

    if 'image' in request.FILES:
        image = request.FILES['image']
    else:
        image = None

    if (id == "0"):
        ad = Ad()
    else:
        ad = Ad.objects.get(pk=id)

    ad.title = title
    ad.description = description
    ad.end_date = end_date
    ad.category = category
    ad.user = User.objects.get(pk=request.session['userid'])
    if image != None:
        ad.image = image

    ad.save()
    return redirect(index)     

def ad_edit(request, id):
    if 'userid' not in request.session:
        return redirect(dashboard)  

    try:
        ad = Ad.objects.get(pk=id)
    except Ad.DoesNotExist:
        context = {
            'report': "This ad doesn't exist!"
        }
        return render(request, 'report.html', context)    

    if ad.user.id != request.session['userid']:
        context = {
            'report': "This is not your ad!"
        }
        return render(request, 'report.html', context) 

    context = {
        'ad_id' : ad.id,
        'categories' : Category.objects.all(),
        'ad' : ad,
        'end_date' : ad.end_date.strftime('%Y-%m-%d')
    }
    return render(request, 'ad_form.html', context)    


def ad_delete(request):
    if 'userid' not in request.session:
        return JsonResponse({'success':0})

    id = request.GET["id"]
    ad = Ad.objects.get(pk=id)
    ad.delete()

    return JsonResponse({'success' : 1}) 

