#!/bin/bash

# Wrapper script to run guidellm with authentication patch
# Usage: ./guidellm_patched.sh benchmark run [OPTIONS]

# Apply the patch by importing it before guidellm
python -c "import patch_guidellm; from guidellm.__main__ import cli; cli()" "$@"

