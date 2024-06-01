from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import List
from .DatabaseBaseClass import DatabaseBaseClass
from ..database_config_defs import MainConfig, DatabaseTag
from ..models import TableAndDescription, DatabaseQueryResponse, TableNameAndColumns
from dotenv import load_dotenv
import os

class Postgres(DatabaseBaseClass):
    def __init__(self, config: MainConfig):
        if config.db.database_tag != DatabaseTag.POSTGRESQL:
            raise ValueError("PostgreSQLConfig can only be used with PostgreSQL.")
        if config.db is None:
            raise ValueError("PostgreSQL requires PostgreSQL Config.")
        
        load_dotenv()
        self.config = config

        self.connection_string = f"postgresql://{config.postgresql.user}:{config.postgresql.password}@{config.postgresql.host}:{config.postgresql.port}/{config.postgresql.database_name}"
        
        self.engine = create_engine(self.connection_string)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def disconnect(self):
        self.session.close()

    def provide_table_names(self) -> List[TableAndDescription]:
        metadata_query = """
        SELECT
            c.relname AS table_name,
            pgd.description AS description,
            (
                SELECT STRING_AGG(a.attname, ', ')
                FROM pg_catalog.pg_attribute a
                WHERE a.attrelid = c.oid
                    AND a.attnum > 0
                    AND NOT a.attisdropped
            ) AS columns
        FROM
            pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            LEFT JOIN pg_catalog.pg_description pgd ON pgd.objoid = c.oid AND pgd.objsubid = 0
        WHERE
            c.relkind = 'r' -- only tables
            AND n.nspname = 'public' -- only public schema
        ORDER BY
            c.relname;
        """
        result = self.session.execute(text(metadata_query)).fetchall()
        return [TableAndDescription(table_name=row[0], description=row[1], columns=row[2]) for row in result]

    def provide_column_names_of_tables(self, table_names: List[str]) -> List[TableNameAndColumns]:
        table_columns_info = []

        for table_name in table_names:
            metadata_query = f"""
            SELECT
                a.attname AS column_name
            FROM
                pg_catalog.pg_attribute a
                JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
                JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
            WHERE
                c.relname = '{table_name}'
                AND n.nspname = 'public'
                AND a.attnum > 0
                AND NOT a.attisdropped
            ORDER BY
                a.attnum;
            """

            result = self.session.execute(text(metadata_query), {'table_name': table_name}).fetchall()
            column_names = [row[0] for row in result]
            table_columns_info.append(TableNameAndColumns(TableName=table_name, Columns=column_names))
        
        return table_columns_info

    def execute_query(self, query: str) -> DatabaseQueryResponse:
        result = self.session.execute(text(query))
        rows = result.fetchall()
        columns = list(result.keys())
        ##
        print("RowsType: ", type(rows))
        print("ColumnsType: ", type(columns))
        ##
        return DatabaseQueryResponse(rows= rows, columns= columns)
