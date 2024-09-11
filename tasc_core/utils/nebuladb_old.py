from psycopg2 import connect
from pandas import DataFrame, read_sql_query
from pandas.io.sql import get_schema
from re import sub
from io import StringIO


class NebulaConnector:
    """This object creates a connection to the Amazon RDS Postgres database and handles any SQL query you want to run.

    Example:
        You can get data from Nebula in 3 lines::

            from eii.utils.nebula import NebulaConnector

            nebula = NebulaConnector()
            df = nebula.select_df("SELECT * FROM public.v_xref_idx_map LIMIT 10")

    """

    def __init__(self, username: str = None, password: str = None, host: str = '') -> None:
        self.user = username
        self.pwd = password
        self.host = host
        self.conn = None
        self.cursor = None

    def _open_conn(self):
        self.conn = connect(f"dbname='postgres' host='{self.host}' user='{self.user}'  password='{self.pwd}'")
        self.cursor = self.conn.cursor()

    def _close_conn(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()

    def execute_query(self, query: str) -> None:
        """Execute a SQL command. Used typically for commands that don't return a result, e.g. GRANT, ALTER

        Args:
            query (str): SQL command
        """
        self._open_conn()
        try:
            self.cursor.execute(query=query)
        except Exception as e:
            print(f"Could not execute query:\n{e}")
            self.conn.rollback()
        else:
            self.conn.commit()
        self._close_conn()

    def create_from_df(self, table_name: str, df: DataFrame) -> None:
        """CREATE table in NEBULA tasc_prod and insert a Pandas DataFrame. The table format created will mirror
        the dataframe types.

        Args:
            table_name (str): name of table you want to create. does not need the "tasc_prod." prefix
            df (DataFrame):  Dataframe you want to upload.
        """

        # this upload method does not expect the "tasc_prod." prefix. Remove it if it exists.
        table_name = sub("tasc_prod.", '', table_name)

        # use pandas get_schema method to generate original create table SQL
        create_table_sql = get_schema(df, "tasc_prod." + table_name)

        # get_schema adds quotation marks around the table name, which we don't want
        create_table_sql = sub('"', '', create_table_sql, 2)
        create_table_sql = sub('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS', create_table_sql)
        self.execute_query(create_table_sql)

    def insert_df(self, table_name: str, df: DataFrame) -> None:
        """INSERT DataFrame as new records into an NEBULA tasc_prod table. Make sure you have INSERT permissions
        on the table you're inserting into.

        Args:
            table_name (str): name of table you want to insert into. Does not need the "tasc_prod." prefix.
            df (DataFrame): Dataframe you want to insert
        """

        if df is None:
            print('df empty, nothing to insert')
            return None

        # this upload method does not expect the "tasc_prod." prefix. Remove it if it exists.
        table_name = sub("tasc_prod.", '', table_name)

        # create the table if it doesn't exist already
        self.create_from_df(table_name, df)

        # load dataframe up in stringIO buffer and then upload
        self._open_conn()
        try:
            buffer = StringIO()
            df.to_csv(buffer, index=False, header=False)
            buffer.seek(0)
            self.cursor.execute('SET search_path TO tasc_prod')
            column_names = ','.join(df.columns)
            self.cursor.copy_expert(f"copy {table_name}({column_names}) from stdout (format csv)", buffer)
        except Exception as e:
            self.conn.rollback()
            self._close_conn()
            raise Exception(f'Could not insert into table: {e})')
        else:
            self.conn.commit()
        self._close_conn()

    def upsert_df(self, table_name: str, df: DataFrame, conflict_columns: list) -> None:
        """Insert dataframe into tasc_prod table and update records if the record already exists (based on
        conflict_columns). The SQL query used is inspired by: https://stackoverflow.com/a/17267423/1960089

        Args: table_name (str): name of table in tasc_prod, excluding "tasc_prod." schema prefix df (
        DataFrame): dataframe with column headers matching the table headers in the tasc_prod table
        conflict_columns (list): a list of column names (strings) that can be used to uniquely identify which rows to
        update
        """

        if df is None:
            print('df empty, nothing to insert')
            return None

        columns_list = df.columns.tolist()
        update_list = [col for col in columns_list if col not in conflict_columns]
        if not set(conflict_columns).issubset(columns_list):
            print('Conflict columns provided must exist in dataframe column headers')
            return None

        # this upload method does not expect the "tasc_prod." prefix. Remove it if it exists.
        table_name = sub("tasc_prod.", '', table_name)

        # create temp table
        columns_str = ",".join(columns_list)
        create_temp_table_sql = get_schema(df, 'temp')
        create_temp_table_sql = sub('"', '', create_temp_table_sql, 2)
        create_temp_table_sql = sub('CREATE TABLE', 'CREATE TEMPORARY TABLE', create_temp_table_sql)

        # populate the temp table with data from the dataframe
        values_str = "%s," * len(columns_list)
        values = list(df.itertuples(index=False, name=None))
        insert_to_temp_sql = f"INSERT INTO temp ({columns_str}) VALUES ({values_str[:-1]})"

        # lock the target table
        lock_target_table_sql = f"LOCK TABLE tasc_prod.{table_name} IN EXCLUSIVE MODE"

        # update records where the conflict_columns return a match in the target table
        update_list_str = ", ".join([f'{col}=temp.{col}' for col in update_list])
        conflict_str = " AND ".join([f'{table_name}.{col}=temp.{col}' for col in conflict_columns])
        update_target_table_sql = f"""UPDATE tasc_prod.{table_name} SET {update_list_str} FROM temp 
                                    WHERE {conflict_str}"""

        # insert rows that don't match on conflict cols
        insert_columns_str = ",".join([f'{table_name}.{col}' for col in columns_list])
        null_filter_str = " AND ".join([f"{table_name}.{col} IS NULL" for col in conflict_columns])
        insert_target_table_sql = f"""INSERT INTO tasc_prod.{table_name} SELECT {insert_columns_str} FROM temp 
                                        LEFT OUTER JOIN tasc_prod.{table_name} ON ({conflict_str}) 
                                        WHERE {null_filter_str}"""

        # drop temp table
        drop_temp_table_sql = 'DROP TABLE temp'

        self._open_conn()
        try:
            sql = ';'.join(
                ['BEGIN', create_temp_table_sql, insert_to_temp_sql, lock_target_table_sql, update_target_table_sql,
                 insert_target_table_sql, drop_temp_table_sql])
            self.cursor.executemany(query=sql, vars_list=values)
        except Exception as e:
            self.conn.rollback()
            self._close_conn()
            raise Exception(f'Could not upsert into table:\n{e})')
        else:
            self.conn.commit()
        self._close_conn()

    def select_df(self, query: str) -> DataFrame:
        """GET data from NEBULA database and return the results in a pandas DataFrame.

        Args:
            query (str): SQL SELECT query you want to execute

        Returns:
            DataFrame: NEBULA response from your query

        Example:
            You can get data from NEBULA in 3 lines

                from eii.utils.nebula import NebulaConnector

                nebula = NebulaConnector()
                df = nebula.select_df("SELECT * FROM public.v_xref_idx_map LIMIT 10")

        """
        self._open_conn()
        data = read_sql_query(query, con=self.conn)
        self._close_conn()
        return data
