# Power Platform Security Audit Copilot

This project provides a command-line tool and a conceptual guide for building a Copilot to perform security audits on a Microsoft Power Platform tenant. It can help administrators identify risks, enforce governance, and maintain a secure environment by querying Power Platform Admin APIs.

## About The Project

This repository contains two main approaches for building a Power Platform Security Copilot:

1.  **Python CLI Tool (Implemented):** A working command-line application (`main.py`) that can connect to your tenant and run security queries.
2.  **Microsoft Copilot Studio Guide (Conceptual):** A detailed guide (`COPILOT_STUDIO_GUIDE.MD`) on how to build this as a low-code, interactive chatbot.

The core purpose is to answer security-related questions like:
*   "Which Power Apps are shared with everyone?"
*   "Which environments have no Data Loss Prevention (DLP) policies?"
*   "Show me all users with the System Administrator role."

## Features

*   **Permissions & Access Control Analysis:** Find over-privileged users and publicly shared assets.
*   **DLP Policy Auditing:** Analyze DLP policies across different environments.
*   **Connector & Connection Review:** Identify custom connectors and potentially risky connections.
*   **Asset Monitoring:** Find old, orphaned, or unused Power Apps and Flows.
*   **Extensible:** The Python-based framework is designed to be easily extendable with new audit queries.

For a full list of conceptual features, see [INTRODUCTION.MD](INTRODUCTION.MD).

## Getting Started (Python CLI)

This section will guide you through setting up the Python command-line tool.

### Prerequisites

*   Python 3.9+
*   A Microsoft 365 Account with **Power Platform Administrator** or **Global Administrator** privileges.

### Installation & Configuration

1.  **Clone the repository:**
    ```sh
    git clone <your-repository-url>
    cd power-platform-security-audit-copilot
    ```

2.  **Set up a virtual environment:**
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure Credentials:**
    This tool uses a Microsoft Entra ID (Azure AD) App Registration for authentication.
    *   **Create the App Registration:** Follow the detailed steps in [BUILD.MD](BUILD.MD) to set up the necessary permissions.
    *   **Create your `.env` file:** Copy the example file and add your credentials.
        ```sh
        cp .env.example .env
        ```
    *   Now, edit the `.env` file and replace the placeholder values with your **Tenant ID**, **Client ID**, and **Client Secret**. The `.env` file is ignored by Git to keep your secrets safe.

## Usage

Once configured, you can run audits from your terminal.

**Example 1: Find all publicly shared Power Apps**
```sh
python main.py "find public apps"
```

**Example 2: Test the connection to your tenant**
```sh
python main.py "test connection"
```

## Alternative Approach: Microsoft Copilot Studio

For a low-code, chat-based experience (e.g., in Microsoft Teams), you can implement this Copilot using Microsoft's native tools. Our guide provides a complete walkthrough of this alternative architecture.

See [COPILOT_STUDIO_GUIDE.MD](COPILOT_STUDIO_GUIDE.MD) for details.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss new features or bugs.

## License

This project is licensed under the MIT License.
