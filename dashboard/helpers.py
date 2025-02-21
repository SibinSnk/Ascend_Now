from email_validator import validate_email, EmailNotValidError
from flask import flash,redirect,url_for
from dashboard.models import *
import re

def register_validations(email,password,confirm_password,phone,role):
    try:
        validate_email(email, check_deliverability=False)

    except EmailNotValidError:
        flash('Invalid email format.', 'danger')
        return redirect(url_for('register'))

    if User.query.filter_by(email=email).first():
        flash('Email is already registered. Please log in.', 'danger')
        return redirect(url_for('register'))

    if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[@$!%*?&]', password):
        flash('Password must be at least 8 characters long, include an uppercase letter, a number, and a special character.', 'danger')
        return redirect(url_for('register'))
    
    if not phone.isdigit():
        flash('Phone number should be digits.', 'danger')
        return redirect(url_for('register')) 

    if password != confirm_password:
        flash('Passwords do not match.', 'danger')
        return redirect(url_for('register'))
    
    if role not in ['Admin', 'Teacher']:
        flash('Invalid role selection.', 'danger')
        return redirect(url_for('register'))