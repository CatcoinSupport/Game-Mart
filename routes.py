import os
from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Product, Section, PaymentMethod, Order, OrderItem, SiteSettings
from utils import save_uploaded_file, delete_file, calculate_cart_total
from email_service import send_order_notification
import logging

logger = logging.getLogger(__name__)

# Auth routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        # First user becomes admin
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Main routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        featured_products = Product.query.filter_by(is_featured=True).all()
        payment_methods = PaymentMethod.query.filter_by(is_active=True).all()
        site_description = SiteSettings.get_setting('site_description', 
            'Welcome to our Digital Goods Marketplace - Your trusted source for game codes, digital currencies, and more!')
        
        return render_template('index.html', 
                             featured_products=featured_products,
                             payment_methods=payment_methods,
                             site_description=site_description)
    else:
        # Show landing page for non-authenticated users
        site_description = SiteSettings.get_setting('site_description', 
            'Welcome to our Digital Goods Marketplace - Your trusted source for game codes, digital currencies, and more!')
        return render_template('index.html', 
                             featured_products=[],
                             payment_methods=[],
                             site_description=site_description)

@app.route('/products')
@login_required
def products():
    sections = Section.query.all()
    selected_section = request.args.get('section', type=int)
    
    if selected_section:
        products_list = Product.query.filter_by(section_id=selected_section).all()
        section_name = Section.query.get(selected_section).name
    else:
        products_list = Product.query.all()
        section_name = "All Products"
    
    return render_template('products.html', 
                         sections=sections,
                         products=products_list,
                         selected_section=selected_section,
                         section_name=section_name)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    custom_input_value = request.form.get('custom_input', '')
    
    # Validate custom input if required
    if product.custom_input_required and not custom_input_value.strip():
        flash(f'{product.custom_input_label} is required for this product', 'error')
        return redirect(url_for('products'))
    
    # Check stock
    if quantity > product.quantity:
        flash('Not enough stock available', 'error')
        return redirect(url_for('products'))
    
    # Initialize cart in session
    if 'cart' not in session:
        session['cart'] = []
    
    # Check if product already in cart
    cart = session['cart']
    for item in cart:
        if item['product_id'] == product_id and item['custom_input_value'] == custom_input_value:
            item['quantity'] += quantity
            break
    else:
        cart.append({
            'product_id': product_id,
            'quantity': quantity,
            'custom_input_value': custom_input_value,
            'price': product.price
        })
    
    session['cart'] = cart
    session.modified = True
    
    flash(f'{product.name} added to cart', 'success')
    return redirect(url_for('products'))

@app.route('/cart')
@login_required
def cart():
    cart_items = []
    total = 0
    
    if 'cart' in session:
        for item in session['cart']:
            product = Product.query.get(item['product_id'])
            if product:
                cart_item = {
                    'product': product,
                    'quantity': item['quantity'],
                    'custom_input_value': item['custom_input_value'],
                    'price': item['price'],
                    'subtotal': item['price'] * item['quantity']
                }
                cart_items.append(cart_item)
                total += cart_item['subtotal']
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    if 'cart' in session:
        cart = session['cart']
        session['cart'] = [item for item in cart if item['product_id'] != product_id]
        session.modified = True
        flash('Item removed from cart', 'info')
    
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty', 'error')
        return redirect(url_for('products'))
    
    cart_items = []
    total = 0
    
    for item in session['cart']:
        product = Product.query.get(item['product_id'])
        if product:
            cart_item = {
                'product': product,
                'quantity': item['quantity'],
                'custom_input_value': item['custom_input_value'],
                'price': item['price'],
                'subtotal': item['price'] * item['quantity']
            }
            cart_items.append(cart_item)
            total += cart_item['subtotal']
    
    payment_methods = PaymentMethod.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        payment_method_id = request.form.get('payment_method_id')
        payment_id = request.form.get('payment_id', '').strip()
        payment_confirmation = request.files.get('payment_confirmation')
        
        # Validate inputs
        if not payment_method_id:
            flash('Please select a payment method', 'error')
            return render_template('checkout.html', cart_items=cart_items, total=total, payment_methods=payment_methods)
        
        if not payment_id:
            flash('Payment ID is required', 'error')
            return render_template('checkout.html', cart_items=cart_items, total=total, payment_methods=payment_methods)
        
        if not payment_confirmation or payment_confirmation.filename == '':
            flash('Payment confirmation image is required', 'error')
            return render_template('checkout.html', cart_items=cart_items, total=total, payment_methods=payment_methods)
        
        # Save payment confirmation image
        confirmation_filename = save_uploaded_file(payment_confirmation, app.config['PAYMENT_UPLOAD_FOLDER'])
        if not confirmation_filename:
            flash('Invalid payment confirmation image', 'error')
            return render_template('checkout.html', cart_items=cart_items, total=total, payment_methods=payment_methods)
        
        # Create order
        order = Order(
            user_id=current_user.id,
            payment_method_id=int(payment_method_id),
            total_amount=total,
            payment_id=payment_id,
            payment_confirmation_filename=confirmation_filename,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Add order items
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=item['price'],
                custom_input_value=item['custom_input_value']
            )
            db.session.add(order_item)
            
            # Update product quantity
            item['product'].quantity -= item['quantity']
        
        db.session.commit()
        
        # Send order confirmation email
        send_order_notification(order)
        
        # Clear cart
        session.pop('cart', None)
        session.modified = True
        
        flash(f'Order #{order.id} placed successfully! You will receive an email confirmation.', 'success')
        return redirect(url_for('index'))
    
    return render_template('checkout.html', cart_items=cart_items, total=total, payment_methods=payment_methods)

