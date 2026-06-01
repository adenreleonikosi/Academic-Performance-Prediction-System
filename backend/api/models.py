"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal, Dict
from datetime import datetime


class PredictionRequest(BaseModel):
    """Request model for single student prediction"""
    
    # Academic History Features
    cumulative_gpa_before_sem: float = Field(
        ..., 
        ge=0.0, 
        le=5.0, 
        description="Overall GPA before current semester"
    )
    previous_semester_gpa: float = Field(
        ..., 
        ge=0.0, 
        le=5.0, 
        description="GPA from the immediate previous semester"
    )
    avg_gpa_change_from_previous_semester: float = Field(
        default=None, 
        ge=-5.0, 
        le=5.0, 
        description="GPA change from previous semester (auto-calculated if not provided)"
    )
    
    # Engagement Features
    avg_module_completion_pct: float = Field(
        ..., 
        ge=0.0, 
        le=100.0, 
        description="Average module completion rate (%)"
    )
    avg_video_watch_pct: float = Field(
        ..., 
        ge=0.0, 
        le=100.0, 
        description="Average video watch percentage"
    )
    avg_quiz_score: float = Field(
        ..., 
        ge=0.0, 
        le=100.0, 
        description="Average quiz score across courses"
    )
    
    # Behavioral Features
    total_late_submissions: int = Field(
        ..., 
        ge=0, 
        description="Total late assignment submissions"
    )
    days_active: int = Field(
        ..., 
        ge=0, 
        le=365, 
        description="Number of active learning days"
    )
    days_since_last_activity: int = Field(
        ..., 
        ge=0, 
        le=365, 
        description="Days since last system activity"
    )
    
    # Performance Signals
    num_failed_courses: int = Field(
        ..., 
        ge=0, 
        description="Number of failed courses"
    )
    grade_stddev_across_courses: float = Field(
        ..., 
        ge=0.0, 
        le=5.0, 
        description="Standard deviation of grades"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
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
        }
    }


class PredictionResponse(BaseModel):
    """Response model for predictions"""
    
    prediction: int = Field(..., ge=0, le=2, description="Predicted class: 0, 1, or 2")
    prediction_label: Literal["At-Risk", "Medium", "High"] = Field(
        ..., 
        description="Human-readable prediction"
    )
    probabilities: Dict[str, float] = Field(
        ..., 
        description="Probability for each class"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Model confidence (max probability)"
    )
    risk_level: Literal["Critical", "Moderate", "Low"] = Field(
        ..., 
        description="Risk level for interventions"
    )
    recommended_actions: List[str] = Field(
        ..., 
        description="Recommended intervention actions"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
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
                    "Consider honors program eligibility"
                ]
            }
        }
    }


class BatchPredictionRequest(BaseModel):
    """Request model for batch predictions"""
    
    students: List[PredictionRequest] = Field(
        ..., 
        min_length=1,
        max_length=100,
        description="List of students (max 100 per request)"
    )


class BatchPredictionResponse(BaseModel):
    """Response model for batch predictions"""
    
    predictions: List[PredictionResponse]
    total_students: int
    summary: Dict[str, int] = Field(
        ..., 
        description="Count of students in each category"
    )


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str
    model_loaded: bool
    timestamp: datetime
    
    model_config = {
        "protected_namespaces": ()
    }


class ModelInfoResponse(BaseModel):
    """Model information response"""
    
    model_name: str
    model_type: str
    version: str
    features_count: int
    training_date: Optional[str] = None
    performance_metrics: Dict
    
    model_config = {
        "protected_namespaces": ()
    }
