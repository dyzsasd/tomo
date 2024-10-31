import asyncio
import uuid
import logging
import os

from dotenv import load_dotenv

from tomo.core.output_channels import CollectingOutputChannel
from tomo.core.policies.manager import LocalPolicyManager
from tomo.core.policies.policies import QuickResponsePolicy
from tomo.core.processor import MessageProcessor
from tomo.core.sessions import InMemorySessionManager
from tomo.core.user_message import TextUserMessage
from tomo.nlu.parser import NLUParser
from tomo.shared.action_executor import ActionExector


# Load environment variables from .env file
load_dotenv()

# Now you can access the OpenAI API key as an environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set logging level to DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Define log format
)


nlu_config = {
    "llm_type": "openai",
    "llm_params": {"model_name": "gpt-3.5-turbo", "temperature": 0.0},
    "intents": [
        "greet: The user want to say hello and ask some information with the robot",
        "weather: The user want to know the weather information of same where",
        "find_flight: The user want to find the flight for their trip",
    ],
    "entities": [
        "weather_place: the city where the user want to find the weather information",
        "origin: the city where the user lives.",
        "destination: the place that the user want travel to",
    ],
}


async def main():
    # Initialize dependencies required by MessageProcessor
    session_manager = InMemorySessionManager()
    policy_manager = LocalPolicyManager(
        policies=[
            QuickResponsePolicy(
                message="Thanks for your requirement, just a minute !", waiting_time=100
            ),
        ],
    )
    action_executor = ActionExector()
    nlu_parser = NLUParser(config=nlu_config)

    # Initialize the MessageProcessor with required dependencies
    message_processor = MessageProcessor(
        session_manager=session_manager,
        policy_manager=policy_manager,
        action_exector=action_executor,
        nlu_parser=nlu_parser,
    )
    # Define a session ID (could be a user ID or conversation ID)
    session_id = uuid.uuid4().hex
    output_channel = CollectingOutputChannel()

    await message_processor.start_new_session(session_id, output_channel)

    print("Welcome to the bot shell. Type 'quit' or 'exit' to end the conversation.")

    while True:
        # Retrieve and print the bot's response(s)
        for bot_message in output_channel.messages:
            if bot_message.text:
                print(f"Bot: {bot_message.text}")
            if bot_message.image:
                print(f"Bot sent an image: {bot_message.image}")
            if bot_message.buttons:
                print("Bot sent buttons:")
                for idx, button in enumerate(bot_message.buttons):
                    print(f"{idx + 1}: {button.get('title')}")
            if bot_message.quick_replies:
                print("Bot sent quick replies:")
                for idx, reply in enumerate(bot_message.quick_replies):
                    print(f"{idx + 1}: {reply.get('title')}")
            if bot_message.custom:
                print(f"Bot sent custom data: {bot_message.custom}")
            if bot_message.attachment:
                print(f"Bot sent an attachment: {bot_message.attachment}")
            if bot_message.elements:
                print("Bot sent elements:")
                for element in bot_message.elements:
                    print(
                        f"- {element.get('title', '')}: {element.get('subtitle', '')}"
                    )
            # Handle other message types as needed

        # Clear the messages after processing
        output_channel.messages.clear()

        # Read input from the command line
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break

        # Create a UserMessage instance for the user's input
        user_message = TextUserMessage(
            text=user_input,
            output_channel=output_channel,
            session_id=session_id,
            input_channel="cmdline",
        )

        # Process the message asynchronously
        await message_processor.handle_message(user_message)


if __name__ == "__main__":
    # Run the main coroutine
    asyncio.run(main())
