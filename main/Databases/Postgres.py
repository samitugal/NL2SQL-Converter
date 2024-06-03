from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import List
from .DatabaseBaseClass import DatabaseBaseClass
from ..database_config_defs import MainConfig, DatabaseTag
from ..models import TableAndDescription, DatabaseQueryResponse, TableNameAndColumns, TableRelationModel
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
        
    def provide_table_relations(self) -> list[TableRelationModel]:
        metadata_query = """
        SELECT
            kcu.table_name AS child_table,
            kcu.column_name AS child_column,
            ccu.table_name AS parent_table,
            ccu.column_name AS parent_column
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        ORDER BY
            kcu.table_name, kcu.column_name;
        """
        result = self.session.execute(text(metadata_query)).fetchall()
        
        table_relations = []
        for row in result:
            relation = TableRelationModel(
                ParentTableName=row[2],  # parent_table
                ParentTableColumnName=row[3],  # parent_column
                ChildTableName=row[0],  # child_table
                ChildTableColumnName=row[1]  # child_column
            )
            table_relations.append(relation)
        
        return table_relations

    def execute_query(self, query: str) -> DatabaseQueryResponse:
        result = self.session.execute(text(query))
        rows = result.fetchall()
        columns = list(result.keys())
        ##

        return DatabaseQueryResponse(rows= rows, columns= columns)
