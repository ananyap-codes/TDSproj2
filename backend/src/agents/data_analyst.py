"""
Data Analyst Agent using LLM for intelligent data analysis
"""

import os
import json
import pandas as pd
import numpy as np
from openai import OpenAI
from typing import Dict, Any, List, Optional
import re

class DataAnalystAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o"  # Use latest GPT-4 model

    def analyze(self, questions: str, data_files: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze data using LLM based on user questions
        """
        try:
            # Prepare data summary for LLM
            data_summary = self._prepare_data_summary(data_files)

            # Create analysis prompt
            prompt = self._create_analysis_prompt(questions, data_summary)

            # Get LLM analysis
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=4000
            )

            analysis_text = response.choices[0].message.content

            # Parse the structured response
            parsed_result = self._parse_analysis_response(analysis_text)

            # Perform actual calculations if needed
            if parsed_result.get('requires_computation', False):
                computed_results = self._perform_computations(
                    parsed_result.get('computations', []), 
                    data_files
                )
                parsed_result.update(computed_results)

            return parsed_result

        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "success": False
            }

    def _get_system_prompt(self) -> str:
        """System prompt for the data analyst agent"""
        return """You are an expert data analyst with advanced statistical knowledge. 

Your task is to analyze data and answer user questions. You must:

1. Provide accurate, data-driven insights
2. Suggest appropriate visualizations when helpful
3. Explain statistical concepts clearly
4. Return responses in a specific JSON format

Response format:
{
    "answers": ["answer1", "answer2", ...],  // Array of strings answering each question
    "insights": "Key insights from the analysis",
    "needs_visualization": true/false,
    "chart_config": {
        "type": "scatter|bar|line|histogram|heatmap",
        "x_column": "column_name",
        "y_column": "column_name", 
        "title": "Chart Title",
        "data_source": "filename"
    },
    "requires_computation": true/false,
    "computations": [
        {
            "type": "correlation|regression|statistical_test",
            "columns": ["col1", "col2"],
            "data_source": "filename"
        }
    ],
    "statistical_summary": "Summary of key statistics",
    "success": true
}

Be precise with column names and ensure all referenced columns exist in the data."""

    def _prepare_data_summary(self, data_files: Dict[str, Any]) -> str:
        """Prepare a summary of all data files for the LLM"""
        summary_parts = []

        for filename, data in data_files.items():
            if isinstance(data, pd.DataFrame):
                summary = f"\nFile: {filename}\n"
                summary += f"Shape: {data.shape[0]} rows, {data.shape[1]} columns\n"
                summary += f"Columns: {list(data.columns)}\n"

                # Add data types
                summary += f"Data types: {dict(data.dtypes)}\n"

                # Add basic statistics for numeric columns
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    summary += f"Numeric columns statistics:\n{data[numeric_cols].describe().to_string()}\n"

                # Sample data
                summary += f"Sample data (first 5 rows):\n{data.head().to_string()}\n"

                summary_parts.append(summary)

        return "\n".join(summary_parts)

    def _create_analysis_prompt(self, questions: str, data_summary: str) -> str:
        """Create the analysis prompt for the LLM"""
        return f"""
Please analyze the following data and answer the user's questions:

USER QUESTIONS:
{questions}

DATA SUMMARY:
{data_summary}

Provide a comprehensive analysis addressing each question. Include specific calculations, 
statistical tests, or visualizations that would help answer the questions.
"""

    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured format"""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # Fallback: create structured response from text
                return {
                    "answers": [response_text],
                    "insights": response_text,
                    "needs_visualization": False,
                    "requires_computation": False,
                    "success": True
                }
        except json.JSONDecodeError:
            # Fallback for non-JSON responses
            return {
                "answers": [response_text],
                "insights": response_text, 
                "needs_visualization": False,
                "requires_computation": False,
                "success": True
            }

    def _perform_computations(self, computations: List[Dict], data_files: Dict[str, Any]) -> Dict[str, Any]:
        """Perform actual statistical computations"""
        results = {}

        for comp in computations:
            try:
                comp_type = comp.get('type')
                data_source = comp.get('data_source')
                columns = comp.get('columns', [])

                if data_source not in data_files:
                    continue

                data = data_files[data_source]

                if comp_type == 'correlation' and len(columns) >= 2:
                    corr_value = data[columns[0]].corr(data[columns[1]])
                    results[f'correlation_{columns[0]}_{columns[1]}'] = corr_value

                elif comp_type == 'regression' and len(columns) >= 2:
                    from sklearn.linear_model import LinearRegression
                    X = data[columns[0]].values.reshape(-1, 1)
                    y = data[columns[1]].values
                    model = LinearRegression().fit(X, y)
                    results[f'regression_{columns[0]}_{columns[1]}'] = {
                        'r_squared': model.score(X, y),
                        'coefficient': model.coef_[0],
                        'intercept': model.intercept_
                    }

            except Exception as e:
                results[f'computation_error_{comp_type}'] = str(e)

        return results
