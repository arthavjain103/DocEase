"""File Conversion Operations"""
import os
import logging
import platform
import shutil
import subprocess
from pdf2docx import Converter as PDFToWordConverter
from docx2pdf import convert as word_to_pdf_convert
from PIL import Image
from database import get_db_connection
from flask import session

logger = logging.getLogger(__name__)


def _convert_word_to_pdf_with_libreoffice(input_path, output_path):
    """Attempt DOCX->PDF conversion using LibreOffice/soffice CLI."""
    soffice = shutil.which('soffice') or shutil.which('libreoffice')
    if not soffice:
        logger.warning("LibreOffice (soffice) not found on PATH. Word->PDF conversion cannot be done on Linux without it.")
        return None

    outdir = os.path.dirname(output_path) or os.getcwd()
    try:
        cmd = [soffice, '--headless', '--convert-to', 'pdf', '--outdir', outdir, input_path]
        logger.debug(f"Running LibreOffice: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        produced_name = os.path.splitext(os.path.basename(input_path))[0] + '.pdf'
        produced_path = os.path.join(outdir, produced_name)
        if os.path.exists(produced_path):
            return produced_path
        logger.error(f"LibreOffice reported success but output not found: {produced_path}")
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"LibreOffice conversion failed: {e.stderr.decode(errors='ignore')}")
        return None


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
            output_path += '.pdf'
            system_name = platform.system().lower()
            if system_name.startswith('win'):
                try:
                    word_to_pdf_convert(file_path, output_path)
                    logger.info(f"Word to PDF conversion successful (docx2pdf): {output_path}")
                except Exception as e:
                    logger.error(f"docx2pdf failed: {e}")
                    return None
            else:
                # Linux / others
                produced = _convert_word_to_pdf_with_libreoffice(file_path, output_path)
                if produced:
                    output_path = produced
                    logger.info(f"Word to PDF conversion successful (LibreOffice): {output_path}")
                else:
                    logger.warning("Word->PDF conversion skipped: LibreOffice not installed on this Linux system.")
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
