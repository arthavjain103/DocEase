"""Authentication routes"""
from flask import render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import logging

logger = logging.getLogger(__name__)


def init_auth_routes(app, get_db_connection, RegisterForm, LoginForm):
    """Initialize authentication routes"""
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():  # Uses WTForms validation
            username = form.username.data
            password = form.password.data
            hashed_password = generate_password_hash(password)
            
            conn = get_db_connection()
            existing = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if existing:
                conn.close()
                flash('Username already exists.', 'error')
                return redirect(url_for('register'))
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('Logged in successfully.', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password.', 'error')
                return redirect(url_for('login'))
        
        return render_template('login.html', form=form)

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Logged out successfully.', 'success')
        return redirect(url_for('login'))
