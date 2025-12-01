"""File Conversion Operations"""
import os
import logging
from pdf2docx import Converter as PDFToWordConverter
from docx2pdf import convert as word_to_pdf_convert
from PIL import Image
from database import get_db_connection
from flask import session

logger = logging.getLogger(__name__)


def convert_file(file_path, conversion_type):
    """Convert file based on conversion type with proper logging"""
    output_path = os.path.splitext(file_path)[0]
    
    try:
        logger.info(f"Starting conversion: {conversion_type} for {os.path.basename(file_path)}")
        
        if conversion_type == 'pdf-to-word':
            output_path += '.docx'
            cv = PDFToWordConverter(file_path)
            cv.convert(output_path)
            cv.close()
            logger.info(f"PDF to Word conversion successful: {output_path}")
            
        elif conversion_type == 'word-to-pdf':
            try:
                output_path += '.pdf'
                word_to_pdf_convert(file_path, output_path)
                logger.info(f"Word to PDF conversion successful: {output_path}")
            except Exception as e:
                # This usually fails on Linux/Render since MS Word isn't installed
                error_msg = str(e)
                logger.error(f"Word to PDF conversion failed: {error_msg}")
                # Return special marker to indicate deployment limitation
                if 'not implemented' in error_msg.lower() or 'linux' in error_msg.lower() or 'windows' in error_msg.lower():
                    return 'NOT_AVAILABLE_ON_DEPLOYMENT'
                return None
            
        elif conversion_type == 'image-to-pdf':
            output_path += '.pdf'
            image = Image.open(file_path)
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            image.save(output_path, 'PDF', resolution=100.0)
            logger.info(f"Image to PDF conversion successful: {output_path}")
        else:
            logger.error(f"Unknown conversion type: {conversion_type}")
            return None
        
        return output_path
    except Exception as e:
        logger.error(f"Conversion error ({conversion_type}): {str(e)}", exc_info=True)
        return None


def log_conversion(filename, conversion_type, output_file):
    """Log file conversion to database"""
    try:
        output_filename = os.path.basename(output_file)
        user_id = session.get('user_id')
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO conversions (filename, conversion_type, output_file, user_id) VALUES (?, ?, ?, ?)',
            (filename, conversion_type, output_filename, user_id)
        )
        conn.commit()
        conn.close()
        logger.info(f"Conversion logged: {filename} -> {conversion_type} (user_id={user_id})")
    except Exception as e:
        logger.error(f"Error logging conversion: {str(e)}", exc_info=True)    
