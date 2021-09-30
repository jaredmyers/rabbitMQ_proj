#!/usr/bin/env/ python
import pika

credentials = pika.PlainCredentials('taco', 'tastegood')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, 'testHost', credentials))
channel = connection.channel()

channel.queue_declare(queue='testQueue', durable=True)

channel.basic_publish(exchange='testExchange', routing_key='', body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()
