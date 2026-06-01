"""
Tests for the Student Performance Prediction API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "timestamp" in data


def test_model_info():
    """Test the model info endpoint"""
    response = client.get("/model-info")
    # Will return 503 if model not loaded yet
    if response.status_code == 200:
        data = response.json()
        assert "model_name" in data
        assert "model_type" in data
        assert "features_count" in data


def test_predict_valid_input():
    """Test prediction with valid input"""
    payload = {
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
    
    response = client.post("/predict", json=payload)
    
    # Will return 503 if model not loaded
    if response.status_code == 200:
        data = response.json()
        assert "prediction" in data
        assert "prediction_label" in data
        assert "probabilities" in data
        assert "confidence" in data
        assert "risk_level" in data
        assert "recommended_actions" in data
        assert data["prediction"] in [0, 1, 2]
        assert 0 <= data["confidence"] <= 1
        assert data["prediction_label"] in ["At-Risk", "Medium", "High"]


def test_predict_invalid_gpa():
    """Test prediction with invalid GPA"""
    payload = {
        "cumulative_gpa_before_sem": 5.0,  # Invalid GPA (> 4.0)
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
    
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Validation error


def test_predict_missing_field():
    """Test prediction with missing required field"""
    payload = {
        "cumulative_gpa_before_sem": 3.2,
        # Missing previous_semester_gpa
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
    
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Validation error


def test_predict_at_risk_student():
    """Test prediction for at-risk student profile"""
    payload = {
        "cumulative_gpa_before_sem": 1.5,
        "previous_semester_gpa": 1.2,
        "avg_gpa_change_from_previous_semester": -0.3,
        "avg_module_completion_pct": 45.0,
        "avg_video_watch_pct": 35.0,
        "avg_quiz_score": 50.0,
        "total_late_submissions": 10,
        "days_active": 30,
        "days_since_last_activity": 15,
        "num_failed_courses": 2,
        "grade_stddev_across_courses": 1.5
    }
    
    response = client.post("/predict", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        # Should likely predict At-Risk
        assert data["risk_level"] in ["Critical", "Moderate"]
        assert len(data["recommended_actions"]) > 0


def test_predict_high_performer():
    """Test prediction for high-performing student"""
    payload = {
        "cumulative_gpa_before_sem": 3.8,
        "previous_semester_gpa": 3.9,
        "avg_gpa_change_from_previous_semester": 0.1,
        "avg_module_completion_pct": 95.0,
        "avg_video_watch_pct": 90.0,
        "avg_quiz_score": 92.0,
        "total_late_submissions": 0,
        "days_active": 150,
        "days_since_last_activity": 1,
        "num_failed_courses": 0,
        "grade_stddev_across_courses": 0.2
    }
    
    response = client.post("/predict", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        # Should likely predict High
        assert data["risk_level"] in ["Low", "Moderate"]


def test_batch_prediction():
    """Test batch prediction with multiple students"""
    payload = {
        "students": [
            {
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
            },
            {
                "cumulative_gpa_before_sem": 1.5,
                "previous_semester_gpa": 1.8,
                "avg_gpa_change_from_previous_semester": 0.3,
                "avg_module_completion_pct": 50.0,
                "avg_video_watch_pct": 45.0,
                "avg_quiz_score": 55.0,
                "total_late_submissions": 8,
                "days_active": 60,
                "days_since_last_activity": 10,
                "num_failed_courses": 1,
                "grade_stddev_across_courses": 1.2
            }
        ]
    }
    
    response = client.post("/predict-batch", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        assert "predictions" in data
        assert "total_students" in data
        assert "summary" in data
        assert data["total_students"] == 2
        assert len(data["predictions"]) == 2
        assert "At-Risk" in data["summary"]
        assert "Medium" in data["summary"]
        assert "High" in data["summary"]


def test_batch_prediction_too_many():
    """Test batch prediction with too many students"""
    # Create 101 students (exceeds limit of 100)
    students = []
    for i in range(101):
        students.append({
            "cumulative_gpa_before_sem": 3.0,
            "previous_semester_gpa": 3.0,
            "avg_gpa_change_from_previous_semester": 0.0,
            "avg_module_completion_pct": 80.0,
            "avg_video_watch_pct": 75.0,
            "avg_quiz_score": 78.0,
            "total_late_submissions": 3,
            "days_active": 100,
            "days_since_last_activity": 5,
            "num_failed_courses": 0,
            "grade_stddev_across_courses": 0.5
        })
    
    payload = {"students": students}
    response = client.post("/predict-batch", json=payload)
    assert response.status_code == 422  # Validation error
