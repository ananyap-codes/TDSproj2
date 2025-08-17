# Data Analyst Agent API

A powerful Flask API that uses Large Language Models (LLMs) to source, prepare, analyze, and visualize any data. This API accepts data analysis tasks with optional file attachments and returns comprehensive analysis results within 3 minutes.

## Features

- **Multi-format Data Support**: CSV, Excel, JSON, TSV, text files, and images
- **LLM-Powered Analysis**: Uses OpenAI GPT-4 for intelligent data interpretation
- **Automated Visualization**: Generates charts and plots as base64-encoded images
- **Statistical Computing**: Correlation analysis, regression, statistical tests
- **Data Cleaning**: Automatic data preprocessing and cleaning
- **RESTful API**: Simple POST endpoint for all analysis tasks
- **File Upload Support**: Handles multiple file uploads via multipart/form-data

## Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

1. **Clone and setup**:
```bash
git clone <repository>
cd data_analyst_agent
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. **Run the API**:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## API Usage

### Endpoint

```
POST /api/
```

### Request Format

The API accepts `multipart/form-data` with:

- **questions.txt** (required): Text file containing analysis questions
- **data.csv** (optional): CSV data file
- **image.png** (optional): Image file
- Any other supported data files

### Example Request

```bash
curl "http://localhost:5000/api/" \
  -F "questions.txt=@questions.txt" \
  -F "data.csv=@data.csv" \
  -F "image.png=@image.png"
```

### Example questions.txt

```
1. How many $2 billion movies were released before 2000?
2. Which is the earliest film that grossed over $1.5 billion?
3. What's the correlation between Rank and Peak?
4. Draw a scatterplot of Rank vs Peak with a red dotted regression line.
```

### Response Format

```json
{
  "answers": ["1", "Titanic", "0.485782", "data:image/png;base64,iVBORw0KG..."],
  "insights": "Key insights from analysis...",
  "statistical_summary": "Summary of statistics...",
  "success": true
}
```

For visualization requests, the response includes base64-encoded PNG images under 100KB.

## Supported File Types

- **CSV** (.csv): Comma-separated values
- **Excel** (.xlsx, .xls): Microsoft Excel files  
- **JSON** (.json): JavaScript Object Notation
- **TSV** (.tsv): Tab-separated values
- **Text** (.txt): Plain text files
- **Images** (.png, .jpg, .jpeg): Image files

## Analysis Capabilities

- Statistical analysis (mean, median, correlation, etc.)
- Data visualization (scatter plots, bar charts, histograms, etc.)
- Regression analysis and trend detection
- Data cleaning and preprocessing
- Time series analysis
- Classification and clustering insights

## Chart Types

- Scatter plots with regression lines
- Bar charts and histograms
- Line plots for time series
- Correlation heatmaps
- Box plots for distribution analysis
- Multi-panel visualizations

## Configuration

Key environment variables:

```bash
OPENAI_API_KEY=your_api_key_here
MAX_CONTENT_LENGTH=104857600  # 100MB max upload
CHART_MAX_SIZE_BYTES=100000   # 100KB max chart size
ANALYSIS_TIMEOUT=180          # 3 minutes timeout
```

## API Endpoints

### Health Check
```
GET /
```
Returns API status and version info.

### Data Analysis
```
POST /api/
```
Main endpoint for data analysis tasks.

### Capabilities
```
GET /api/capabilities
```
Returns supported file types and analysis capabilities.

## Error Handling

The API returns appropriate HTTP status codes:

- **200**: Success
- **400**: Bad request (missing questions.txt, invalid files)
- **413**: File too large
- **500**: Internal server error

Error responses include detailed error messages and stack traces for debugging.

## Development

### Project Structure

```
data_analyst_agent/
├── app.py                    # Main Flask application
├── src/
│   ├── agents/
│   │   └── data_analyst.py   # LLM-powered analysis agent
│   ├── utils/
│   │   ├── file_processor.py # File format handlers
│   │   └── data_processor.py # Data cleaning utilities
│   └── visualization/
│       └── chart_generator.py # Chart generation
├── config/
│   └── config.py            # Configuration settings
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
└── docker-compose.yml      # Docker Compose setup
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ app.py
flake8 src/ app.py
```

## Performance Considerations

- **File Size Limits**: 100MB max upload per request
- **Response Time**: 3-minute timeout for analysis
- **Memory Usage**: Optimized for datasets up to 100K rows
- **Chart Size**: Images compressed to <100KB
- **Concurrent Requests**: Supports multiple workers via Gunicorn

## Security

- Input validation for all file uploads
- Secure filename handling
- Environment variable configuration
- No sensitive data logged
- CORS enabled for cross-origin requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the API capabilities endpoint: `GET /api/capabilities`
- Review error messages in API responses
- Ensure OpenAI API key is properly configured
- Verify file formats are supported

## Examples

See the `examples/` directory for sample data files and common use cases.
