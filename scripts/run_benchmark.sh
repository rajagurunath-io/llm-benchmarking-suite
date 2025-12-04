#!/bin/bash

# LLM Performance Benchmark Script
# This script runs benchmarks for different platforms and generates reports

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RESULTS_DIR="${PROJECT_ROOT}/results"
CONFIG_DIR="${PROJECT_ROOT}/config"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log() { echo -e "${BLUE}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }

# Parse command line arguments
PLATFORMS=""
MODELS=""
DEBUG=false
HELP=false

function parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --platforms)
                PLATFORMS="$2"
                shift 2
                ;;
            --models)
                MODELS="$2"
                shift 2
                ;;
            --debug)
                DEBUG=true
                shift
                ;;
            --help)
                HELP=true
                shift
                ;;
            *)
                error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

function show_help() {
    cat << EOF
LLM Performance Benchmark Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --platforms <list>     Comma-separated list of platforms to benchmark
    --models <list>         Comma-separated list of models to test
    --debug                 Enable debug logging
    --help                  Show this help message

ENVIRONMENT VARIABLES:
    PLATFORM_API_BASE_URL   Your platform API endpoint
    PLATFORM_API_KEY        Your platform API key
    OPENROUTER_API_KEY      OpenRouter API key

EXAMPLES:
    # Run default benchmarks
    $0

    # Benchmark specific platforms
    $0 --platforms "your_platform,openrouter"

    # Enable debug mode
    $0 --debug

EOF
}

function check_dependencies() {
    log "Checking dependencies..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
        exit 1
    fi

    # Check guidellm
    if ! python3 -c "import guidellm" 2>/dev/null; then
        log "Installing guidellm..."
        pip3 install guidellm
    fi

    success "Dependencies verified"
}

function verify_connection() {
    local url="$1"
    local api_key="$2"
    local platform_name="$3"

    log "Verifying connection to $platform_name..."

    # Set temporary environment variables
    export OPENAI_API_KEY="$api_key"
    export GUIDELLM__OPENAI__BASE_URL="$url"
    export GUIDELLM__OPENAI__API_KEY="$api_key"

    if python3 "$SCRIPT_DIR/verify_connection.py"; then
        success "Connection to $platform_name verified"
        return 0
    else
        error "Connection to $platform_name failed"
        return 1
    fi
}

