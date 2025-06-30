from flask import Flask, render_template, request, send_file, flash, redirect, url_for, send_from_directory
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from werkzeug.utils import secure_filename
from pdf2docx import Converter as PDFToWordConverter
from docx2pdf import convert as word_to_pdf_convert
from PIL import Image
from PyPDF2 import PdfReader , PdfWriter
import os
import io
import zipfile
import sqlite3




app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a random secret key
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 40 * 1024 * 1024  # 40MB max-limit

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png'}

DB_PATH = os.path.join(os.path.dirname(__file__), 'conversions.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS conversions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            conversion_type TEXT NOT NULL,
            output_file TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB at startup
init_db()

class UploadForm(FlaskForm):
    file = FileField('Select File', validators=[
        FileRequired(),
        FileAllowed(ALLOWED_EXTENSIONS, 'Invalid file type!')
    ])
    submit = SubmitField('Convert')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html', show_features_link=True)

@app.route('/convert')
def convert():
    return render_template('upload.html', show_features_link=False)

@app.route('/pdf-editor', methods=['GET', 'POST'])
def pdf_editor():
    form = UploadForm()

    # Handle merge PDF
    if request.method == 'POST' and request.form.get('conversion_type') == 'merge-pdf':
        print("Merge PDF request detected")
        files = request.files.getlist('pdf_files')
        print(f"Number of files received: {len(files)}")
        
        # Filter out empty files
        pdf_files = []
        for uploaded_file in files:
            print(f"Processing file: {uploaded_file.filename if uploaded_file else 'None'}")
            if uploaded_file and uploaded_file.filename and allowed_file(uploaded_file.filename):
                filename = secure_filename(uploaded_file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                uploaded_file.save(file_path)
                pdf_files.append(file_path)
                print(f"Saved file: {file_path}")
        
        print(f"Total valid PDF files: {len(pdf_files)}")
        
        if len(pdf_files) < 2:
            flash('Please select at least 2 PDF files to merge', 'error')
            return redirect(url_for('pdf_editor'))
        
        # Merge the PDFs
        print("Starting PDF merge process...")
        output_path = merge_pdfs(pdf_files)
        
        if output_path:
            print(f"Merge successful, output: {output_path}")
            log_conversion('MERGE', 'merge-pdf', output_path)
            # Clean up individual files after merging
            for pdf_file in pdf_files:
                try:
                    os.remove(pdf_file)
                    print(f"Cleaned up: {pdf_file}")
                except:
                    pass
            
            return send_file(output_path, as_attachment=True)
        else:
            print("Merge failed")
            flash('PDF merging failed. Please try again.', 'error')
            return redirect(url_for('pdf_editor'))

    # Handle split and other PDF editor actions
    if form.validate_on_submit():
        file = form.file.data
        conversion_type = request.form.get('conversion_type')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            if conversion_type == 'split-pdf':
                # Handle PDF splitting with page range
                start_page = request.form.get('start_page')
                end_page = request.form.get('end_page')
                
                # Convert empty strings to None
                start_page = int(start_page) if start_page else None
                end_page = int(end_page) if end_page else None
                
                output_path = split_pdf(file_path, start_page, end_page)
                if output_path:
                    log_conversion(filename, conversion_type, output_path)
                    return send_file(output_path, as_attachment=True)
                else:
                    flash('PDF splitting failed. Please check your page range and try again.', 'error')
                    return redirect(url_for('pdf_editor'))
            else:
                output_path = convert_file(file_path, conversion_type)
                
                if output_path:
                    log_conversion(filename, conversion_type, output_path)
                    return send_file(output_path, as_attachment=True)
                else:
                    flash('Conversion failed. Please try again.', 'error')
                    return redirect(url_for('pdf_editor'))
    
    return render_template('pdf_editor.html', form=form, show_features_link=False)

@app.route('/file-converter', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    
   
 
    if form.validate_on_submit():
        file = form.file.data
        conversion_type = request.form.get('conversion_type')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
    
            output_path = convert_file(file_path, conversion_type)
                
            if output_path:
                log_conversion(filename, conversion_type, output_path)
                return send_file(output_path, as_attachment=True)
            else:
                    flash('Conversion failed. Please try again.', 'error')
                    return redirect(url_for('upload_file'))
        
    return render_template('converter.html', form=form, show_features_link=False)

def convert_file(file_path, conversion_type):
    output_path = os.path.splitext(file_path)[0]
    
    try:
        if conversion_type == 'pdf-to-word':
            output_path += '.docx'
            cv = PDFToWordConverter(file_path)
            cv.convert(output_path)
            cv.close()
        elif conversion_type == 'word-to-pdf':
            output_path += '.pdf'
            word_to_pdf_convert(file_path, output_path)
        elif conversion_type == 'image-to-pdf':
            output_path += '.pdf'
            image = Image.open(file_path)
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            image.save(output_path, 'PDF', resolution=100.0)
        else:
            return None
        
        return output_path
    except Exception as e:
        print(f"Conversion error: {str(e)}")
        return None
    
def split_pdf(pdf_path, start_page=None, end_page=None):
    try:
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            total_pages = len(reader.pages)
            
            if total_pages == 0:
                print("PDF is empty")
                return None
            
            # Validate page range
            start_page = start_page or 1
            end_page = end_page or total_pages
            
            # Convert to 0-based indexing
            start_idx = start_page - 1
            end_idx = end_page - 1
            
            # Validate range
            if start_idx < 0 or end_idx >= total_pages or start_idx > end_idx:
                print(f"Invalid page range: {start_page}-{end_page}. PDF has {total_pages} pages.")
                return None
            
            # Create a zip file to store all split PDFs
            base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
            zip_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_filename}_pages_{start_page}-{end_page}.zip")
            
            with zipfile.ZipFile(zip_filename, 'w') as zip_file:
                # Split each page in the range into a separate PDF
                for page_num in range(start_idx, end_idx + 1):
                    select_page = reader.pages[page_num]
                    
                    writer = PdfWriter()
                    writer.add_page(select_page)
                    
                    # Create individual PDF file
                    individual_filename = f"{base_filename}_page_{page_num + 1}.pdf"
                    individual_path = os.path.join(app.config['UPLOAD_FOLDER'], individual_filename)
                    
                    with open(individual_path, "wb") as out:
                        writer.write(out)
                    
                    # Add to zip file
                    zip_file.write(individual_path, individual_filename)
                    
                    # Clean up individual file
                    os.remove(individual_path)
                    
                    print(f"Created PDF page {page_num + 1}: {individual_filename}")
            
            print(f"Pages {start_page}-{end_page} split and saved to: {zip_filename}")
            return zip_filename
            
    except Exception as e:
        print(f"PDF splitting error: {str(e)}")
        return None

def merge_pdfs(pdf_files):
    """
    Merge multiple PDF files into a single PDF.
    
    Args:
        pdf_files (list): List of file paths to PDF files.
        
    Returns:
        str or None: Path to the merged PDF file or None if error.
    """
    try:
        if not pdf_files or len(pdf_files) < 2:
            print("Need at least 2 PDF files to merge.")
            return None
        
        writer = PdfWriter()

        for pdf_file in pdf_files:
            if not os.path.exists(pdf_file):
                print(f"⚠ Skipping missing file: {pdf_file}")
                continue

            with open(pdf_file, "rb") as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    writer.add_page(page)
                print(f"Added {len(reader.pages)} pages from {os.path.basename(pdf_file)}")
        
        if not writer.pages:
            print("⚠ No valid pages found to merge.")
            return None

        # Create unique output filename to avoid overwriting
        import uuid
        output_filename = os.path.join(
            app.config['UPLOAD_FOLDER'], 
            f"merged_pdf_{uuid.uuid4().hex}.pdf"
        )

        with open(output_filename, "wb") as output_file:
            writer.write(output_file)

        print(f" Merged PDF saved: {output_filename}")
        return output_filename

    except Exception as e:
        print(f" PDF merging error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def log_conversion(filename, conversion_type, output_file):
    try:
        output_filename = os.path.basename(output_file)
        print(f"Logging conversion: {filename}, {conversion_type}, {output_filename}")
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO conversions (filename, conversion_type, output_file) VALUES (?, ?, ?)',
            (filename, conversion_type, output_filename)
        )
        conn.commit()
        conn.close()
        print("Log successful!")
    except Exception as e:
        print(f"Error logging conversion: {e}")

@app.route('/logs')
def view_logs():
    conn = get_db_connection()
    logs = conn.execute('SELECT * FROM conversions ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('logs.html', logs=logs)

# Serve uploaded files
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':

 
    app.run(debug=True)