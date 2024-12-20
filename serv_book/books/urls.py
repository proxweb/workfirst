from django.urls import path, include
from . import views
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'book', views.BookViewSet)


urlpatterns = [
    path('', views.AllView.as_view()),
    path('api/', include(router.urls)),
    path('addbook/', views.changebook, name='addbook'),
    path('addusers/', views.changeuser, name = 'addusers'),
    path('process/', views.processfunc),
    path('search/', views.searchfunc, name='search'),
    path('issuance/', views.funcissuance, name = 'issuance'),
    path('unissuance/', views.funcunissuance, name = 'unissuance'),
    path('pdf/', views.generate_pdf, name='generate_pdf'),
    path('user/<int:pk>', views.UserDetailView.as_view(), name='user'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book'),
]