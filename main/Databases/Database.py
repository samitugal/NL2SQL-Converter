# Database.py
from ..database_config_defs import MainConfig, DatabaseTag
from .DatabaseBaseClass import DatabaseBaseClass
from .Postgres import Postgres
from ..models import DatabaseQueryResponse, TableNameAndColumns

class Database:
    def __init__(self, config: MainConfig, database: DatabaseBaseClass):
        self.config = MainConfig
        self.database = database

    @staticmethod
    def new_instance_from_config(config: MainConfig):
        if config.db.database_tag == DatabaseTag.POSTGRESQL:
            return Postgres(config)
        else:
            raise NotImplementedError

    def execute_query(self, query: str) -> DatabaseQueryResponse:
        return self.database.execute_query(query)

    def provide_column_names_of_table(self, table_name: str) -> list[TableNameAndColumns]:
        return self.database.provide_column_names_of_table(table_name)

    def close(self):
        self.database.close()

if __name__ == "__main__":
    db = Database.new_instance_from_config(MainConfig)
    db.close()
