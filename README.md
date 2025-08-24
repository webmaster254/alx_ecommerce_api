# Ecommerce API

![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)
![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![REST API](https://img.shields.io/badge/REST%20API-Yes-success?logo=fastapi)
![Swagger](https://img.shields.io/badge/Docs-Swagger-brightgreen?logo=swagger)
![Postman](https://img.shields.io/badge/Tested%20With-Postman-orange?logo=postman)
![Taggit](https://img.shields.io/badge/Django--Taggit-Enabled-lightgrey?logo=django)
![DRF Version](https://img.shields.io/badge/DRF-3.14-red)
![License](https://img.shields.io/badge/license-MIT-blue)

## Table of Contents
- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Installation & Setup](#installation--setup)
- [API Endpoints](#api-endpoints-overview)
- [Postman Testing](#postman-testing-guide)
- [License](#license)


## Overview 
This project is a fully functional E-commerce Product API built with Django and Django REST Framework. It provides a backend solution for managing products, allowing users to create, read, update, and delete product information efficiently.

The API is designed to be scalable, maintainable, and easy to integrate with front-end applications or other services. 

**Key features include:**

- Product Management: CRUD operations for products, including descriptions, pricing, and availability.

- API Documentation: Integrated Swagger/OpenAPI docs for easy testing and exploration.

- Authentication & Authorization: Secure access to protected endpoints.

- Testing & Validation: Ensures robust and reliable API behavior.

This project serves as a foundation for building a full-fledged e-commerce platform and demonstrates best practices in backend development, API design, and software architecture.

##  Features

### Core Modules
- **User Management** - Registration, authentication, profile management
- **Product Catalog** - Products, categories, brands, reviews, and search
- **Shopping Cart** - Cart management with item operations
- **Order Processing** - Order creation, payment, and shipping management
- **Inventory System** - Stock management, purchase orders, suppliers
- **Promotions Engine** - Coupons, discounts, bundle offers, banners

### Advanced Features
- **RESTful API Architecture** - Clean, consistent endpoints
- **Comprehensive Admin Interface** - Django admin integration
- **Stock Movement Tracking** - Complete audit trail for inventory
- **Low Stock Alerts** - Automated inventory monitoring
- **Coupon Validation** - Real-time discount validation
- **Product Search** - Advanced search capabilities
- **Wishlist Management** - User wishlist functionality

## Tech Stack

- **Backend Framework**: Django 4.2+
- **REST API**: Django REST Framework
- **Database**: SQLite (development & production)
- **Authentication**: JWT & Session Authentication
- **API Documentation**: Swagger/OpenAPI 3.0
- **Testing**: Postman
- **Tagging**: django-taggit

##  Installation & Setup

### Prerequisites
- Python 3.8+
- SQLite (included with Python)
- pip (Python package manager)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd ecommerce_api
```

# Create virtual environment
```bash
python -m venv venv
```

# Activate virtual environment
# On Windows:
```bash 
venv\Scripts\activate
```
# On macOS/Linux:
```bash
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Or install manually if no requirements.txt
pip install django djangorestframework django-cors-headers
pip install pillow  # for image handling
```

### Step 3: Configuration
```bash
# Copy environment example file
cp .env.example .env

# Edit .env file with your settings
# Example .env content:
DEBUG=True
SECRET_KEY=your-secret-key-here
```

### Step 4: Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
# Follow prompts to create admin user
```


### Step 5: Run Development Server
```bash
# Start development server
python manage.py runserver

# Server will be available at http://127.0.0.1:8000/
# API documentation at http://127.0.0.1:8000/api/schema/
```

### API Endpoints Overview
**Authentication Endpoints**
- POST /api/users/login/ - User login

- POST /api/users/register/ - User registration

- GET /api/users/profile/ - Get user profile

- PUT /api/users/profile/ - Update user profile

**Product Endpoints**
- GET /api/products/ - List all products

- POST /api/products/ - Create product (admin)

- GET /api/products/{id}/ - Get product details

- GET /api/products/search/ - Search products

- GET /api/products/categories/ - List categories

- GET /api/products/brands/ - List brands

- GET /api/products/reviews/ - Product reviews

- GET /api/products/wishlist/ - User wishlist

**Cart Endpoints**
- GET /api/cart/carts/ - Get user cart

- POST /api/cart/carts/add_item/ - Add item to cart

- GET /api/cart/cart-items/ - List cart items

- PUT /api/cart/cart-items/{id}/ - Update cart item

- POST /api/cart/carts/clear/ - Clear cart

**Order Endpoints**
- GET /api/orders/orders/ - List user orders

- POST /api/orders/orders/ - Create new order

- GET /api/orders/orders/{id}/ - Get order details

- POST /api/orders/orders/{id}/cancel/ - Cancel order

- GET /api/orders/payments/ - Payment methods

- GET /api/orders/shipping/ - Shipping options

**Inventory Endpoints**
- GET /api/inventory/inventory/ - List inventory items

- POST /api/inventory/inventory/ - Create inventory (admin)

- POST /api/inventory/inventory/{id}/adjust_stock/ - Adjust stock

- GET /api/inventory/stock-movements/ - Stock movement history

- GET /api/inventory/purchase-orders/ - Purchase orders

- POST /api/inventory/purchase-orders/{id}/receive_stock/ - Receive stock

- GET /api/inventory/suppliers/ - Supplier management

**Promotion Endpoints**
- GET /api/promotions/coupons/ - List coupons

- POST /api/promotions/coupons/validate/ - Validate coupon

- GET /api/promotions/promotions/ - List promotions

- GET /api/promotions/promotions/active/ - Active promotions

- GET /api/promotions/bundle-offers/ - Bundle offers

- GET /api/promotions/promo-banners/active/ - Active banners

### Authentication Settings
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}
```

### Authentication & Permissions
**User Roles**
- Customer: Browse products, manage cart, place orders

- Staff: Manage products, view orders, basic admin access

- Admin: Full system access, user management, all operations

**Permission Classes**
- IsAuthenticated - Requires user authentication

- IsAdminUser - Requires admin privileges

- IsOwnerOrReadOnly - Owner can modify, others read-only

- DjangoModelPermissions - Django model-level permissions

###  Database Models

**Key Models**
- User - User accounts and profiles

- Product - Products with categories and brands

- Inventory - Stock levels and management

- Cart - Shopping cart functionality

- Order - Order processing

- Promotion - Discount system

### Testing Workflow

1. **Start with Authentication:**

- Register a new user

- Login to get authentication token

2. **Test Products:**

- Browse products

- View product details

3. **Test Cart Operations:**

- Add items to cart

- View cart contents

- Update quantities

- Remove items

4. **Test Orders:**

- Create order from cart

- View order history

- Cancel order (if needed)

5. **Test Inventory:**

- View inventory levels

- Adjust stock quantities

- View stock movements

6. **Test Promotions:**

- Validate coupons

- View active promotions

- Test discount calculations


### Postman Testing Guide

1. Postman Collection Setup
Download Postman: https://www.postman.com/downloads/

2. Import Environment Variables:

- Create a new Environment called "Ecommerce API Local"

- Add these variables:

    - base_url: http://localhost:8000

    - token: (will be set automatically after login)

    - user_id: (will be set automatically)

    - cart_id: (will be set automatically)

### Authentication Flow
1. **User Registration**
**Request:**

- **Method:** POST

- **URL:** {{base_url}}/api/users/register/

- **Headers:**

Content-Type: application/json

## Test Case 1: Successful Registration
```json
{
    "email": "testuser@example.com",
    "password": "testpassword123",
    "password_confirmation": "testpassword123",
    "first_name": "Test",
    "last_name": "User",
    "date_of_birth": "1990-01-15",
    "gender": "M",
    "phone_number": "+1234567890",
    "accepts_marketing": true,
    "profile_picture": "https://example.com/profile.jpg",
    "shipping_address": "123 Test Street, Test City, TS 12345",
    "billing_address": "123 Test Street, Test City, TS 12345",
    "preferred_payment_method": "credit_card",
    "newsletter_subscription": true
}
```
**Required Fields Only (Minimal)**
```json
{
    "email": "testuser@example.com",
    "password": "testpassword123",
    "password_confirm": "testpassword123",
    "first_name": "Test",
    "last_name": "User"
}
```

**Optional Fields**
```json
{
    "date_of_birth": "1990-01-15",
    "gender": "M",
    "phone_number": "+1234567890",
    "accepts_marketing": true,
    "profile_picture": "https://example.com/profile.jpg"
}
```

## Test Case 2: Password Mismatch (Should Fail)
```json
{
    "email": "testuser@example.com",
    "password": "password123",
    "password_confirm": "differentpassword",
    "first_name": "Test",
    "last_name": "User"
}
```

## Test Case 3: Invalid Email (Should Fail)
```json
{
    "email": "invalid-email",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "Test",
    "last_name": "User"
}
```

2. ## User Login
**Request:**
```json
POST {{base_url}}/api/users/login/
Content-Type: application/json

{
    "email": "{{user_email}}",
    "password": "testpassword123"
}
```
3. ## Get User Profile
**Request:**
```json
GET {{base_url}}/api/users/profile/
Authorization: Token {{token}}
```

4. ## Update User Profile
**Request:**
```json
PUT {{base_url}}/api/users/profile/
Authorization: Token {{token}}
Content-Type: application/json

{
    "first_name": "Updated",
    "last_name": "User",
    "date_of_birth": "1990-01-15",
    "gender": "M",
    "phone_number": "+1234567890",
    "accepts_marketing": true
}
```

5. ## Partial Update User Profile (PATCH)
**Request:**
```json
PATCH {{base_url}}/api/users/profile/
Authorization: Token {{token}}
Content-Type: application/json

{
    "phone_number": "+1987654321",
    "accepts_marketing": false
}
```

6. ## Get Current User (Me)
**Request:**
```json
GET {{base_url}}/api/users/users/me/
Authorization: Token {{token}}
```

7. ## Update Current User (Me)
**Request:** 
```json
PUT {{base_url}}/api/users/users/update_me/
Authorization: Token {{token}}
Content-Type: application/json

{
    "first_name": "Current",
    "last_name": "User",
    "date_of_birth": "1992-05-20"
}
```

8. ## Get All Users (Admin Only)
**Request:**
```json
GET {{base_url}}/api/users/users/
Authorization: Token {{token}}
```

9. ## Get User by ID (Admin Only)
**Request:**
```json
GET {{base_url}}/api/users/users/{{user_id}}/
Authorization: Token {{token}}
```

10. ## Promote User to Staff/customer (Admin Only)
**Request:**
```json
POST {{base_url}}/api/users/users/{{user_id}}/promote_to_staff/
Authorization: Token {{token}}
Content-Type: application/json
```

11. ## Deactivate User (Admin Only)
**Request:**
```json
POST {{base_url}}/api/users/users/{{user_id}}/deactivate/
Authorization: Token {{token}}
Content-Type: application/json

{}
```

12. ## Get User Statistics (Admin Only)
**Request:**
```json
GET {{base_url}}/api/users/users/statistics/
Authorization: Token {{token}}
```
---
### Products Endpoints
1. **Get All Products**
**Request:**
```json
GET {{base_url}}/api/products/
Authorization: Token {{token}}
```

2. **Create New Product (Admin Only)**
**Request:**
```json
POST {{base_url}}/api/products/
Authorization: Token {{token}}
Content-Type: application/json

{
    "name": "New Product",
    "slug": "new-product",
    "description": "Product description",
    "price": 99.99,
    "compare_price": 129.99,
    "sku": "SKU12345",
    "quantity": 50,
    "category": 1,
    "brand": 1,
    "status": "DRAFT",
    "is_featured": false,
    "is_digital": false
}
```

3. **Get Product by ID**
**Request:**
```json 
GET {{base_url}}/api/products/{{product_id}}/
Authorization: Token {{token}}
```

4. **Update Product (Full Update - Admin Only)**
**Request:**
```json
PUT {{base_url}}/api/products/{{product_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "name": "Updated Product Name",
    "slug": "updated-product",
    "description": "Updated description",
    "price": 89.99,
    "compare_price": 119.99,
    "sku": "SKU12345",
    "quantity": 40,
    "category": 1,
    "brand": 1,
    "status": "ACTIVE",
    "is_featured": true
}
```

5. **Partial Update Product (Admin Only)**
**Request:**
```json
PATCH {{base_url}}/api/products/{{product_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "price": 79.99,
    "is_featured": false
}
```

6. **Delete Product (Admin Only)**
**Request:**
```json
DELETE {{base_url}}/api/products/{{product_id}}/
Authorization: Token {{token}}
```

7. **Get Product Recommendations**
**Request:**
```json
GET {{base_url}}/api/products/{{product_id}}/recommendations/
Authorization: Token {{token}}
```

## Brands Endpoints
8. **Get All Brands**
**Request:**
```json
GET {{base_url}}/api/products/brands/
Authorization: Token {{token}}
```

9. **Get Brand by ID**
**Request:**
```json
GET {{base_url}}/api/products/brands/{{product_id}}/
Authorization: Token {{token}}
```

## Categories Endpoints
10. **Get All Categories**
**Request:**
```json
GET {{base_url}}/api/products/categories/
Authorization: Token {{token}}
```

11. **Get Category by ID**
**Request:**
```json
GET {{base_url}}/api/products/categories/{{product_id}}/
Authorization: Token {{token}}
```

## Reviews Endpoints
12. **Get All Reviews**
**Request:**
```json 
GET {{base_url}}/api/products/reviews/
Authorization: Token {{token}}
```

13. **Create New Review**
**Request:**
```json
POST {{base_url}}/api/products/reviews/
Authorization: Token {{token}}
Content-Type: application/json

{
    "product": 1,
    "rating": 5,
    "title": "Excellent Product",
    "comment": "This product exceeded my expectations!"
}
```

## Search Endpoints
14. **Search Products (GET)**
**Request:**
```json
GET {{base_url}}/api/products/search/?q=laptop
Authorization: Token {{token}}
```

15. **Search Products (POST)**
**Request:**
```json
POST {{base_url}}/api/products/search/
Authorization: Token {{token}}
Content-Type: application/json

{
    "query": "laptop",
    "category": 1,
    "min_price": 100,
    "max_price": 1000,
    "brands": [1, 2],
    "sort_by": "price",
    "sort_order": "asc"
}
```

## Wishlist Endpoints
16. **Get User Wishlist**
**Request:**
```json
GET {{base_url}}/api/products/wishlist/
Authorization: Token {{token}}
```

17. **Add Product to Wishlist**
**Request:**
```json
POST {{base_url}}/api/products/wishlist/
Authorization: Token {{token}}
Content-Type: application/json

{
    "product": {{product_id}}
}
```
---

### Cart API Postman Testing Guide
**Authentication**
- First, ensure you're authenticated:

```json
POST {{base_url}}/api/users/login/
Content-Type: application/json

{
    "email": "testuser@example.com",
    "password": "testpassword123"
}
```

## Cart Endpoints
1. **Get User Cart**
```json
GET {{base_url}}/api/cart/
Authorization: Token {{token}}
```

2. **Create New Cart**
```json
POST {{base_url}}/api/cart/
Authorization: Token {{token}}
Content-Type: application/json

{
    "notes": "Test cart created via API"
}
```

3. **Get Specific Cart**
```json
GET {{base_url}}/api/cart/{{cart_id}}/
Authorization: Token {{token}}
```

4. **Update Cart (PUT)**
```json
PUT {{base_url}}/api/cart/{{cart_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "notes": "Updated cart notes",
    "is_active": true
}
```

5. **Delete Cart**
```json
DELETE {{base_url}}/api/cart/{{cart_id}}/
Authorization: Token {{token}}
```

6. **Add Item to Cart**
```json
POST {{base_url}}/api/cart/add_item/
Authorization: Token {{token}}
Content-Type: application/json

{
    "product_id": {{product_id}},
    "quantity": 2,
    "notes": "Test item added via API"
}
```

7. **Clear Cart**
```json
POST {{base_url}}/api/cart/clear/
Authorization: Token {{token}}
Content-Type: application/json

{}
```

8. **Get Cart Count**
```json
GET {{base_url}}/api/cart/count/
Authorization: Token {{token}}
```

9. **Get All Cart Items**
```json
GET {{base_url}}/api/cart/cart-items/
Authorization: Token {{token}}
```

10. **Get Specific Cart Item**
```json
GET {{base_url}}/api/cart/cart-items/{{cart_item_id}}/
Authorization: Token {{token}}
```

11. **Update Cart Item (PUT)**
```json
PUT {{base_url}}/api/cart/cart-items/{{cart_item_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "quantity": 5,
    "notes": "Updated quantity to 5"
}
```

12. **Delete Cart Item**
```json
DELETE {{base_url}}/api/cart/cart-items/{{cart_item_id}}/
Authorization: Token {{token}}
```

13.  **Get All Saved Carts**
```json
GET {{base_url}}/api/cart/saved-carts/
Authorization: Token {{token}}
```

14. **Create Saved Cart**
```json
POST {{base_url}}/api/cart/saved-carts/
Authorization: Token {{token}}
Content-Type: application/json

{
    "name": "My Saved Cart",
    "description": "Cart saved for later purchase",
    "items": ["product_id", "quantity" "price"]  
    "notes": "Saved cart notes"
}
```

15. **Get Specific Saved Cart**
```json
GET {{base_url}}/api/cart/saved-carts/{{saved_cart_id}}/
Authorization: Token {{token}}
```

16. **Delete Saved Cart**
```json
DELETE {{base_url}}/api/cart/saved-carts/{{saved_cart_id}}/
Authorization: Token {{token}}
```

---

### Orders API Documentation
- **Base URL**
{{base_url}}/api/orders/

- **Authentication**
All endpoints require authentication using a token:
```json
Authorization: Token {{token}}
```
## Orders Endpoints
1. **Get All Orders**
```json
GET {{base_url}}/api/orders/
Authorization: Token {{token}}
```

2. **Create New Order**
```json
POST {{base_url}}/api/orders/
Authorization: Token {{token}}
Content-Type: application/json

{
    "customer_id": 123,
    "items": [
        {
            "product_id": 456,
            "quantity": 2,
            "price": 29.99
        }
    ],
    "shipping_address": "123 Main St, City, Country",
    "payment_method": "credit_card"
}
```

3. **Get Specific Order**
```json
GET {{base_url}}/api/orders/{{order_id}}/
Authorization: Token {{token}}
```

4. **Update Order (Full Update)**
```json
PUT {{base_url}}/api/orders/{{order_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "customer_id": 123,
    "status": "processing",
    "total_amount": 59.98,
    "shipping_address": "123 Main St, City, Country"
}
```

5. **Update Order (Partial Update)**
```json
PATCH {{base_url}}/api/orders/{{order_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "status": "shipped",
    "tracking_number": "TRK123456789"
}
```

6. **Delete Order**
```json
DELETE {{base_url}}/api/orders/{{order_id}}/
Authorization: Token {{token}}
```

7. **Cancel Order**
```json
POST {{base_url}}/api/orders/{{order_id}}/cancel/
Authorization: Token {{token}}
```

8. **Get Order Items**
```json
GET {{base_url}}/api/orders/{{order_id}}/items/
Authorization: Token {{token}}
```

## Payments Endpoints
9. **Get All Payments**
```json
GET {{base_url}}/api/orders/payments/
Authorization: Token {{token}}
```

10. **Create Payment**
```json
POST {{base_url}}/api/orders/payments/
Authorization: Token {{token}}
Content-Type: application/json

{
    "order_id": 789,
    "amount": 59.98,
    "payment_method": "credit_card",
    "transaction_id": "txn_123456789",
    "status": "completed"
}
```

11. **Get Specific Payment**
```json
GET {{base_url}}/api/orders/payments/{{payment_id}}/
Authorization: Token {{token}}
```

12. **Update Payment (Full Update)**
```json
PUT {{base_url}}/api/orders/payments/{{payment_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "order_id": 789,
    "amount": 59.98,
    "payment_method": "credit_card",
    "status": "refunded"
}
```

13. **Update Payment (Partial Update)**
```json
PATCH {{base_url}}/api/orders/payments/{{payment_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "status": "failed",
    "failure_reason": "Insufficient funds"
}
```

14. **Delete Payment**
```json
DELETE {{base_url}}/api/orders/payments/{{payment_id}}/
Authorization: Token {{token}}
```

## Shipping Endpoints
15. **Get All Shipping Records**
```json
GET {{base_url}}/api/orders/shipping/
Authorization: Token {{token}}
```

16. **Create Shipping Record**
```json
POST {{base_url}}/api/orders/shipping/
Authorization: Token {{token}}
Content-Type: application/json

{
    "order_id": 789,
    "carrier": "UPS",
    "tracking_number": "1Z123456789",
    "shipping_address": "123 Main St, City, Country",
    "status": "in_transit"
}
```

17. **Get Specific Shipping Record**
```json
GET {{base_url}}/api/orders/shipping/{{shipping_id}}/
Authorization: Token {{token}}
```

18. **Update Shipping Record (Full Update)**
```json
PUT {{base_url}}/api/orders/shipping/{{shipping_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "order_id": 789,
    "carrier": "FedEx",
    "tracking_number": "789012345678",
    "status": "delivered"
}
```

19. **Update Shipping Record (Partial Update)**
```json
PATCH {{base_url}}/api/orders/shipping/{{shipping_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "status": "out_for_delivery",
    "estimated_delivery": "2023-12-25T14:00:00Z"
}
```

20. **Delete Shipping Record**
```json
DELETE {{base_url}}/api/orders/shipping/{{shipping_id}}/
Authorization: Token {{token}}
```

---

### Promotions API Documentation

- **Base URL**
{{base_url}}/api/promotions/

- **Authentication**
All endpoints require authentication using a token (except public endpoints):

```json
Authorization: Token {{token}}
```

## Bundle Offers Endpoints
1. **Get All Bundle Offers**
```json
GET {{base_url}}/api/promotions/bundle-offers/
Authorization: Token {{token}}
```

2. **Create Bundle Offer**
```json
POST {{base_url}}/api/promotions/bundle-offers/
Authorization: Token {{token}}
Content-Type: application/json

{
    "name": "Summer Bundle",
    "description": "Special summer product bundle",
    "discount_percentage": 15,
    "products": [1, 2, 3],
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-08-31T23:59:59Z",
    "is_active": true
}
```

3. **Get Specific Bundle Offer**
```json
GET {{base_url}}/api/promotions/bundle-offers/{{bundle_offer_id}}/
Authorization: Token {{token}}
```

4. **Update Bundle Offer (Full Update)**
```json
PUT {{base_url}}/api/promotions/bundle-offers/{{bundle_offer_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "name": "Summer Bundle 2024",
    "description": "Updated summer bundle offer",
    "discount_percentage": 20,
    "products": [1, 2, 4],
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-08-31T23:59:59Z",
    "is_active": true
}
```

5. **Update Bundle Offer (Partial Update)**
```json
PATCH {{base_url}}/api/promotions/bundle-offers/{{bundle_offer_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "discount_percentage": 25,
    "is_active": false
}
```

6. **Delete Bundle Offer**
```json
DELETE {{base_url}}/api/promotions/bundle-offers/{{bundle_offer_id}}/
Authorization: Token {{token}}
```

## Coupon Usages Endpoints
7. **Get All Coupon Usages**
```json
GET {{base_url}}/api/promotions/coupon-usages/
Authorization: Token {{token}}
```

8. **Get Specific Coupon Usage**
```json
GET {{base_url}}/api/promotions/coupon-usages/{{coupon_usage_id}}/
Authorization: Token {{token}}
```

## Coupons Endpoints
9. **Get All Coupons**
```json
GET {{base_url}}/api/promotions/coupons/
Authorization: Token {{token}}
```

10. **Create Coupon**
```json
POST {{base_url}}/api/promotions/coupons/
Authorization: Token {{token}}
Content-Type: application/json

{
    "code": "SUMMER2024",
    "discount_type": "percentage",
    "discount_value": 15,
    "min_order_amount": 50,
    "max_discount": 25,
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-08-31T23:59:59Z",
    "usage_limit": 100,
    "is_active": true
}
```

11. **Get Specific Coupon**
```json
GET {{base_url}}/api/promotions/coupons/{{coupon_id}}/
Authorization: Token {{token}}
```

12. **Update Coupon (Full Update)**
```json
PUT {{base_url}}/api/promotions/coupons/{{coupon_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "code": "SUMMER2024",
    "discount_type": "fixed",
    "discount_value": 10,
    "min_order_amount": 30,
    "max_discount": null,
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-08-31T23:59:59Z",
    "usage_limit": 200,
    "is_active": true
}
```

13. **Update Coupon (Partial Update)**
```json
PATCH {{base_url}}/api/promotions/coupons/{{coupon_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "usage_limit": 150,
    "is_active": false
}
```

14. **Delete Coupon**
```json
DELETE {{base_url}}/api/promotions/coupons/{{coupon_id}}/
Authorization: Token {{token}}
```

15. **Validate Coupon**
```json
POST {{base_url}}/api/promotions/coupons/validate/
Authorization: Token {{token}}
Content-Type: application/json

{
    "code": "SUMMER2024",
    "order_amount": 75
}
```
## Promo Banners Endpoints
16. **Get All Promo Banners**
```json
GET {{base_url}}/api/promotions/promo-banners/
Authorization: Token {{token}}
```

17. **Create Promo Banner**
```json
POST {{base_url}}/api/promotions/promo-banners/
Authorization: Token {{token}}
Content-Type: application/json

{
    "title": "Summer Sale",
    "description": "Up to 50% off on summer collection",
    "image_url": "https://example.com/images/summer-sale.jpg",
    "target_url": "/summer-collection",
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-08-31T23:59:59Z",
    "is_active": true,
    "display_order": 1
}
```

18. **Get Specific Promo Banner**
```json
GET {{base_url}}/api/promotions/promo-banners/{{promo_banner_id}}/
Authorization: Token {{token}}
```

19. **Update Promo Banner (Full Update)**
```json
PUT {{base_url}}/api/promotions/promo-banners/{{promo_banner_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "title": "Summer Sale 2024",
    "description": "Up to 60% off on summer collection",
    "image_url": "https://example.com/images/summer-sale-2024.jpg",
    "target_url": "/summer-2024",
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-08-31T23:59:59Z",
    "is_active": true,
    "display_order": 2
}
```

20. **Update Promo Banner (Partial Update)**
```json
PATCH {{base_url}}/api/promotions/promo-banners/{{promo_banner_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "is_active": false,
    "display_order": 3
}
```

21. **Delete Promo Banner**
```json
DELETE {{base_url}}/api/promotions/promo-banners/{{promo_banner_id}}/
Authorization: Token {{token}}
```

22. **Get Active Promo Banners**
```json
GET {{base_url}}/api/promotions/promo-banners/active/
Authorization: Token {{token}}
```

## Promotion Types Endpoints
23.  **Get All Promotion Types**
```json
GET {{base_url}}/api/promotions/promotion-types/
Authorization: Token {{token}}
```

24. **Create Promotion Type**
```json
POST {{base_url}}/api/promotions/promotion-types/
Authorization: Token {{token}}
Content-Type: application/json

{
    "name": "Seasonal Discount",
    "description": "Discounts based on seasons",
    "is_active": true
}
```

25. **Get Specific Promotion Type**
```json
GET {{base_url}}/api/promotions/promotion-types/{{promotion_type_id}}/
Authorization: Token {{token}}
```

26. **Update Promotion Type (Full Update)**
```json
PUT {{base_url}}/api/promotions/promotion-types/{{promotion_type_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "name": "Seasonal Sale",
    "description": "Special discounts for seasonal products",
    "is_active": true
}
``` 

27. **Update Promotion Type (Partial Update)**
```json
PATCH {{base_url}}/api/promotions/promotion-types/{{promotion_type_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "is_active": false
}
``` 

28. **Delete Promotion Type**
```json
DELETE {{base_url}}/api/promotions/promotion-types/{{promotion_type_id}}/
Authorization: Token {{token}}
```

## Promotion Usages Endpoints
29. **Get All Promotion Usages**
```json
GET {{base_url}}/api/promotions/promotion-usages/
Authorization: Token {{token}}
```

30. **Get Specific Promotion Usage**
```json
GET {{base_url}}/api/promotions/promotion-usages/{{promotion_usage_id}}/
Authorization: Token {{token}}
```

## Promotions Endpoints
31. **Get All Promotions**
```json
GET {{base_url}}/api/promotions/promotions/
Authorization: Token {{token}}
```

32. **Create Promotion**
```json
POST {{base_url}}/api/promotions/promotions/
Authorization: Token {{token}}
Content-Type: application/json

{
    "name": "Summer Sale 2024",
    "description": "Annual summer discount event",
    "promotion_type": 1,
    "discount_value": 20,
    "min_order_amount": 0,
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-08-31T23:59:59Z",
    "is_active": true
}
```

33. **Get Specific Promotion**
```json
GET {{base_url}}/api/promotions/promotions/{{promotion_id}}/
Authorization: Token {{token}}
```

34. **Update Promotion (Full Update)**
```json
PUT {{base_url}}/api/promotions/promotions/{{promotion_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "name": "Summer Sale 2024 Extended",
    "description": "Extended summer discount event",
    "promotion_type": 1,
    "discount_value": 25,
    "min_order_amount": 25,
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-09-15T23:59:59Z",
    "is_active": true

}
```

35. **Update Promotion (Partial Update)**
```json
PATCH {{base_url}}/api/promotions/promotions/{{promotion_id}}/
Authorization: Token {{token}}
Content-Type: application/json

{
    "discount_value": 30,
    "end_date": "2024-09-30T23:59:59Z"
}
```

36. **Delete Promotion**
```json
DELETE {{base_url}}/api/promotions/promotions/{{promotion_id}}/
Authorization: Token {{token}}
```
37. **Get Applicable Products for Promotion**
```json
GET {{base_url}}/api/promotions/promotions/{{promotion_id}}/applicable_products/
Authorization: Token {{token}}
```

38. **Get Active Promotions**
```json
GET {{base_url}}/api/promotions/promotions/active/
Authorization: Token {{token}}
```

## Public Promotions Endpoints (No Authentication Required)
39. **Get All Active Public Promotions**
```json
GET {{base_url}}/api/promotions/public/promotions/all_active/
```

40. **Get Promotions for Specific Product**
```json
GET {{base_url}}/api/promotions/public/promotions/for_product/{{product_id}}/
```
