import { useState, useRef, useCallback } from 'react';
import { Upload as UploadIcon, File, CheckCircle, AlertCircle, Loader, Zap, Brain, Database, Clock } from 'lucide-react';
import api, { getApiErrorMessage } from '../api';

// Processing steps shown to the user while waiting
const STEPS = [
  { icon: UploadIcon, label: 'Uploading document…',      duration: 1500 },
  { icon: Zap,        label: 'Reading document content…', duration: 2500 },
  { icon: Brain,      label: 'Gemini AI extracting data…', duration: 0 },   // stays until response
  { icon: Database,   label: 'Saving to your vault…',    duration: 1000 },
];

export default function Upload({ user }) {
  const [file, setFile]       = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [stepIdx, setStepIdx] = useState(0);
  const [result, setResult]   = useState(null);
  const [error, setError]     = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);
  const stepTimer    = useRef(null);

  const pickFile = (selected) => {
    if (!selected) return;
    // Validate size ≤ 10 MB
    if (selected.size > 10 * 1024 * 1024) {
      setError('File is too large. Please upload a file under 10 MB.');
      return;
    }
    setFile(selected);
    setPreview(selected.type.startsWith('image/') ? URL.createObjectURL(selected) : null);
    setResult(null);
    setError(null);
  };

  const handleFileChange = (e) => pickFile(e.target.files[0]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    pickFile(e.dataTransfer.files[0]);
  }, []);

  const advanceStep = (idx) => {
    setStepIdx(idx);
    if (STEPS[idx].duration > 0 && idx + 1 < STEPS.length - 1) {
      stepTimer.current = setTimeout(() => advanceStep(idx + 1), STEPS[idx].duration);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    advanceStep(0);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', user.id);

    try {
      // Step 2 will fire during the wait via timeout above
      setTimeout(() => setStepIdx(2), STEPS[0].duration + STEPS[1].duration);

      const response = await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120_000,   // 2-minute max timeout
      });

      clearTimeout(stepTimer.current);
      setStepIdx(3);
      setTimeout(() => {
        setResult(response.data);
        setLoading(false);
      }, 800);
    } catch (err) {
      clearTimeout(stepTimer.current);
      setError(getApiErrorMessage(err, 'Failed to process the document.'));
      setLoading(false);
    }
  };

  const currentStep = STEPS[stepIdx];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload Document</h1>
        <p className="mt-2 text-gray-600">
          Drop your receipts, invoices, IDs, or medical bills. Gemini AI will extract and categorize them automatically.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* ── Left: Dropzone + button ───────────────────────────── */}
        <div className="space-y-4">
          <div
            onClick={() => !loading && fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            className={`
              border-2 border-dashed rounded-2xl p-10 text-center transition-all cursor-pointer
              flex flex-col items-center justify-center min-h-[280px]
              ${dragOver
                ? 'border-indigo-500 bg-indigo-50 scale-[1.01]'
                : 'border-gray-300 bg-white hover:bg-gray-50 hover:border-indigo-400'}
              ${loading ? 'pointer-events-none opacity-60' : ''}
            `}
          >
            <input
              type="file"
              className="hidden"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".jpg,.jpeg,.png,.webp,.pdf"
            />

            {preview ? (
              <img src={preview} alt="Preview" className="max-h-56 rounded-lg object-contain" />
            ) : file ? (
              <div className="flex flex-col items-center text-indigo-600">
                <File className="w-14 h-14 mb-3" />
                <span className="font-semibold text-sm text-center break-all px-2">{file.name}</span>
                <span className="text-xs text-gray-400 mt-1">{(file.size / 1024).toFixed(1)} KB</span>
              </div>
            ) : (
              <div className="flex flex-col items-center text-gray-500">
                <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mb-4">
                  <UploadIcon className="w-8 h-8" />
                </div>
                <p className="font-semibold text-gray-900 text-lg mb-1">Click or drag & drop</p>
                <p className="text-sm">JPG, PNG, WEBP, or PDF — max 10 MB</p>
              </div>
            )}
          </div>

          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="w-full py-4 bg-indigo-600 text-white rounded-xl font-semibold shadow-md hover:bg-indigo-700 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-3"
          >
            {loading ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                {currentStep.label}
              </>
            ) : (
              <>
                <Brain className="w-5 h-5" />
                Process Document
              </>
            )}
          </button>

          {/* ── Progress steps ─────────────────────────────────── */}
          {loading && (
            <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm space-y-3">
              <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Processing</p>
              {STEPS.map((step, i) => {
                const Icon = step.icon;
                const done    = i < stepIdx;
                const active  = i === stepIdx;
                return (
                  <div key={i} className={`flex items-center gap-3 transition-all duration-300 ${done ? 'opacity-40' : active ? 'opacity-100' : 'opacity-25'}`}>
                    <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 transition-colors ${done ? 'bg-green-100 text-green-600' : active ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-400'}`}>
                      {done
                        ? <CheckCircle className="w-4 h-4" />
                        : active
                          ? <Loader className="w-4 h-4 animate-spin" />
                          : <Icon className="w-4 h-4" />
                      }
                    </div>
                    <span className={`text-sm font-medium ${active ? 'text-gray-900' : 'text-gray-500'}`}>
                      {step.label}
                    </span>
                  </div>
                );
              })}
              <p className="text-xs text-gray-400 flex items-center gap-1 pt-1">
                <Clock className="w-3 h-3" /> AI processing typically takes 5–15 seconds
              </p>
            </div>
          )}
        </div>

        {/* ── Right: Results / Errors ───────────────────────────── */}
        <div>
          {error && (
            <div className="p-4 bg-red-50 text-red-700 rounded-xl flex items-start gap-3 mb-6 border border-red-100">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          {result && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden animate-fade-in">
              <div className="bg-gradient-to-r from-emerald-50 to-teal-50 px-6 py-4 border-b border-emerald-100 flex items-center justify-between">
                <h3 className="font-bold text-emerald-900 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-emerald-600" />
                  Extraction Complete
                </h3>
                <span className="px-3 py-1 bg-white text-emerald-700 text-xs font-bold rounded-full shadow-sm border border-emerald-100">
                  {result.category}
                </span>
              </div>

              {/* Summary callout */}
              {result.summary && (
                <div className="px-6 pt-4 pb-2">
                  <p className="text-sm text-gray-600 italic bg-gray-50 rounded-xl p-3 border border-gray-100">
                    "{result.summary}"
                  </p>
                </div>
              )}

              <div className="p-6">
                <dl className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  {Object.entries(result).map(([key, value]) => {
                    if (
                      !value ||
                      key === 'category' ||
                      key === 'summary' ||
                      key === 'error' ||
                      (typeof value === 'object' && Object.keys(value).length === 0) ||
                      (Array.isArray(value) && value.length === 0)
                    ) return null;

                    const displayKey = key
                      .split('_')
                      .map(w => w.charAt(0).toUpperCase() + w.slice(1))
                      .join(' ');

                    const isComplex = typeof value === 'object';

                    return (
                      <div
                        key={key}
                        className={`rounded-xl p-3 bg-gray-50 border border-gray-100 ${isComplex ? 'sm:col-span-2' : ''}`}
                      >
                        <dt className="text-xs font-bold text-indigo-500 uppercase tracking-widest mb-1.5">
                          {displayKey}
                        </dt>
                        {isComplex ? (
                          <pre className="text-sm text-gray-800 whitespace-pre-wrap font-sans">
                            {JSON.stringify(value, null, 2)}
                          </pre>
                        ) : (
                          <dd className="text-sm font-semibold text-gray-900">{String(value)}</dd>
                        )}
                      </div>
                    );
                  })}
                </dl>
              </div>
            </div>
          )}

          {!result && !error && !loading && (
            <div className="h-full flex flex-col items-center justify-center text-gray-400 py-16">
              <Brain className="w-12 h-12 mb-4 opacity-30" />
              <p className="text-sm font-medium">Results will appear here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
