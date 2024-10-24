import asyncio
import uuid

from tomo.core.output_channels import CollectingOutputChannel
from tomo.core.policies.manager import EmptyPolicyManager
from tomo.core.processor import MessageProcessor
from tomo.core.sessions import InMemorySessionManager
from tomo.core.user_message import UserMessage
from tomo.nlu.parser import NLUParser
from tomo.shared.action_executor import ActionExector


async def main():
    # Initialize dependencies required by MessageProcessor
    session_manager = InMemorySessionManager()
    policy_manager = EmptyPolicyManager()
    action_executor = ActionExector()
    nlu_parser = NLUParser()

    # Initialize the MessageProcessor with required dependencies
    message_processor = MessageProcessor(
        session_manager=session_manager,
        policy_manager=policy_manager,
        action_exector=action_executor,
        nlu_parser=nlu_parser,
    )
    # Define a session ID (could be a user ID or conversation ID)
    session_id = uuid.uuid4().hex

    print("Welcome to the bot shell. Type 'quit' or 'exit' to end the conversation.")

    while True:
        # Create an instance of CollectingOutputChannel to capture bot responses
        output_channel = CollectingOutputChannel()

        # Read input from the command line
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break

        # Create a UserMessage instance for the user's input
        user_message = UserMessage(
            text=user_input,
            output_channel=output_channel,
            session_id=session_id,
            input_channel="cmdline"
        )

        # Process the message asynchronously
        await message_processor.handle_message(user_message)

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
                        f"- {element.get('title', '')}: {element.get('subtitle', '')}")
            # Handle other message types as needed

        # Clear the messages after processing
        output_channel.messages.clear()

if __name__ == "__main__":
    # Run the main coroutine
    asyncio.run(main())
