import json
from typing import TypeVar, Any
from jinja2 import Environment, PackageLoader, select_autoescape
from pydantic import BaseModel
from pprint import pformat

U = TypeVar("U", bound=BaseModel)

class PromptRenderer:
    def __init__(self, package_name: str, template_dir: str):
        self._jinja_env = Environment(
            loader = PackageLoader(package_name, template_dir),
            autoescape = select_autoescape(["xml"])
        )

    def render_prompt(self, prompt_template: str, values: dict[str, Any]) -> str:
        if not prompt_template.endswith(".xml"):
            prompt_template = prompt_template + ".xml"
        
        values = {k: pformat(v, indent=2) for k, v in values.items()}
        
        return self._jinja_env.get_template(prompt_template).render(values)

    def render_prompt_with_json_schema(self, prompt_template: str, model: type[U],  values: dict[str, Any]) -> str:
        rendered_prompt = self.render_prompt(prompt_template, values)
        rendered_prompt += "\nConform to the following JSON schema for output:\n" + json.dumps(model.model_json_schema(), indent=2)

        return rendered_prompt