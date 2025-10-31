import json
import base64

# Parse inputs
try:
    data = json.loads(data_json)
    recommendations = json.loads(chart_json)
except:
    return {
        "dashboard_html": "<html><body><h1>Error parsing data</h1></body></html>"
    }

# Generate HTML with Chart.js (works without external libraries)
html = """<!DOCTYPE html>
<html>
<head>
    <title>Data Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 20px;
        }
        .summary {
            background: #f7f9fc;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 4px solid #667eea;
        }
        .chart-container {
            margin-bottom: 40px;
            padding: 20px;
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }
        .chart-title {
            font-size: 1.2em;
            color: #444;
            margin-bottom: 10px;
            font-weight: 600;
        }
        .chart-desc {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 15px;
        }
        canvas {
            max-height: 400px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Data Visualization Dashboard</h1>
        <div class="summary">
            <h3>Analysis Summary</h3>
            <p>""" + recommendations.get('summary', 'Data analysis complete.') + """</p>
            <p><strong>Dataset:</strong> """ + f"{len(data)} rows" + """</p>
        </div>
"""

# Generate charts using Chart.js
for i, chart in enumerate(recommendations.get('charts', [])):
    chart_id = f"chart_{i}"
    chart_type = chart.get('type', 'bar')
    title = chart.get('title', f'Chart {i + 1}')
    description = chart.get('description', '')
    x_col = chart.get('x_column')
    y_col = chart.get('y_column')

    html += f"""
        <div class="chart-container">
            <div class="chart-title">{title}</div>
            <div class="chart-desc">{description}</div>
            <canvas id="{chart_id}"></canvas>
        </div>
    """

    # Prepare data for Chart.js
    if chart_type in ['bar', 'line', 'scatter']:
        if x_col and y_col:
            labels = []
            values = []
            for row in data[:30]:  # Limit to first 30 rows for display
                if x_col in row and y_col in row:
                    labels.append(str(row[x_col]))
                    try:
                        values.append(float(row[y_col]))
                    except:
                        values.append(0)

            chart_config = {
                'type': 'line' if chart_type == 'line' else 'bar',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': y_col,
                        'data': values,
                        'backgroundColor': 'rgba(102, 126, 234, 0.5)',
                        'borderColor': 'rgba(102, 126, 234, 1)',
                        'borderWidth': 2
                    }]
                }
            }
        else:
            chart_config = None

    elif chart_type == 'pie' and x_col:
        # Count occurrences for pie chart
        counts = {}
        for row in data:
            if x_col in row:
                val = str(row[x_col])
                counts[val] = counts.get(val, 0) + 1

        # Get top 10 values
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]

        chart_config = {
            'type': 'pie',
            'data': {
                'labels': [item[0] for item in sorted_counts],
                'datasets': [{
                    'data': [item[1] for item in sorted_counts],
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.5)',
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 206, 86, 0.5)',
                        'rgba(75, 192, 192, 0.5)',
                        'rgba(153, 102, 255, 0.5)',
                        'rgba(255, 159, 64, 0.5)',
                        'rgba(199, 199, 199, 0.5)',
                        'rgba(83, 102, 255, 0.5)',
                        'rgba(255, 99, 255, 0.5)',
                        'rgba(99, 255, 132, 0.5)'
                    ]
                }]
            }
        }
    else:
        chart_config = None

    if chart_config:
        html += f"""
        <script>
            new Chart(document.getElementById('{chart_id}'), {json.dumps(chart_config)});
        </script>
        """

html += """
    </div>
</body>
</html>
"""

return {
    "dashboard_html": html
}