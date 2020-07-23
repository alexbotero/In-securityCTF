from .import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('migrate', views.migrate, name='migrate'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('stego1', views.stego1, name='stego1'),
    path('stego2', views.stego2, name='stego2'),
    path('stego3', views.stego3, name='stego3'),
    path('stego4', views.stego4, name='stego4'),
    path('reversing1', views.reversing1, name='reversing1'),
    path('crypto1', views.crypto1, name='crypto1'),
    path('crypto2', views.crypto2, name='crypto2'),
    path('crypto3', views.crypto3, name='crypto3'),
    path('crypto4', views.crypto4, name='crypto4'),
    path('crypto5', views.crypto5, name='crypto5'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


