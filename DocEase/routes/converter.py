"""File Converter routes"""
from flask import render_template, request, flash, redirect, url_for, send_file
import os
import logging

logger = logging.getLogger(__name__)


def init_converter_routes(app, UploadForm, allowed_file, validate_upload_path, validate_file_size,
                          is_valid_pdf, CONVERTER_EXTENSIONS, convert_file, log_conversion):

    @app.route('/file-converter', methods=['GET', 'POST'])
    def upload_file():
        form = UploadForm()
        
        if form.validate_on_submit():
            file = form.file.data
            conversion_type = request.form.get('conversion_type')
            
            if not file:
                flash('No file provided', 'error')
                return redirect(url_for('upload_file'))
            
            filename = file.filename
            
            if not allowed_file(filename, CONVERTER_EXTENSIONS):
                logger.warning(f"Invalid file type for converter: {filename}. Allowed: {CONVERTER_EXTENSIONS}")
                flash('Invalid file type! Allowed: PDF, Word (docx/doc), or Image (jpg/jpeg/png)', 'error')
                return redirect(url_for('upload_file'))
            
            try:
                save_path = validate_upload_path(filename, app.config['UPLOAD_FOLDER'])
            except ValueError as e:
                logger.error(f"Path validation failed: {str(e)}")
                flash(str(e), 'error')
                return redirect(url_for('upload_file'))

            file.save(save_path)

            if not validate_file_size(save_path, app.config['MAX_CONTENT_LENGTH']):
                os.remove(save_path)
                logger.warning(f"File too large: {filename}")
                flash("File too large.", "error")
                return redirect(url_for('upload_file'))

            if filename.lower().endswith(".pdf") and not is_valid_pdf(save_path):
                os.remove(save_path)
                logger.warning(f"Invalid PDF file: {filename}")
                flash("Invalid or corrupted PDF file.", "error")
                return redirect(url_for('upload_file'))

            output_path = convert_file(save_path, conversion_type)

            if output_path and os.path.isfile(output_path):
                log_conversion(filename, conversion_type, output_path)
                logger.info(f"Conversion successful: {filename} → {os.path.basename(output_path)}")
                return send_file(output_path, as_attachment=True)
            else:
                logger.error(f"Conversion failed for: {filename}")
                flash('Conversion failed. Please try again.', 'error')
                return redirect(url_for('upload_file'))
            
        return render_template('converter.html', form=form, show_features_link=False)
