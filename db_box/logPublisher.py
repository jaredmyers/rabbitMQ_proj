import subprocess, select
from testClass import RunPublisher
import credentials as cred

#import sys
#sys.tracebacklimit = 0

def sendLog(log_lines):
    exchange = 'exchangeAll'
    connection = RunPublisher(cred.user, cred.pw, cred.ip_address)
    connection.fan_publish(exchange, log_lines)


#source_path = '/var/log/mysql/mysql_gen.log'


