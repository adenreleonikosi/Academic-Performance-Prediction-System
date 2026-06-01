import { useState } from 'react';
import type { FormEvent } from 'react';
import type { StudentData, PredictionResponse } from './types';
import { predictPerformance } from './api';
import React from 'react';
import BatchForm from './BatchForm';

function App() {
  const [showLanding, setShowLanding] = useState(true);
  const [isBatchMode, setIsBatchMode] = useState(false);

  const [formData, setFormData] = useState<StudentData>({
    cumulative_gpa_before_sem: 3.0,
    previous_semester_gpa: 3.0,
    avg_gpa_change_from_previous_semester: 0.0,
    avg_module_completion_pct: 75.0,
    avg_video_watch_pct: 75.0,
    avg_quiz_score: 75.0,
    total_late_submissions: 2,
    days_active: 90,
    days_since_last_activity: 3,
    num_failed_courses: 0,
    grade_stddev_across_courses: 0.5,
  });

  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: keyof StudentData, value: string) => {
    const numValue = parseFloat(value) || 0;
    const config = getInputConfig(field);
    
    // Clamp value between min and max
    const clampedValue = Math.min(Math.max(numValue, config.min), config.max);
    
    setFormData((prev) => {
      const next = {
        ...prev,
        [field]: clampedValue,
      } as StudentData;

      // Auto-generate avg_gpa_change_from_previous_semester from GPA fields
      if (field === 'cumulative_gpa_before_sem' || field === 'previous_semester_gpa') {
        const cumulative = field === 'cumulative_gpa_before_sem' ? clampedValue : prev.cumulative_gpa_before_sem;
        const previous = field === 'previous_semester_gpa' ? clampedValue : prev.previous_semester_gpa;

        // Based on existing notebook/schema example, define change = previous - cumulative
        const rawChange = previous - cumulative;
        const changeConfig = getInputConfig('avg_gpa_change_from_previous_semester');
        const clampedChange = Math.min(Math.max(parseFloat(rawChange.toFixed(2)), changeConfig.min), changeConfig.max);
        next.avg_gpa_change_from_previous_semester = clampedChange;
      }

      return next;
    });
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const prediction = await predictPerformance(formData);
      setResult(prediction);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const formatFieldName = (field: string): string => {
    return field
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (l) => l.toUpperCase());
  };

  const getInputConfig = (field: keyof StudentData) => {
    const configs: Record<keyof StudentData, { min: number; max: number; step: number }> = {
      cumulative_gpa_before_sem: { min: 0, max: 5, step: 0.01 },
      previous_semester_gpa: { min: 0, max: 5, step: 0.01 },
      avg_gpa_change_from_previous_semester: { min: -5, max: 5, step: 0.01 },
      avg_module_completion_pct: { min: 0, max: 100, step: 0.01 },
      avg_video_watch_pct: { min: 0, max: 100, step: 0.01 },
      avg_quiz_score: { min: 0, max: 100, step: 0.01 },
      total_late_submissions: { min: 0, max: 100, step: 0.01 },
      days_active: { min: 0, max: 365, step: 0.01 },
      days_since_last_activity: { min: 0, max: 365, step: 0.01 },
      num_failed_courses: { min: 0, max: 20, step: 0.01 },
      grade_stddev_across_courses: { min: 0, max: 5, step: 0.01 },
    };
    return configs[field];
  };

  return (
    <div className="app">
      {showLanding ? (
        <div className="header">
          <h1>Student Performance Predictor</h1>
          <p>Predict semester performance based on academic metrics</p>
          <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
            <button
              className="submit-button"
              onClick={() => setShowLanding(false)}
            >
              Start Prediction
            </button>
          </div>
        </div>
      ) : (
        <>
          <header className="header">
            <h1>Student Performance Predictor</h1>
            <p>Predict semester performance based on academic metrics</p>
          </header>

          <div style={{ display: 'flex', gap: 8, marginTop: 12, marginBottom: 12 }}>
            <button
              className="submit-button"
              onClick={() => {
                setIsBatchMode(false);
                setResult(null);
              }}
              style={{ background: !isBatchMode ? '#222' : '#f0f0f0', color: !isBatchMode ? '#fff' : '#333' }}
            >
              Single Prediction
            </button>
            <button
              className="submit-button"
              onClick={() => {
                setIsBatchMode(true);
                setResult(null);
              }}
              style={{ background: isBatchMode ? '#222' : '#f0f0f0', color: isBatchMode ? '#fff' : '#333' }}
            >
              Batch Prediction
            </button>
          </div>

          {isBatchMode ? (
            <div className="form-container">
              {/* Lazy-load batch form component */}
              <React.Suspense fallback={<div>Loading batch form...</div>}>
                <BatchForm />
              </React.Suspense>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="form-container">
              <div className="form-grid">
                {Object.keys(formData).filter(f => f !== 'avg_gpa_change_from_previous_semester').map((field) => {
                  const key = field as keyof StudentData;
                  const config = getInputConfig(key);
                  return (
                    <div key={field} className="form-field">
                      <label htmlFor={field}>{formatFieldName(field)}</label>
                      <input
                        id={field}
                        type="number"
                        value={formData[key]}
                        onChange={(e) => handleInputChange(key, e.target.value)}
                        min={config.min}
                        max={config.max}
                        step={config.step}
                        disabled={loading}
                        required
                      />
                    </div>
                  );
                })}
              </div>
              <button type="submit" className="submit-button" disabled={loading}>
                {loading ? 'Predicting...' : 'Predict Performance'}
              </button>
            </form>
          )}
        </>
      )}

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="result-container">
          <div className="result-header">
            <div
              className={`prediction-label ${result.prediction_label.toLowerCase().replace(' ', '-')}`}
            >
              {result.prediction_label}
            </div>
            <div className="risk-level">{result.risk_level}</div>
          </div>

          <div className="confidence-container">
            <div className="confidence-label">
              Confidence: {(result.confidence * 100).toFixed(1)}%
            </div>
            <div className="confidence-bar">
              <div
                className="confidence-fill"
                style={{ width: `${result.confidence * 100}%` }}
              />
            </div>
          </div>

          <div className="probabilities">
            <h3>Class Probabilities</h3>
            {Object.entries(result.probabilities).map(([label, prob]) => (
              <div key={label} className="probability-item">
                <span className="probability-class">{label}</span>
                <span className="probability-value">
                  {(prob * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>

          {result.recommended_actions.length > 0 && (
            <div className="recommendations">
              <h3>Recommended Actions</h3>
              <ul>
                {result.recommended_actions.map((action, index) => (
                  <li key={index}>{action}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
