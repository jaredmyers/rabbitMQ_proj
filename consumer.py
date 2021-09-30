#!/usr/bin/env python3

import pika

connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
        )

channel = connection.channel()

def callback(ch,method,properties,body):
    print("[x] Received %r" % body)

channel.basic_consume(
        queue='hello', on_message_callback=callback, auto_ack=True
        )

print('[*] Waiting for messages to exit press ctrlC')
channel.start_consuming()

