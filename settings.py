import logging
import requests
from pymongo import MongoClient


client = MongoClient()
DB = client.hupu


class MongoFormatter(logging.Formatter):

    def format(self, record):
        """Formats LogRecord into python dictionary."""
        return {
            'timestamp': record.created,
            'level': record.levelname,
            'message': record.getMessage(),
        }


class MongoHandler(logging.Handler):

    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level)
        self.formatter = MongoFormatter()
        self.collection = DB.logs

    def emit(self, record):
        """Inserting new logging record to mongo database."""
        try:
            self.collection.save(self.format(record))
        except Exception:
            pass


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d %b %Y %H:%M:%S',
)

# add mongohandler
logger = logging.getLogger('')
logger.setLevel(logging.INFO)
logger.addHandler(MongoHandler())


def send_email(msg, subject='hupu'):
    requests.post(
        'http://0.0.0.0:5000/email/',
        params={'subject': subject, 'msg': msg}
    )

# pymysql.err.OperationalError: (2003, "Can't connect to MySQL server on 'host'
# ([Errno -8] Servname not supported for ai_socktype)")

# mysql_config = dict(
#     host='localhost',
#     user='root',
#     passwd='      ',
#     db='hupu',
#     charset='utf8',
#     unix_socket='/var/run/mysqld/mysqld.sock'
# )