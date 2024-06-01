from typing import Protocol
from ..models import TableAndDescription, TableNameAndColumns

class DatabaseBaseClass(Protocol):

    def provide_table_names() -> list[TableAndDescription]:
        ...
    
    def provide_column_names_of_table(table_names: list[str]) -> list[TableNameAndColumns]:
        ...

    def disconnect():
        ...

    def first_step():
        ...