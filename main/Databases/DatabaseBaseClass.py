from typing import Protocol
from ..models import TableAndDescription

class DatabaseBaseClass(Protocol):

    def provide_table_names() -> list[TableAndDescription]:
        ...

    def disconnect():
        ...

    def first_step():
        ...