# File serving routes
@app.route('/uploads/products/<filename>')
def uploaded_product_file(filename):
    return send_from_directory(app.config['PRODUCT_UPLOAD_FOLDER'], filename)

@app.route('/uploads/payments/<filename>')
@login_required
def uploaded_payment_file(filename):
    # Only admins can view payment confirmations
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    return send_from_directory(app.config['PAYMENT_UPLOAD_FOLDER'], filename)

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Calculate statistics
    total_products = Product.query.count()
    total_sections = Section.query.count()
    total_users = User.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    total_profit = db.session.query(db.func.sum(Order.total_amount)).filter_by(status='accepted').scalar() or 0
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         total_sections=total_sections,
                         total_users=total_users,
                         pending_orders=pending_orders,
                         total_profit=total_profit,
                         recent_orders=recent_orders)

@app.route('/admin/products', methods=['GET', 'POST'])
@login_required
def admin_products():
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        section_id = int(request.form['section_id'])
        is_featured = 'is_featured' in request.form
        custom_input_label = request.form.get('custom_input_label', '').strip()
        custom_input_placeholder = request.form.get('custom_input_placeholder', '').strip()
        custom_input_required = 'custom_input_required' in request.form
        admin_description = request.form.get('admin_description', '').strip()
        image = request.files.get('image')
        
        # Save image if provided
        image_filename = None
        if image and image.filename:
            image_filename = save_uploaded_file(image, app.config['PRODUCT_UPLOAD_FOLDER'])
            if not image_filename:
                flash('Invalid image file', 'error')
                return redirect(url_for('admin_products'))
        
        product = Product(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            section_id=section_id,
            is_featured=is_featured,
            custom_input_label=custom_input_label,
            custom_input_placeholder=custom_input_placeholder,
            custom_input_required=custom_input_required,
            admin_description=admin_description,
            image_filename=image_filename
        )
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully', 'success')
        return redirect(url_for('admin_products'))
    
    products = Product.query.all()
    sections = Section.query.all()
    return render_template('admin/products.html', products=products, sections=sections)

@app.route('/admin/products/delete/<int:product_id>')
@login_required
def admin_delete_product(product_id):
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(product_id)
    
    # Delete product image
    if product.image_filename:
        delete_file(product.image_filename, app.config['PRODUCT_UPLOAD_FOLDER'])
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/sections', methods=['GET', 'POST'])
@login_required
def admin_sections():
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        
        section = Section(name=name, description=description)
        db.session.add(section)
        db.session.commit()
        
        flash('Section added successfully', 'success')
        return redirect(url_for('admin_sections'))
    
    sections = Section.query.all()
    return render_template('admin/sections.html', sections=sections)

