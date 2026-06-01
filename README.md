# Student Performance Prediction API

A FastAPI-based REST API for predicting semester-level academic performance and identifying at-risk students for early intervention.

## Overview

This API uses a machine learning model (Logistic Regression with SMOTE) trained on student performance data to predict academic risk classification. The model analyzes student features including GPA history, engagement metrics, and behavioral indicators.

## Performance Metrics

- **Test Accuracy**: 99.33%
- **Test Recall**: 99.67% (catches 99.67% of at-risk students!)
- **Test F1-Score**: 98.88%
- **Validation ROC-AUC**: 99.95%

## Features

- **Single Prediction**: Predict for one student at a time
- **Batch Prediction**: Predict for multiple students (up to 100)
- **Risk Classification**: 3-level classification (At-Risk, Medium, High)
- **Intervention Recommendations**: Actionable suggestions for each risk level
- **Model Information**: Get details about the loaded model
- **Health Check**: Monitor API and model status
- **Input Validation**: Automatic validation of all inputs
- **Interactive Documentation**: Built-in Swagger UI and ReDoc

## Project Structure

```
Student Performance/
├── api/
│   ├── __init__.py           # Package initialization
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic request/response models
│   ├── config.py            # Configuration settings
│   └── utils.py             # Helper functions
├── data/
│   └── raw/                 # Original dataset
├── model_artifacts/
│   ├── logistic_regression_pipeline.pkl  # Trained model
│   ├── feature_columns.json              # Feature names/order
│   └── model_metadata.json               # Model info
├── notebooks/
│   └── Student Performance.ipynb         # Model training notebook
├── tests/
│   └── test_api.py                       # API tests
├── .env                                  # Environment variables
├── .gitignore                           # Git ignore rules
├── requirements.txt                      # Python dependencies
└── README.md                            # This file
```

## Installation

### 1. Navigate to the project directory

```bash
cd "d:\Student Performance"
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Model Export (Required Before Running)

Before running the API, you need to export your trained model from the Jupyter notebook:

1. Open `Student Performance.ipynb`
2. Run all cells up to and including the last cell (Model Export)
3. This will create files in `model_artifacts/` directory:
   - `logistic_regression_pipeline.pkl`
   - `feature_columns.json`
   - `model_metadata.json`

## Running the API

### Option 1: Using uvicorn directly

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Using Python

```bash
python -m api.main
```

The API will be available at:
- **Main URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Root
- `GET /` - Welcome message and API info

### Health & Info
- `GET /health` - Health check endpoint
- `GET /model-info` - Get model metadata and performance metrics

### Predictions
- `POST /predict` - Single student prediction
- `POST /predict-batch` - Batch predictions (up to 100 students)

## Usage Examples

### Single Prediction

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "cumulative_gpa_before_sem": 3.2,
    "previous_semester_gpa": 3.5,
    "avg_gpa_change_from_previous_semester": 0.3,
    "avg_module_completion_pct": 85.5,
    "avg_video_watch_pct": 78.2,
    "avg_quiz_score": 82.0,
    "total_late_submissions": 2,
    "days_active": 120,
    "days_since_last_activity": 3,
    "num_failed_courses": 0,
    "grade_stddev_across_courses": 0.5
  }'
```

### Python Client Example

```python
import requests

# API endpoint
url = "http://localhost:8000/predict"

# Student data
student_data = {
    "cumulative_gpa_before_sem": 3.2,
    "previous_semester_gpa": 3.5,
    "avg_gpa_change_from_previous_semester": 0.3,
    "avg_module_completion_pct": 85.5,
    "avg_video_watch_pct": 78.2,
    "avg_quiz_score": 82.0,
    "total_late_submissions": 2,
    "days_active": 120,
    "days_since_last_activity": 3,
    "num_failed_courses": 0,
    "grade_stddev_across_courses": 0.5
}

# Make prediction
response = requests.post(url, json=student_data)
result = response.json()

print(f"Prediction: {result['prediction_label']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Risk Level: {result['risk_level']}")
print(f"Recommended Actions:")
for action in result['recommended_actions']:
    print(f"  - {action}")
```

### Response Example

```json
{
  "prediction": 2,
  "prediction_label": "High",
  "probabilities": {
    "At-Risk": 0.001,
    "Medium": 0.029,
    "High": 0.970
  },
  "confidence": 0.970,
  "risk_level": "Low",
  "recommended_actions": [
    "Maintain current strategies",
    "Consider honors program eligibility",
    "Explore research opportunities",
    "Mentor other students",
    "Plan for advanced coursework"
  ]
}
```

## Input Features

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `cumulative_gpa_before_sem` | float | 0.0-4.0 | Overall GPA before current semester |
| `previous_semester_gpa` | float | 0.0-4.0 | GPA from immediate previous semester |
| `avg_gpa_change_from_previous_semester` | float | -4.0 to 4.0 | GPA change from previous semester |
| `avg_module_completion_pct` | float | 0.0-100.0 | Average module completion rate (%) |
| `avg_video_watch_pct` | float | 0.0-100.0 | Average video watch percentage |
| `avg_quiz_score` | float | 0.0-100.0 | Average quiz score across courses |
| `total_late_submissions` | int | 0+ | Total late assignment submissions |
| `days_active` | int | 0-365 | Number of active learning days |
| `days_since_last_activity` | int | 0-365 | Days since last system activity |
| `num_failed_courses` | int | 0+ | Number of failed courses |
| `grade_stddev_across_courses` | float | 0.0-4.0 | Standard deviation of grades |

## Risk Classifications

### At-Risk (Class 0)
- **GPA Range**: < 2.0
- **Risk Level**: Critical
- **Interventions**: Immediate advisor meeting, tutoring services, course load reduction

### Medium (Class 1)
- **GPA Range**: 2.0 - 3.5
- **Risk Level**: Moderate
- **Interventions**: Regular monitoring, study skills support, time management

### High (Class 2)
- **GPA Range**: > 3.5
- **Risk Level**: Low
- **Interventions**: Maintain strategies, honor programs, advanced opportunities

## Testing

Run the test suite:

```bash
pytest tests/test_api.py -v
```

## Environment Variables

Create a `.env` file in the project root:

```env
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

## Production Deployment

### Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t student-performance-api .
docker run -p 8000:8000 student-performance-api
```

## Troubleshooting

### Model not loading
- Ensure you've run the model export cell in the notebook
- Check that `model_artifacts/` contains all three files
- Verify file paths in `api/config.py`

### Import errors
- Activate your virtual environment
- Run `pip install -r requirements.txt`

### Port already in use
- Change port in `.env` or use `--port` flag
- Kill existing process: `netstat -ano | findstr :8000`

## License

MIT License

## Contact

For questions or issues, please open an issue on the project repository.
