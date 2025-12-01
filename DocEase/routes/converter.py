from flask import render_template, request, flash, redirect, url_for, send_from_directory, jsonify
import os
import logging
import time

logger = logging.getLogger(__name__)

def init_converter_routes(app, UploadForm, allowed_file, validate_upload_path,
                          validate_file_size, is_valid_pdf, CONVERTER_EXTENSIONS,
                          convert_file, log_conversion):
    
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
                flash('Invalid file type!', 'error')
                return redirect(url_for('upload_file'))

            try:
                save_path = validate_upload_path(filename, app.config['UPLOAD_FOLDER'])
            except ValueError as e:
                flash(str(e), 'error')
                return redirect(url_for('upload_file'))

            file.save(save_path)

            if not validate_file_size(save_path, app.config['MAX_CONTENT_LENGTH']):
                os.remove(save_path)
                flash("File too large.", "error")
                return redirect(url_for('upload_file'))

            if filename.lower().endswith(".pdf") and not is_valid_pdf(save_path):
                os.remove(save_path)
                flash("Invalid or corrupted PDF.", "error")
                return redirect(url_for('upload_file'))

            output_path = convert_file(save_path, conversion_type)

            if not output_path:
                flash("Conversion failed.", "error")
                return redirect(url_for('upload_file'))

            log_conversion(filename, conversion_type, output_path)

            return render_template("processing.html", output_file=os.path.basename(output_path))

        return render_template('converter.html', form=form, show_features_link=False)

    @app.route('/check-file/<filename>')
    def check_file(filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return jsonify({"ready": True})
        return jsonify({"ready": False})

    @app.route('/download/<filename>')
    def download_ready_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
