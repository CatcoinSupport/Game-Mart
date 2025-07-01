import os
import logging
from datetime import datetime
from models import SiteSettings

logger = logging.getLogger(__name__)

def send_email(to_email, subject, text_content=None, html_content=None):
    """
    Send email using local email logging (alternative to SendGrid)
    """
    try:
        # Get sender email from settings or use default
        from_email = SiteSettings.get_setting('sender_email', 'noreply@marketplace.com')
        
        # Create email content
        content = html_content if html_content else text_content
        if not content:
            logger.error("No email content provided")
            return False
        
        # Log email to file instead of sending (since SendGrid is not available)
        email_log = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'from': from_email,
            'to': to_email,
            'subject': subject,
            'content': content
        }
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Write to email log file
        with open('logs/emails.log', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Time: {email_log['timestamp']}\n")
            f.write(f"From: {email_log['from']}\n")
            f.write(f"To: {email_log['to']}\n")
            f.write(f"Subject: {email_log['subject']}\n")
            f.write(f"Content:\n{email_log['content']}\n")
            f.write(f"{'='*50}\n")
        
        logger.info(f"Email logged successfully to logs/emails.log for {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Email logging error: {e}")
        return False

def send_order_notification(order, status_change=False):
    """
    Send order notification email to user
    """
    try:
        if status_change:
            subject = f"Order #{order.id} Status Update - {order.status.title()}"
            if order.status == 'accepted':
                html_content = f"""
                <h2>Great News! Your Order Has Been Accepted</h2>
                <p>Dear {order.user.username},</p>
                <p>Your order #{order.id} has been accepted and is being processed.</p>
                <p><strong>Order Details:</strong></p>
                <ul>
                """
                for item in order.order_items:
                    html_content += f"<li>{item.product.name} x {item.quantity} - ${item.price * item.quantity:.2f}"
                    if item.custom_input_value:
                        html_content += f" (Input: {item.custom_input_value})"
                    html_content += "</li>"
                
                html_content += f"""
                </ul>
                <p><strong>Total Amount:</strong> ${order.total_amount:.2f}</p>
                <p>You should receive your digital goods shortly. If you have any questions, please contact our support team.</p>
                <p>Thank you for your business!</p>
                """
            elif order.status == 'rejected':
                html_content = f"""
                <h2>Order Update Required</h2>
                <p>Dear {order.user.username},</p>
                <p>Unfortunately, your order #{order.id} requires attention.</p>
                <p>Please check your payment confirmation and contact our support team if you need assistance.</p>
                <p><strong>Order Total:</strong> ${order.total_amount:.2f}</p>
                <p>Payment ID: {order.payment_id}</p>
                """
        else:
            subject = f"Order Confirmation #{order.id}"
            html_content = f"""
            <h2>Order Confirmation</h2>
            <p>Dear {order.user.username},</p>
            <p>Thank you for your order! We've received your payment confirmation and are reviewing it.</p>
            <p><strong>Order #:</strong> {order.id}</p>
            <p><strong>Order Details:</strong></p>
            <ul>
            """
            for item in order.order_items:
                html_content += f"<li>{item.product.name} x {item.quantity} - ${item.price * item.quantity:.2f}"
                if item.custom_input_value:
                    html_content += f" (Input: {item.custom_input_value})"
                html_content += "</li>"
            
            html_content += f"""
            </ul>
            <p><strong>Total Amount:</strong> ${order.total_amount:.2f}</p>
            <p><strong>Payment ID:</strong> {order.payment_id}</p>
            <p>We'll review your payment confirmation and update you on the status soon.</p>
            """
        
        return send_email(order.user.email, subject, html_content=html_content)
        
    except Exception as e:
        logger.error(f"Error sending order notification: {e}")
        return False
