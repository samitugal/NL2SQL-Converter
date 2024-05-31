from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import omegaconf
from omegaconf import OmegaConf

class DatabaseTag(Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    ORACLE = "oracle"
    SQLITE = "sqlite"
    MSSQL = "mssql"

@dataclass
class DatabaseConfig:
    database_tag: DatabaseTag = omegaconf.MISSING

@dataclass
class PostgreSQLConfig:
    database_name: str = omegaconf.MISSING
    user: str = omegaconf.MISSING
    password: str = omegaconf.MISSING
    host: str = omegaconf.MISSING
    port: int = omegaconf.MISSING

@dataclass
class MainConfig:
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    postgresql: Optional[PostgreSQLConfig] = None

    @staticmethod
    def from_file(yaml_path: str) -> "MainConfig":
        conf = OmegaConf.structured(MainConfig)
        conf = OmegaConf.merge(conf, OmegaConf.load(yaml_path))

        return conf

if __name__ == "__main__":
    cfg = MainConfig()
    yaml_str = OmegaConf.to_yaml(cfg)

    conf = OmegaConf.structured(MainConfig)
    conf = OmegaConf.merge(conf, OmegaConf.load("./configs/postgresql.yaml"))
    print(conf)