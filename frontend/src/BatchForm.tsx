import { useState } from 'react';
import type { StudentData } from './types';
import { predictBatch } from './api';

function parseCsv(text: string): { data: StudentData[]; inputs: any[] } {
  const lines = text.split(/\r?\n/).map(l => l.trim()).filter(l => l.length > 0 && !l.startsWith('#'));
  if (lines.length === 0) return { data: [], inputs: [] };
  const header = lines[0].split(',').map(h => h.trim());
  const rows = lines.slice(1);
  const data: StudentData[] = [];
  const inputs: any[] = [];
  
  rows.forEach((row, idx) => {
    const cols = row.split(',').map(c => c.trim());
    const obj: any = { id: idx + 1 };
    header.forEach((h, i) => {
      const key = h;
      const raw = cols[i] ?? '';
      const num = raw === '' ? null : Number(raw);
      obj[key] = num;
    });
    // Remove expected_category if present
    if ('expected_category' in obj) delete obj.expected_category;
    const studentData = Object.keys(obj).reduce((acc: any, k) => {
      if (k !== 'id') acc[k] = obj[k];
      return acc;
    }, {}) as StudentData;
    data.push(studentData);
    inputs.push(obj);
  });
  
  return { data, inputs };
}

export default function BatchForm() {
  const [fileText, setFileText] = useState<string>('');
  const [preview, setPreview] = useState<any[] | null>(null);
  const [inputs, setInputs] = useState<any[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const onFile = (f: File | null) => {
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => {
      const text = String(reader.result ?? '');
      setFileText(text);
      const { data, inputs: inp } = parseCsv(text);
      setPreview(data.slice(0, 10));
      setInputs(inp.slice(0, 10));
    };
    reader.readAsText(f);
  };

  const handleSubmit = async () => {
    setError(null);
    setResult(null);
    setCurrentPage(1);
    setUploadProgress(null);
    if (!fileText) return setError('No file loaded');
    const { data } = parseCsv(fileText);
    if (data.length === 0) return setError('No valid rows found in CSV');

    // Chunking parameters
    const CHUNK_SIZE = 100;
    const totalRows = data.length;
    const totalChunks = Math.ceil(totalRows / CHUNK_SIZE);

    setLoading(true);
    try {
      const aggregatedPreds: any[] = [];
      const aggregatedSummary: Record<string, number> = { 'At-Risk': 0, 'Medium': 0, 'High': 0 };

      for (let c = 0; c < totalChunks; c++) {
        const start = c * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, totalRows);
        const chunk = data.slice(start, end);

        setUploadProgress(`Processing rows ${start + 1}–${end} of ${totalRows} (chunk ${c + 1}/${totalChunks})`);

        const resp = await predictBatch(chunk);

        // Append predictions
        aggregatedPreds.push(...resp.predictions);

        // Merge summary counts
        aggregatedSummary['At-Risk'] = (aggregatedSummary['At-Risk'] ?? 0) + (resp.summary['At-Risk'] ?? 0);
        aggregatedSummary['Medium'] = (aggregatedSummary['Medium'] ?? 0) + (resp.summary['Medium'] ?? 0);
        aggregatedSummary['High'] = (aggregatedSummary['High'] ?? 0) + (resp.summary['High'] ?? 0);
      }

      setResult({ predictions: aggregatedPreds, total_students: aggregatedPreds.length, summary: aggregatedSummary });
      setUploadProgress(null);
    } catch (err: any) {
      setError(err?.message ?? 'Batch prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const getPaginatedResults = () => {
    if (!result) return { preds: [], total: 0 };
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return { preds: result.predictions.slice(start, end), total: result.predictions.length };
  };

  const { preds, total } = getPaginatedResults();
  const totalPages = Math.ceil(total / itemsPerPage);

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>Upload CSV (header required)</label>
        <input type="file" accept=".csv" onChange={(e) => onFile(e.target.files?.[0] ?? null)} />
      </div>

      {preview && (
        <div style={{ marginBottom: 16 }}>
          <h4>Preview (first 10 rows)</h4>
          <div style={{ maxHeight: 160, overflow: 'auto', border: '1px solid #e0e0e0', padding: 8 }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr>
                  {inputs && inputs[0] && Object.keys(inputs[0]).map(k => (
                    <th key={k} style={{ textAlign: 'left', padding: 4, borderBottom: '1px solid #eee', fontWeight: 600 }}>{k}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.map((_, i) => (
                  <tr key={i}>
                    {inputs && inputs[i] && Object.keys(inputs[i]).map(k => (
                      <td key={k} style={{ padding: 4, borderBottom: '1px solid #f6f6f6' }}>{String((inputs[i] as any)[k])}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
        <button className="submit-button" onClick={handleSubmit} disabled={loading}>{loading ? 'Running...' : 'Run Batch'}</button>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="result-container">
          <div style={{ marginBottom: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
            <h4 style={{ marginTop: 0 }}>Summary</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 12 }}>
              <div><strong>Total:</strong> {result.total_students}</div>
              <div><strong>At-Risk:</strong> {result.summary['At-Risk'] ?? 0}</div>
              <div><strong>Medium:</strong> {result.summary['Medium'] ?? 0}</div>
              <div><strong>High:</strong> {result.summary['High'] ?? 0}</div>
            </div>
          </div>

          <h4>Predictions ({total} total)</h4>
          {preds.map((p: any, i: number) => {
            const studentId = (currentPage - 1) * itemsPerPage + i + 1;
            return (
              <div key={i} style={{ padding: 12, marginBottom: 12, border: '1px solid #e0e0e0', borderRadius: 4, background: '#fafafa' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                  <div>
                    <strong style={{ fontSize: '1.1rem' }}>Student #{studentId}</strong>
                  </div>
                  <div style={{ color: p.prediction === 0 ? '#d32f2f' : p.prediction === 1 ? '#f57c00' : '#388e3c' }}>
                    <strong>{p.prediction_label}</strong> — {(p.confidence * 100).toFixed(1)}%
                  </div>
                </div>
                <div style={{ marginTop: 8, marginBottom: 8, fontSize: '0.9rem', color: '#666' }}>
                  <strong>Probabilities:</strong> At-Risk: {(p.probabilities['At-Risk'] * 100).toFixed(1)}%, Medium: {(p.probabilities['Medium'] * 100).toFixed(1)}%, High: {(p.probabilities['High'] * 100).toFixed(1)}%
                </div>
                <div style={{ fontSize: '0.85rem', lineHeight: 1.5, color: '#555' }}>
                  <strong>Actions:</strong> {p.recommended_actions.join(' • ')}
                </div>
              </div>
            );
          })}

          {totalPages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 8, marginTop: 16 }}>
              <button
                className="submit-button"
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                style={{ padding: '0.5rem 0.6rem', fontSize: '0.9rem', minWidth: '96px', width: '120px' }}
              >
                ← Previous
              </button>
              <span style={{ fontSize: '0.9rem' }}>Page {currentPage} of {totalPages}</span>
              <button
                className="submit-button"
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                style={{ padding: '0.5rem 0.6rem', fontSize: '0.9rem', minWidth: '96px', width: '120px' }}
              >
                Next →
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
