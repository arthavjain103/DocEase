"""PDF Editor routes - Merge, Split, Encrypt, Decrypt"""
from flask import render_template, request, flash, redirect, url_for, send_file
import os
import logging

logger = logging.getLogger(__name__)


def init_pdf_editor_routes(app, get_db_connection, UploadForm, EncryptPDFForm, DecryptPDFForm,
                           allowed_file, validate_upload_path, validate_file_size, is_valid_pdf,
                           PDF_EDITOR_EXTENSIONS, split_pdf, merge_pdfs, convert_file, log_conversion,
                           EncryptOps, DecryptOps):
    """Initialize PDF editor routes"""
    
    @app.route('/pdf-editor', methods=['GET', 'POST'])
    def pdf_editor():
        form = UploadForm()

        # Handle merge PDF
        if request.method == 'POST' and request.form.get('conversion_type') == 'merge-pdf':
            logger.info("Merge PDF request received")
            files = request.files.getlist('pdf_files')
            logger.info(f"Number of files received: {len(files)}")
            
            # Filter out empty files - PDF editor only accepts PDF files
            pdf_files = []
            for uploaded_file in files:
                if not uploaded_file or not uploaded_file.filename:
                    continue
                    
                # Validate PDF extension only for PDF editor
                if not allowed_file(uploaded_file.filename, PDF_EDITOR_EXTENSIONS):
                    logger.warning(f"Invalid file type for PDF editor: {uploaded_file.filename}")
                    flash(f'Only PDF files allowed. Received: {uploaded_file.filename}', 'error')
                    continue
                
                # Validate file path
                try:
                    file_path = validate_upload_path(uploaded_file.filename, app.config['UPLOAD_FOLDER'])
                except ValueError as e:
                    logger.error(f"Path validation failed: {str(e)}")
                    flash(str(e), 'error')
                    continue
                
                # Save file
                uploaded_file.save(file_path)
                
                # Validate file size
                if not validate_file_size(file_path, app.config['MAX_CONTENT_LENGTH']):
                    os.remove(file_path)
                    logger.warning(f"File too large: {uploaded_file.filename}")
                    flash(f'File {uploaded_file.filename} is too large', 'error')
                    continue
                
                # Validate PDF file integrity
                if not is_valid_pdf(file_path):
                    os.remove(file_path)
                    logger.warning(f"Invalid PDF file: {uploaded_file.filename}")
                    flash(f'File {uploaded_file.filename} is not a valid PDF', 'error')
                    continue
                
                pdf_files.append(file_path)
                logger.debug(f"Saved and validated PDF file: {file_path}")
            
            logger.info(f"Total valid PDF files: {len(pdf_files)}")
            
            if len(pdf_files) < 2:
                logger.warning("Merge attempted with fewer than 2 PDF files")
                flash('Please select at least 2 PDF files to merge', 'error')
                return redirect(url_for('pdf_editor'))
            
            # Merge the PDFs
            logger.info("Starting PDF merge process...")
            output_path = merge_pdfs(pdf_files)
            
            if output_path:
                logger.info(f"Merge successful, output: {output_path}")
                log_conversion('MERGE', 'merge-pdf', output_path)
                # Clean up individual files after merging
                for pdf_file in pdf_files:
                    try:
                        os.remove(pdf_file)
                        logger.debug(f"Cleaned up: {pdf_file}")
                    except Exception as e:
                        logger.error(f"Failed to clean up file {pdf_file}: {str(e)}")
                
                return send_file(output_path, as_attachment=True)
            else:
                logger.error("PDF merge failed")
                flash('PDF merging failed. Please try again.', 'error')
                return redirect(url_for('pdf_editor'))

        # Handle split and other PDF editor actions
        if form.validate_on_submit():
            file = form.file.data
            conversion_type = request.form.get('conversion_type')
            
            if not file:
                flash('No file provided', 'error')
                return redirect(url_for('pdf_editor'))
            
            # PDF editor only works with PDF files
            if not allowed_file(file.filename, PDF_EDITOR_EXTENSIONS):
                logger.warning(f"Invalid file type for PDF editor: {file.filename}")
                flash('Only PDF files allowed for PDF editor', 'error')
                return redirect(url_for('pdf_editor'))
            
            # Validate upload path
            try:
                file_path = validate_upload_path(file.filename, app.config['UPLOAD_FOLDER'])
            except ValueError as e:
                logger.error(f"Path validation failed: {str(e)}")
                flash(str(e), 'error')
                return redirect(url_for('pdf_editor'))
            
            file.save(file_path)
            
            # Validate file size
            if not validate_file_size(file_path, app.config['MAX_CONTENT_LENGTH']):
                os.remove(file_path)
                logger.warning(f"File too large: {file.filename}")
                flash('File is too large', 'error')
                return redirect(url_for('pdf_editor'))
            
            # Validate PDF integrity
            if not is_valid_pdf(file_path):
                os.remove(file_path)
                logger.warning(f"Invalid PDF file: {file.filename}")
                flash('Invalid or corrupted PDF file', 'error')
                return redirect(url_for('pdf_editor'))
            
            filename = file.filename
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

    @app.route('/encrypt', methods=['GET', 'POST'])
    def encrypt_pdf():
        form = EncryptPDFForm()
        
        if form.validate_on_submit():
            try:
                pdf_file = form.pdf.data
                password = form.password.data
                
                # Encrypt only works with PDF files
                if not allowed_file(pdf_file.filename, PDF_EDITOR_EXTENSIONS):
                    logger.warning(f"Invalid file type for encryption: {pdf_file.filename}")
                    flash('Invalid file type. Only PDF files allowed.', 'error')
                    return redirect(url_for('encrypt_pdf'))

                filename = pdf_file.filename
                
                # Validate upload path
                try:
                    input_path = validate_upload_path(filename, app.config['UPLOAD_FOLDER'])
                except ValueError as e:
                    logger.error(f"Path validation failed: {str(e)}")
                    flash(str(e), 'error')
                    return redirect(url_for('encrypt_pdf'))
                
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"encrypted_{__import__('werkzeug.utils', fromlist=['secure_filename']).secure_filename(filename)}")
                
                pdf_file.save(input_path)
                
                # Validate file size
                if not validate_file_size(input_path, app.config['MAX_CONTENT_LENGTH']):
                    os.remove(input_path)
                    logger.warning(f"File too large: {filename}")
                    flash("File too large.", "error")
                    return redirect(url_for('encrypt_pdf'))
                
                # Validate PDF integrity
                if not is_valid_pdf(input_path):
                    os.remove(input_path)
                    logger.warning(f"Invalid PDF file: {filename}")
                    flash("Invalid or corrupted PDF file.", "error")
                    return redirect(url_for('encrypt_pdf'))
                
                # Use EncryptOps class
                result = EncryptOps.encrypt(input_path, output_path, password)
                
                if result:
                    log_conversion(filename, 'encrypt-pdf', output_path)
                    logger.info(f"PDF encrypted successfully: {output_path}")
                    return send_file(output_path, as_attachment=True)
                else:
                    flash('Encryption failed.', 'error')
                    return redirect(url_for('encrypt_pdf'))
                
            except Exception as e:
                logger.error(f"PDF encryption error: {str(e)}")
                flash(f'Encryption failed: {str(e)}', 'error')
                return redirect(url_for('encrypt_pdf'))

        return render_template('encrypt.html', form=form)

    @app.route('/decrypt', methods=['GET', 'POST'])
    def decrypt_pdf():
        form = DecryptPDFForm()
        
        if form.validate_on_submit():
            try:
                pdf_file = form.pdf.data
                password = form.password.data
                
                # Decrypt only works with PDF files
                if not allowed_file(pdf_file.filename, PDF_EDITOR_EXTENSIONS):
                    logger.warning(f"Invalid file type for decryption: {pdf_file.filename}")
                    flash('Invalid file type. Only PDF files allowed.', 'error')
                    return redirect(url_for('decrypt_pdf'))

                filename = pdf_file.filename
                
                # Validate upload path
                try:
                    input_path = validate_upload_path(filename, app.config['UPLOAD_FOLDER'])
                except ValueError as e:
                    logger.error(f"Path validation failed: {str(e)}")
                    flash(str(e), 'error')
                    return redirect(url_for('decrypt_pdf'))
                
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"decrypted_{__import__('werkzeug.utils', fromlist=['secure_filename']).secure_filename(filename)}")

                pdf_file.save(input_path)
                
                # Validate file size
                if not validate_file_size(input_path, app.config['MAX_CONTENT_LENGTH']):
                    os.remove(input_path)
                    logger.warning(f"File too large: {filename}")
                    flash("File too large.", "error")
                    return redirect(url_for('decrypt_pdf'))
                
                # Validate PDF integrity
                if not is_valid_pdf(input_path):
                    os.remove(input_path)
                    logger.warning(f"Invalid PDF file: {filename}")
                    flash("Invalid or corrupted PDF file.", "error")
                    return redirect(url_for('decrypt_pdf'))
                
                # Use DecryptOps class
                success, message = DecryptOps.decrypt(input_path, output_path, password)
                
                if success:
                    log_conversion(filename, 'decrypt-pdf', output_path)
                    logger.info(f"PDF decrypted successfully: {output_path}")
                    return send_file(output_path, as_attachment=True)
                else:
                    if message == "Incorrect password":
                        logger.warning(f"Decryption failed - incorrect password: {filename}")
                    flash(f'Decryption failed: {message}', 'error')
                    return redirect(url_for('decrypt_pdf'))
                
            except Exception as e:
                logger.error(f"PDF decryption error: {str(e)}")
                flash(f'Decryption failed: {str(e)}', 'error')
                return redirect(url_for('decrypt_pdf'))

        return render_template('decrypt.html', form=form)
