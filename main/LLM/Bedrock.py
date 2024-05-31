import boto3
import html
import re
from typing import TypeVar
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
from anthropic import AnthropicBedrock

from ..models import TableDecisionOutput, TableAndDescription, GenerateResponseRequest
from ..llm_config_defs import LLMMainConfig, LLMTag
from .BaseLLM import BaseLLM
from ..PromptRenderer import PromptRenderer

U = TypeVar("U", bound=BaseModel)

class Bedrock(BaseLLM):
    def __init__(self, config: LLMMainConfig):
        if config.llm.llm_tag != LLMTag.BEDROCK:
            raise ValueError("BedrockPipeline can only be used with Bedrock")
        if config.bedrock is None:
            raise ValueError("BedrockPipeline requires a BedrockConfig")

        self.config = config
        load_dotenv()

        self.prompt_renderer = PromptRenderer("main", "prompts")
        self.client = AnthropicBedrock(aws_region=config.bedrock.region_name)
        self.aws_translator = boto3.client(service_name='translate', region_name=config.bedrock.region_name, use_ssl=True)
    
    def _send_anthropic_message(self, content: str) -> str:

        message = self.client.messages.create(
            temperature=self.config.llm.temperature,
            model=self.config.bedrock.model_id, # type: ignore[union-attr]
            max_tokens=4096,
            messages=[{"role": "user", "content": content}]
        )
        output = message.content[-1].text
        print(content)
        return output
    
    def _clean_json_string(self, json_string):
        json_regex = re.compile(r'```json(.*?)```', re.DOTALL)
        json_match = json_regex.search(json_string)
        return json_match.group(1).strip()
    
    def _parse_response(self, model: type[U], response: str) -> U:
        return model.model_validate_json(self._clean_json_string(response))

    def _validated_anthropic_request(self, model: type[U], content: str) -> U:
        response = self._send_anthropic_message(html.unescape(content))
        return self._parse_response(model, response)

    def translate(self, request: GenerateResponseRequest) -> str:
        translated_request = self.aws_translator.translate_text(Text=str(request), SourceLanguageCode="auto", TargetLanguageCode="en")["TranslatedText"]
        return translated_request

    def table_decision_step(self, request: str, table_names_and_descriptions: list[TableAndDescription]) -> TableDecisionOutput:
        prompt = self.prompt_renderer.render_prompt_with_json_schema(
            "TableDecisionStep", TableDecisionOutput, {
                "translated_request": self.translate(request = request),
                "tables_and_descriptions": table_names_and_descriptions
            }
        )
        return self._validated_anthropic_request(TableDecisionOutput, prompt)

    