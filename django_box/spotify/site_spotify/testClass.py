"""
Test Class for demo
"""
import pika, sys, uuid

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
        print(f"Sent {message}")
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
        print(f"Sent {message}")
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

    def rpc_publish(self, message, queue):

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        #self.callback_queue = result.method.queue
        callback_queue = result.method.queue

        def on_response(ch, method, props, body):
            if self.corr_id == props.correlation_id:
                self.response = body

        self.channel.basic_consume(
            queue=callback_queue,
            on_message_callback=on_response,
            auto_ack=True)

        def call(n):
            self.response = None
            self.corr_id = str(uuid.uuid4())
            self.channel.basic_publish(
                exchange='',
                routing_key=queue,
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.corr_id,
                ),
                body=str(n))
            while self.response is None:
                self.connection.process_data_events()
            return int(self.response)
        
        call(message)


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
                file.write(str.encode("\n"))

        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True)

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("interupted")
        sys.exit("exited program")

    def rpc_subscribe(self, queue):

        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=queue)


        def fib(n):
            if n == 0:
                return 0
            elif n == 1:
                return 1
            else:
                return fib(n - 1) + fib(n - 2)


        def on_request(ch, method, props, body):
            n = int(body)

            print(" [.] fib(%s)" % n)
            response = fib(n)

            ch.basic_publish(exchange='',
                            routing_key=props.reply_to,
                            properties=pika.BasicProperties(correlation_id = \
                                                                props.correlation_id),
                            body=str(response))
            ch.basic_ack(delivery_tag=method.delivery_tag)


        #channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=queue, on_message_callback=on_request)

        print(" [x] Awaiting RPC requests")
        self.channel.start_consuming()

class RpcPublisher():

    def __init__(self, user, pw, ip):
        self.credentials = pika.PlainCredentials(user, pw)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            ip,
            5672,
            'testHost',
            self.credentials)
        )

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, message, queue):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        print("running calls publish...")
        print(message)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=message)
        print("while loop for processing...")
        while self.response is None:
            self.connection.process_data_events()
        return self.response

