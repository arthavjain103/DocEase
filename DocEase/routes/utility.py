"""Utility routes - Home, Convert, Logs, Uploads"""
from flask import render_template, flash, redirect, url_for, session, send_from_directory
import logging

logger = logging.getLogger(__name__)


def init_utility_routes(app, get_db_connection):
    """Initialize utility routes"""
    
    @app.route('/')
    def home():
        return render_template('home.html', show_features_link=True)

    @app.route('/convert')
    def convert():
        return render_template('upload.html', show_features_link=False)

    @app.route('/logs')
    def view_logs():
        user_id = session.get('user_id')
        if not user_id:
            flash('Please log in to view your history.', 'error')
            return redirect(url_for('login'))
        conn = get_db_connection()
        logs = conn.execute('SELECT * FROM conversions WHERE user_id = ? ORDER BY timestamp DESC', (user_id,)).fetchall()
        conn.close()
        return render_template('logs.html', logs=logs)

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
