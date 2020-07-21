from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('ad/view/<int:id>', views.ad_view, name='ad_view'),

    path('ad/form', views.ad_form, name='ad_form'),
    path('ad/create', views.ad_create, name='ad_create'),
    path('ad/delete', views.ad_delete, name='ad_delete'),
    path('ad/edit/<int:id>', views.ad_edit, name='ad_edit'),

    path('dashboard', views.dashboard, name='dashboard'),
    path('search', views.search, name='search'),

    path('favorite/<int:id>', views.favorite, name='favorite'),
    path('unfavorite/<int:id>', views.unfavorite, name='unfavorite'),

    path('login/form', views.login_form, name='login_form'),
    path('login', views.login, name='login'),
    path('registration/form', views.registration_form, name='registration_form'),
    path('registration', views.registration, name='registration'),

    path('logout', views.logout, name='logout'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
