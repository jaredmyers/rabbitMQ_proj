from typing import ContextManager
from site_spotify.send_to_db import send_to_db

def get_thread_info():

    message = 'get_threads'
    response = send_to_db(message, 'threads')


class Thread_main():
    
    def __init__(self, id, content, author, time):
        self.id = id
        self.content = content
        self.author = author
        self.time = time