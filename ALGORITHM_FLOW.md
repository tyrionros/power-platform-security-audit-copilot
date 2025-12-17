## Copilot Algorithm Flow

This describes the step-by-step logic the Copilot follows to process a user's request and provide a security analysis.

#### **Example Query: "Find all Power Apps shared publicly"**

**Step 1: Initialization & User Input**
*   The user executes the program with a natural language query: `python main.py "Find all Power Apps shared publicly"`.
*   The application starts, loads the credentials from the `.env` file, and obtains an authentication token from Microsoft Entra ID.

**Step 2: Intent Recognition**
*   The application analyzes the input string to determine the user's goal. This can range from simple to complex:
    *   **Simple Method (Keyword Matching):** The program looks for keywords like `"apps"`, `"shared"`, and `"publicly"` or `"everyone"`. The combination of these keywords maps to a predefined function, e.g., `handle_find_public_apps()`.
    *   **Advanced Method (NLU/LLM):** The query is sent to a language model to classify the intent (e.g., `Intent: FindPublicAssets`) and extract entities (e.g., `AssetType: PowerApp`).

**Step 3: Data Retrieval (API Interaction)**
*   Based on the recognized intent, the Copilot executes a sequence of API calls.
    1.  **Get All Environments**: Calls the Power Platform API to get a list of all environments in the tenant.
    2.  **Get All Apps**: Iterates through each environment and calls the API to get a list of all Power Apps within it.
    3.  **Get App Permissions**: For each app, it makes another API call to get its role assignments (the list of users/groups who have access).

**Step 4: Security Analysis**
*   The raw data from the APIs is now processed internally.
    1.  The agent iterates through the permissions for each app.
    2.  It checks each permission entry to see if the assigned principal (the user or group) matches the well-known identifier for "Everyone" or "Public."
    3.  A list of "findings" is compiled, containing any apps that have such a permission.

**Step 5: Response Generation**
*   The findings are formatted into a human-readable report.
    *   **If issues are found:** "Found 2 publicly shared apps:\n- **App Name:** 'Sales Data Entry', **Environment:** 'Default-a1b2c3d4'\n- **App Name:** 'Onboarding Form', **Environment:** 'Production'"
    *   **If no issues are found:** "✅ No publicly shared Power Apps were found across all environments."

**Step 6: (Optional) Action & Remediation Loop**
*   For certain findings, the Copilot can offer to take action.
*   The agent could prompt the user: "Would you like me to remove public access from these apps? (yes/no)"
*   If the user responds "yes," a new intent (`RemediatePublicAccess`) is triggered. The Copilot then makes the necessary `DELETE` API calls to remove the specific role assignments, thereby securing the apps. It then confirms the action was completed.
