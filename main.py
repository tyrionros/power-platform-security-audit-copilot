import os
import requests
import json
import typer
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = typer.Typer()

# --- Configuration ---
load_dotenv()
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# --- Constants ---
POWER_PLATFORM_ADMIN_API_BASE = "https://api.powerplatform.com/providers/Microsoft.PowerApps/"
MICROSOFT_GRAPH_SCOPES = ["https://api.powerplatform.com/.default"]
AUTHORITY_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

# --- Authentication ---
def get_access_token() -> str:
    """
    Obtains an access token for the Power Platform Admin API using client credentials flow.
    """
    if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        logger.error("Authentication credentials (TENANT_ID, CLIENT_ID, CLIENT_SECRET) are not set in .env file.")
        raise ValueError("Missing authentication credentials.")

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": " ".join(MICROSOFT_GRAPH_SCOPES),
        "grant_type": "client_credentials",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    logger.info("Attempting to get access token...")
    try:
        response = requests.post(AUTHORITY_URL, data=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        token_data = response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise ValueError("Access token not found in response.")
        logger.info("Successfully obtained access token.")
        return access_token
    except requests.exceptions.RequestException as e:
        logger.error(f"Error obtaining access token: {e}")
        raise
    except ValueError as e:
        logger.error(f"Authentication failed: {e}")
        raise

# --- Power Platform API Interactions ---
def _make_power_platform_api_call(access_token: str, url: str) -> dict:
    """Helper to make authenticated GET requests to Power Platform Admin API."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    logger.debug(f"Calling Power Platform API: {url}")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling API {url}: {e}")
        raise

def get_environments(access_token: str) -> list:
    """Retrieves a list of Power Platform environments."""
    url = f"{POWER_PLATFORM_ADMIN_API_BASE}environments?api-version=2020-10-12"
    data = _make_power_platform_api_call(access_token, url)
    return data.get("value", [])

def get_power_apps_in_environment(access_token: str, environment_id: str) -> list:
    """Retrieves a list of Power Apps in a specific environment."""
    url = f"{POWER_PLATFORM_ADMIN_API_BASE}environments/{environment_id}/apps?api-version=2020-10-12"
    data = _make_power_platform_api_call(access_token, url)
    return data.get("value", [])

def get_app_permissions(access_token: str, environment_id: str, app_id: str) -> list:
    """Retrieves permissions for a specific Power App."""
    url = f"{POWER_PLATFORM_ADMIN_API_BASE}environments/{environment_id}/apps/{app_id}/permissions?api-version=2020-10-12"
    data = _make_power_platform_api_call(access_token, url)
    return data.get("value", [])

# --- Audit Logic ---
def find_public_apps(access_token: str) -> list:
    """
    Audits for Power Apps shared with 'Everyone' or public access.
    Returns a list of dictionaries with app details.
    """
    logger.info("Starting audit for publicly shared apps...")
    public_apps_findings = []
    
    try:
        environments = get_environments(access_token)
        logger.info(f"Found {len(environments)} environments.")
        
        for env in environments:
            env_id = env.get("name")
            env_display_name = env.get("properties", {{}}).get("displayName", env_id)
            logger.debug(f"Checking environment: {env_display_name} ({env_id})")

            apps = get_power_apps_in_environment(access_token, env_id)
            logger.debug(f"Found {len(apps)} apps in {env_display_name}.")

            for app in apps:
                app_id = app.get("name")
                app_display_name = app.get("properties", {{}}).get("displayName", app_id)
                app_owner = app.get("properties", {{}}).get("owner", "N/A")
                
                permissions = get_app_permissions(access_token, env_id, app_id)
                
                for perm in permissions:
                    principal_type = perm.get("properties", {{}}).get("principal", {{}}).get("type")
                    principal_display_name = perm.get("properties", {{}}).get("principal", {{}}).get("displayName")
                    
                    # Heuristic for public sharing:
                    # In Power Platform, 'Everyone' access is often represented as a principal
                    # without a specific GUID, or with a well-known principal type.
                    # This check might need refinement based on exact API response structure.
                    if principal_type == "Public" or (principal_display_name and "everyone" in principal_display_name.lower()):
                        public_apps_findings.append({
                            "environment_id": env_id,
                            "environment_display_name": env_display_name,
                            "app_id": app_id,
                            "app_display_name": app_display_name,
                            "app_owner": app_owner,
                            "permission_type": "Public",
                            "principal_display_name": principal_display_name
                        })
                        logger.warning(f"Public app found: {app_display_name} in {env_display_name}")
                        break # No need to check other permissions for this app once one public permission is found
    except Exception as e:
        logger.error(f"An error occurred during public app audit: {e}")
        return []
        
    logger.info(f"Finished audit. Found {len(public_apps_findings)} publicly shared apps.")
    return public_apps_findings

# --- CLI Command ---
@app.command()
def audit(query: str = typer.Argument(..., help="The security audit query, e.g., 'find public apps'")):
    """
    Performs a security audit on the Power Platform based on the provided query.
    """
    logger.info(f"Audit initiated with query: '{query}'")

    try:
        access_token = get_access_token()
    except Exception:
        logger.critical("Failed to get access token. Please check your .env credentials and App Registration permissions.")
        raise typer.Exit(code=1)

    # Simple intent recognition for demonstration
    if "public apps" in query.lower() or "apps shared with everyone" in query.lower():
        findings = find_public_apps(access_token)
        if findings:
            typer.echo("\n--- Publicly Shared Power Apps Findings ---")
            for finding in findings:
                typer.echo(f"  - App: {finding['app_display_name']} (ID: {finding['app_id']})")
                typer.echo(f"    Environment: {finding['environment_display_name']} (ID: {finding['environment_id']})")
                typer.echo(f"    Owner: {finding['app_owner']}")
                typer.echo(f"    Access Type: {finding['permission_type']}")
                typer.echo(f"    Principal: {finding['principal_display_name']}\n")
            typer.echo(f"Total publicly shared apps found: {len(findings)}")
        else:
            typer.echo("✅ No publicly shared Power Apps were found.")
    elif "test connection" in query.lower():
        typer.echo("Attempting to get environments...")
        try:
            envs = get_environments(access_token)
            typer.echo(f"Successfully connected and found {len(envs)} environments.")
            if envs:
                typer.echo("Sample environment: " + envs[0].get("properties", {{}}).get("displayName", "N/A"))
        except Exception as e:
            typer.echo(f"Failed to list environments: {e}")
            raise typer.Exit(code=1)
    else:
        typer.echo(f"Sorry, I don't understand the query: '{query}'.")
        typer.echo("Try 'find public apps' or 'test connection'.")

if __name__ == "__main__":
    app()
