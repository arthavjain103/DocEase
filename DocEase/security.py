import os
from werkzeug.utils import secure_filename

# File extension sets for different operations
PDF_EXTENSIONS = {'pdf'}
WORD_EXTENSIONS = {'docx', 'doc'}
IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png'}
CSV_EXTENSIONS = {'csv'}
CONVERTER_EXTENSIONS = {'pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png', 'csv'}
PDF_EDITOR_EXTENSIONS = {'pdf'}  # PDF editor only works with PDFs


def validate_upload_path(filename, upload_folder):
    """Validate and secure the upload path to prevent path traversal attacks."""
    secure_name = secure_filename(filename)
    if not secure_name:
        raise ValueError(f"Invalid filename: {filename}")

    filepath = os.path.join(upload_folder, secure_name)
    abs_filepath = os.path.abspath(filepath)
    abs_upload_folder = os.path.abspath(upload_folder)

    if not abs_filepath.startswith(abs_upload_folder):
        raise ValueError(f"Path traversal attempt detected: {filename}")

    return filepath


def is_valid_pdf(file_path):
    """Validate that a file is actually a PDF by checking magic bytes."""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except Exception:
        return False


def validate_file_size(file_path, max_size):
    """Validate that file doesn't exceed maximum size."""
    try:
        file_size = os.path.getsize(file_path)
        return file_size <= max_size
    except Exception:
        return False


def allowed_file(filename, allowed_extensions):
    """Check if file has an allowed extension."""
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions


def get_file_extension(filename):
    """Get the file extension from a filename (lowercase)."""
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()
