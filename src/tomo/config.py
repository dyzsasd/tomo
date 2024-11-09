from typing import List, Dict, Any
import yaml

from tomo.shared.intent import Intent
from tomo.shared.slots import Slot


# Policy configuration
class PolicyConfig:
    def __init__(self, policy_type: str, **kwargs):
        self.policy_type = policy_type
        self.kwargs = kwargs  # Store other policy-specific fields dynamically


# NLU configuration
class NLUConfig:
    def __init__(self, nlu_type: str, config: Dict[str, Any]):
        self.nlu_type = nlu_type
        self.config = config


# Assistant configuration
class AssistantConfig:
    def __init__(
        self,
        name: str,
        intents: List[Intent],
        slots: List[Slot],
        policies: List[PolicyConfig],
        nlu: NLUConfig,
    ):
        self.name = name
        self.intents = intents
        self.slots = slots
        self.policies = policies
        self.nlu = nlu


# Configuration loader class
class AssistantConfigLoader:
    def __init__(self, yaml_file: str):
        self.yaml_file = yaml_file

    def load(self) -> AssistantConfig:
        # Load YAML data
        with open(self.yaml_file, "r") as file:
            data = yaml.safe_load(file)

        # Parse assistant configuration
        assistant_data = data["assistant"]
        name = assistant_data.get("name", "Default Assistant")

        # Parse intents
        intents = [Intent(**intent) for intent in assistant_data.get("intents", [])]

        # Parse slots
        slots = [Slot(**slot) for slot in assistant_data.get("slots", [])]

        # Parse policies
        policies = [
            PolicyConfig(**policy_data)
            for policy_data in assistant_data.get("policies", [])
        ]

        # Parse NLU config
        nlu_data = assistant_data["nlu"]
        nlu = NLUConfig(nlu_type=nlu_data["nlu_type"], config=nlu_data["config"])

        # Create AssistantConfig instance
        assistant_config = AssistantConfig(
            name=name, intents=intents, slots=slots, policies=policies, nlu=nlu
        )

        return assistant_config
