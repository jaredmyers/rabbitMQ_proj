import subprocess, select
from testClass import SendFanout
import credentials as cred


def sendLog(log_lines):
    exchange = 'exchangeAll'
    connection = SendFanout(cred.user, cred.pw, cred.ip_address)
    connection.send_fanout(exchange, log_lines)


#source_path = '/var/log/mysql/mysql_gen.log'


