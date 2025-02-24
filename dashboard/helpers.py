from email_validator import validate_email, EmailNotValidError
from flask import flash,redirect,url_for
from dashboard.models import *
import re
import os
import requests

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
    
def generate_payload(sender, message):
    payload = {
        "messaging_product": "whatsapp",
        "to": sender,
    }

    if 'list_data' in message and message['list_data'] is not None:
        payload['type'] = 'interactive'
        payload['interactive'] = {
            "type": "list",
            "body": {
                "text": message.get('text', '')
            },
            "action": {
                "button": message.get("list_data").get("header_text"),
                "sections": [
                    {
                        "title": message.get("list_data").get("header_text"),
                        "rows": []
                    }
                ]
            }
        }
        for item in message.get("list_data").get("data", []):
            payload['interactive']['action']['sections'][0]['rows'].append({
                "id": item.lower().replace(" ", "_"),  # Create a simple ID by converting to lowercase and replacing spaces with underscores
                "title": item
            })
    elif 'cta_url' in message and message['cta_url'] is not None:
        payload['type'] = "interactive"
        payload['interactive'] = {
            "type": "cta_url",
            "body": {
                "text": message.get("text", "")
            },
            "action": {
                "name": "cta_url",
                "parameters": {
                    "display_text": message['cta_url'][0].get('button_display_text'),
                    "url": message['cta_url'][0].get('button_redirect_url')
                }
            }
        }
    elif 'cta_button' in message and message['cta_button'] is not None:
        payload['type'] = 'interactive'
        payload['interactive'] = {
            "type": "button",
            "body": {
                "text": message.get("text", "")
            },
            "action": {
                "buttons": []
            }
        }
        for index, button_title in enumerate(message['cta_button']):
            button_id = f"button_{index + 1}"
            payload['interactive']['action']['buttons'].append({
                'type': 'reply',
                'reply': {
                    'id': button_id,
                    'title': button_title
                }
            })
    elif 'text' in message and message['text'] is not None:
        payload['type'] = 'text'
        payload['text'] = {
            "body": message['text'],
        }
    return payload

def send_whatsapp_message(sender, message):
    phone_number_id = os.environ.get("phone_number_id")
    access_token = os.environ.get("whatsapp_access_token")
    url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = generate_payload(sender, message)
    try:
        response = requests.post(url, headers=headers, json=payload)
        print('whatsapp message response: ', response.json())
        if response.status_code == 200:
            response_json = response.json()
            message_id = response_json.get('messages')[0].get('id')
            return True, "Message sent successfully.", message_id
        else:
            return False, "Message not sent.", None
    except Exception as e:
        print('whatsapp error: ', str(e))
        return False, str(e), None