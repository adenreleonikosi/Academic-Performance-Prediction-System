# 🚀 Quick Start Guide

## Step 1: Re-run the Notebook

The CSV path has been fixed. Now run the notebook to export the model:

1. Open `Student Performance.ipynb` in VS Code or Jupyter
2. Run all cells from top to bottom (including the new last cell)
3. The last cell will export model artifacts to `model_artifacts/`

**Expected output from last cell:**
```
✓ Model saved to: d:\Student Performance\model_artifacts\logistic_regression_pipeline.pkl
✓ Feature columns saved (11 features)
✓ Metadata saved

✅ All artifacts exported successfully!
   Location: d:\Student Performance\model_artifacts
```

## Step 2: Install Dependencies

```powershell
cd "d:\Student Performance"
pip install -r requirements.txt
```

## Step 3: Run the API

```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
INFO:     Loading model...
INFO:     Model loaded successfully
```

## Step 4: Test the API

Open your browser to:
- **http://localhost:8000** - Welcome page
- **http://localhost:8000/docs** - Interactive Swagger UI
- **http://localhost:8000/redoc** - Alternative documentation

### Test from Command Line

```powershell
# Health check
curl http://localhost:8000/health

# Model info
curl http://localhost:8000/model-info

# Make a prediction
curl -X POST "http://localhost:8000/predict" `
  -H "Content-Type: application/json" `
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

## Step 5: Run Tests (Optional)

```powershell
pytest tests/test_api.py -v
```

## Troubleshooting

### If notebook fails:
- Ensure the CSV file exists at: `c:\Users\Nonso\Downloads\FY Projects\student_performance_large.csv`
- Check that all previous cells ran successfully

### If API fails to start:
- Make sure model artifacts were exported (Step 1)
- Check `model_artifacts/` folder contains 3 files
- Verify dependencies are installed

### If predictions fail:
- Check all 11 required features are provided
- Verify GPA values are between 0.0-4.0
- Ensure percentages are between 0.0-100.0

## Next Steps

1. **Frontend Integration**: Use the `/predict` endpoint from a web app
2. **Batch Processing**: Use `/predict-batch` for cohort analysis
3. **Monitoring**: Set up logging and performance tracking
4. **Deployment**: Deploy to cloud (AWS, Azure, GCP) or Docker

## Project Structure

```
Student Performance/
├── api/                     # ✅ FastAPI application
│   ├── main.py             # Main API endpoints
│   ├── models.py           # Pydantic schemas
│   ├── config.py           # Settings
│   └── utils.py            # Helper functions
├── model_artifacts/         # ⏳ Created after running notebook
│   ├── logistic_regression_pipeline.pkl
│   ├── feature_columns.json
│   └── model_metadata.json
├── tests/                   # ✅ API tests
├── data/raw/               # ✅ Data directory
├── Student Performance.ipynb # ✅ Updated with export code
├── requirements.txt         # ✅ Dependencies
├── README.md               # ✅ Full documentation
└── .env                    # ✅ Environment config
```

## Support

If you encounter issues, check:
1. Python version (3.10+ recommended)
2. All dependencies installed
3. Model artifacts exist
4. Port 8000 is not in use

Happy coding! 🎓📊
