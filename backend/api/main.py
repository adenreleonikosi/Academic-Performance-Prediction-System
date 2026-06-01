"""
FastAPI application for Student Performance Predictions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging
from datetime import datetime

from .models import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse,
    ModelInfoResponse
)
from .config import settings, ALLOWED_ORIGINS
from .utils import (
    load_model, 
    preprocess_input, 
    get_model_info,
    get_class_label,
    get_risk_level,
    get_recommended_actions
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Student Performance Prediction API",
    description="API for predicting semester-level academic performance and risk classification",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable for model (loaded on startup)
model = None
model_metadata = None


@app.on_event("startup")
async def startup_event():
    """Load model on application startup"""
    global model, model_metadata
    try:
        logger.info("Loading model...")
        model, model_metadata = load_model()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Student Performance Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "description": "Semester-level academic performance prediction system"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        timestamp=datetime.utcnow()
    )


@app.get("/model-info", response_model=ModelInfoResponse, tags=["Model"])
async def model_info():
    """Get information about the loaded model"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return ModelInfoResponse(**get_model_info(model_metadata))


@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict(request: PredictionRequest):
    """
    Make a single prediction for a student
    
    Returns:
    - prediction: 0 (At-Risk), 1 (Medium), or 2 (High)
    - prediction_label: Human-readable class label
    - probabilities: Probability for each of the 3 classes
    - confidence: Model confidence level
    - risk_level: Risk classification for interventions
    - recommended_actions: List of intervention strategies
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Preprocess input
        input_data = preprocess_input(request.dict())
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        probabilities = model.predict_proba(input_data)[0]
        
        # Get prediction label
        prediction_label = get_class_label(prediction)
        
        # Build probability dictionary
        prob_dict = {
            "At-Risk": float(probabilities[0]),
            "Medium": float(probabilities[1]),
            "High": float(probabilities[2])
        }
        
        # Get confidence (max probability)
        confidence = float(max(probabilities))
        
        # Get risk level and recommendations
        risk_level = get_risk_level(prediction)
        recommended_actions = get_recommended_actions(prediction_label)
        
        logger.info(
            f"Prediction made: {prediction_label} "
            f"(confidence: {confidence:.4f})"
        )
        
        return PredictionResponse(
            prediction=int(prediction),
            prediction_label=prediction_label,
            probabilities=prob_dict,
            confidence=confidence,
            risk_level=risk_level,
            recommended_actions=recommended_actions
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")


@app.post("/predict-batch", response_model=BatchPredictionResponse, tags=["Predictions"])
async def predict_batch(request: BatchPredictionRequest):
    """
    Make predictions for multiple students at once (up to 100)
    
    Returns list of predictions with summary statistics
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        predictions = []
        class_counts = {"At-Risk": 0, "Medium": 0, "High": 0}
        
        for idx, student in enumerate(request.students):
            # Preprocess input
            input_data = preprocess_input(student.dict())
            
            # Make prediction
            prediction = model.predict(input_data)[0]
            probabilities = model.predict_proba(input_data)[0]
            
            # Get prediction label
            prediction_label = get_class_label(prediction)
            
            # Build probability dictionary
            prob_dict = {
                "At-Risk": float(probabilities[0]),
                "Medium": float(probabilities[1]),
                "High": float(probabilities[2])
            }
            
            # Get confidence
            confidence = float(max(probabilities))
            
            # Get risk level and recommendations
            risk_level = get_risk_level(prediction)
            recommended_actions = get_recommended_actions(prediction_label)
            
            # Add to results
            predictions.append(PredictionResponse(
                prediction=int(prediction),
                prediction_label=prediction_label,
                probabilities=prob_dict,
                confidence=confidence,
                risk_level=risk_level,
                recommended_actions=recommended_actions
            ))
            
            # Update counts
            class_counts[prediction_label] += 1
        
        logger.info(
            f"Batch prediction completed: {len(predictions)} students. "
            f"At-Risk: {class_counts['At-Risk']}, "
            f"Medium: {class_counts['Medium']}, "
            f"High: {class_counts['High']}"
        )
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_students=len(predictions),
            summary=class_counts
        )
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Batch prediction failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
