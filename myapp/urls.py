from django.urls import path
from . import views


urlpatterns = [
    path('menu-items/', views.menu_items_view, name='menu-item'),
    path('menu-items/<int:menu_item_id>/', views.manage_menu_item, name='menu-details'),
    path('categories/', views.categories_view, name='categories-list'),
    path('categories/<int:pk>/', views.categories_detail_view, name='categories-detail'),
    path('groups/manager/users/', views.manage_manager, name='manager'),
    path('group/manager/users/<int:userId>/', views.remove_manager, name='manager-delete'),
    path('cart/menu-items/', views.manage_cart, name='add_to_cart'),
    path('cart/menu-items/', views.clear_cart, name='clear_cart'),
    path('cart/orders/', views.manage_user_orders, name='user_order'),
    path('orders/', views.view_assigned_orders, name='order-list'),
    path('orders/', views.create_order, name='create-order'),
    path('orders/<int:order_id>/', views.manage_order_items, name='order-detail'),
    ]



