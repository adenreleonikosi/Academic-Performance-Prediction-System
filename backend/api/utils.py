"""
Utility functions for model loading and data preprocessing
"""

import joblib
import json
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any, List
import logging
from pathlib import Path

from .config import settings

logger = logging.getLogger(__name__)


# Intervention strategies based on performance class
INTERVENTION_STRATEGIES = {
    "At-Risk": [
        "Schedule immediate academic advisor meeting",
        "Refer to tutoring services and study skills workshops",
        "Reduce course load for next semester",
        "Connect with peer mentorship program",
        "Develop personalized academic success plan",
        "Monitor engagement weekly"
    ],
    "Medium": [
        "Monitor engagement bi-weekly",
        "Encourage office hours attendance",
        "Review time management strategies",
        "Provide study group resources",
        "Check in with academic advisor mid-semester"
    ],
    "High": [
        "Maintain current strategies",
        "Consider honors program eligibility",
        "Explore research opportunities",
        "Mentor other students",
        "Plan for advanced coursework"
    ]
}


def load_model() -> Tuple[Any, Dict]:
    """
    Load the trained model and metadata
    
    Returns:
        Tuple of (model, metadata)
    """
    try:
        # Load the model pipeline
        model = joblib.load(settings.MODEL_PATH)
        logger.info(f"Model loaded from {settings.MODEL_PATH}")
        
        # Load metadata if exists
        metadata = {}
        if Path(settings.MODEL_METADATA_PATH).exists():
            with open(settings.MODEL_METADATA_PATH, 'r') as f:
                metadata = json.load(f)
            logger.info("Model metadata loaded")
        
        return model, metadata
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise


def preprocess_input(input_data: Dict) -> pd.DataFrame:
    """
    Preprocess input data to match model training format
    
    All features are numeric - no categorical encoding needed!
    Auto-computes derived features if missing.
    
    Args:
        input_data: Dictionary containing student features
        
    Returns:
        DataFrame ready for model prediction
    """
    try:
        # Create DataFrame from input
        df = pd.DataFrame([input_data])
        
        # Auto-compute avg_gpa_change_from_previous_semester if missing
        if 'avg_gpa_change_from_previous_semester' not in df.columns or pd.isna(df['avg_gpa_change_from_previous_semester'].iloc[0]):
            if 'cumulative_gpa_before_sem' in df.columns and 'previous_semester_gpa' in df.columns:
                df['avg_gpa_change_from_previous_semester'] = df['previous_semester_gpa'] - df['cumulative_gpa_before_sem']
                logger.info("Computed avg_gpa_change_from_previous_semester from base GPA values")
        
        # Validate and clip GPA values
        gpa_features = ['cumulative_gpa_before_sem', 'previous_semester_gpa']
        for col in gpa_features:
            if col in df.columns:
                df[col] = df[col].clip(0.0, 5.0)
        
        # Validate and clip GPA change
        if 'avg_gpa_change_from_previous_semester' in df.columns:
            df['avg_gpa_change_from_previous_semester'] = df['avg_gpa_change_from_previous_semester'].clip(-5.0, 5.0)
        
        # Validate and clip percentage features
        pct_features = ['avg_module_completion_pct', 'avg_video_watch_pct', 'avg_quiz_score']
        for col in pct_features:
            if col in df.columns:
                df[col] = df[col].clip(0.0, 100.0)
        
        # Load expected feature columns if available
        if Path(settings.FEATURE_COLUMNS_PATH).exists():
            with open(settings.FEATURE_COLUMNS_PATH, 'r') as f:
                expected_columns = json.load(f)
            
            # Reorder columns to match training
            df = df[expected_columns]
        
        logger.info(f"Input preprocessed successfully. Shape: {df.shape}")
        return df
        
    except Exception as e:
        logger.error(f"Error preprocessing input: {str(e)}")
        raise


def get_model_info(metadata: Dict) -> Dict:
    """
    Get information about the loaded model
    
    Args:
        metadata: Model metadata dictionary
        
    Returns:
        Dictionary with model information
    """
    return {
        "model_name": metadata.get("model_name", "Logistic Regression (SMOTE)"),
        "model_type": metadata.get("model_type", "Multiclass Classification"),
        "version": metadata.get("version", "1.0.0"),
        "features_count": metadata.get("features_count", 11),
        "training_date": metadata.get("training_date", None),
        "performance_metrics": metadata.get("performance_metrics", {
            "test_accuracy": 0.9933,
            "test_f1_macro": 0.9888,
            "test_recall_macro": 0.9967
        })
    }


def get_class_label(prediction: int) -> str:
    """
    Convert numeric prediction to human-readable label
    
    Args:
        prediction: Numeric class (0, 1, or 2)
        
    Returns:
        String label
    """
    labels = {
        0: "At-Risk",
        1: "Medium",
        2: "High"
    }
    return labels.get(prediction, "Unknown")


def get_risk_level(prediction: int) -> str:
    """
    Get risk level for intervention planning
    Note: Inverted from prediction (High performance = Low risk)
    
    Args:
        prediction: Numeric class (0, 1, or 2)
        
    Returns:
        Risk level string
    """
    risk_map = {
        0: "Critical",  # At-Risk performance
        1: "Moderate",  # Medium performance
        2: "Low"        # High performance
    }
    return risk_map.get(prediction, "Unknown")


def get_recommended_actions(prediction_label: str) -> List[str]:
    """
    Get recommended intervention actions
    
    Args:
        prediction_label: Class label (At-Risk, Medium, High)
        
    Returns:
        List of recommended actions
    """
    return INTERVENTION_STRATEGIES.get(prediction_label, [])
