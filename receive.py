#!/usr/bin/env python
import pika, sys, os

def main():

    user = ''
    password = ''

    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, 'testHost', credentials))
    channel = connection.channel()
    

    channel.queue_declare(queue='testQueue', durable=True)
    
    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    channel.basic_consume(queue='testQueue', on_message_callback=callback, auto_ack=True)
   
    print(' [*] Waiting for messages. To exit press ctrl+c')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os.exit(0)
