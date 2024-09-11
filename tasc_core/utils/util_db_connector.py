from pandas import DataFrame, read_sql_query
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError
from sqlalchemy import create_engine, text, engine as sa_engine


class DbConnector:
    """A generic database connector object that creates a SQLAlchemy engine for a database.
    """

    def __init__(self, server_adapter, host, database, port: int = 5432, username='', password='', driver='') -> None:
        """

        Args:
            server_adapter (_type_): Server adapter to use when forming connection string. e.g. 'postgresql+psycopg2'
            host (_type_): Name of database host.
            database (_type_): Name of database
            port (str, optional): Port number. Defaults to ''.
            username (str, optional): _description_. Defaults to ''.
            password (str, optional): _description_. Defaults to ''.
            driver (str, optional): _description_. Defaults to ''.
        """
        connection_string = self.get_connection_string(server_adapter, host, database, port, username, password)
        self.engine = create_engine(connection_string)

    @staticmethod
    def get_connection_string(server_adapter, host, database, port: int, username='', password=''):

        connection_url = sa_engine.URL.create(
            drivername=server_adapter,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database
        )
        return connection_url

    def select_df(self, query: str) -> DataFrame:  # type: ignore
        """GET data from the database and return the results in a pandas DataFrame.

        Args:
            query (str): SQL SELECT query you want to execute

        Returns:
            DataFrame: AEON response from your query

        Example:
            You can get data from AEON in 3 lines

                from eii.utils.aeon import AeonConnector

                aeon = AeonConnector()
                df = aeon.select_df("SELECT * FROM public.v_xref_idx_map LIMIT 10")

        """
        try:
            with self.engine.connect() as connection:
                return read_sql_query(text(query), connection)
        except SQLAlchemyError as e:
            self.handle_error(e)

    def execute_query(self, query: str) -> None:
        """Execute a SQL command. Used typically for commands that don't return a result, e.g. GRANT, ALTER

        Args:
            query (str): SQL command
        """
        try:
            with self.engine.connect() as connection:
                connection.execute(text(query))
                connection.commit()
        except SQLAlchemyError as e:
            self.handle_error(e)

    def handle_error(self, error):
        """Custom error handler for SQLAlchemy errors.
        """
        if isinstance(error, OperationalError):
            if 'authentication failed' in str(error):
                print(f"Could not connect to the database. Username, password combo incorrect: {error}")
            else:
                print(f"Could not connect to the database. Connection details seem incorrect: {error}")

        elif isinstance(error, InterfaceError):
            print(f"Could not connect to the database. Driver provided likely incorrect: {error}")

        raise
