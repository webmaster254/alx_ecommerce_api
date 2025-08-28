# E-Commerce API - Database Entity Relationship Diagram

## Complete System ERD

### Mermaid Interactive Diagram
```mermaid
erDiagram
    %% ==================== USERS APP ====================
    CUSTOM_USER {
        int id PK
        string email UK
        string role
        date date_of_birth
        char gender
        string phone_number
        bool accepts_marketing
        bool email_verified
        bool phone_verified
        bool is_active
        string last_login_ip
        string registration_ip
        datetime date_joined
        string profile_picture
        string loyalty_tier
        text internal_note
    }

    USER_PROFILE {
        int id PK
        int user_id FK
        text shipping_address
        text billing_address
        string preferred_payment_method
        json cart
        bool newsletter_subscription
        int loyalty_points
    }

    %% ==================== PRODUCTS APP ====================
    CATEGORY {
        int id PK
        string name UK
        text description
        string slug UK
        datetime created_at
        datetime updated_at
    }

    PRODUCT {
        int id PK
        string name
        string slug UK
        text description
        decimal price
        decimal compare_price
        string sku UK
        int quantity
        string status
        bool is_featured
        datetime created_at
        datetime updated_at
    }

    %% ==================== ORDERS APP ====================
    ORDER {
        int id PK
        int user_id FK
        string order_number UK
        string status
        string payment_status
        decimal total
        string payment_method
        datetime created_at
        datetime updated_at
    }

    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal price
    }

    %% ==================== RELATIONSHIPS ====================
    CUSTOM_USER ||--|| USER_PROFILE : "has"
    CUSTOM_USER ||--o{ ORDER : "places"
    CATEGORY ||--o{ PRODUCT : "categorizes"
    ORDER ||--o{ ORDER_ITEM : "contains"
    ORDER_ITEM }|--|| PRODUCT : "is_a"
```

### Full Detailed Diagram
![Complete E-Commerce ERD Diagram](https://github.com/Dama5323/alx_ecommerce_api/raw/main/CAPSTONE%20PROJECT%20ERD.png)

## Database Schema Overview

This ERD represents the complete database structure for the E-Commerce API application, showing all entities, their attributes, and relationships.

## Key Database Features

### 1. **User Management**
- **CUSTOM_USER**: Extended user model with authentication and profile data
- **USER_PROFILE**: Additional user information and preferences

### 2. **Product Management**
- **CATEGORY**: Product categorization system
- **PRODUCT**: Comprehensive product information with inventory tracking

### 3. **Order Management**
- **ORDER**: Customer order information and status tracking
- **ORDER_ITEM**: Individual items within orders with pricing

### 4. **Relationships**
- One-to-One: User ↔ UserProfile
- One-to-Many: User → Orders, Category → Products, Order → OrderItems
- Many-to-One: OrderItems → Product

## Database Tables Summary

| Table | Purpose | Key Features |
|-------|---------|--------------|
| `custom_user` | User authentication | Email, role, verification status |
| `user_profile` | Extended user data | Addresses, preferences, loyalty |
| `category` | Product categories | Hierarchical organization |
| `product` | Product information | Pricing, inventory, variants |
| `order` | Customer orders | Status tracking, payment info |
| `order_item` | Order line items | Quantity, price at time of order |

## Data Integrity
- Unique constraints prevent duplicate entries
- Foreign key relationships maintain referential integrity
- Validation ensures data consistency across related tables

This ERD provides a comprehensive view of the e-commerce database structure, supporting all major features including user management, product catalog, and order processing.