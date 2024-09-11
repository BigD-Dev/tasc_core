from pandas import DataFrame
from pandas.io.sql import get_schema  # type: ignore
from re import sub
from io import StringIO
from blkcore.user import get_user
from blkcore.sso import get_auth_passwd
from eii.utils.util_db_connector import DbConnector  # from util_db_connector import DbConnector #


class NebulaConnector(DbConnector):
    """This object handles connections to Nebula database and any SQL query you want to run.
    NebulaConnector inherits the READ-only methods from the generic DbConnector object (e.g. select_df() and execute_query()), and
    adds on WRITE methods (e.g. insert_df()), since Nebula has a sandbox schema where EII Citizen Developers often have WRITE permissions.

    Example:
        You can get data from Nebula in 3 lines::

            from eii.utils.nebula import NebulaConnector

            nebula = NebulaConnector()
            df = nebula.select_df("SELECT * FROM public.v_xref_idx_map LIMIT 10")

    """

    def __init__(self, server_adapter='postgresql+psycopg2', host='iresa-mpp', database='nebula', port='5432',
                 username='', password='', driver='') -> None:
        username = username or get_user()
        password = password or get_auth_passwd()
        super().__init__(server_adapter, host, database, port, username, password, driver)  # type: ignore

    def create_from_df(self, table_name: str, df: DataFrame) -> None:
        """CREATE table in Nebula sandbox and insert a Pandas DataFrame. The table format created will mirror the dataframe types.

        Args:
            table_name (str): name of table you want to create. does not need the "sandbox." prefix
            df (DataFrame):  Dataframe you want to upload.
        """

        # this upload method does not expect the "sandbox." prefix. Remove it if it exists.
        table_name = sub("sandbox.", '', table_name)

        # use pandas get_schema method to generate original create table SQL
        create_table_sql = get_schema(df, "sandbox." + table_name)

        # get_schema adds quotation marks around the table name, which we don't want
        create_table_sql = sub('"', '', create_table_sql, 2)
        create_table_sql = sub('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS', create_table_sql)
        self.execute_query(create_table_sql)

    def insert_df(self, table_name: str, df: DataFrame) -> None:
        """INSERT DataFrame as new records into an Nebula sandbox table. Make sure you have INSERT permissions on the table you're inserting into.

        Args:
            table_name (str): name of table you want to insert into. Does not need the "sandbox." prefix.
            df (DataFrame): Dataframe you want to insert
        """

        if df is None:
            print('df empty, nothing to insert')
            return None

        # this upload method does not expect the "sandbox." prefix. Remove it if it exists.
        table_name = sub("sandbox.", '', table_name)

        # create the table if it doesn't exist already
        self.create_from_df(table_name, df)

        conn = self.engine.raw_connection()
        try:
            cursor = conn.cursor()
            try:
                # Convert DataFrame to CSV format in memory
                buffer = StringIO()
                df.to_csv(buffer, index=False, header=False)
                buffer.seek(0)
                cursor.execute(f"SET search_path TO sandbox")
                column_names = ','.join(df.columns)
                cursor.copy_expert(f"copy {table_name}({column_names}) from stdout (format csv)", buffer)
                conn.commit()
            finally:
                cursor.close()
        except Exception as e:
            conn.rollback()
            raise Exception(f'Could not insert into table: {e}')
        finally:
            conn.close()

    def upsert_df(self, table_name: str, df: DataFrame, conflict_columns: list) -> None:
        """Insert dataframe into sandbox table and update records if the record already exists (based on conflict_columns).
        The SQL query used is insipired by: https://stackoverflow.com/a/17267423/1960089

        Args:
            table_name (str): name of table in sandbox, excluding "sandbox." schema prefix
            df (DataFrame): dataframe with column headers matching the table headers in the sandbox table
            conflict_columns (list): a list of column names (strings) that can be used to uniquely identify which rows to update
        """
        self.insert_df(table_name='eii_package_usage', df=DataFrame([{'username': get_user(),
                                                                      'environment': 'NebulaConnector',
                                                                      'module': 'eii.utils.nebula.upsert',
                                                                      'detail': None}]))
        print(
            'We intend to deprecate upsert_df end of Jan 2024 as part of the python 3.9 upgrade. Please inform James Gnanamithran if this will impact your code.')

        if df is None:
            print('df empty, nothing to insert')
            return None

        columns_list = df.columns.tolist()
        update_list = [col for col in columns_list if col not in conflict_columns]
        if not set(conflict_columns).issubset(columns_list):
            print('Conflict columns provided must exist in dataframe column headers')
            return None

        # this upload method does not expect the "sandbox." prefix. Remove it if it exists.
        table_name = sub("sandbox.", '', table_name)

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
        lock_target_table_sql = f"LOCK TABLE sandbox.{table_name} IN EXCLUSIVE MODE"

        # update records where the conflict_columns return a match in the target table
        update_list_str = ", ".join([f'{col}=temp.{col}' for col in update_list])
        conflict_str = " AND ".join([f'{table_name}.{col}=temp.{col}' for col in conflict_columns])
        update_target_table_sql = f"UPDATE sandbox.{table_name} SET {update_list_str} FROM temp WHERE {conflict_str}"

        # insert rows that don't match on conflict cols
        insert_columns_str = ",".join([f'{table_name}.{col}' for col in columns_list])
        null_filter_str = " AND ".join([f"{table_name}.{col} IS NULL" for col in conflict_columns])
        insert_target_table_sql = f'INSERT INTO sandbox.{table_name} SELECT {insert_columns_str} FROM temp LEFT OUTER JOIN sandbox.{table_name} ON ({conflict_str}) WHERE {null_filter_str}'

        # drop temp table
        drop_temp_table_sql = 'DROP TABLE temp'

        conn = self.engine.raw_connection()
        try:
            cursor = conn.cursor()
            try:
                sql = ';'.join(
                    ['BEGIN', create_temp_table_sql, insert_to_temp_sql, lock_target_table_sql, update_target_table_sql,
                     insert_target_table_sql, drop_temp_table_sql])
                cursor.executemany(sql, values)
                conn.commit()
            finally:
                cursor.close()
        except Exception as e:
            conn.rollback()
            raise Exception(f'Could not insert into table: {e}')
        finally:
            conn.close()