"""DocEase - Flask Application with Modular Routes"""
# Compatibility fix for Python 3.10+ must be imported FIRST
import compatibility

from flask import Flask, render_template, send_from_directory
import os
import atexit
import logging
from dotenv import load_dotenv

# Import all route modules
from routes.authentication import init_auth_routes
from routes.converter import init_converter_routes
from routes.pdf_editor import init_pdf_editor_routes
from routes.utility import init_utility_routes

# Import database modules
from database import get_db_connection, init_db, init_users_table, migrate_users_column

# Import security functions
from security import (
    validate_upload_path,
    allowed_file,
    validate_file_size,
    is_valid_pdf,
    get_file_extension,
    PDF_EXTENSIONS,
    WORD_EXTENSIONS,
    IMAGE_EXTENSIONS,
    CONVERTER_EXTENSIONS,
    PDF_EDITOR_EXTENSIONS
)

# Import forms
from forms import UploadFileForm as UploadForm, EncryptPDFForm, DecryptPDFForm, RegisterForm, LoginForm

# Import converter and PDF operations
# Import converter and PDF operations
from converter_ops import convert_file, log_conversion
from pdf_ops import PDFOperations, EncryptOps, DecryptOps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24).hex())
UPLOAD_FOLDER = "/tmp/docease_uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE', 40)) * 1024 * 1024
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Use security module extension sets
ALLOWED_EXTENSIONS = CONVERTER_EXTENSIONS


def cleanup_uploads():
    """Clean up old upload files on shutdown"""
    try:
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                        logger.info(f"Cleaned up: {filepath}")
                except Exception as e:
                    logger.error(f"Failed to clean up file {filepath}: {str(e)}")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")


# Register cleanup function to run at shutdown
atexit.register(cleanup_uploads)


# Initialize Database
with app.app_context():
    init_db()
    init_users_table()
    migrate_users_column()


# Create wrapper functions for PDF operations with app config
def split_pdf(pdf_path, start_page=None, end_page=None):
    """Wrapper for PDF split"""
    return PDFOperations.split_pdf(pdf_path, app.config, start_page, end_page)


def merge_pdfs(pdf_files):
    """Wrapper for PDF merge"""
    return PDFOperations.merge_pdfs(pdf_files, app.config)


# Initialize all routes
init_auth_routes(app, get_db_connection, RegisterForm, LoginForm)

init_converter_routes(
    app, UploadForm, allowed_file, validate_upload_path, validate_file_size,
    is_valid_pdf, CONVERTER_EXTENSIONS, convert_file, log_conversion
)

init_pdf_editor_routes(
    app, get_db_connection, UploadForm, EncryptPDFForm, DecryptPDFForm,
    allowed_file, validate_upload_path, validate_file_size, is_valid_pdf,
    PDF_EDITOR_EXTENSIONS, split_pdf, merge_pdfs, convert_file, log_conversion,
    EncryptOps, DecryptOps
)

init_utility_routes(app, get_db_connection)


if __name__ == "__main__":
    from os import environ
    app.run(
        host="0.0.0.0",
        port=int(environ.get("PORT", 5000)),
    )
