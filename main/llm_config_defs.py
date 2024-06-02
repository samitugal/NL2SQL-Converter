from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import omegaconf
from omegaconf import OmegaConf

class LLMTag(Enum):
    BEDROCK = "bedrock"
    OPENAI = "openai"
    GEMINI = "gemini"

@dataclass
class LLMConfig:
    llm_tag: LLMTag = omegaconf.MISSING
    temperature: float = 0.0

@dataclass
class BedrockConfig:
    region_name: str = "us-east-1"
    model_id: str = "claude-3-sonnet-20240229-v1:0"

@dataclass
class OpenAIConfig:
    llm_tag: LLMTag = LLMTag.OPENAI
    model_name: str = "gpt-4-1106-preview"
    json_mode: bool = True

@dataclass
class LLMMainConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    bedrock: Optional[BedrockConfig] = None
    openai: Optional[OpenAIConfig] = None

    @staticmethod
    def from_file(yaml_path: str) -> "MainConfig":
        conf = OmegaConf.structured(LLMMainConfig)
        conf = OmegaConf.merge(conf, OmegaConf.load(yaml_path))

        return conf

if __name__ == "__main__":
    cfg = LLMMainConfig()
    yaml_str = OmegaConf.to_yaml(cfg)

    conf = OmegaConf.structured(MainConfig)
    conf = OmegaConf.merge(conf, OmegaConf.load("./configs/openai.yaml"))

    print(conf)