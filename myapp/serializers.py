from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups']

class CategorySerializer (serializers.ModelSerializer):
    class Meta:
         model = Category
         fields = ['id','slug','title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        models = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']

class OrderItemSerialzers(serializers.ModelSerializer):
    class Meta:
        model = OrderItem 
        fields = ['id', 'order', 'menuitem', 'quantity', 'unit_price']
        
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerialzers(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items']
    