export interface StudentData {
  cumulative_gpa_before_sem: number;
  previous_semester_gpa: number;
  avg_gpa_change_from_previous_semester: number;
  avg_module_completion_pct: number;
  avg_video_watch_pct: number;
  avg_quiz_score: number;
  total_late_submissions: number;
  days_active: number;
  days_since_last_activity: number;
  num_failed_courses: number;
  grade_stddev_across_courses: number;
}

export interface PredictionResponse {
  prediction: number;
  prediction_label: string;
  probabilities: {
    [key: string]: number;
  };
  confidence: number;
  risk_level: string;
  recommended_actions: string[];
}
