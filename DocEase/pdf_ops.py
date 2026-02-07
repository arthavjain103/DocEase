"""PDF Operations - Split, Merge, Encrypt, Decrypt, Watermark, Rotate"""
import os
import zipfile
import logging
import csv
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from io import BytesIO
import uuid

logger = logging.getLogger(__name__)


class PDFOperations:
    """Core PDF operations"""
    
    @staticmethod
    def split_pdf(pdf_path, app_config, start_page=None, end_page=None):
        """Split PDF into individual pages and return as ZIP file"""
        try:
            with open(pdf_path, "rb") as f:
                reader = PdfReader(f)
                total_pages = len(reader.pages)
                
                if total_pages == 0:
                    logger.warning(f"PDF is empty: {os.path.basename(pdf_path)}")
                    return None
                
                # Validate page range
                start_page = start_page or 1
                end_page = end_page or total_pages
                
                # Convert to 0-based indexing
                start_idx = start_page - 1
                end_idx = end_page - 1
                
                # Validate range
                if start_idx < 0 or end_idx >= total_pages or start_idx > end_idx:
                    logger.error(f"Invalid page range: {start_page}-{end_page}. PDF has {total_pages} pages.")
                    return None
                
                # Create a zip file to store all split PDFs
                base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
                zip_filename = os.path.join(app_config['UPLOAD_FOLDER'], f"{base_filename}_pages_{start_page}-{end_page}.zip")
                
                logger.info(f"Starting PDF split: pages {start_page}-{end_page} from {base_filename}")
                
                with zipfile.ZipFile(zip_filename, 'w') as zip_file:
                    # Split each page in the range into a separate PDF
                    for page_num in range(start_idx, end_idx + 1):
                        select_page = reader.pages[page_num]
                        
                        writer = PdfWriter()
                        writer.add_page(select_page)
                        
                        # Create individual PDF file
                        individual_filename = f"{base_filename}_page_{page_num + 1}.pdf"
                        individual_path = os.path.join(app_config['UPLOAD_FOLDER'], individual_filename)
                        
                        with open(individual_path, "wb") as out:
                            writer.write(out)
                        
                        # Add to zip file
                        zip_file.write(individual_path, individual_filename)
                        
                        # Clean up individual file
                        os.remove(individual_path)
                        
                        logger.debug(f"Created PDF page {page_num + 1}: {individual_filename}")
                
                logger.info(f"PDF split successful. Pages {start_page}-{end_page} saved to: {zip_filename}")
                return zip_filename
                
        except Exception as e:
            logger.error(f"PDF splitting error: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def merge_pdfs(pdf_files, app_config):
        """
        Merge multiple PDF files into a single PDF.
        
        Args:
            pdf_files (list): List of file paths to PDF files.
            app_config (dict): Flask app config
            
        Returns:
            str or None: Path to the merged PDF file or None if error.
        """
        try:
            if not pdf_files or len(pdf_files) < 2:
                logger.warning("Need at least 2 PDF files to merge.")
                return None
            
            logger.info(f"Starting PDF merge for {len(pdf_files)} files")
            writer = PdfWriter()

            for pdf_file in pdf_files:
                if not os.path.exists(pdf_file):
                    logger.warning(f"Skipping missing file: {pdf_file}")
                    continue

                with open(pdf_file, "rb") as f:
                    reader = PdfReader(f)
                    for page in reader.pages:
                        writer.add_page(page)
                    logger.debug(f"Added {len(reader.pages)} pages from {os.path.basename(pdf_file)}")
            
            if not writer.pages:
                logger.error("No valid pages found to merge.")
                return None

            # Create unique output filename to avoid overwriting
            output_filename = os.path.join(
                app_config['UPLOAD_FOLDER'], 
                f"merged_pdf_{uuid.uuid4().hex}.pdf"
            )

            with open(output_filename, "wb") as output_file:
                writer.write(output_file)

            logger.info(f"PDF merge successful: {output_filename}")
            return output_filename

        except Exception as e:
            logger.error(f"PDF merging error: {str(e)}", exc_info=True)
            return None


class EncryptOps:
    """Encryption operations"""
    
    @staticmethod
    def encrypt(input_path, output_path, password):
        """Encrypt a PDF with password protection"""
        try:
            logger.info(f"Processing PDF encryption: {os.path.basename(input_path)}")
            
            reader = PdfReader(input_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            writer.encrypt(password)

            with open(output_path, 'wb') as f:
                writer.write(f)

            logger.info(f"PDF encrypted successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"PDF encryption error: {str(e)}")
            return False


class DecryptOps:
    """Decryption operations"""
    
    @staticmethod
    def decrypt(input_path, output_path, password):
        """Decrypt a password-protected PDF"""
        try:
            logger.info(f"Processing PDF decryption: {os.path.basename(input_path)}")

            reader = PdfReader(input_path)

            if reader.is_encrypted:
                if not reader.decrypt(password):
                    logger.warning(f"Decryption failed - incorrect password: {os.path.basename(input_path)}")
                    return False, "Incorrect password"

            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)

            with open(output_path, 'wb') as f:
                writer.write(f)

            logger.info(f"PDF decrypted successfully: {output_path}")
            return True, "Success"
            
        except Exception as e:
            logger.error(f"PDF decryption error: {str(e)}")
            return False, str(e)
        
class WatermarkOps:
    @staticmethod
    def add_text_watermark(input_path, output_path, text, opacity=0.2):
        try:
            from PyPDF2 import PdfReader, PdfWriter
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            import io

            reader = PdfReader(input_path)
            writer = PdfWriter()

            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=A4)
            c.setFillAlpha(opacity)
            c.setFont("Helvetica-Bold", 40)
            c.drawCentredString(300, 400, text)
            c.save()

            packet.seek(0)
            watermark = PdfReader(packet).pages[0]

            for page in reader.pages:
                page.merge_page(watermark)
                writer.add_page(page)

            with open(output_path, "wb") as f:
                writer.write(f)

            return True
        except Exception as e:
            logger.error(f"WatermarkOps error: {str(e)}")
            return False

class RotateOps:

    @staticmethod
    def rotate(input_path, output_path, angle):
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()

            for page in reader.pages:
                page.rotate(angle)
                writer.add_page(page)

            with open(output_path, "wb") as f:
                writer.write(f)

            return True
        except Exception:
            return False


class CSVToPDFOps:
    """CSV to PDF conversion operations"""
    
    @staticmethod
    def convert(csv_path, pdf_path):
        """Convert CSV file to PDF"""
        try:
            logger.info(f"Starting CSV to PDF conversion: {os.path.basename(csv_path)}")
            
            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4
            
            y = height - 40
            
            with open(csv_path, newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    text = " | ".join(row)
                    c.drawString(40, y, text)
                    y -= 20
                    
                    if y < 40:
                        c.showPage()
                        y = height - 40
            
            c.save()
            logger.info(f"CSV to PDF conversion successful: {pdf_path}")
            return True
        except Exception as e:
            logger.error(f"CSV to PDF conversion error: {str(e)}")
            return False
