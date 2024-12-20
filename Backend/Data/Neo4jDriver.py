import logging
import os

from neo4j import GraphDatabase, basic_auth

from Utilities.Decorators import handle_errors


class Neo4jDriver:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", password))

    def close(self):
        self.driver.close()

    @handle_errors(debug_logging=True)
    def execute_write(self, query, parameters=None, field=None):
        """

        :param query: The actual cypher query itself
        :param parameters: The associated parameters required to execute the cypher query
        :param field: Optional field to RETURN
        :return:
        """
        with self.driver.session() as session:
            return session.write_transaction(
                lambda tx: self._extract_field(tx.run(query, parameters), field)
            )

    @staticmethod
    def _extract_field(result, field):
        record = result.single()

        if record is None:
            logging.error("No record returned by the query.")
            return None

        logging.info(f"Record returned: {record}")
        try:
            value = record.get(field)
            logging.info(f"Field '{field}' value: {value}")
            return value
        except KeyError:
            logging.error(f"Field '{field}' not found in the record.")

        return None

    @handle_errors()
    def execute_read(self, query, parameters=None):
        with self.driver.session() as session:
            return session.read_transaction(lambda tx: list(tx.run(query, parameters)))

    @handle_errors(debug_logging=True, raise_errors=True)
    def execute_delete(self, query, parameters=None):
        with self.driver.session() as session:
            session.write_transaction(lambda tx: tx.run(query, parameters))
            logging.info(f"Successfully executed delete operation: {query} with params: {parameters}")

