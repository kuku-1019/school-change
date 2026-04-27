# listings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('category/<int:category_id>/', views.item_list, name='item_list_by_category'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('item/new/', views.new_item, name='new_item'),
    path('item/<int:item_id>/edit/', views.edit_item, name='edit_item'),
    path('item/<int:item_id>/delete/', views.delete_item, name='delete_item'),
    path('item/<int:item_id>/mark_sold/', views.mark_sold, name='mark_sold'),
    path('my_items/', views.my_items, name='my_items'),
    path('search/', views.search_items, name='search_items'),
    path('api/load-more/', views.load_more_items, name='load_more_items'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('seller/<int:seller_id>/', views.seller_shop, name='seller_shop'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('buy_now/<int:item_id>/', views.buy_now, name='buy_now'),
]