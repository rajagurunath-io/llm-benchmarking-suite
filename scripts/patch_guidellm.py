"""
Monkey-patch guidellm to add Authorization header for authenticated endpoints.
Import this before using guidellm CLI or library.
"""
import os
from guidellm.backends.openai import OpenAIHTTPBackend

# Store the original process_startup method
_original_process_startup = OpenAIHTTPBackend.process_startup

async def patched_process_startup(self):
    """Patched process_startup that adds Authorization header."""
    await _original_process_startup(self)
    
    # Inject the Authorization header with the API key from the environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        self._async_client.headers["Authorization"] = f"Bearer {api_key}"
        print(f"✓ Added Authorization header for {self.target}")
    else:
        print("⚠ Warning: OPENAI_API_KEY not found in environment variables.")

# Apply the monkey patch
OpenAIHTTPBackend.process_startup = patched_process_startup

print("✓ guidellm patched to support API key authentication")