function run_platform_benchmark() {
    local platform_name="$1"
    local url="$2"
    local api_key="$3"
    local model="$4"

    log "Running benchmark for $platform_name with model $model..."

    # Create output directory
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local output_dir="${RESULTS_DIR}/${platform_name}_${timestamp}"
    mkdir -p "$output_dir"

    # Set environment variables
    export GUIDELLM__OPENAI__BASE_URL="$url"
    export GUIDELLM__OPENAI__API_KEY="$api_key"
    export OPENAI_API_KEY="$api_key"

    # Configure logging
    if [[ "$DEBUG" == "true" ]]; then
        export GUIDELLM__LOGGING__CONSOLE_LOG_LEVEL="DEBUG"
        export GUIDELLM__LOGGING__LOG_FILE="${output_dir}/debug.log"
        export GUIDELLM__LOGGING__LOG_FILE_LEVEL="DEBUG"
    else
        export GUIDELLM__LOGGING__CONSOLE_LOG_LEVEL="INFO"
    fi

    # Run benchmark
    guidellm benchmark run \
        --target "$url" \
        --processor "$model" \
        --model "$model" \
        --data "prompt_tokens=1000,output_tokens=800,samples=100" \
        --max-requests 100 \
        --profile constant \
        --rate 1 \
        --output-dir "$output_dir" \
        --outputs json --outputs csv --outputs html \
        --backend-kwargs '{"validate_backend": false}' || {
        error "Benchmark failed for $platform_name"
        return 1
    }

    # Copy results to standardized locations
    local date_suffix=$(date +%Y%m%d)
    cp "$output_dir"/*.json "${RESULTS_DIR}/csv/${platform_name}_${date_suffix}.json" 2>/dev/null || true
    cp "$output_dir"/*.csv "${RESULTS_DIR}/csv/${platform_name}_${date_suffix}.csv" 2>/dev/null || true
    cp "$output_dir"/*.html "${RESULTS_DIR}/html/${platform_name}_${date_suffix}.html" 2>/dev/null || true

    success "Benchmark completed for $platform_name"
    echo "$output_dir"
}

function main() {
    parse_args "$@"

    if [[ "$HELP" == "true" ]]; then
        show_help
        exit 0
    fi

    log "Starting LLM Performance Benchmark Suite"

    # Create results directories
    mkdir -p "${RESULTS_DIR}/html"
    mkdir -p "${RESULTS_DIR}/csv"
    mkdir -p "${RESULTS_DIR}/json"

    # Check dependencies
    check_dependencies

    # Default platforms if not specified
    if [[ -z "$PLATFORMS" ]]; then
        PLATFORMS="your_platform,openrouter"
    fi

    # Default models if not specified
    if [[ -z "$MODELS" ]]; then
        MODELS="openai/gpt-oss-120b"
    fi

    # Convert to arrays
    IFS=',' read -ra PLATFORM_ARRAY <<< "$PLATFORMS"
    IFS=',' read -ra MODEL_ARRAY <<< "$MODELS"

    local platform_results=()

    # Run benchmarks for each platform
    for platform in "${PLATFORM_ARRAY[@]}"; do
        platform=$(echo "$platform" | xargs)  # trim whitespace

        case "$platform" in
            "your_platform")
                if [[ -n "${PLATFORM_API_BASE_URL:-}" && -n "${PLATFORM_API_KEY:-}" ]]; then
                    verify_connection "$PLATFORM_API_BASE_URL" "$PLATFORM_API_KEY" "Your Platform"
                    for model in "${MODEL_ARRAY[@]}"; do
                        result=$(run_platform_benchmark "your_platform" "$PLATFORM_API_BASE_URL" "$PLATFORM_API_KEY" "$model")
                        platform_results+=("$result")
                    done
                else
                    warn "Platform credentials not configured, skipping your platform"
                fi
                ;;
            "openrouter")
                if [[ -n "${OPENROUTER_API_KEY:-}" ]]; then
                    verify_connection "https://openrouter.ai/api/v1" "$OPENROUTER_API_KEY" "OpenRouter"
                    for model in "${MODEL_ARRAY[@]}"; do
                        # Use OpenRouter-compatible models
                        openrouter_model="openai/gpt-4o"  # Default to GPT-4 for OpenRouter
                        result=$(run_platform_benchmark "openrouter" "https://openrouter.ai/api/v1" "$OPENROUTER_API_KEY" "$openrouter_model")
                        platform_results+=("$result")
                    done
                else
                    warn "OpenRouter API key not configured, skipping OpenRouter"
                fi
                ;;
            *)
                warn "Unknown platform: $platform"
                ;;
        esac
    done

    # Generate comparison report if we have multiple results
    if [[ ${#platform_results[@]} -gt 1 ]]; then
        log "Generating comparison report..."
        python3 "$SCRIPT_DIR/generate_comparison.py" \
            --results-dir "$RESULTS_DIR" \
            --output "${RESULTS_DIR}/html/comparison_$(date +%Y%m%d).html" \
            --date "$(date +%Y-%m-%d)" || {
            warn "Comparison report generation failed"
        }
    fi

    # Create index page
    log "Creating index page..."
    python3 "$SCRIPT_DIR/create_index.py" \
        --results-dir "$RESULTS_DIR" \
        --output "${RESULTS_DIR}/index.html"

    success "Benchmark suite completed successfully!"
    log "Results are available in: $RESULTS_DIR"
    log "View the HTML reports in: ${RESULTS_DIR}/html/"
}

# Run main function with all arguments
main "$@"