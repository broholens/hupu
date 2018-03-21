import logging
from pymongo import MongoClient

client = MongoClient()
DB = client.hupu

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='hupu.log',
    filemode='a'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)-6s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# pymysql.err.OperationalError: (2003, "Can't connect to MySQL server on 'host'
# ([Errno -8] Servname not supported for ai_socktype)")

mysql_config = dict(
    host='localhost',
    user='root',
    passwd='      ',
    db='hupu',
    charset='utf8',
    unix_socket='/var/run/mysqld/mysqld.sock'
)