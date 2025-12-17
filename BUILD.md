## Project Build Book: Power Platform Security Copilot

This document outlines the steps required to set up the development environment, configure, and run the Power Platform Security Copilot.

### 1. Prerequisites

Before you begin, ensure you have the following installed and configured:

*   **Python 3.9+**: The core programming language.
*   **Pip**: Python's package installer.
*   **Git**: For version control.
*   **Microsoft 365 Account**: An account with at least **Power Platform Administrator** or **Global Administrator** privileges is required to query the necessary APIs.

### 2. Environment Setup

These steps will get the project running on your local machine.

#### Step 2.1: Clone the Repository
```sh
# Clone the project repository from your Git provider
git clone <your-repository-url>
cd power-platform-security-audit-copilot
```

#### Step 2.2: Create a Python Virtual Environment
It is best practice to isolate project dependencies.

```sh
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

#### Step 2.3: Install Dependencies
A `requirements.txt` file will manage the necessary Python libraries.

```sh
# Create a requirements.txt file with the following content:
# requests: For making HTTP API calls
# python-dotenv: For managing environment variables
# typer: For building a clean command-line interface (CLI)
# pandas: For data analysis and formatting (optional but recommended)

# Install the packages
pip install requests python-dotenv typer pandas
```

### 3. Configuration: Authenticating with Power Platform

To access platform data, you must create an **App Registration** in Microsoft Entra ID (formerly Azure AD). This provides the Copilot with secure, service-principal-based credentials.

**HIGHLY IMPORTANT:** Never hard-code credentials in your source code.

#### Step 3.1: Create an Entra ID App Registration
1.  Navigate to the **Microsoft Entra admin center**.
2.  Go to **Identity** > **Applications** > **App registrations**.
3.  Click **New registration**.
4.  Give it a name (e.g., `PowerPlatformSecurityCopilot`).
5.  Set the supported account types to **"Accounts in this organizational directory only"**.
6.  Click **Register**.

#### Step 3.2: Grant API Permissions
1.  In your new App registration, go to **API permissions**.
2.  Click **Add a permission**.
3.  Select **Power Platform as an admin** (this may be listed under "APIs my organization uses").
4.  Select **Application permissions**.
5.  Add the following permissions:
    *   `PowerApps.Read.All`
    *   `PowerAutomate.Read.All`
    *   (and any other permissions you need based on the features)
6.  Click **Grant admin consent for [Your Organization]**. The status should update with a green checkmark.

#### Step 3.3: Create a Client Secret
1.  Go to **Certificates & secrets**.
2.  Click **New client secret**.
3.  Give it a description and an expiration period.
4.  **Crucially, copy the "Value" of the secret immediately.** You will not be able to see it again.

#### Step 3.4: Create the `.env` Configuration File
In the root of the project, create a file named `.env`. This file will hold your secrets. **Ensure you add `.env` to your `.gitignore` file to prevent it from ever being committed.**

```
# .env file
TENANT_ID="your-directory-tenant-id"
CLIENT_ID="your-application-client-id"
CLIENT_SECRET="your-client-secret-value"
```
*   `TENANT_ID` and `CLIENT_ID` can be found on the **Overview** page of your App registration.

### 4. Running the Application
The Copilot will be executed from the command line.

```sh
# Run the main application script, passing a query
python main.py "Show me all apps shared with Everyone"
```

### 5. Running Tests
A testing framework like `pytest` should be used to validate functionality.

```sh
# Install pytest
pip install pytest

# Run all tests in the 'tests/' directory
pytest
```