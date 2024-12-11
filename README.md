# Tomo

Tomo is a project that provides a chatbot message processing framework. It handles sessions, user messages, policy predictions, and action execution within a customizable architecture. The system supports asynchronous processing and aims to provide a foundation for building LLM-powered conversational agents.

## Features

- **Asynchronous Message Processing**: Tomo supports async communication with users and async action execution.
- **Session Management**: The system manages user sessions, including session creation, updates, and persistence.
- **Policy Management**: Supports policy-driven message handling, including prediction of actions.
- **Modular Architecture**: Extensible message processors, output channels, policies, and actions.
- **Customizable Framework**: Easily integrate your own logic and services via well-defined interfaces.
- **Python 3.11 Compatible**: Leverages Python's latest async capabilities for better performance.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/tomo.git
   cd tomo
   ```

2. **Install Dependencies with Poetry**:
   Install the project's dependencies using Poetry:
   ```bash
   poetry install
   ```

3. **Install Pre-Commit Hooks (Optional)**:
   For consistent code quality and formatting, you can set up pre-commit hooks:
   ```bash
   poetry run pre-commit install
   ```
   This will automatically run linting and formatting tools on staged files before each commit.

## Usage

### Running the Shell Interface

Tomo includes a command-line shell interface (`shell.py`) that allows you to interact with the message processor. You can start the shell to process user inputs and simulate chatbot responses.

To run the shell:
```bash
poetry run python -m tomo.shell
```

### Running the Service

To run the Tomo service, you can use the provided `run.py` script:

1. Ensure you have the dependencies installed using Poetry.
2. Run the following command:
   ```bash
   poetry run python run.py
   ```
   This will start the Tomo service and make it available for processing messages.

### Preparing the Development Environment

To set up the development environment for Tomo:

1. Install Python 3.11 and Poetry if you haven't already.
2. Clone the Tomo repository.
3. Install the project dependencies using Poetry:
   ```bash
   poetry install
   ```
4. (Optional) Set up pre-commit hooks for consistent code quality and formatting:
   ```bash
   poetry run pre-commit install
   ```

Now you're ready to start contributing to the Tomo project!

## Project Structure

The Tomo project has the following structure:

```
tomo/
├── tomo/
│   ├── actions/
│   ├── channels/
│   ├── policies/
│   ├── processors/
│   ├── sessions/
│   ├── utils/
│   ├── shell.py
│   └── run.py
├── tests/
├── pyproject.toml
├── README.md
└── .pre-commit-config.yaml
```

- `actions/`: Defines the available actions that can be executed by the message processors.
- `channels/`: Implements the output channels for sending messages to users.
- `policies/`: Defines the policies that govern how messages are handled.
- `processors/`: Implements the message processors that handle user input and produce responses.
- `sessions/`: Manages the user sessions, including session creation, updates, and persistence.
- `utils/`: Provides utility functions and classes used throughout the project.
- `shell.py`: The command-line interface for interacting with the Tomo message processor.
- `run.py`: The script for running the Tomo service.
- `tests/`: Contains the project's test suite.
- `pyproject.toml`: The Poetry configuration file.
- `README.md`: The project's documentation.
- `.pre-commit-config.yaml`: Configuration for the pre-commit hooks.

## Contributing

We welcome contributions to the Tomo project! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and ensure the tests pass.
4. Commit your changes and push to your fork.
5. Submit a pull request to the main repository.

Please ensure that your code follows the project's style guidelines and that you've added tests for any new functionality.

## License

This project is licensed under the [MIT License](LICENSE).
