import logging
import os
from typing import Optional, Any, Dict

from neo4j import GraphDatabase, basic_auth

from Constants.Constants import NEO4J_URI, NEO4J_PASSWORD
from Utilities.Decorators import handle_errors


class Neo4jDriver:
    """
    This class manages the connection to the Neo4j database and provides read and write functionalities.
    """

    def __init__(self):
        """Initializes the Neo4jDriver and establishes a connection to the database."""
        uri = os.getenv(NEO4J_URI)
        password = os.getenv(NEO4J_PASSWORD)
        if not uri or not password:
            raise ValueError("NEO4J_URI and NEO4J_PASSWORD environment variables must be set.")

        self.driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", password))

    def close(self) -> None:
        """Closes the connection to the Neo4j database."""
        if self.driver:
            self.driver.close()

    @handle_errors(debug_logging=True)
    def execute_write(self,
                      query: str,
                      parameters: Optional[Dict[str, Any]] = None,
                      field: Optional[str] = None) -> Any:
        """
        Executes a write transaction on the Neo4j database.

        :param query: The Cypher query string to execute.
        :param parameters: The parameters to be passed to the query.
        :param field: Optional field to return from the executed query.
        :return: The value extracted from the query result if a field is specified.
        """
        with self.driver.session() as session:
            return session.write_transaction(
                lambda tx: self._extract_field(tx.run(query, parameters), field)
            )

    @staticmethod
    def _extract_field(result, field: Optional[str]) -> Optional[Any]:
        """
        Extracts a specified field from the query result.

        :param result: The result set from the executed query.
        :param field: The name of the field to be extracted.
        :return: The value of the specified field or None if not found.
        """
        record = result.single()
        if record is None:
            logging.warning(f"No record returned by the query for {field}")
            return None

        logging.info(f"Record returned: {record}")

        if field:
            try:
                value = record.get(field)
                logging.info(f"Field '{field}' value: {value}")
                return value
            except KeyError:
                logging.error(f"Field '{field}' not found in the record.")

        return None

    @handle_errors()
    def execute_read(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Executes a read transaction on the Neo4j database.

        :param query: The Cypher query to execute.
        :param parameters: Optional parameters for the query.
        :return: A list of records returned by the query.
        """
        with self.driver.session() as session:
            return session.read_transaction(lambda tx: list(tx.run(query, parameters)))

    @handle_errors(debug_logging=True, raise_errors=True)
    def execute_delete(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        """
        Executes a delete operation on the Neo4j database.

        :param query: The Cypher query for the delete operation.
        :param parameters: Optional parameters for the query.
        """
        with self.driver.session() as session:
            session.write_transaction(lambda tx: tx.run(query, parameters))
            logging.info(f"Successfully executed delete operation: {query} with params: {parameters}")
