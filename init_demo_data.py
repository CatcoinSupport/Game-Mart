#!/usr/bin/env python3
"""
Initialize demo data for the digital goods marketplace
"""

from app import app, db
from models import Section, Product, PaymentMethod, SiteSettings

def init_demo_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create sections
        sections_data = [
            {
                'name': 'Free Fire',
                'description': 'Free Fire diamonds, characters, and bundles'
            },
            {
                'name': 'PUBG Mobile',
                'description': 'PUBG Mobile UC, royale passes, and skins'
            },
            {
                'name': 'Mobile Legends',
                'description': 'Mobile Legends diamonds and skins'
            },
            {
                'name': 'Gift Cards',
                'description': 'Digital gift cards for various platforms'
            },
            {
                'name': 'Crypto Currency',
                'description': 'Digital cryptocurrency vouchers'
            }
        ]
        
        created_sections = {}
        for section_data in sections_data:
            section = Section(
                name=section_data['name'],
                description=section_data['description']
            )
            db.session.add(section)
            db.session.flush()
            created_sections[section_data['name']] = section
        
        # Create products
        products_data = [
            {
                'name': '100 Free Fire Diamonds',
                'description': 'Get 100 diamonds instantly for Free Fire. Perfect for buying characters and weapons.',
                'price': 2.99,
                'quantity': 50,
                'section': 'Free Fire',
                'is_featured': True,
                'custom_input_label': 'Free Fire Player ID',
                'custom_input_placeholder': 'Enter your Free Fire Player ID',
                'custom_input_required': True,
                'admin_description': 'Please enter your Free Fire Player ID to receive diamonds'
            },
            {
                'name': '500 Free Fire Diamonds',
                'description': 'Get 500 diamonds for Free Fire. Great value pack for serious players.',
                'price': 12.99,
                'quantity': 30,
                'section': 'Free Fire',
                'is_featured': True,
                'custom_input_label': 'Free Fire Player ID',
                'custom_input_placeholder': 'Enter your Free Fire Player ID',
                'custom_input_required': True,
                'admin_description': 'Please enter your Free Fire Player ID to receive diamonds'
            },
            {
                'name': '60 PUBG Mobile UC',
                'description': 'Unknown Cash for PUBG Mobile. Buy skins, crates, and royale pass.',
                'price': 1.99,
                'quantity': 40,
                'section': 'PUBG Mobile',
                'is_featured': False,
                'custom_input_label': 'PUBG Mobile Player ID',
                'custom_input_placeholder': 'Enter your PUBG Mobile Player ID',
                'custom_input_required': True,
                'admin_description': 'Please enter your PUBG Mobile Player ID to receive UC'
            },
            {
                'name': '300 PUBG Mobile UC',
                'description': 'Premium UC pack for PUBG Mobile. Perfect for royale pass and premium crates.',
                'price': 8.99,
                'quantity': 25,
                'section': 'PUBG Mobile',
                'is_featured': True,
                'custom_input_label': 'PUBG Mobile Player ID',
                'custom_input_placeholder': 'Enter your PUBG Mobile Player ID',
                'custom_input_required': True,
                'admin_description': 'Please enter your PUBG Mobile Player ID to receive UC'
            },
            {
                'name': '100 Mobile Legends Diamonds',
                'description': 'Diamonds for Mobile Legends. Buy heroes, skins, and battle passes.',
                'price': 3.49,
                'quantity': 35,
                'section': 'Mobile Legends',
                'is_featured': False,
                'custom_input_label': 'Mobile Legends User ID',
                'custom_input_placeholder': 'Enter your Mobile Legends User ID',
                'custom_input_required': True,
                'admin_description': 'Please enter your Mobile Legends User ID and Zone ID'
            },
            {
                'name': '$10 Google Play Gift Card',
                'description': 'Digital Google Play gift card. Use for apps, games, movies, and more.',
                'price': 10.99,
                'quantity': 20,
                'section': 'Gift Cards',
                'is_featured': False,
                'custom_input_label': 'Email Address',
                'custom_input_placeholder': 'Enter email to receive gift card',
                'custom_input_required': True,
                'admin_description': 'Please enter your email address to receive the gift card code'
            },
            {
                'name': '$25 Steam Gift Card',
                'description': 'Steam digital gift card. Perfect for buying games and in-game content.',
                'price': 26.99,
                'quantity': 15,
                'section': 'Gift Cards',
                'is_featured': True,
                'custom_input_label': 'Steam Username',
                'custom_input_placeholder': 'Enter your Steam username',
                'custom_input_required': True,
                'admin_description': 'Please enter your Steam username to receive the gift card'
            },
            {
                'name': '$5 Bitcoin Voucher',
                'description': 'Digital Bitcoin voucher. Redeem for cryptocurrency in your wallet.',
                'price': 5.50,
                'quantity': 10,
                'section': 'Crypto Currency',
                'is_featured': False,
                'custom_input_label': 'Bitcoin Wallet Address',
                'custom_input_placeholder': 'Enter your Bitcoin wallet address',
                'custom_input_required': True,
                'admin_description': 'Please enter your Bitcoin wallet address to receive the voucher'
            }
        ]
        
        for product_data in products_data:
            section = created_sections[product_data['section']]
            product = Product(
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                quantity=product_data['quantity'],
                section_id=section.id,
                is_featured=product_data['is_featured'],
                custom_input_label=product_data['custom_input_label'],
                custom_input_placeholder=product_data['custom_input_placeholder'],
                custom_input_required=product_data['custom_input_required'],
                admin_description=product_data['admin_description']
            )
            db.session.add(product)
        
        # Create payment methods
        payment_methods_data = [
            {
                'name': 'Bitcoin',
                'wallet_address': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
                'description': 'Pay with Bitcoin - fast and secure',
                'is_active': True
            },
            {
                'name': 'Ethereum',
                'wallet_address': '0x742d35CC6634C0532925a3b8D4c35c8C0F2C0C0C',
                'description': 'Pay with Ethereum - low fees',
                'is_active': True
            },
            {
                'name': 'Payeer',
                'wallet_address': 'P1234567890',
                'description': 'Payeer digital wallet payments',
                'is_active': True
            },
            {
                'name': 'Perfect Money',
                'wallet_address': 'U1234567',
                'description': 'Perfect Money instant payments',
                'is_active': True
            }
        ]
        
        for method_data in payment_methods_data:
            payment_method = PaymentMethod(
                name=method_data['name'],
                wallet_address=method_data['wallet_address'],
                description=method_data['description'],
                is_active=method_data['is_active']
            )
            db.session.add(payment_method)
        
        # Create site settings
        settings_data = [
            {
                'key': 'site_description',
                'value': 'Welcome to GameMart - Your trusted marketplace for game codes, digital currencies, and gift cards. Fast delivery, secure payments, and 24/7 support.'
            },
            {
                'key': 'sender_email',
                'value': 'noreply@gamemart.com'
            }
        ]
        
        for setting_data in settings_data:
            setting = SiteSettings(
                key=setting_data['key'],
                value=setting_data['value']
            )
            db.session.add(setting)
        
        # Commit all changes
        db.session.commit()
        print("Demo data initialized successfully!")
        print("Created:")
        print(f"- {len(sections_data)} sections")
        print(f"- {len(products_data)} products")
        print(f"- {len(payment_methods_data)} payment methods")
        print(f"- {len(settings_data)} site settings")

if __name__ == '__main__':
    init_demo_data()