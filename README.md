# Lemon_api


## Description

This project provides a RESTful API for managing restaurant operations, including menu items, categories, orders, and user roles.

## Endpoints

### restricted_access (POST, PUT, PATCH, DELETE)

- **Description:** Restricts access to users with admin privileges.
- **Features:**
  - Accessible only to users with admin privileges (IsAdminUser permission).
  - Throttling applied using custom throttles (CustomThrottle, CustomUserThrottle).

### restricted_access_detail (POST, PUT, PATCH, DELETE)

- **Description:** Similar to restricted_access but for specific resources.
- **Features:**
  - Accessible only to users with admin privileges (IsAdminUser permission).
  - Throttling applied using custom throttles (CustomThrottle, CustomUserThrottle).

### menu_items_view (GET)

- **Description:** Allows users to retrieve a list of menu items with pagination, filtering, and searching.
- **Features:**
  - Accessible to authenticated users (IsAuthenticated permission).
  - Pagination implemented with a page size of 3 items per page.
  - Filtering by category name or menu item title using the search query parameter.

### manage_menu_item (GET, PUT, PATCH, DELETE)

- **Description:** Allows users to manage menu items, including listing, creating, updating, and deleting menu items. Only users with staff privileges can perform create, update, and delete operations.
- **Features:**
  - Accessible to authenticated users (IsAuthenticated permission).
  - Pagination, filtering, and sorting supported for listing menu items.
  - Create, update, and delete operations restricted to users with staff privileges (request.user.is_staff).

### categories_view (GET, POST, PUT, DELETE)

- **Description:** Allows admins to manage categories, including listing, creating, updating, and deleting categories.
- **Features:**
  - Accessible only to users with admin privileges (IsAdminUser permission).
  - Create, update, and delete operations restricted to admins.

### manage_manager (GET, POST, DELETE)

- **Description:** Allows admins to manage managers, including listing, creating, and deleting manager users. Managers are users assigned to the "Manager" group.
- **Features:**
  - Accessible only to users with admin privileges (IsAdminUser permission).
  - Create and delete operations restricted to admins.

### view_assigned_orders (GET)

- **Description:** Allows delivery crew members to view orders assigned to them with support for pagination, sorting, and filtering.
- **Features:**
  - Accessible to authenticated users who belong to the "Delivery Crew" group (IsDeliveryCrewUser permission).
  - Pagination, sorting, and filtering supported for viewing assigned orders.

### manage_delivery_crew (GET, POST, DELETE)

- **Description:** Allows admins to manage delivery crew members, including listing, assigning, and removing delivery crew members.
- **Features:**
  - Accessible only to users with admin privileges (IsAdminUser permission).
  - Create and delete operations restricted to admins.

### manage_cart (GET, POST, DELETE)

- **Description:** Allows users to manage their shopping carts, including listing, adding items, and clearing the cart.
- **Features:**
  - Accessible to authenticated users (IsAuthenticated permission).
  - Supports listing, adding items, and clearing the cart.

### manage_user_orders (GET, POST)

- **Description:** Allows users to manage their orders, including listing and creating orders.
- **Features:**
  - Accessible to authenticated users (IsAuthenticated permission).
  - Supports listing order history and placing new orders.

### view_assigned_orders (GET)

- **Description:** Allows delivery crew members to view orders assigned to them with support for pagination, sorting, and filtering.
- **Features:**
  - Accessible to authenticated users who belong to the "Delivery Crew" group (IsDeliveryCrewUser permission).
  - Pagination, sorting, and filtering supported for viewing assigned orders.

### manage_order_items (GET, PATCH)

- **Description:** Allows users to manage order items, including viewing and updating the status of order items.
- **Features:**
  - Accessible to authenticated users (IsAuthenticated permission).
  - Supports viewing order items associated with their orders and updating the status of those items.

### create_order (POST)

- **Description:** Allows users to create new orders by transferring items from the shopping cart to the order and clearing the cart.
- **Features:**
  - Accessible to authenticated users (IsAuthenticated permission).
  - Creates a new order and adds items from the user's shopping cart to the order.

### order (GET, POST, PUT, PATCH, DELETE)

- **Description:** Allows users to manage orders, including listing, creating, updating, and deleting orders.
- **Features:**
  - Accessible to authenticated users (IsAuthenticated permission).
  - Supports listing order details, creating new orders, updating order status, and deleting orders.

## Other Requirements

- Django 3.x
- Django REST Framework
- Python 3.x
- Pip (Python package installer)

## Installation

1. Clone the repository: `git clone https://github.com/Paschal-ike/Lemon_api.git`
2. Navigate to the project directory: 
3. Install dependencies: `pip install -r requirements.txt`
4. Configure database settings in `settings.py`
5. Run migrations: `python manage.py migrate`
6. Start the development server: `python manage.py runserver`

## Usage

- Make requests to the API endpoints using tools like cURL, Postman, or your preferred HTTP client.

## Contributors

- (https://github.com/paschal-ike)

