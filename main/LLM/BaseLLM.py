from typing import Protocol
from ..models import TableAndDescription, TableDecisionOutput, QueryGenerationOutput, TableRelationModel

class BaseLLM(Protocol):

    def translate(self, request: str) -> str:
        ...

    def table_decision_step(self, request: str, tables_and_descriptions: list[TableAndDescription], table_relations = list[TableRelationModel]) -> TableDecisionOutput:
        ...

    def generate_sql_query_step(self, request: str, table_names: TableDecisionOutput, sql_type: str) -> QueryGenerationOutput:
        ...
    