from django.urls import path
from . import views


urlpatterns = [
    # path('users/', djoser_views.UserCreateView.as_view(), name='user-create'),  # User registration
    # path('users/token/', djoser_views.TokenCreateView.as_view(), name='token-create'),  # Token generation
    # path('users/token/login/', djoser_views.TokenCreateView.as_view(), name='token-login'),  # Login
    path('menu-item/', views.list_meun_item, name='menu-item'),
    path('menu-items/<int:menu_item_id>/', views.retrieve_menu_items, name='menu-details'),
    path('api/menu-items/', views.list_create_menu_items, name='menu-items-list-create'),
    path('api/menu-items/<int:menu_item_id>/', views.retrieve_update_delete_menu_item, name='menu-item-detail'),
    path('groups/manager/users/', views.list_manager, name='manager-list'),
    path('groups/manager/users/', views.assign_manager, name='assign-manager'),
    path('group/manager/users/<int:userId>/', views.remove_manager, name='manager-delete'),
    path('groups/delivery-crew/users/', views.list_delivery_crew, name='delivery-crew-list'),
    path('groups/delivery-crew/users/create/', views.assign_delivery_crew, name='delivery-crew'),
    path('groups/delivery-crew/users/<int:pk>/delete/', views.remove_delivery_crew, name='delivery-crew-delete'),
    path('cart/menu-items/', views.get_cart_items, name='cart-items'),
    path('api/cart/menu-items/', views.add_to_cart, name='add_to_cart'),
    path('api/cart/menu-items/', views.clear_cart, name='clear_cart'),
    path('orders/', views.get_user_order, name='order-list'),
    path('orders/', views.create_order, name='create-order'),
    path('orders/<int:orderId>/', views.get_order_items, name='order-detail'),
    ]



