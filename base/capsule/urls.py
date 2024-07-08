# capsule/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/items/', views.item_list, name='item_list'),
    path('items/', views.item_list, name='all_items'),
    path('outfits/', views.outfit_list, name='outfit_list'),
    path('outfits/<int:outfit_id>/', views.outfit_detail, name='outfit_detail'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_item/', views.add_item, name='add_item'),
    path('add_outfit/', views.add_outfit, name='add_outfit'),
    path('create_outfit/', views.create_outfit, name='create_outfit'),
    path('category/<int:category_id>/', views.category_items, name='category_items'),
    path('subcategory/<int:subcategory_id>/', views.subcategory_items, name='subcategory_items'),
]
