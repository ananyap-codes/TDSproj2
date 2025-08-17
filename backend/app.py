"""
Data Analyst Agent API
A Flask API that uses LLMs to source, prepare, analyze, and visualize any data.
"""

import os
import json
import base64
import io
import traceback
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import openai
from datetime import datetime

from src.agents.data_analyst import DataAnalystAgent
from src.utils.file_processor import FileProcessor
from src.utils.data_processor import DataProcessor
from src.visualization.chart_generator import ChartGenerator

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'temp_uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
file_processor = FileProcessor()
data_processor = DataProcessor()
chart_generator = ChartGenerator()
analyst_agent = DataAnalystAgent()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Data Analyst Agent API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/', methods=['POST'])
def analyze_data():
    """
    Main API endpoint for data analysis.
    Accepts files and questions, returns analysis results.
    """
    try:
        # Extract questions (always required)
        if 'questions.txt' not in request.files:
            return jsonify({"error": "questions.txt file is required"}), 400

        questions_file = request.files['questions.txt']
        questions = questions_file.read().decode('utf-8')

        # Process all uploaded files
        uploaded_files = {}
        data_files = {}

        for file_key in request.files:
            if file_key == 'questions.txt':
                continue

            file = request.files[file_key]
            if file.filename == '':
                continue

            # Save file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Process the file
            processed_data = file_processor.process_file(filepath)
            if processed_data is not None:
                data_files[filename] = processed_data

            uploaded_files[filename] = filepath

        # Analyze the data using LLM agent
        analysis_result = analyst_agent.analyze(questions, data_files)

        # Generate visualizations if needed
        if analysis_result.get('needs_visualization', False):
            chart_data = chart_generator.generate_chart(
                data_files, 
                analysis_result.get('chart_config', {})
            )
            if chart_data:
                analysis_result['chart'] = chart_data

        # Clean up temporary files
        for filepath in uploaded_files.values():
            if os.path.exists(filepath):
                os.remove(filepath)

        return jsonify(analysis_result), 200

    except Exception as e:
        # Clean up files on error
        for filepath in uploaded_files.values():
            if os.path.exists(filepath):
                os.remove(filepath)

        return jsonify({
            "error": f"Analysis failed: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

@app.route('/api/capabilities', methods=['GET'])
def get_capabilities():
    """Returns API capabilities and supported file types"""
    return jsonify({
        "supported_file_types": [
            "CSV (.csv)",
            "Excel (.xlsx, .xls)", 
            "JSON (.json)",
            "Text (.txt)",
            "Images (.png, .jpg, .jpeg)",
            "TSV (.tsv)"
        ],
        "analysis_capabilities": [
            "Statistical analysis",
            "Data visualization", 
            "Correlation analysis",
            "Trend analysis",
            "Data cleaning and preparation",
            "Regression analysis",
            "Classification",
            "Clustering"
        ],
        "chart_types": [
            "Line plots",
            "Bar charts", 
            "Scatter plots",
            "Histograms",
            "Heatmaps",
            "Box plots",
            "Pie charts"
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
