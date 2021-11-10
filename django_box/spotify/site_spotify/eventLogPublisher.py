import time
import subprocess
import select
import PikaClasses
import credentials as cred

'''
Event Logs webserver events by scanning for newlines in
webservers log and sending out to fanout queue

'''

log_to_scan = "/var/log/nginx/access.log"

def send_log(log_lines):
    exchange = 'exchangeAll'
    connection = PikaClasses.RunPublisher(cred.user, cred.pw, cred.ip_address)
    connection.fan_publish(exchange, log_lines)

f = subprocess.Popen(['tail','-F', log_to_scan],\
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
p = select.poll()
p.register(f.stdout)

while True:
    if p.poll(1):
        send_log(f.stdout.readline())
    