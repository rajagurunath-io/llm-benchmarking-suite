#!/usr/bin/env python3
"""
Index page generator for LLM benchmark reports.
Creates an index.html page listing all available benchmark reports.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

def generate_index_html(results_dir, output_path):
    """Generate an index HTML page for benchmark results."""

    results_path = Path(results_dir)
    html_dir = results_path / 'html'

    if not html_dir.exists():
        print(f"HTML results directory not found: {html_dir}")
        return generate_empty_index(output_path)

    # Find all HTML files
    html_files = []
    for html_file in html_dir.glob('*.html'):
        if html_file.name == 'index.html':
            continue
        html_files.append(html_file)

    # Sort by modification time (newest first)
    html_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    # Group reports by date
    reports_by_date = {}
    for html_file in html_files:
        # Try to extract date from filename
        parts = html_file.stem.split('_')
        date_str = parts[-1] if parts[-1].replace('-', '').replace('_', '').isdigit() else None

        try:
            if date_str and len(date_str) == 8:  # YYYYMMDD format
                date_obj = datetime.strptime(date_str, '%Y%m%d')
            elif date_str and '-' in date_str:  # YYYY-MM-DD format
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                # Use file modification time
                date_obj = datetime.fromtimestamp(html_file.stat().st_mtime)
        except ValueError:
            date_obj = datetime.fromtimestamp(html_file.stat().st_mtime)

        date_key = date_obj.strftime('%Y-%m-%d')
        if date_key not in reports_by_date:
            reports_by_date[date_key] = []

        platform = '_'.join(parts[:-1]) if len(parts) > 1 else html_file.stem
        reports_by_date[date_key].append({
            'platform': platform,
            'filename': html_file.name,
            'file_path': html_file.relative_to(results_path).as_posix(),
            'size': html_file.stat().st_size,
            'modified': date_obj
        })

    # Generate HTML
    index_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Performance Benchmark Reports</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
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
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #3498db;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
            display: block;
        }}
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .date-section {{
            margin: 30px 0;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            overflow: hidden;
        }}
        .date-header {{
            background: #2c3e50;
            color: white;
            padding: 15px 20px;
            font-size: 1.2em;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .date-badge {{
            background: #3498db;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
        }}
        .reports-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
            background: #f8f9fa;
        }}
        .report-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #e1e5e9;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }}
        .report-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .report-title {{
            font-weight: bold;
            color: #2c3e50;
            font-size: 1.1em;
            margin-bottom: 10px;
        }}
        .report-meta {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .report-size {{
            display: inline-block;
            background: #e8f4f8;
            color: #3498db;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-top: 5px;
        }}
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #7f8c8d;
        }}
        .empty-state h3 {{
            margin-top: 0;
            color: #95a5a6;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e1e5e9;
            color: #7f8c8d;
        }}
        .refresh-info {{
            background: #e8f5e8;
            border: 1px solid #d4edda;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            color: #155724;
        }}
        .comparison-badge {{
            background: #27ae60;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-left: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 LLM Performance Benchmark Reports</h1>
            <p>Automated performance testing and comparison of LLM inference platforms</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <span class="stat-number">{total_reports}</span>
                <div class="stat-label">Total Reports</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">{total_dates}</span>
                <div class="stat-label">Test Days</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">{platforms_count}</span>
                <div class="stat-label">Platforms Tested</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">{last_updated}</span>
                <div class="stat-label">Last Updated</div>
            </div>
        </div>

        <div class="refresh-info">
            🔄 This page is automatically updated when new benchmark results are available.
           Reports are generated daily at 00:00 UTC.
        </div>

        {reports_html}

        <div class="footer">
            <p>
                Generated with guidellm benchmark suite •
                <a href="https://github.com/YOUR_USERNAME/llm-benchmark-suite">Repository</a> •
                Last generated: {generation_time}
            </p>
        </div>
    </div>
</body>
</html>
    """

    if not reports_by_date:
        return generate_empty_index(output_path)

    # Calculate statistics
    total_reports = sum(len(reports) for reports in reports_by_date.values())
    total_dates = len(reports_by_date)
    platforms = set()
    for reports in reports_by_date.values():
        for report in reports:
            platforms.add(report['platform'])
    platforms_count = len(platforms)

    # Find most recent report for last updated time
    last_updated = "Never"
    if reports_by_date:
        most_recent_date = sorted(reports_by_date.keys(), reverse=True)[0]
        if reports_by_date[most_recent_date]:
            last_modified = max(report['modified'] for report in reports_by_date[most_recent_date])
            last_updated = last_modified.strftime('%H:%M')

    # Generate HTML for reports
    reports_html = ""
    for date_str in sorted(reports_by_date.keys(), reverse=True):
        reports = reports_by_date[date_str]

        # Format date for display
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            display_date = date_obj.strftime('%B %d, %Y')
            day_ago = (datetime.now() - date_obj).days
            if day_ago == 0:
                time_suffix = " (Today)"
            elif day_ago == 1:
                time_suffix = " (Yesterday)"
            else:
                time_suffix = f" ({day_ago} days ago)"
        except ValueError:
            display_date = date_str
            time_suffix = ""

        reports_html += f"""
        <div class="date-section">
            <div class="date-header">
                <span>{display_date}{time_suffix}</span>
                <span class="date-badge">{len(reports)} reports</span>
            </div>
            <div class="reports-grid">
        """

        for report in reports:
            report_title = report['platform'].replace('_', ' ').title()

            # Add comparison badge
            comparison_badge = ""
            if 'comparison' in report['filename'].lower():
                comparison_badge = '<span class="comparison-badge">Comparison</span>'

            # Format file size
            size_kb = report['size'] / 1024
            if size_kb < 1:
                size_str = f"{report['size']} B"
            elif size_kb < 1024:
                size_str = f"{size_kb:.1f} KB"
            else:
                size_str = f"{size_kb/1024:.1f} MB"

            reports_html += f"""
            <div class="report-card" onclick="window.open('{report['file_path']}', '_blank')">
                <div class="report-title">
                    {report_title}
                    {comparison_badge}
                </div>
                <div class="report-meta">
                    📊 {report['modified'].strftime('%H:%M')} •
                    <span class="report-size">{size_str}</span>
                </div>
            </div>
            """

        reports_html += """
            </div>
        </div>
        """

    return index_template.format(
        total_reports=total_reports,
        total_dates=total_dates,
        platforms_count=platforms_count,
        last_updated=last_updated,
        reports_html=reports_html,
        generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    )

