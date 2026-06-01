import type { StudentData, PredictionResponse } from './types';

const API_BASE_URL = '/api';

export async function predictPerformance(
  data: StudentData
): Promise<PredictionResponse> {
  // Remove derived field - let backend compute it
  const { avg_gpa_change_from_previous_semester, ...payload } = data;

  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Prediction failed');
  }

  return response.json();
}

export async function predictBatch(
  students: StudentData[]
): Promise<{
  predictions: PredictionResponse[];
  total_students: number;
  summary: Record<string, number>;
}> {
  const response = await fetch(`${API_BASE_URL}/predict-batch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ students }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Batch prediction failed');
  }

  return response.json();
}