@app.route('/admin/sections/delete/<int:section_id>')
@login_required
def admin_delete_section(section_id):
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    section = Section.query.get_or_404(section_id)
    
    # Delete all products in this section and their images
    for product in section.products:
        if product.image_filename:
            delete_file(product.image_filename, app.config['PRODUCT_UPLOAD_FOLDER'])
    
    db.session.delete(section)
    db.session.commit()
    
    flash('Section and all its products deleted successfully', 'success')
    return redirect(url_for('admin_sections'))

@app.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(status=status_filter).order_by(Order.created_at.desc()).all()
    
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)

@app.route('/admin/orders/update/<int:order_id>/<status>')
@login_required
def admin_update_order(order_id, status):
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if status not in ['pending', 'accepted', 'rejected']:
        flash('Invalid status', 'error')
        return redirect(url_for('admin_orders'))
    
    order = Order.query.get_or_404(order_id)
    old_status = order.status
    order.status = status
    db.session.commit()
    
    # Send status update email if status changed
    if old_status != status:
        send_order_notification(order, status_change=True)
    
    flash(f'Order #{order_id} status updated to {status}', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/payment_methods', methods=['GET', 'POST'])
@login_required
def admin_payment_methods():
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        wallet_address = request.form['wallet_address']
        description = request.form.get('description', '')
        is_active = 'is_active' in request.form
        
        payment_method = PaymentMethod(
            name=name,
            wallet_address=wallet_address,
            description=description,
            is_active=is_active
        )
        db.session.add(payment_method)
        db.session.commit()
        
        flash('Payment method added successfully', 'success')
        return redirect(url_for('admin_payment_methods'))
    
    payment_methods = PaymentMethod.query.all()
    return render_template('admin/payment_methods.html', payment_methods=payment_methods)

@app.route('/admin/payment_methods/delete/<int:method_id>')
@login_required
def admin_delete_payment_method(method_id):
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    payment_method = PaymentMethod.query.get_or_404(method_id)
    db.session.delete(payment_method)
    db.session.commit()
    
    flash('Payment method deleted successfully', 'success')
    return redirect(url_for('admin_payment_methods'))

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        site_description = request.form['site_description']
        sender_email = request.form['sender_email']
        
        SiteSettings.set_setting('site_description', site_description)
        SiteSettings.set_setting('sender_email', sender_email)
        
        flash('Settings updated successfully', 'success')
        return redirect(url_for('admin_settings'))
    
    site_description = SiteSettings.get_setting('site_description', 
        'Welcome to our Digital Goods Marketplace - Your trusted source for game codes, digital currencies, and more!')
    sender_email = SiteSettings.get_setting('sender_email', 'noreply@marketplace.com')
    
    users = User.query.all()
    return render_template('admin/settings.html', 
                         site_description=site_description,
                         sender_email=sender_email,
                         users=users)

@app.route('/admin/emails')
@login_required
def admin_emails():
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    emails = []
    try:
        if os.path.exists('logs/emails.log'):
            with open('logs/emails.log', 'r', encoding='utf-8') as f:
                content = f.read()
                # Parse email log entries
                entries = content.split('=' * 50)
                for entry in entries:
                    if entry.strip():
                        lines = entry.strip().split('\n')
                        email_data = {}
                        content_started = False
                        content_lines = []
                        
                        for line in lines:
                            if line.startswith('Time: '):
                                email_data['time'] = line.replace('Time: ', '')
                            elif line.startswith('From: '):
                                email_data['from'] = line.replace('From: ', '')
                            elif line.startswith('To: '):
                                email_data['to'] = line.replace('To: ', '')
                            elif line.startswith('Subject: '):
                                email_data['subject'] = line.replace('Subject: ', '')
                            elif line.startswith('Content:'):
                                content_started = True
                            elif content_started:
                                content_lines.append(line)
                        
                        if email_data.get('time'):
                            email_data['content'] = '\n'.join(content_lines)
                            emails.append(email_data)
                
                # Sort by time (newest first)
                emails.sort(key=lambda x: x.get('time', ''), reverse=True)
    except Exception as e:
        logger.error(f"Error reading email log: {e}")
    
    return render_template('admin/emails.html', emails=emails)
