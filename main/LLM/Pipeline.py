from ..llm_config_defs import LLMMainConfig
from .BaseLLM import BaseLLM
from ..models import TableAndDescription, QueryGenerationOutput, TableDecisionOutput

class Pipeline:
    def __init__(self, config: LLMMainConfig, llm: BaseLLM):
        self.config = config
        self.llm = llm

    @staticmethod
    def new_instance_from_config(config: LLMMainConfig) -> "Pipeline": 
        from .Bedrock import Bedrock
        
        match config.llm.llm_tag:
            case config.llm.llm_tag:
                return Pipeline(config, Bedrock(config))
            case _:
                raise ValueError("Invalid LLM tag")

    def return_table_names_list(self, request:str, table_names_and_descriptions: list[TableAndDescription]) -> TableDecisionOutput:
        translated_request = self.llm.translate(request= request)
        table_decision_step = self.llm.table_decision_step(request= translated_request, table_names_and_descriptions= table_names_and_descriptions)
        return TableDecisionOutput(
            table_names = table_decision_step.table_names
        )
    
    def generate_sql_query_step(self, request: str, table_names: TableDecisionOutput, sql_type: str) -> QueryGenerationOutput:
        translated_request = self.llm.translate(request= request)
        query_generation_step = self.llm.query_generation_step(request= translated_request, table_names= table_names, sql_type= sql_type)
        return QueryGenerationOutput(
            result = query_generation_step.result
        )