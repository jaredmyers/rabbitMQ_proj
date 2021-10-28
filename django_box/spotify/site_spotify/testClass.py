"""
Test Class for demo
"""
import pika, sys

class RunPublisher():
    """
    A class for sending messages to a specific rabbitMQ queue

    """
    def __init__(self, user, pw, ip):
        """
        Constructs attributes for rabbit connection

        Parameters
        ----------
            user : str
                user cred for rabbit
            pw : str
                password cred for rabbit
            ip : str
                ip address of rabbit
        """
        self.credentials = pika.PlainCredentials(user, pw)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            ip,
            5672,
            'testHost',
            self.credentials)
        )

    def send_message(self, exchange, queue, message):
        """
        Send messages to specified queue

        Parameters
        ----------
            exchange : str
                exchange of destination queue
            queue : str
                destination queue
            message : str
                message to be sent
        """
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue, durable=True)

        self.channel.basic_publish(exchange=exchange, routing_key='', body=message)
        print(f"Sent {message}!")
        self.connection.close()
    
    def db_publish(self, exchange, queue, message):
        """
        Send messages to specified queue

        Parameters
        ----------
            exchange : str
                exchange of destination queue
            queue : str
                destination queue
            message : str
                message to be sent
        """
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue, durable=True)

        self.channel.basic_publish(exchange=exchange, routing_key=queue, body=message)
        print(f"Sent {message}!")
        self.connection.close()

    def fan_publish(self, exchange, message):
        """
        Sends messages to all queues in specified exchange

        Parameters
        ----------
            exchange : str
                destination queue
            message : str
                message to be sent
        """

        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange, exchange_type='fanout', durable=True)

        self.channel.basic_publish(exchange=exchange, routing_key='', body=message)
        print(" [x]Sent %r" % message)
        self.connection.close()


class RunSubscriber():
    """
    A class for listening for messages from a specific rabbitMQ queue
    """
    def __init__(self, user, pw, ip):
        """
        Constructs attributes for rabbit connection

        Parameters
        ----------
            user : str
                user cred for rabbit
            pw : str
                password cred for rabbit
            ip : str
                ip address of rabbit
        """

        self.credentials = pika.PlainCredentials(user,pw)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            ip,
            5672,
            'testHost',
            self.credentials)
        )
        self.channel = None
        

    def listen_for_messages(self, queue):
        """
        Listen for messages on specified queue

        Parameters
        ----------
            queue : str
                destination queue
        """

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue,durable=True)

        def callback(ch, method, properties, body):
            print(" [x] Received %r" % body)

        self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
   
        print(f' [*] Waiting for messages on {queue}')

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("interupted")
            sys.exit("exited program")
        
    def db_subscribe(self, exchange, queue):
        """
        Grab messages on specified database queue

        Parameters
        ----------
            queue : str
                destination queue
        """
        def callback(ch, method, properties, body):
            print(" [x] Received %r" % body)
            
        self.channel = self.connection.channel()
        queue_state = self.channel.queue_declare(queue=queue,durable=True, passive=True)
        queue_empty = queue_state.method.message_count == 0
        self.channel.queue_bind(exchange=exchange, queue=queue, routing_key=queue)

        if not queue_empty:
            method, properties, body = self.channel.basic_get(queue, auto_ack=True)
            #callback(self.channel,method,properties,body)
        else:
            return 'empty'
        
        #self.connection.close()
       
        return body

    def listen_fanout(self, exchange, log_path):
        """
        listens for all messages coming into specific exchange

        Parameters
        ----------
            exchange : str
                destination exchange
        """

        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange, exchange_type='fanout', durable=True)

        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange=exchange, queue=queue_name)

        print("Waiting for logs...")

        def callback(ch, method, properties,body):
            print("[x] %r" % body)
            send_log(body)

        def send_log(log_body):
            with open(log_path, 'ab') as file:
                file.write(log_body)

        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True)

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("interupted")
        sys.exit("exited program")