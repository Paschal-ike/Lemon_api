from django.shortcuts import render

# Create your views here.
from rest_framework import status, throttling
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.db import transaction
from datetime import datetime
#from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *

class IsDeliveryCrewUser(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated and belongs to the delivery crew group
        return request.user.is_authenticated and request.user.groups.filter(name='Delivery Crew').exists()

class CustomThrottle(throttling.AnonRateThrottle):
     rate = '100/day'

class CustomUserThrottle(throttling.UserRateThrottle):
     rate = '100/day'




     



@api_view(['POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
@throttle_classes([CustomThrottle, CustomUserThrottle])
def restricted_access(request):
     return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
@throttle_classes([CustomThrottle, CustomUserThrottle])
def restricted_access_detail(request, menu_id):
     return Response({"error":"Access Denied"}, status=status.HTTP_403_FORBIDDEN)
     

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def menu_items_view(request):
    paginator = PageNumberPagination()
    paginator.page_size = 3 
    if request.method == 'GET':
        search_query = request.GET.get('search')
        if search_query:
            # Filter menu items by category name or menu item title
            menu_items = MenuItem.objects.filter(
                Q(category__title__icontains=search_query) | Q(title__icontains=search_query)
            )
        else:
            menu_items = MenuItem.objects.all()
        paginated_menu_items = paginator.paginate_queryset(menu_items, request)  
        serializer = MenuItemSerializer(menu_items, many=True)
        return Response(serializer.data)
   
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([CustomThrottle, CustomUserThrottle])
def manage_menu_item(request, menu_item_id=None):
    if menu_item_id is None:
        # If menu_item_id is None, handle listing all menu items or creating a new menu item
        if request.method == 'GET':
            menu_items = MenuItem.objects.all()
            serializer = MenuItemSerializer(menu_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'POST':
            # Handle creating a new menu item
            serializer = MenuItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        # If menu_item_id is provided, handle operations on a specific menu item
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
@permission_classes([IsAuthenticated, IsDeliveryCrewUser])
def view_assigned_orders(request):
    # Retrieve orders assigned to the authenticated delivery crew user
    assigned_orders = Order.objects.filter(delivery_crew=request.user)

    # Apply filtering
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ['created_at', 'total_amount']  # Define fields for sorting
    search_fields = ['id', 'status', 'customer_name']  # Define fields for searching
    for backend in filter_backends:
        assigned_orders = backend().filter_queryset(request, assigned_orders, view=view_assigned_orders)
    
    # Apply sorting
    assigned_orders = OrderingFilter().filter_queryset(request, assigned_orders, view=view_assigned_orders)
    
    # Paginate the queryset
    paginator = PageNumberPagination()
    paginated_orders = paginator.paginate_queryset(assigned_orders, request)

    # Serialize the paginated queryset
    serializer = OrderSerializer(paginated_orders, many=True)

    # Return paginated and serialized data
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def manage_manager(request):
    if request.method == 'GET':
        # Handle GET request to list managers
        managers = User.objects.filter(groups__name='Manager')
        serializer = UserSerializer(managers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Handle POST request to assign a user to a group
        try:
            # Retrieve the username and group name from the request data
            username = request.data.get('username')
            group_name = request.data.get('group_name')
            
            # Check if both username and group_name are provided in the request data
            if not username or not group_name:
                return Response({"error": "Username and group name are required in the request body."}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve the user object based on the provided username
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "User with the provided username does not exist."}, status=status.HTTP_404_NOT_FOUND)

            # Retrieve the group object based on the provided group name
            try:
                group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                return Response({"error": "Group with the provided name does not exist."}, status=status.HTTP_404_NOT_FOUND)

            # Assign the user to the specified group
            user.groups.add(group)

            return Response({"success": f"User '{username}' assigned to group '{group_name}' successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_cart(request):
    if request.method == 'GET':
        try:
            # Retrieve cart items associated with the authenticated user
            cart_items = Cart.objects.filter(user=request.user)
            
            # Serialize the cart items
            serializer = CartSerializer(cart_items, many=True)
            
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    elif request.method == 'POST':
        try:
            # Extract data from the request body
            menuitem_id = request.data.get('menuitem')
            quantity = request.data.get('quantity')

            # Validate the input data
            if not menuitem_id or not quantity:
                return Response({'error': 'Menu item and quantity are required.'}, status=400)

            # Check if the item already exists in the cart
            existing_cart_item = Cart.objects.filter(user=request.user, menuitem=menuitem_id).first()
            if existing_cart_item:
                # If item already exists, update its quantity
                existing_cart_item.quantity += int(quantity)
                existing_cart_item.save()
                serializer = CartSerializer(existing_cart_item)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Get the unit price of the menu item
                menuitem = MenuItem.objects.get(id=menuitem_id)
                unit_price = menuitem.price

                # Calculate the total price for the new cart item
                price = unit_price * int(quantity)

                # Create a new cart item instance
                cart_item = Cart.objects.create(
                    user=request.user,
                    menuitem_id=menuitem_id,
                    unit_price=unit_price,
                    quantity=quantity,
                    price=price
                )

                # Serialize the cart item
                serializer = CartSerializer(cart_item)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except MenuItem.DoesNotExist:
            return Response({'error': 'Menu item does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
     user = request.user
     cart_items = Cart.objects.filter(user=user)
     cart_items.delete()
     return Response(status=status.HTTP_204_NO_CONTENT)
 
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_user_orders(request):
    if request.method == 'GET':
        try:
            # Retrieve orders associated with the authenticated user
            orders = Order.objects.filter(user=request.user)
            
            # Serialize the orders
            serializer = OrderSerializer(orders, many=True)
            
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    elif request.method == 'POST':
        try:
            # Extract the date from the request data
            date = request.data.get('date')

            # Validate the input data
            if not date:
                return Response({'error': 'Date field is required.'}, status=400)

            # Convert the date string to a datetime object
            order_date = datetime.strptime(date, '%Y-%m-%d').date()

            # Retrieve the cart items associated with the authenticated user
            cart_items = Cart.objects.filter(user=request.user)
            
            # Calculate the total amount of the order
            total_amount = sum(cart_item.price for cart_item in cart_items)

            #Create a new order instance
            with transaction.atomic():
                order = Order.objects.create(user=request.user, total=total_amount, date=order_date)
                # Add cart items to the order
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order, 
                        menuitem=cart_item.menuitem, 
                        quantity=cart_item.quantity,
                        unit_price=cart_item.unit_price
                        )


            # Clear the cart after placing the order
            cart_items.delete()

            # Serialize the order
            serializer = OrderSerializer(order)

            return Response(serializer.data, status=201)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDeliveryCrewUser])
@throttle_classes([CustomThrottle, CustomUserThrottle])
def view_assigned_orders(request):
    # Retrieve orders assigned to the authenticated delivery crew user
    assigned_orders = Order.objects.filter(delivery_crew=request.user)

    # Apply filtering
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ['created_at', 'total_amount']  # Define fields for sorting
    search_fields = ['id', 'status', 'customer_name']  # Define fields for searching
    for backend in filter_backends:
        assigned_orders = backend().filter_queryset(request, assigned_orders, view=view_assigned_orders)
    
    # Apply sorting
    assigned_orders = OrderingFilter().filter_queryset(request, assigned_orders, view=view_assigned_orders)
    
    # Paginate the queryset
    paginator = PageNumberPagination()
    paginated_orders = paginator.paginate_queryset(assigned_orders, request)

    # Serialize the paginated queryset
    serializer = OrderSerializer(paginated_orders, many=True)

    # Return paginated and serialized data
    return paginator.get_paginated_response(serializer.data)
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
          
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def manage_order_items(request, order_id):
    try:
        # Retrieve the order object based on the provided order ID
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if the request method is GET
    if request.method == 'GET':
        try:
            user = request.user
            # Check if the order belongs to the current user
            if order.user != user:
                return Response({'error': 'Order does not belong to the current user'}, status=status.HTTP_403_FORBIDDEN)
            
            # Retrieve order items associated with the order
            order_items = OrderItem.objects.filter(order=order)
            serializer = OrderItemSerialzers(order_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Check if the request method is PATCH
    elif request.method == 'PATCH':
        try:
            # Check if the authenticated user is the assigned delivery crew for the order
            if order.delivery_crew != request.user:
                return Response({'message': 'You are not assigned as the delivery crew for this order.'}, status=status.HTTP_403_FORBIDDEN)
            
            # Retrieve the status value from the request data
            status_value = request.data.get('status')

            # Validate the status value
            if status_value not in [True, False]:
                return Response({'message': 'Invalid status value. Please provide either true or false.'}, status=status.HTTP_400_BAD_REQUEST)

            # Update the status of the order
            order.status = status_value
            order.save()

            # Serialize the updated order object
            serializer = OrderSerializer(order)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def categories_view(request):
    if request.method == 'GET':
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if request.user.is_staff:  # Check if the user is admin
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def categories_detail_view(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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