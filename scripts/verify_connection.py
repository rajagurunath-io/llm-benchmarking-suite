#!/usr/bin/env python3
"""
Connection verification script for guidellm benchmarks.
Tests API connectivity and authentication before running benchmarks.
"""

import os
import sys
import json
import requests
from datetime import datetime

def log_info(message):
    """Print info message with timestamp."""
    print(f"[INFO] {datetime.now().strftime('%H:%M:%S')} {message}")

def log_error(message):
    """Print error message with timestamp."""
    print(f"[ERROR] {datetime.now().strftime('%H:%M:%S')} {message}", file=sys.stderr)

def log_success(message):
    """Print success message with timestamp."""
    print(f"[SUCCESS] {datetime.now().strftime('%H:%M:%S')} {message}")

def get_env_var(var_name):
    """Get environment variable or None."""
    value = os.environ.get(var_name)
    if not value:
        log_error(f"Environment variable {var_name} not set")
        return None
    return value

def test_simple_api_connection(base_url, api_key):
    """Test basic API connectivity with a simple request."""
    try:
        # Construct the models endpoint URL
        if not base_url.endswith('/'):
            base_url += '/'
        if not base_url.endswith('v1/'):
            base_url += 'v1/'

        models_url = base_url.rstrip('/') + '/models'

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        log_info(f"Testing connection to: {models_url}")
        log_info(f"Using API key (first 10 chars): {api_key[:10]}...")

        response = requests.get(models_url, headers=headers, timeout=30)

        if response.status_code == 200:
            log_success("API connection successful")
            try:
                models_data = response.json()
                if 'data' in models_data and isinstance(models_data['data'], list):
                    model_count = len(models_data['data'])
                    log_success(f"Found {model_count} available models")
                    if model_count > 0:
                        # Show first few model IDs
                        model_ids = [model.get('id', 'unknown') for model in models_data['data'][:5]]
                        log_info(f"Sample models: {', '.join(model_ids)}")
                    return True
                else:
                    log_error("Unexpected response format from /models endpoint")
                    return False
            except json.JSONDecodeError:
                log_error("Failed to parse JSON response from /models endpoint")
                return False
        else:
            log_error(f"API request failed with status {response.status_code}")
            log_error(f"Response: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        log_error("Connection timeout (30s)")
        return False
    except requests.exceptions.ConnectionError:
        log_error("Connection error - unable to reach API endpoint")
        return False
    except Exception as e:
        log_error(f"Unexpected error during connection test: {str(e)}")
        return False

def test_guidellm_import():
    """Test if guidellm can be imported successfully."""
    try:
        import guidellm
        log_success("guidellm imported successfully")
        return True
    except ImportError as e:
        log_error(f"Failed to import guidellm: {e}")
        return False

def test_guidellm_configuration():
    """Test guidellm environment configuration."""
    try:
        # Check if guidellm can read the configuration
        from guidellm.config import get_environment
        env_config = get_environment()
        log_success("guidellm configuration loaded")
        return True
    except Exception as e:
        log_error(f"guidellm configuration error: {e}")
        return False

def main():
    """Main verification function."""
    log_info("Starting connection verification for guidellm benchmark")

    # Get environment variables
    base_url = get_env_var('GUIDELLM__OPENAI__BASE_URL') or get_env_var('OPENAI_API_BASE')
    api_key = get_env_var('GUIDELLM__OPENAI__API_KEY') or get_env_var('OPENAI_API_KEY')

    if not base_url or not api_key:
        log_error("Missing required environment variables")
        log_error("Required: GUIDELLM__OPENAI__BASE_URL and GUIDELLM__OPENAI__API_KEY")
        log_error("Or: OPENAI_API_BASE and OPENAI_API_KEY")
        return 1

    # Run verification tests
    success_count = 0
    total_tests = 3

    # Test 1: Basic API connectivity
    log_info("\n=== Test 1: API Connectivity ===")
    if test_simple_api_connection(base_url, api_key):
        success_count += 1

    # Test 2: guidellm import
    log_info("\n=== Test 2: guidellm Import ===")
    if test_guidellm_import():
        success_count += 1

    # Test 3: guidellm configuration
    log_info("\n=== Test 3: guidellm Configuration ===")
    if test_guidellm_configuration():
        success_count += 1

    # Final result
    log_info(f"\n=== Verification Summary ===")
    log_info(f"Passed: {success_count}/{total_tests} tests")

    if success_count == total_tests:
        log_success("All verification tests passed ✓")
        log_info("Ready to run benchmarks!")
        return 0
    else:
        log_error("Some verification tests failed ✗")
        log_error("Please fix the issues before running benchmarks")
        return 1

if __name__ == "__main__":
    sys.exit(main())