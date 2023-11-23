"""Script tp create the GPT assistants."""
import typer
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


def create_assistants() -> None:
    """Create OpenAI GPT assistants.

    Create OpenAI GPT assistants with the OpenAI API and save their IDs in a YAML file.
    """
    client = OpenAI()

    assistants_ids = {}

    for (
        assistant_level,
        assistant_instructions,
    ) in ASSISTANTS_CUSTOM_INSTRUCTIONS.items():
        assistant = client.beta.assistants.create(
            name=f"{ASSISTANT_NAME_PREFIX}{assistant_level}",
            model=ASSISTANT_MODEL,
            description=ASSISTANT_DESCRIPTION,
            instructions=f"{assistant_instructions}\n{ASSISTANT_COMMON_INSTRUCTIONS}",
        )
        assistants_ids[assistant_level] = assistant.id

    with ASSISTANTS_IDS_YAML_PATH.open("w") as assistants_ids_yaml:
        yaml.dump(assistants_ids, assistants_ids_yaml)


if __name__ == "__main__":
    typer.run(create_assistants)
