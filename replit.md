# Digital Goods Marketplace

## Overview

This is a Flask-based digital goods marketplace application designed for selling gaming-related digital products. The application features a modern, gaming-themed user interface with full e-commerce functionality including user authentication, product management, shopping cart, order processing, and admin panel.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive design
- **Styling**: Gaming-themed CSS with custom variables and gradients
- **JavaScript**: Vanilla JavaScript with Bootstrap components for interactivity
- **UI Framework**: Bootstrap 5.1.3 with Font Awesome 6.0.0 icons

### Backend Architecture
- **Framework**: Flask 3.1.1 with SQLAlchemy ORM
- **Database**: SQLite (default) with PostgreSQL support via psycopg2-binary
- **Authentication**: Flask-Login for session management
- **File Handling**: Werkzeug for secure file uploads with Pillow for image processing
- **Email Service**: SendGrid integration for transactional emails

### Database Schema
- **Users**: Authentication and role management (admin/customer)
- **Sections**: Product categories/sections
- **Products**: Digital goods with custom input fields for gaming accounts
- **Orders & OrderItems**: Order management with status tracking
- **PaymentMethod**: Multiple payment options (likely crypto wallets)
- **SiteSettings**: Configurable site-wide settings

## Key Components

### Authentication System
- User registration and login with password hashing
- Role-based access control (admin/customer)
- Session management with Flask-Login
- First registered user automatically becomes admin

### Product Management
- Hierarchical product organization with sections
- Image upload with automatic resizing (800x600 max)
- Featured products for homepage display
- Custom input fields for gaming account information
- Stock quantity tracking
- Admin-only product descriptions

### Shopping Cart & Orders
- Session-based cart management
- Multi-step checkout process
- Custom input collection (gaming IDs, usernames)
- Order status tracking (pending/accepted/rejected)
- Email notifications for order updates

### Payment Integration
- Multiple payment method support
- File upload for payment confirmations
- Admin order review and approval system

### Admin Panel
- Comprehensive dashboard with statistics
- Product, section, and user management
- Order processing and status updates
- Site settings configuration
- Payment method management

## Data Flow

1. **User Registration/Login**: Creates session, redirects to products
2. **Product Browsing**: Filtered by sections, add to cart functionality
3. **Cart Management**: Session-stored items with quantity control
4. **Checkout Process**: Order creation, payment method selection
5. **Order Processing**: Admin review, status updates, email notifications
6. **Admin Management**: CRUD operations on all entities

## External Dependencies

### Required Services
- **SendGrid**: Email delivery service (API key required)
- **File Storage**: Local uploads directory structure

### Python Dependencies
- Flask ecosystem (Flask, SQLAlchemy, Login)
- Database drivers (psycopg2-binary for PostgreSQL)
- Image processing (Pillow)
- Email service (SendGrid)
- Security utilities (Werkzeug)

### Frontend Dependencies
- Bootstrap 5.1.3 (CDN)
- Font Awesome 6.0.0 (CDN)

## Deployment Strategy

### Development Setup
- Uses Gunicorn WSGI server
- SQLite database for local development
- Debug mode enabled in main.py
- File uploads to local directories

### Production Configuration
- Gunicorn with autoscale deployment target
- Environment variables for sensitive data:
  - `SESSION_SECRET`: Flask session encryption
  - `DATABASE_URL`: Database connection string
  - `SENDGRID_API_KEY`: Email service authentication
- ProxyFix middleware for reverse proxy deployment
- Connection pooling and health checks configured

### File Upload Structure
- `/uploads/products/`: Product images
- `/uploads/payments/`: Payment confirmation files
- 16MB maximum file size limit
- Automatic image optimization and resizing

## Changelog
- June 26, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.