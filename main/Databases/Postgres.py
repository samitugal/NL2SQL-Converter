from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .DatabaseBaseClass import DatabaseBaseClass
from ..database_config_defs import MainConfig, DatabaseTag
from ..models import TableAndDescription
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

    def provide_table_names(self) -> list[TableAndDescription]:
        print(self.connection_string)
        metadata_query = """
        SELECT
            c.relname AS table_name,
            pgd.description AS description
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
        return [TableAndDescription(table_name=row[0], description=row[1]) for row in result]
