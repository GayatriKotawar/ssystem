import { useState, useRef } from 'react';
import { Upload as UploadIcon, File, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import api from '../api';

export default function Upload({ user }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      if (selected.type.startsWith('image/')) {
        setPreview(URL.createObjectURL(selected));
      } else {
        setPreview(null);
      }
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', user.id);

    try {
      const response = await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process document');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload Document</h1>
        <p className="mt-2 text-gray-600">Drag and drop your receipts, invoices, IDs, or medical bills. Gemini 2.5 Flash will automatically extract and categorize them.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div 
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 rounded-2xl p-12 text-center hover:bg-gray-50 hover:border-indigo-400 transition-all cursor-pointer bg-white shadow-sm flex flex-col items-center justify-center min-h-[300px]"
          >
            <input 
              type="file" 
              className="hidden" 
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".jpg,.jpeg,.png,.pdf"
            />
            
            {preview ? (
              <img src={preview} alt="Preview" className="max-h-64 rounded-lg object-contain" />
            ) : file ? (
              <div className="flex flex-col items-center text-indigo-600">
                <File className="w-16 h-16 mb-4" />
                <span className="font-medium">{file.name}</span>
              </div>
            ) : (
              <div className="flex flex-col items-center text-gray-500">
                <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mb-4">
                  <UploadIcon className="w-8 h-8" />
                </div>
                <p className="font-semibold text-gray-900 text-lg mb-1">Click to upload</p>
                <p className="text-sm">JPG, PNG, or PDF</p>
              </div>
            )}
          </div>

          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="w-full py-4 bg-indigo-600 text-white rounded-xl font-medium shadow-md hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center"
          >
            {loading ? (
              <>
                <Loader className="w-5 h-5 mr-3 animate-spin" />
                Analyzing with Gemini 2.5...
              </>
            ) : 'Process Document'}
          </button>
        </div>

        <div>
          {error && (
            <div className="p-4 bg-red-50 text-red-700 rounded-xl flex items-start space-x-3 mb-6">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <p>{error}</p>
            </div>
          )}

          {result && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden transform opacity-100 transition-all animate-fade-in-up">
              <div className="bg-gradient-to-r from-emerald-50 to-teal-50 px-6 py-4 border-b border-emerald-100 flex items-center justify-between">
                <h3 className="font-bold text-emerald-900 flex items-center">
                  <CheckCircle className="w-5 h-5 mr-2 text-emerald-600" />
                  Extraction Success
                </h3>
                <span className="px-3 py-1 bg-white text-emerald-700 text-xs font-bold rounded-full shadow-sm border border-emerald-100">
                  {result.category}
                </span>
              </div>
              <div className="p-6">
                <dl className="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
                  {Object.entries(result).map(([key, value]) => {
                    if (
                      !value || 
                      key === 'category' ||
                      (typeof value === 'object' && Object.keys(value).length === 0) ||
                      (Array.isArray(value) && value.length === 0)
                    ) return null;
                    
                    // Format key nicely
                    const displayKey = key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                    
                    // Format value nicely if it's an object/array
                    let displayValue = value;
                    if (typeof value === 'object') {
                      displayValue = JSON.stringify(value, null, 2);
                    }
                    
                    return (
                      <div key={key} className={`border border-gray-50 rounded-lg p-3 bg-gray-50 ${typeof value === 'object' ? 'sm:col-span-2' : 'sm:col-span-1'}`}>
                        <dt className="text-xs font-bold text-indigo-500 uppercase tracking-widest mb-1.5">
                          {displayKey}
                        </dt>
                        {typeof value === 'object' ? (
                          <pre className="text-sm font-medium text-gray-800 whitespace-pre-wrap font-sans">{displayValue}</pre>
                        ) : (
                          <dd className="text-sm font-semibold text-gray-900">{displayValue}</dd>
                        )}
                      </div>
                    );
                  })}
                </dl>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
