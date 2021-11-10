from typing import ContextManager
from site_spotify.send_to_db import send_to_db
import json

'''
interface between webfront and MQ
for anything regarding forum threads and chat
interfaces with database driver which establishes MQ connection

'''

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

def create_chat(sessionId, chat_recipient):
    message = "create_chat:" + sessionId + ":" + chat_recipient
    response = send_to_db(message, 'threads')
    print("sent from create_chat: ")
    print(response)

    return response

def get_username(sessionId):
    message = "get_username:" + sessionId
    response = send_to_db(message, 'threads')
    print("sent from get_username: ")
    print(response)

    return response

def new_chat_message(username, message, room_id):
    message = "new_chat_message:"+username+":"+message+":"+room_id
    response = send_to_db(message, 'threads')
    print("sent from create_chat_message: ")
    print(response)
    return response

def get_chat_messages(room_id):
    message = "get_messages:"+room_id
    response = send_to_db(message, 'threads')
    print("sent from get_chat_messages:")
    print(response)
    chat_messages = response.split(";")
    del chat_messages[-1]

    p = 0
    message_dict = {}
    for i in chat_messages:
        message = i.split(":")
        message_dict[p] = [message[0], message[1]]
        p+=1

    return message_dict

def remove_friend(sessionId, friendname):
    message = "remove_friend:" + sessionId + ':' + friendname
    response = send_to_db(message, 'threads')
    print("send from add_friend:")
    print(response)

    return response

class ThreadMain():
    
    def __init__(self, author, threadID, title, content, date):
        self.threadID = threadID
        self.content = content
        self.author = author
        self.date = date
        self.title = title

class ThreadReplies():

    def __init__(self, author, content, date):
        self.author = author
        self.content = content
        self.date = date