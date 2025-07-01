import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import logging

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_folder, max_size=(800, 600)):
    """
    Save uploaded file with unique filename and optional resizing
    """
    if not file or not allowed_file(file.filename):
        return None
    
    try:
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(upload_folder, unique_filename)
        
        # Save the file
        file.save(filepath)
        
        # Resize image if it's too large (for product images)
        if upload_folder.endswith('products'):
            try:
                with Image.open(filepath) as img:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(filepath, optimize=True, quality=85)
            except Exception as e:
                logger.warning(f"Could not resize image {filepath}: {e}")
        
        logger.info(f"File saved successfully: {unique_filename}")
        return unique_filename
        
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None

def delete_file(filename, upload_folder):
    """
    Delete file from upload folder
    """
    try:
        if filename:
            filepath = os.path.join(upload_folder, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"File deleted: {filename}")
                return True
    except Exception as e:
        logger.error(f"Error deleting file {filename}: {e}")
    return False

def format_currency(amount):
    """Format currency for display"""
    return f"${amount:.2f}"

def calculate_cart_total(cart_items):
    """Calculate total amount for cart items"""
    total = 0
    for item in cart_items:
        total += item['price'] * item['quantity']
    return total
