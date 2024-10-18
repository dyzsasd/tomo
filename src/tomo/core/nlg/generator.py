import logging
from typing import List, Optional, Union, Text, Any, Dict

from your_project_domain_module import Domain  # Placeholder for your project's domain class
from your_project_trackers_module import DialogueStateTracker  # Placeholder for tracker
from your_project_endpoints_module import EndpointConfig  # Placeholder for endpoint config

logger = logging.getLogger(__name__)


class NaturalLanguageGenerator:
    """Generate bot utterances for TOMO based on a dialogue state."""

    async def generate(
        self,
        utter_action: Text,
        tracker: "DialogueStateTracker",
        output_channel: Text,
        **kwargs: Any,
    ) -> Optional[Dict[Text, Any]]:
        """Generate a response for TOMO for the requested utter action.

        TOMO will use predefined responses from the domain or any ML-based 
        generation depending on the use case.
        """
        raise NotImplementedError("This method should be implemented in a subclass.")

    @staticmethod
    def create(
        obj: Union["NaturalLanguageGenerator", EndpointConfig, None],
        domain: Optional[Domain],
    ) -> "NaturalLanguageGenerator":
        """Factory method to create the TOMO's NLG generator."""
        if isinstance(obj, NaturalLanguageGenerator):
            return obj
        else:
            return _create_from_endpoint_config(obj, domain)


def _create_from_endpoint_config(
    endpoint_config: Optional[EndpointConfig] = None, domain: Optional[Domain] = None
) -> "NaturalLanguageGenerator":
    """Create a generator based on the endpoint configuration for TOMO."""
    domain = domain or Domain.empty()

    if endpoint_config is None:
        from tomo_nlg import TemplatedNaturalLanguageGenerator
        # The default implementation for TOMO will be template-based NLG
        nlg: "NaturalLanguageGenerator" = TemplatedNaturalLanguageGenerator(domain.responses)
    elif endpoint_config.type is None or endpoint_config.type.lower() == "callback":
        from tomo_nlg import CallbackNaturalLanguageGenerator
        # Use callback-based NLG if specified
        nlg = CallbackNaturalLanguageGenerator(endpoint_config=endpoint_config)
    elif endpoint_config.type.lower() == "response":
        from tomo_nlg import TemplatedNaturalLanguageGenerator
        # Fallback to template-based generation using the domain responses
        nlg = TemplatedNaturalLanguageGenerator(domain.responses)
    else:
        nlg = _load_from_module_name_in_endpoint_config(endpoint_config, domain)

    logger.debug(f"Instantiated TOMO NLG as '{nlg.__class__.__name__}'.")
    return nlg


def _load_from_module_name_in_endpoint_config(
    endpoint_config: EndpointConfig, domain: Domain
) -> "NaturalLanguageGenerator":
    """Initializes a custom natural language generator."""
    try:
        nlg_class = your_project_utils.common.class_from_module_path(
            endpoint_config.type
        )
        return nlg_class(endpoint_config=endpoint_config, domain=domain)
    except (AttributeError, ImportError) as e:
        raise Exception(
            f"Could not find a class based on the module path "
            f"'{endpoint_config.type}'. Failed to create a "
            f"`NaturalLanguageGenerator` instance. Error: {e}"
        )


class ResponseVariationFilter:
    """Filters response variations based on the channel, action, and condition for TOMO."""

    def __init__(self, responses: Dict[Text, List[Dict[Text, Any]]]) -> None:
        self.responses = responses

    @staticmethod
    def _matches_filled_slots(
        filled_slots: Dict[Text, Any], response: Dict[Text, Any]
    ) -> bool:
        """Checks if the response variation matches the filled slots in TOMO."""
        constraints = response.get("condition", [])
        for constraint in constraints:
            name = constraint["name"]
            value = constraint["value"]
            filled_slots_value = filled_slots.get(name)
            if isinstance(filled_slots_value, str) and isinstance(value, str):
                if filled_slots_value.casefold() != value.casefold():
                    return False
            elif filled_slots_value != value:
                return False
        return True

    def responses_for_utter_action(
        self,
        utter_action: Text,
        output_channel: Text,
        filled_slots: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Returns responses that fit the channel, action, and condition for TOMO."""
        default_responses = list(
            filter(lambda x: x.get("condition") is None, self.responses[utter_action])
        )
        conditional_responses = list(
            filter(
                lambda x: x.get("condition") and self._matches_filled_slots(filled_slots, x),
                self.responses[utter_action],
            )
        )
        conditional_channel = list(
            filter(lambda x: x.get("channel") == output_channel, conditional_responses)
        )
        default_channel = list(
            filter(lambda x: x.get("channel") == output_channel, default_responses)
        )
        if conditional_channel:
            return conditional_channel
        if default_channel:
            return default_channel
        return conditional_responses if conditional_responses else default_responses