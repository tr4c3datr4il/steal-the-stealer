from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, text
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Database:
    def __init__(self):
        self.host = os.environ.get('DB_HOST', 'localhost')
        self.user = os.environ.get('DB_USER', 'teledb')
        self.password = os.environ.get('DB_PASSWORD', '123456')
        self.db_name = os.environ.get('DB_NAME', 'teledb')
        self.db_path = 'mysql+mysqldb://{}:{}@{}/{}'.format(
            self.user, 
            self.password, 
            self.host, 
            self.db_name
        )
        self.engine = create_engine(self.db_path)
        self.connection = self.engine.connect()

        self.clearTable() # we need to make this into an option
        self.createTable()

    def createTable(self):
        table = Table('hashes', MetaData(),
            Column('hash', String(255), primary_key=True)
        )
        table.create(self.engine, checkfirst=True)

    def clearTable(self):
        table = Table('hashes', MetaData())
        table.drop(self.engine, checkfirst=True)

    def insertHash(self, hash_str):
        try:
            # input validation
            if not hash_str:
                return False

            cmd = text(f"""
                INSERT INTO hashes (hash) 
                VALUES ('{hash_str}') 
                ON DUPLICATE KEY UPDATE hash = '{hash_str}'
            """)
            self.transaction = self.connection.begin()
            cursor = self.connection.execute(cmd)
            self.transaction.commit()

            result = cursor.rowcount
            # logging.info(f"Inserted hash: {hash_str} - Result: {result}")

            return True 
        except Exception as e:
            logging.error(f"Error inserting hash: {hash_str} - {e}")
            self.transaction.rollback()

            return False

    def getHash(self, hash_str):
        try:
            # input validation
            if not hash_str:
                return False
            
            cmd = text(f"""
                SELECT * FROM hashes WHERE hash = '{hash_str}'
            """)

            self.transaction = self.connection.begin()
            cursor = self.connection.execute(cmd)
            self.transaction.commit()

            result = cursor.fetchone()
            # logging.info(f"Get hash: {hash_str} - Result: {result}")

            # The result will be None or a tuple -> corrected value
            return result
        except Exception as e:
            logging.error(f"Error getting hash: {hash_str} - {e}")
            self.transaction.rollback()

            return False
        
    def close(self):
        self.connection.close()
        self.engine.dispose()