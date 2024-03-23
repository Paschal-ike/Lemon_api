from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny 
from django.contrib.auth.models import User, Group
#from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *

#View to list all menu items 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_meun_item(request):
     menu_items = MenuItem.objects.all()
     serializer = MenuItemSerializer(menu_items, many=True)
     return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
def restricted_access(request):
     return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieve_menu_items(request, menu_item_id):
     try:
          menu_item = MenuItem.objects.get(pk=menu_item_id)
     except MenuItem.DoesNotExist:
          return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)
     serializer = MenuItemSerializer(menu_item)
     return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
def restricted_access_detail(request, menu_id):
     return Response({"error":"Access Denied"}, status=status.HTTP_403_FORBIDDEN)
     
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def list_create_menu_items(request):
    if request.method == 'GET':
        menu_items = MenuItem.objects.all()
        serializer = MenuItemSerializer(menu_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        if request.user.is_staff:  # Only managers can create menu items
            serializer = MenuItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def retrieve_update_delete_menu_item(request, menu_item_id):
    try:
        menu_item = MenuItem.objects.get(id=menu_item_id)
    except MenuItem.DoesNotExist:
        return Response({'message': 'Menu item does not exist.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = MenuItemSerializer(menu_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method in ['PUT', 'PATCH', 'DELETE']:
        if request.user.is_staff:  # Only managers can update and delete menu items
            if request.method == 'PUT':
                serializer = MenuItemSerializer(menu_item, data=request.data)
            elif request.method == 'PATCH':
                serializer = MenuItemSerializer(menu_item, data=request.data, partial=True)
            else:  # DELETE method
                menu_item.delete()
                return Response({'message': 'Menu item deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_menu_items(request):
     queryset = MenuItem.objects.all()
     
     #filtering
     category = request.query_params.get('category')
     if category:
          queryset = queryset.filter(category__title=category)
          
     #pagiantion
     paginator = PageNumberPagination
     paginator.page_size = 10
     paginated_queryset = paginator.paginate_queryset(queryset, request)
     
     #sorting
     sort_by = request.query_params.get('sort_by', 'title')
     queryset = queryset.order_by(sort_by)
     
     serializer = MenuItemSerializer(paginated_queryset, many=True)
     return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request):
     user = request.user
     queryset = Order.objects.filter(user=user)
     
     #filtering
     status = request.query_params.get('status')
     if status:
          queryset = queryset.filter(status=status)
          
     #pagination
     paginator = PageNumberPagination()     
     paginator.page_size = 10
     paginated_queryset = paginator.paginate_queryset(queryset, request)
     
     #sorting
     sort_by = request.query_params.get('sort_by', '-date')
     queryset = queryset.order_by(sort_by)
     
     serializer = OrderSerializer(paginated_queryset, many=True)
     return paginator.get_paginated_response(serializer.data)
                   
@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_manager(request):
     managers = User.objects.filter(group='Manager')
     serializer = UserSerializer(managers, many=True)
     return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def assign_manager(request): 
     try:
          user_id = request.data.get('user_id')
          user = User.objects.get(id=user_id)
          manager_group = Group.objects.get(name='Manager')
          user.groups.add(manager_group)
          return Response(status=status.HTTP_201_CREATED)
     except User.DoesNotExist:
          return Response({"Error":"User not found"},status=status.HTTP_404_NOT_FOUND)
     except Group.DoesNotExist:
          return Response({"error":"Group not found"}, status=status.HTTP_404_NOT_FOUND)
     
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def remove_manager(request, user_id):
     try:
          user = User.objects.get(id=user_id)
          manager_group = Group.objects.get(name="Manager")
          user.groups.remove(manager_group)
          return Response(status=status.HTTP_200_OK)
     except User.DoesNotExist:
          return Response({"Error":"User not found"},status=status.HTTP_404_NOT_FOUND)
     except Group.DoesNotExist:
          return Response({"error":"Group not found"}, status=status.HTTP_404_NOT_FOUND)
     
@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_delivery_crew(request):
    delivery_crew = User.objects.filter(groups__name='Delivery Crew')
    serializer = UserSerializer(delivery_crew, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def assign_delivery_crew(request):
    try:
        user_id = request.data.get('user_id')
        user = User.objects.get(id=user_id)
        delivery_crew_group = Group.objects.get(name='Delivery Crew')
        user.groups.add(delivery_crew_group)
        return Response(status=status.HTTP_201_CREATED)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Group.DoesNotExist:
        return Response({'error': 'Delivery Crew group not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def remove_delivery_crew(request, userId):
    try:
        user = User.objects.get(id=userId)
        delivery_crew_group = Group.objects.get(name='Delivery Crew')
        user.groups.remove(delivery_crew_group)
        return Response(status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Group.DoesNotExist:
        return Response({'error': 'Delivery Crew group not found'}, status=status.HTTP_404_NOT_FOUND)
           
@api_view(['GET'])
@permission_classes(IsAuthenticated) 
def get_cart_items(request):
     user = request.user
     cart_items = Cart.objects.filter(user=user)
     serializer = CartSerializer(cart_items, many=True)
     return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes(IsAuthenticated) 
def add_to_cart(request):
     try:
          user = request.data
          menu_item_id = request.data.get('menu_item_id')
          menu_item = MenuItem.objects.get(id=menu_item_id)
          
          existing_cart_item = Cart.objects.filter(user=user, menuitem=menu_item)
          if existing_cart_item.exists():
               return Response({'error':'Item already in cart'}, status=status.HTTP_400_BAD_REQUEST)
          
          cart_item_data = {
               'user': user,
               'menuitem': menu_item,
               'quantity' : 1,
               'unit_price': menu_item.price,
               'price': menu_item.price
          }
          
          serializer = CartSerializer(data=cart_item_data)
          if serializer.is_valid():
               serializer.save()
               return Response(status=status.HTTP_201_CREATED)
          return Response(status=status.HTTP_400_BAD_REQUEST)
     except MenuItem.DoesNotExist:
          return Response({'error':'Item not found'},status=status.HTTP_404_NOT_FOUND)
     
     
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
     user = request.user
     cart_items = Cart.objects.filter(user=user)
     cart_items.delete()
     return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_order(request):
     user = request.user
     orders = Order.objects.filter(user=user)
     serializer = OrderSerializer(orders, many=True)
     return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
     try:
          user = request.user
          new_order = Order.objects.create(user=user)   #create a new order  
          #Get current cart Item and create order item
          cart_items = Cart.objects.filter(user=user) 
          for item in cart_items:
               OrderItem.objects.create(
                    order=new_order,
                    menuitem = item.menuitem,
                    quantity= item.quantity,
                    unit_price =item.unit_price
               )  
          cart_items.delete() #Clear Cart
          serializer = OrderSerializer(new_order)
          return Response(serializer.data, status=status.HTTP_201_CREATED)
     except Exception as e:
          return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
          
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_items(request, orderId):
     try:
          user = request.user
          order = Order.objects.get(id=orderId)
          if order.user != user:
               return Response({'error': 'Order does not belong to the current user'}, status=status.HTTP_403_FORBIDDEN)
          
          order_items = OrderItem.objects.filter(order=order)
          serializer = OrderItemSerialzers(order_items, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)
     except Order.DoesNotExist:
          return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)    

# class ManagerGroupUsersListView(generics.ListAPIView):
#      queryset = User.objects.filter(groups__name='Manager')
#      serializer_class = UserSerializer
#      permission_classes = [IsAuthenticated]

# class ManagerGroupUserCreateView(generics.CreateAPIView):
#      queryset = User.objects.all()
#      serializer_class = UserSerializer
#      permission_classes = [IsAdminUser]
     
#      def perform_create(self, serializer):
#           group = Group.objects.get(name='Manager')
#           serializer.save()
#           group.user_set.add(serializer.instance)

# class ManagerGroupUserDeleteView(generics.DestroyAPIView):
#      queryset = User.objects.all()
#      serializer_class = UserSerializer
#      permission_classes = [IsAdminUser]
     
#      def delete(self, request, *args, **kwargs):
#           user = self.get_object()
#           group = Group.objects.get(name='Manager')
#           if user.groups.filter(name='Manager').exists():
#                group.user_set.remove(user)
#                return Response(status=status.HTTP_200_OK)
#           else:
#                return Response(status=status.HTTP_404_NOT_FOUND  )
          
          
# class DeliveryCrewrGroupUsersListView(generics.ListAPIView):
#      queryset = User.objects.filter(group__name="Delivery Crew")
#      serializer_class = UserSerializer
#      permission_classes = [IsAuthenticated]

# class DeliveryCrewGroupUserCreateView(generics.CreateAPIView):
#      queryset = User.objects.all()
#      serializer_class = UserSerializer
#      permission_classes = [IsAdminUser]
     
#      def perform_create(self, serializer):
#           group = Group.objects.get(name='Delivery Crew')
#           serializer.save()
#           group.user_set.add(serializer.instance)

# class DeliveryCrewGroupUserDeleteView(generics.DestroyAPIView):
#      queryset = User.objects.all()
#      serializer_class = UserSerializer
#      permission_classes = [IsAdminUser]
     
#      def delete(self, request, *args, **kwargs):
#           user = self.get_object()
#           group = Group.objects.get(name='Delivery Crew')
#           if user.groups.filter(name='Delivery Crew').exists():
#                group.user_set.remove(user)
#                return Response(status=status.HTTP_200_OK)
#           else:
#                return Response(status=status.HTTP_404_NOT_FOUND  )
     

# class CategoriesView(generics.ListCreateAPIView):
#      queryset = Category.objects.all()
#      serializer_class = CategorySerializer
#      permission_classes = [IsAdminUser]

# class CategoriesDetailView(generics.RetrieveUpdateDestroyAPIView):
#      queryset = Category.objects.all()
#      serializer_class = CategorySerializer
#      permission_classes = [IsAdminUser]

# class MenuItemsListView(generics.ListAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer
#     permission_classes = [IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
#     ordering_fields = ['title','price']
#     filterset_fields = ['category']
#     search_fields = ['title']
    

# @api_view(['GET', 'POST', 'DELETE'])   
# def cart_items(request):
#      if request.method == 'GET':
#           cart_items = Cart.objects.filter(user=request.user)
#           serializer = CartSerializer(cart_items, many=True)
#           return Response(serializer.data)
     
#      elif request.method == 'POST':
#           serializer = CartSerializer(data=request.data)
#           if serializer.is_valid():
#                serializer.save(user=request.user)
#                return Response(serializer.data, status=status.HTTP_201_CREATED)
#           return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
     
#      elif request.method == 'DELETE':
#           cart_items = Cart.objects.filter(user=request.user)
#           cart_items.delete()
#           return Response(status=status.HTTP_204_NO_CONTENT)     

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_list(request):
     if request.method == 'GET':
          orders = Order.objects.filter(user=request.user)
          serializer = OrderSerializer(orders, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)
     
     elif request.method == 'POST':
          serializer = OrderSerializer(data=request.data)
          if serializer.is_valid():
               serializer.save(user=request.user)
               return Response(serializer.data, status=status.HTTP_201_CREATED)
          return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
     
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def order_detail(request, orderId):
     try:
          order = Order.objects.get(id=orderId)
     except Order.DoesNotExist:
          return Response(status=status.HTTP_404_NOT_FOUND)
     
     if request.method == "GET":
          if order.user == request.user:
               serializer = OrderSerializer(order)
               return Response(serializer.data, status=status.HTTP_200_OK)
          else:
               return Response(status=status.HTTP_403_FORBIDDEN)
          
     elif request.method == "PUT":
          if order.user == request.user:
               serializer = OrderSerializer(order, data=request.data)
               if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
               return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
          else:
               return Response(status=status.HTTP_403_FORBIDDEN)
     
     elif request.method == "PATCH":
          if order.user == request.user:
               order.status = request.data.get('status')
               order.save()
               return Response(status=status.HTTP_200_OK) 
          else:
               return Response(status=status.HTTP_403_FORBIDDEN)
     
               
     elif request.method == "DELETE":
          if order.user == request.user:
               order.delete()
               return Response(status=status.HTTP_204_NO_CONTENT)
          else:
               return Response(status=status.HTTP_403_FORBIDDEN)