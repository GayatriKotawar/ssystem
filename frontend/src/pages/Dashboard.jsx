import { useState, useEffect } from 'react';
import { FileText, DollarSign, AlertCircle, Calendar } from 'lucide-react';
import api from '../api';

export default function Dashboard({ user }) {
  const [documents, setDocuments] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [docsRes, alertsRes] = await Promise.all([
          api.get(`/documents/${user.id}`),
          api.get(`/alerts/${user.id}`)
        ]);
        setDocuments(docsRes.data.documents);
        setAlerts(alertsRes.data.alerts);
      } catch (err) {
        console.error("Failed to fetch dashboard data", err);
      } finally {
        setLoading(false);
      }
    };
    
    if (user?.id) fetchDashboardData();
  }, [user.id]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  // Calculate Metrics
  const totalDocs = documents.length;
  const totalExpenses = documents.reduce((acc, doc) => {
    try {
      const data = JSON.parse(doc.extracted_data);
      const amtStr = String(data.amount || '0').replace(/[,₹$]/g, '').trim();
      const num = parseFloat(amtStr);
      return acc + (isNaN(num) ? 0 : num);
    } catch { return acc; }
  }, 0);
  
  const expiringCount = alerts.filter(a => a.message.toLowerCase().includes('expir')).length;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Welcome back, {user.name}. Here's what's happening today.</p>
      </div>

      {alerts.length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <AlertCircle className="w-5 h-5 mr-2 text-orange-500" /> Action Required
          </h2>
          <div className="space-y-3">
            {alerts.map((alert, idx) => (
              <div key={idx} className={`p-4 rounded-xl flex items-start ${alert.type === 'error' ? 'bg-red-50 text-red-800' : 'bg-orange-50 text-orange-800'}`}>
                <span className="text-xl mr-3">{alert.type === 'error' ? '🚨' : '⚠️'}</span>
                <div>
                  <p className="font-medium">{alert.message}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Total Documents</p>
            <p className="text-2xl font-bold text-gray-900">{totalDocs}</p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-green-50 text-green-600 rounded-xl">
            <DollarSign className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Tracked Expenses</p>
            <p className="text-2xl font-bold text-gray-900">₹{totalExpenses.toLocaleString()}</p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-orange-50 text-orange-600 rounded-xl">
            <Calendar className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Upcoming Expiries</p>
            <p className="text-2xl font-bold text-gray-900">{expiringCount}</p>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">Recently Uploaded</h3>
        </div>
        <div className="divide-y divide-gray-100">
          {documents.slice(0, 5).map(doc => (
            <div key={doc.id} className="p-6 flex items-center justify-between hover:bg-gray-50 transition-colors">
              <div className="flex items-center space-x-4">
                <div className="p-2 bg-gray-100 rounded-lg text-gray-500">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{doc.file_name}</p>
                  <p className="text-xs text-gray-500">{new Date(doc.upload_date).toLocaleDateString()}</p>
                </div>
              </div>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700">
                {doc.document_category}
              </span>
            </div>
          ))}
          {documents.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              No documents yet. Go to Upload Document to get started.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
