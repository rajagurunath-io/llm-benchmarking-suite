#!/usr/bin/env python3
"""
Comparison report generator for guidellm benchmark results.
Generates HTML comparison reports between different platforms.
"""

import os
import sys
import json
import csv
import argparse
from datetime import datetime
from pathlib import Path

def load_result_data(file_path):
    """Load benchmark result data from JSON or CSV file."""
    try:
        if file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                return json.load(f)
        elif file_path.endswith('.csv'):
            # Load CSV data - assuming standard format
            data = []
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            return data
        else:
            print(f"Unsupported file format: {file_path}")
            return None
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def extract_metrics(data):
    """Extract key metrics from benchmark data."""
    metrics = {}

    if isinstance(data, list):
        # Handle list of results
        if len(data) == 0:
            return metrics

        # Calculate averages for numeric fields
        numeric_fields = ['request_latency', 'response_time', 'tokens_per_second', 'prompt_tokens', 'completion_tokens']

        for field in numeric_fields:
            if field in data[0]:
                try:
                    values = [float(row.get(field, 0)) for row in data if row.get(field)]
                    if values:
                        metrics[field] = {
                            'avg': sum(values) / len(values),
                            'min': min(values),
                            'max': max(values),
                            'count': len(values)
                        }
                except (ValueError, TypeError):
                    continue

        # Count total requests
        metrics['total_requests'] = len(data)

        # Calculate success rate (assuming successful requests have no error field)
        successful = sum(1 for row in data if not row.get('error'))
        metrics['success_rate'] = (successful / len(data)) * 100 if data else 0

    elif isinstance(data, dict):
        # Handle single result object
        if 'metrics' in data:
            metrics.update(data['metrics'])
        if 'summary' in data:
            metrics.update(data['summary'])

    return metrics