def generate_empty_index(output_path):
    """Generate an empty index page when no reports are available."""
    empty_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Performance Benchmark Reports</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .container {{
            max-width: 800px;
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
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #7f8c8d;
        }}
        .empty-state h3 {{
            margin-top: 0;
            color: #95a5a6;
            font-size: 1.5em;
        }}
        .setup-steps {{
            text-align: left;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .setup-steps ol {{
            margin: 0;
            padding-left: 20px;
        }}
        .setup-steps li {{
            margin: 10px 0;
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
            <h1>🚀 LLM Performance Benchmark Reports</h1>
        </div>

        <div class="empty-state">
            <h3>No Benchmark Reports Available</h3>
            <p>Benchmark reports will appear here once the automated tests are configured and running.</p>
        </div>

        <div class="setup-steps">
            <h4>🔧 Setup Instructions:</h4>
            <ol>
                <li>Configure repository secrets (API keys, endpoints)</li>
                <li>Enable GitHub Pages in repository settings</li>
                <li>Trigger the first benchmark run manually</li>
                <li>Wait for the daily automation to take effect</li>
            </ol>
            <p><strong>Next scheduled run:</strong> Daily at 00:00 UTC</p>
        </div>

        <div class="footer">
            <p>
                Generated with guidellm benchmark suite •
                <a href="https://github.com/YOUR_USERNAME/llm-benchmark-suite">Repository</a> •
                Generated: {generation_time}
            </p>
        </div>
    </div>
</body>
</html>
    """

    return empty_template.format(
        generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    )

def main():
    """Main function."""
    import argparse
    parser = argparse.ArgumentParser(description='Generate index page for benchmark reports')
    parser.add_argument('--results-dir', required=True, help='Directory containing benchmark results')
    parser.add_argument('--output', required=True, help='Output HTML file path')

    args = parser.parse_args()

    html_content = generate_index_html(args.results_dir, args.output)

    with open(args.output, 'w') as f:
        f.write(html_content)

    print(f"Index page generated: {args.output}")

if __name__ == "__main__":
    main()