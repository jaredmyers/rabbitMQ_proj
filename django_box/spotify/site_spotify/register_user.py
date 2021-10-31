import hashlib
import uuid
import bcrypt
from site_spotify.send_to_db import send_to_db

def generate_hashpw(pw):
    salt = bcrypt.gensalt()
    pw = pw.encode()
    hashed = bcrypt.hashpw(pw, salt)

    return hashed.decode('utf-8')

def register_user(username,pw):
    hashpw = generate_hashpw(pw)
    message = f'register:{username}:{hashpw}'
    response = send_to_db(message, 'check_session')

    return response

def process_login(username, pw):
    message = f'login:{username}:{pw}'
    response = send_to_db(message,'check_session')
    
    return response