def generate_html_report(platforms_data, output_path, report_date):
    """Generate HTML comparison report."""

    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Performance Comparison Report - {date}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid #e1e5e9;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            color: #7f8c8d;
            font-size: 1.1em;
            margin: 10px 0 0 0;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .platform-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            border-left: 4px solid #3498db;
        }}
        .platform-card h3 {{
            margin: 0 0 15px 0;
            color: #2c3e50;
            font-size: 1.3em;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            padding: 5px 0;
            border-bottom: 1px solid #e1e5e9;
        }}
        .metric:last-child {{
            border-bottom: none;
        }}
        .metric-label {{
            font-weight: 500;
            color: #555;
        }}
        .metric-value {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .chart-container {{
            margin: 40px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .chart-container h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        canvas {{
            max-height: 400px;
        }}
        .best-value {{
            color: #27ae60 !important;
            font-weight: bold;
        }}
        .error-message {{
            background: #e74c3c;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .info-message {{
            background: #3498db;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e1e5e9;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 LLM Performance Comparison</h1>
            <p>Benchmark report generated on {date}</p>
        </div>

        {error_message}

        <div class="metrics-grid">
            {platform_cards}
        </div>

        {charts}

        <div class="footer">
            <p>Generated with guidellm benchmark suite • <a href="https://github.com/YOUR_USERNAME/llm-benchmark-suite">Repository</a></p>
        </div>
    </div>

    <script>
        {chart_scripts}
    </script>
</body>
</html>
    """

    # Generate platform cards
    platform_cards = ""
    for platform_name, metrics in platforms_data.items():
        if not metrics:
            continue

        card_html = f"""
        <div class="platform-card">
            <h3>{platform_name}</h3>
        """

        # Add key metrics
        key_metrics = {
            'Total Requests': metrics.get('total_requests', 'N/A'),
            'Success Rate': f"{metrics.get('success_rate', 0):.1f}%" if metrics.get('success_rate') else 'N/A',
            'Avg Latency': f"{metrics.get('request_latency', {}).get('avg', 0):.2f}s" if metrics.get('request_latency') else 'N/A',
            'Tokens/sec': f"{metrics.get('tokens_per_second', {}).get('avg', 0):.1f}" if metrics.get('tokens_per_second') else 'N/A'
        }

        for label, value in key_metrics.items():
            card_html += f'<div class="metric"><span class="metric-label">{label}:</span><span class="metric-value">{value}</span></div>'

        card_html += "</div>"
        platform_cards += card_html

    # Generate charts
    charts_html = ""
    chart_scripts = ""

    if len(platforms_data) > 1:
        # Success rate chart
        charts_html += """
        <div class="chart-container">
            <h3>Success Rate Comparison</h3>
            <canvas id="successRateChart"></canvas>
        </div>
        """

        # Latency chart
        charts_html += """
        <div class="chart-container">
            <h3>Average Latency Comparison</h3>
            <canvas id="latencyChart"></canvas>
        </div>
        """

        # Throughput chart
        charts_html += """
        <div class="chart-container">
            <h3>Tokens per Second Comparison</h3>
            <canvas id="throughputChart"></canvas>
        </div>
        """

        # Generate chart data
        platforms = list(platforms_data.keys())
        success_rates = [platforms_data[p].get('success_rate', 0) for p in platforms]
        latencies = [platforms_data[p].get('request_latency', {}).get('avg', 0) for p in platforms]
        throughputs = [platforms_data[p].get('tokens_per_second', {}).get('avg', 0) for p in platforms]

        chart_scripts = f"""
        // Success Rate Chart
        new Chart(document.getElementById('successRateChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(platforms)},
                datasets: [{{
                    label: 'Success Rate (%)',
                    data: {json.dumps(success_rates)},
                    backgroundColor: '#3498db',
                    borderColor: '#2980b9',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});

        // Latency Chart
        new Chart(document.getElementById('latencyChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(platforms)},
                datasets: [{{
                    label: 'Average Latency (seconds)',
                    data: {json.dumps(latencies)},
                    backgroundColor: '#e74c3c',
                    borderColor: '#c0392b',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});

        // Throughput Chart
        new Chart(document.getElementById('throughputChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(platforms)},
                datasets: [{{
                    label: 'Tokens per Second',
                    data: {json.dumps(throughputs)},
                    backgroundColor: '#27ae60',
                    borderColor: '#229954',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        """

    error_message = ""
    if not platforms_data:
        error_message = '<div class="error-message">No benchmark data found. Please run benchmarks first.</div>'

    return html_template.format(
        date=report_date,
        error_message=error_message,
        platform_cards=platform_cards,
        charts=charts_html,
        chart_scripts=chart_scripts
    )

def main():
    """Main function to generate comparison report."""
    parser = argparse.ArgumentParser(description='Generate comparison report from benchmark results')
    parser.add_argument('--results-dir', required=True, help='Directory containing benchmark results')
    parser.add_argument('--output', required=True, help='Output HTML file path')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'), help='Report date')

    args = parser.parse_args()

    results_dir = Path(args.results_dir)

    # Find result files
    platforms_data = {}

    # Look for CSV files (primary format)
    csv_files = list(results_dir.glob('csv/*.csv'))
    for csv_file in csv_files:
        platform_name = csv_file.stem.split('_')[0]  # Extract platform name from filename
        data = load_result_data(csv_file)
        if data:
            metrics = extract_metrics(data)
            platforms_data[platform_name] = metrics
            print(f"Loaded data for {platform_name} from {csv_file}")

    # Also check JSON files as fallback
    if not platforms_data:
        json_files = list(results_dir.glob('json/*.json'))
        for json_file in json_files:
            platform_name = json_file.stem.split('_')[0]
            data = load_result_data(json_file)
            if data:
                metrics = extract_metrics(data)
                platforms_data[platform_name] = metrics
                print(f"Loaded data for {platform_name} from {json_file}")

    if not platforms_data:
        print("No benchmark data found!")
        # Still generate an empty report
        html_content = generate_html_report({}, args.output, args.date)
    else:
        print(f"Found data for {len(platforms_data)} platforms")
        html_content = generate_html_report(platforms_data, args.output, args.date)

    # Write HTML report
    with open(args.output, 'w') as f:
        f.write(html_content)

    print(f"Comparison report generated: {args.output}")

if __name__ == "__main__":
    main()