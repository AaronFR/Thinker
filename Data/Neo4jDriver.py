import logging
import os

from neo4j import GraphDatabase, basic_auth


class Neo4jDriver:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", password))

    def close(self):
        self.driver.close()

    def execute_write(self, query, parameters=None):
        with self.driver.session() as session:
            return session.write_transaction(
                lambda tx: list(tx.run(query, parameters)))

    def execute_read(self, query, parameters=None):
        with self.driver.session() as session:
            return session.read_transaction(lambda tx: list(tx.run(query, parameters)))

    def execute_delete(self, query, parameters=None):
        with self.driver.session() as session:
            try:
                session.write_transaction(lambda tx: tx.run(query, parameters))
                logging.info(f"Successfully executed delete operation: {query} with params: {parameters}")
            except Exception as e:
                logging.error(f"Failed to execute write operation: {e}")
                raise

