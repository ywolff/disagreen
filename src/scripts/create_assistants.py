"""Create the GPT assistant with the OpenAI API."""
import yaml
from openai import OpenAI

from src.constants.assistants_config import (
    ASSISTANT_COMMON_INSTRUCTIONS,
    ASSISTANT_DESCRIPTION,
    ASSISTANT_MODEL,
    ASSISTANT_NAME_PREFIX,
    ASSISTANTS_CUSTOM_INSTRUCTIONS,
)
from src.constants.paths import ASSISTANTS_IDS_YAML_PATH

client = OpenAI()

assistants_ids = {}

for assistant in client.beta.assistants.list():
    if assistant.name and assistant.name.startswith(ASSISTANT_NAME_PREFIX):
        client.beta.assistants.delete(assistant.id)

for assistant_level, assistant_instructions in ASSISTANTS_CUSTOM_INSTRUCTIONS.items():
    assistant = client.beta.assistants.create(
        name=f"{ASSISTANT_NAME_PREFIX}{assistant_level}",
        model=ASSISTANT_MODEL,
        description=ASSISTANT_DESCRIPTION,
        instructions=f"{assistant_instructions}\n{ASSISTANT_COMMON_INSTRUCTIONS}",
    )
    assistants_ids[assistant_level] = assistant.id

with ASSISTANTS_IDS_YAML_PATH.open("w") as assistants_ids_yaml:
    yaml.dump(assistants_ids, assistants_ids_yaml)
