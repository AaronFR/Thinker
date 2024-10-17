import os

from neo4j import GraphDatabase


class Neo4jDriver:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_write(self, query, parameters=None):
        with self.driver.session() as session:
            return session.write_transaction(lambda tx: tx.run(query, parameters))
