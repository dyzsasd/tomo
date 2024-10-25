# **Tomo**

**Tomo** is a project that provides a chatbot message processing framework. It handles sessions, user messages, policy predictions, and action execution within a customizable architecture. The system supports asynchronous processing and aims to provide a foundation for building LLM-powered conversational agents.

---

## **Table of Contents**

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## **Features**

- **Asynchronous Message Processing**: Tomo supports async communication with users and async action execution.
- **Session Management**: The system manages user sessions, including session creation, updates, and persistence.
- **Policy Management**: Supports policy-driven message handling, including prediction of actions.
- **Modular Architecture**: Extensible message processors, output channels, policies, and actions.
- **Customizable Framework**: Easily integrate your own logic and services via well-defined interfaces.
- **Python 3.11 Compatible**: Leverages Python's latest async capabilities for better performance.

---

## **Installation**

To install and set up **Tomo**, ensure that you have **Python 3.11** and **Poetry** installed.

### **1. Clone the Repository**

```bash
git clone https://github.com/yourusername/tomo.git
cd tomo

2. Install Dependencies with Poetry

Install the project’s dependencies using Poetry:

poetry install

3. Install Pre-Commit Hooks (Optional)

For consistent code quality and formatting, you can set up pre-commit hooks:

poetry run pre-commit install

This will automatically run linting and formatting tools on staged files before each commit.

Usage

Running the Shell Interface

Tomo includes a command-line shell interface (shell.py) that allows you to interact with the message processor. You can start the shell to process user inputs and simulate chatbot responses.

Running the Shell

poetry run python -m tomo.shell
