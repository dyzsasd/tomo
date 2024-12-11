import argparse
import asyncio
import uuid
import logging
import os

from dotenv import load_dotenv

from tomo.assistant import Assistant  # Ensure correct import path
from tomo.core.output_channels import CollectingOutputChannel
from tomo.core.policies import LocalPolicyManager
from tomo.core.processor import MessageProcessor
from tomo.core.session_managers import InMemorySessionManager
from tomo.core.user_message import TextUserMessage
from tomo.shared.action_executor import ActionExector
from tomo.config import AssistantConfigLoader

# Load environment variables from .env file
load_dotenv()

# Now you can access the OpenAI API key as an environment variable
api_key = os.getenv("OPENAI_API_KEY")


def configure_logging():
    # Step 1: Configure the root logger to WARNING to suppress lower-level logs
    logging.basicConfig(
        level=logging.WARN,  # Set root logger to WARNING
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Define log format
    )

    # Step 2: Get the 'tomo' logger
    target_logger = logging.getLogger("tomo")

    # Step 3: Set the 'tomo' logger's level to DEBUG (or desired level)
    target_logger.setLevel(logging.DEBUG)

    # Step 4: Create and attach a StreamHandler with desired format to the 'tomo' logger
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)  # Handler level
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    target_logger.addHandler(handler)

    # Step 5: Disable propagation to prevent logs from bubbling up to root logger
    target_logger.propagate = False


configure_logging()


def parse_args():
    parser = argparse.ArgumentParser(description="Bot shell")
    parser.add_argument(
        "-c",
        "--config",
        default="config.yaml",
        help="Path to the assistant config file",
    )
    return parser.parse_args()


async def main(config_path):
    # Step 1: Load the assistant configuration
    config_loader = AssistantConfigLoader(config_path)
    assistant_config = config_loader.load()

    # Step 2: Initialize the Assistant instance
    assistant = Assistant(config=assistant_config)

    # Step 3: Initialize dependencies required by MessageProcessor using assistant components
    session_manager = InMemorySessionManager(assistant=assistant)
    policy_manager = LocalPolicyManager(
        policies=assistant.policies,  # Use policies from the Assistant instance
    )
    action_executor = ActionExector()
    nlu_parser = assistant.nlu_parser  # Use NLU parser from the Assistant instance

    # Step 4: Initialize the MessageProcessor with required dependencies
    message_processor = MessageProcessor(
        session_manager=session_manager,
        policy_manager=policy_manager,
        action_exector=action_executor,
        nlu_parser=nlu_parser,
    )

    # Define a session ID (could be a user ID or conversation ID)
    session_id = uuid.uuid4().hex
    output_channel = CollectingOutputChannel()

    # Start a new session
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
    args = parse_args()
    asyncio.run(main(args.config))
