# Database.py
from ..database_config_defs import MainConfig, DatabaseTag
from .DatabaseBaseClass import DatabaseBaseClass
from .Postgres import Postgres

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

if __name__ == "__main__":
    db = Database.new_instance_from_config(MainConfig)
    db.close()
