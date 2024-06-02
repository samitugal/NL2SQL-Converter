import html
import re
import json

from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.globals import set_debug
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError
from typing import TypeVar

from ..models import TableDecisionOutput, TableAndDescription, GenerateResponseRequest, QueryGenerationOutput, TableNameAndColumns, TranslateModelOutput
from ..llm_config_defs import LLMMainConfig, LLMTag
from .BaseLLM import BaseLLM
from ..PromptRenderer import PromptRenderer

U = TypeVar("U", bound=BaseModel)

class OpenAI(BaseLLM):
    def __init__(self, config: LLMMainConfig):
        if(config.llm.llm_tag != LLMTag.OPENAI):
            raise ValueError("OpenAIPipeline can only be used with OpenAI")
        if config.openai is None:
            raise ValueError("OpenAIPipeline requires a OpenAIConfig")
        
        load_dotenv()
        self.config = config
        self.prompt_renderer = PromptRenderer("main", "prompts")
        
        if config.openai.json_mode:
            model_kwargs = {"response_format": {"type": "json_object"}}
        else:
            model_kwargs = {}
        self.client = ChatOpenAI(model=config.openai.model_name, temperature=config.llm.temperature, model_kwargs=model_kwargs)

    def _send_openai_message(self, content: str) -> str:
        messages = [
            ("human", content),
        ]
        output = self.client.invoke(messages)
        print(output.content)
        return output.content
    
    def _clean_json_string(self, json_string):
        try:
            json.loads(json_string)
            return json_string
        except json.JSONDecodeError:
            json_regex = re.compile(r'```json(.*?)```', re.DOTALL)
            json_match = json_regex.search(json_string)
            if json_match:
                raw_json = json_match.group(1).strip()
                cleaned_json = re.sub(r'[\x00-\x1F]+', '', raw_json)
                if cleaned_json != raw_json:
                    return cleaned_json
                else:
                    return raw_json
            else:
                raise ValueError("No JSON content found within triple backticks")
    
    def _parse_response(self, model: type[U], response: str) -> U:
        return model.model_validate_json(self._clean_json_string(response))

    def _validated_openai_request(self, model: type[U], content: str) -> U:
        response = self._send_openai_message(html.unescape(content))
        return self._parse_response(model, response)

    def translate(self, request: str) -> TranslateModelOutput:
        translate_model_prompt = self.prompt_renderer.render_prompt_with_json_schema(
            "TranslatePrompt", TranslateModelOutput, {
                "request": request
            }
        )
        return self._validated_openai_request(TranslateModelOutput, translate_model_prompt)

    def table_decision_step(self, request: str, table_names_and_descriptions: list[TableAndDescription]) -> TableDecisionOutput:
        table_decision_prompt = self.prompt_renderer.render_prompt_with_json_schema(
            "TableDecisionStep", TableDecisionOutput, {
                "translated_request": request,
                "tables_and_descriptions": table_names_and_descriptions
            }
        )     
        return self._validated_openai_request(TableDecisionOutput, table_decision_prompt)
    
    def query_generation_step(self, request: str, table_names: TableDecisionOutput, column_list: list[TableNameAndColumns], sql_type: str) -> QueryGenerationOutput:
        query_generation_prompt = self.prompt_renderer.render_prompt_with_json_schema(
            "QueryGeneratorStep", QueryGenerationOutput, {
                "translated_request": request,
                "table_names": table_names,
                "table_names_and_column_information": column_list,
                "sql_type": sql_type
            }
        )   
        return self._validated_openai_request(QueryGenerationOutput, query_generation_prompt)
