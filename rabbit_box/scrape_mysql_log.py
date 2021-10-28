import subprocess, select
from testClass import SendFanout
import credentials as cred

exchange = 'exchangeAll'
source_path = '/var/log/mysql/mysql_gen.log'

def send(log_line):
    connection = SendFanout(cred.user, cred.pw, cred.ip_address)
    connection.send_fanout(exchange, log_line)

f = subprocess.Popen(['tail','-F', source_path],\
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
p = select.poll()
p.register(f.stdout)
while True:
    if p.poll(1):
       # print(f.stdout.readline())
       send(f.stdout.readline())