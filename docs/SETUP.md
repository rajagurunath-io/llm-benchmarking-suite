# Setup Guide for LLM Performance Benchmark Suite

This guide will walk you through setting up the automated LLM benchmark suite on GitHub.

## 📋 Prerequisites

- GitHub account
- Access to LLM platform APIs (your platform and comparison platforms)
- Basic understanding of GitHub Actions and environment variables

## 🚀 Quick Setup (5 minutes)

### 1. Fork and Clone

```bash
# Fork this repository on GitHub, then clone it
git clone https://github.com/YOUR_USERNAME/llm-benchmark-suite.git
cd llm-benchmark-suite
```

### 2. Configure Repository Secrets

Go to your repository → Settings → Secrets and variables → Actions and add these secrets:

**Required for Your Platform:**
- `PLATFORM_API_BASE_URL`: Your LLM platform API endpoint
- `PLATFORM_API_KEY`: Your platform API key

**Optional for Comparison:**
- `OPENROUTER_API_KEY`: OpenRouter API key
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key

**Example:**
```
PLATFORM_API_BASE_URL = https://your-platform.com/v1
PLATFORM_API_KEY = sk-your-platform-api-key
OPENROUTER_API_KEY = sk-or-v1-your-openrouter-key
```

### 3. Enable GitHub Pages

1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: `gh-pages`
4. Folder: `/root`
5. Click Save

### 4. Trigger First Run

1. Go to Actions → Benchmark Suite
2. Click "Run workflow"
3. Wait for completion (2-5 minutes)
4. Check your reports at: `https://YOUR_USERNAME.github.io/llm-benchmark-suite`

## 🔧 Detailed Configuration

### Platform Configuration

Edit `config/platforms.conf` to customize which platforms and models to test:

```ini
[your_platform]
name = "Your Platform"
base_url = "${PLATFORM_API_BASE_URL}"
api_key = "${PLATFORM_API_KEY}"
models = [
    "openai/gpt-oss-120b",
    "meta-llama/llama-3.1-70b-instruct"
]
```

### Benchmark Parameters

Edit `config/benchmark.conf` to adjust test parameters:

```ini
[default]
samples = 100
prompt_tokens = 1000
output_tokens = 800
max_requests = 100
rate = 1
```

### Custom Models

Add your custom models to the platform configuration:

```ini
[your_platform]
models = [
    "your-custom-model-1",
    "your-custom-model-2",
    "meta-llama/llama-3.1-70b-instruct"
]
```

## 📊 Understanding the Results

### Performance Metrics

- **Throughput**: Requests per second the platform can handle
- **Latency**: Average response time for requests
- **Token Rate**: Tokens generated per second
- **Success Rate**: Percentage of successful requests
- **Error Rate**: Percentage of failed requests

### Report Structure

```
results/
├── html/
│   ├── your_platform_20240101.html    # Your platform report
│   ├── openrouter_20240101.html        # OpenRouter report
│   ├── comparison_20240101.html        # Comparison report
│   └── index.html                      # Index page
├── csv/
│   ├── your_platform_20240101.csv     # Raw data
│   └── openrouter_20240101.csv
└── json/
    ├── your_platform_20240101.json    # JSON data
    └── openrouter_20240101.json
```

### HTML Reports

Each HTML report includes:
- 📈 **Performance Charts**: Interactive visualizations
- 📊 **Metrics Summary**: Key performance indicators
- ⏱️ **Latency Distribution**: Response time analysis
- 💰 **Cost Analysis**: Token cost efficiency
- 📅 **Historical Trends**: Performance over time

## 🛠️ Local Development

### Prerequisites

```bash
pip install guidellm pandas matplotlib jinja2
```

### Running Locally

```bash
# Set environment variables
export PLATFORM_API_BASE_URL="https://your-platform.com/v1"
export PLATFORM_API_KEY="your-api-key"

# Run benchmarks
./scripts/run_benchmark.sh

# View results
open results/html/latest_report.html
```

### Debug Mode

```bash
# Enable debug logging
./scripts/run_benchmark.sh --debug

# Or set environment variable
export DEBUG=true
./scripts/run_benchmark.sh
```

## 🔍 Troubleshooting

### Common Issues

**Q: "No reports generated"**
- Check API keys in repository secrets
- Verify API endpoints are accessible
- Check Action logs for errors

**Q: "GitHub Pages not updating"**
- Ensure Actions have write permissions
- Check if gh-pages branch exists
- Verify Pages is configured to deploy from gh-pages

**Q: "API connection failed"**
- Verify API endpoints are correct
- Check API keys are valid and have required permissions
- Test API endpoints with curl first

**Q: "Benchmark runs but fails"**
- Check if models are available on the platform
- Verify rate limits aren't being exceeded
- Check platform status for outages

### Debug Commands

```bash
# Test API connection manually
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://your-platform.com/v1/models

# Check guidellm installation
python -c "import guidellm; print(guidellm.__version__)"

# Run connection verification
python scripts/verify_connection.py
```

### Log Analysis

Check GitHub Action logs for detailed error messages:
1. Go to Actions → Benchmark Suite → Latest run
2. Click on individual steps to see detailed logs
3. Look for error messages in the benchmark execution step

## 📅 Automation Schedule

The workflow runs automatically:
- **Frequency**: Daily at 00:00 UTC
- **Platforms**: Configured in `config/platforms.conf`
- **Models**: As specified in platform configuration
- **Retention**: 30 days of historical data

### Manual Triggers

You can also trigger runs manually:
1. Go to Actions → Benchmark Suite
2. Click "Run workflow"
3. Optional: specify platforms, models, or enable debug mode

## 📈 Customizing Benchmarks

### Adding New Platforms

1. Add platform config to `config/platforms.conf`
2. Add required API secrets to repository
3. Update workflow if needed
4. Test locally before pushing

### Custom Test Scenarios

Create new test scenarios in `config/benchmark.conf`:

```ini
[stress_test]
samples = 1000
max_requests = 2000
rate = 20
prompt_tokens = 2000
output_tokens = 1500
```

### Custom Metrics

Add custom metrics by modifying the benchmark scripts:
- Edit `scripts/run_benchmark.sh` for execution parameters
- Update `scripts/generate_comparison.py` for new metric visualizations

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test locally
4. Commit changes: `git commit -m "Add feature"`
5. Push to fork: `git push origin feature-name`
6. Create pull request

### Testing Changes

```bash
# Test locally before pushing
export DEBUG=true
./scripts/run_benchmark.sh --platforms "your_platform" --debug

# Verify report generation
python scripts/generate_comparison.py \
    --results-dir results \
    --output test_report.html \
    --date $(date +%Y-%m-%d)
```

## 📞 Support

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review GitHub Action logs
3. Open an issue on the repository
4. Check platform API documentation

## 📄 License

This benchmark suite is licensed under the MIT License. See LICENSE file for details.