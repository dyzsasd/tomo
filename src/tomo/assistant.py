import logging

from tomo.config import AssistantConfig, NLUConfig, PolicyConfig
from tomo.core.policies import Policy
from tomo.nlu.parser import NLUParser


logger = logging.getLogger(__name__)


class Assistant:
    def __init__(self, config: AssistantConfig):
        self.config = config
        self.name = config.name
        self.slots = config.slots
        self.policies = []
        self.nlu_parser = None
        self.initialize_components()

    def initialize_components(self):
        # Initialize policies
        for policy_conf in self.config.policies:
            policy = self.create_policy(policy_conf)
            if policy:
                self.policies.append(policy)
        # Initialize NLU parser
        self.nlu_parser = self.create_nlu_parser(self.config.nlu)

    def create_policy(self, policy_conf: PolicyConfig):
        return Policy.create(policy_conf.policy_type, **policy_conf.kwargs)

    def create_nlu_parser(self, nlu_config: NLUConfig):
        config = nlu_config.config or {}
        if nlu_config.nlu_type == "LLMNLUParser":
            return NLUParser(intents=self.config.intents, config=config)
        logger.warning(f"Unknown NLU parser type: {nlu_config.nlu_type}")
        return None
