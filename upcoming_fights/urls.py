from django.urls import path
from upcoming_fights import views

urlpatterns = [
    path('', views.index, name='index'),
    path('follow/', views.follow_fighter, name='follow_fighter'),
    path('unfollow/', views.unfollow_fighter, name='unfollow_fighter'),
    path('followed-fighters/', views.followed_fighters, name='followed_fighters'),
    path('search-fighters/', views.search_fighters, name='search_fighters'),
    path('trending', views.trending_fighters, name='trending'),
]