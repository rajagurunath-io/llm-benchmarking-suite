# LLM Performance Benchmark Suite

Automated benchmark suite for comparing LLM inference performance across different platforms using guidellm.

## 🚀 Features

- **Automated Daily Benchmarks**: GitHub Actions runs benchmarks automatically every day
- **Multiple Platform Support**: Compare your platform against OpenRouter and other providers
- **Rich Visualizations**: HTML reports with interactive charts and graphs
- **Data Export**: CSV and JSON exports for further analysis
- **GitHub Pages Hosting**: Automatic deployment of HTML reports to GitHub Pages
- **Historical Tracking**: Track performance trends over time

## 📊 Report Preview

The benchmark generates comprehensive reports including:
- Performance metrics (throughput, latency, tokens/sec)
- Error rates and success rates
- Cost efficiency analysis
- Visual charts and graphs
- Historical trend analysis

## 🛠️ Quick Start

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/llm-benchmark-suite.git
cd llm-benchmark-suite
```

### 2. Configure Secrets

Add the following repository secrets in GitHub Settings:

```
PLATFORM_API_BASE_URL          # Your platform API endpoint
PLATFORM_API_KEY              # Your platform API key
OPENROUTER_API_KEY           # OpenRouter API key (for comparison)
```

### 3. Enable GitHub Pages

1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: `gh-pages`
4. Folder: `/root`

### 4. Manually Trigger First Run

1. Go to Actions → Benchmark Suite
2. Click "Run workflow"
3. Wait for completion
4. Check the reports at `https://YOUR_USERNAME.github.io/llm-benchmark-suite`

## 📁 Repository Structure

```
llm-benchmark-suite/
├── .github/
│   └── workflows/
│       └── benchmark.yml          # Daily benchmark automation
├── config/
│   ├── benchmark.conf             # Benchmark configuration
│   └── platforms.conf             # Platform configurations
├── scripts/
│   ├── run_benchmark.sh           # Main benchmark script
│   ├── setup_pages.sh             # GitHub Pages setup
│   └── verify_connection.py       # Connection verification
├── results/
│   ├── html/                      # HTML reports
│   ├── csv/                       # CSV exports
│   └── json/                      # JSON exports
├── docs/
│   ├── SETUP.md                   # Detailed setup instructions
│   ├── CONFIGURATION.md           # Configuration guide
│   └── API.md                     # API documentation
└── README.md
```

## ⚙️ Configuration

### Platform Configuration

Edit `config/platforms.conf` to add or modify platforms:

```ini
[your_platform]
name = "Your Platform"
base_url = "${PLATFORM_API_BASE_URL}"
api_key = "${PLATFORM_API_KEY}"
models = ["openai/gpt-oss-120b", "meta-llama/llama-3.1-70b-instruct"]

[openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
api_key = "${OPENROUTER_API_KEY}"
models = ["openai/gpt-4o", "anthropic/claude-3.5-sonnet"]
```

### Benchmark Parameters

Edit `config/benchmark.conf` to customize benchmark settings:

```ini
[default]
samples = 100
prompt_tokens = 1000
output_tokens = 800
rate = 1
max_requests = 100
profile = "constant"
```

## 📈 Automated Schedule

- **Daily Runs**: Every day at 00:00 UTC
- **Platforms**: Your platform vs OpenRouter
- **Models**: Configurable in platform configuration
- **Retention**: 30 days of historical data

## 🔧 Development

### Local Testing

```bash
# Install dependencies
pip install guidellm

# Set environment variables
export PLATFORM_API_BASE_URL="https://your-platform.com/v1"
export PLATFORM_API_KEY="your-api-key"

# Run benchmark locally
./scripts/run_benchmark.sh

# View local results
open results/html/latest_report.html
```

### Adding New Platforms

1. Add platform configuration to `config/platforms.conf`
2. Add required API secrets to GitHub repository
3. Update benchmark script to include new platform
4. Test locally before pushing

## 📊 Understanding Reports

### Performance Metrics

- **Throughput**: Requests per second
- **Latency**: Response time distribution
- **Token Rate**: Tokens generated per second
- **Success Rate**: Percentage of successful requests
- **Error Rate**: Percentage of failed requests

### Cost Analysis

- **Cost per 1M tokens**: Based on platform pricing
- **Efficiency**: Performance per dollar
- **Comparison**: Relative cost efficiency

### Historical Trends

- **Performance over time**: Daily/weekly/monthly trends
- **Platform comparisons**: Relative performance changes
- **Anomaly detection**: Unusual performance patterns

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add your improvements
4. Test thoroughly
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Troubleshooting

### Common Issues

**Q: Benchmark fails with API errors**
A: Check API keys and endpoints in repository secrets

**Q: GitHub Pages not updating**
A: Ensure Actions have write permissions and Pages is configured correctly

**Q: Missing reports**
A: Check Action logs for errors and verify script execution

**Q: Performance degradation**
A: Monitor platform status and check for rate limiting

### Debug Mode

Enable debug logging by setting `DEBUG=true` in the benchmark script.

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check troubleshooting guide
- Review Action logs for errors