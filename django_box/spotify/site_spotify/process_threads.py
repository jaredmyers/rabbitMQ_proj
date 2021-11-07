from typing import ContextManager
from site_spotify.send_to_db import send_to_db
import json

def get_thread_info():
    message = 'get_threads'
    response = send_to_db(message, 'threads')
    print("from get_thread_info: ")
    print(response)
      
    list_json_strings = response.split(";")
    del list_json_strings[-1]

    return list_json_strings

def get_reply_page(id):
    message = 'get_reply_page:'+id
    response = send_to_db(message, 'threads')
    print("from get_reply_page: ")
    print(response)
    return response

def send_new_thread(sessionId, threadname, threadcontent):
    message = 'new_thread:' + sessionId + ':' + threadname + ':' + threadcontent
    response = send_to_db(message,'threads')
    print("from send_new_thread: ")
    print(response)

def send_new_reply(sessionId, threadID, replycontent):
    message = "new_reply:" + sessionId + ":" + threadID + ":" + replycontent
    response = send_to_db(message, 'threads')
    print("from send_new_reply: ")
    print(response)

def add_friend(sessionId, friendname):
    message = "add_friend:" + sessionId + ':' + friendname
    response = send_to_db(message, 'threads')
    print("send from add_friend:")
    print(response)

    return response

def get_friends(sessionId):
    message = "get_friends:" + sessionId
    response = send_to_db(message, 'threads')
    print("sent from get_friends: ")
    print(response)

    if not response:
        return []
    
    friends_list = response.split(":")
    del friends_list[-1]

    return friends_list

class Thread_main():
    
    def __init__(self, author, threadID, title, content, date):
        self.threadID = threadID
        self.content = content
        self.author = author
        self.date = date
        self.title = title

class Thread_replies():

    def __init__(self, author, content, date):
        self.author = author
        self.content = content
        self.date = date