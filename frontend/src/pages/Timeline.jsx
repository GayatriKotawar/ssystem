import { useState, useEffect } from 'react';
import { Calendar, AlertCircle } from 'lucide-react';
import api from '../api';

export default function Timeline({ user }) {
  const [documents, setDocuments] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTimelineData = async () => {
      try {
        const [docsRes, alertsRes] = await Promise.all([
          api.get(`/documents/${user.id}`),
          api.get(`/alerts/${user.id}`)
        ]);
        setDocuments(docsRes.data.documents);
        setAlerts(alertsRes.data.alerts);
      } catch (err) {
        console.error("Failed to fetch timeline data", err);
      } finally {
        setLoading(false);
      }
    };
    
    if (user?.id) fetchTimelineData();
  }, [user.id]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  // Pre-process Data for Timeline
  const timelineEvents = [];
  
  documents.forEach(doc => {
    try {
      const data = JSON.parse(doc.extracted_data);
      let desc = [];
      if (data.expiry_date) desc.push(`Expires: ${data.expiry_date}`);
      if (data.due_date) desc.push(`Due: ${data.due_date}`);
      
      timelineEvents.push({
        id: doc.id,
        date: new Date(doc.upload_date).toLocaleDateString(),
        title: doc.file_name,
        category: doc.document_category,
        details: desc.length > 0 ? desc.join(' | ') : 'Processed'
      });
    } catch {
      // ignore JSON parse errors internally
    }
  });

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Life Timeline</h1>
        <p className="mt-2 text-gray-600">Track and respond to crucial dates recognized by Gemini AI.</p>
      </div>

      {alerts.length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-orange-100 p-6">
          <h2 className="text-lg font-semibold text-orange-900 mb-4 flex items-center">
            <AlertCircle className="w-5 h-5 mr-2" /> Attention Needed
          </h2>
          <div className="space-y-3">
            {alerts.map((alert, idx) => (
              <div key={idx} className={`p-4 rounded-xl text-sm font-medium border ${alert.type === 'error' ? 'bg-red-50 text-red-800 border-red-100' : 'bg-orange-50 text-orange-800 border-orange-100'}`}>
                {alert.message}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-8 flex items-center">
          <Calendar className="w-6 h-6 mr-3 text-indigo-600" />
          Document History
        </h3>
        
        <div className="relative border-l-2 border-indigo-100 ml-3 space-y-8 pb-4">
          {timelineEvents.map((event, idx) => (
            <div key={idx} className="relative pl-8">
              {/* Timeline Dot */}
              <div className="absolute w-4 h-4 bg-indigo-600 rounded-full -left-[9px] top-1.5 ring-4 ring-white"></div>
              
              <div className="bg-gray-50 rounded-xl p-5 border border-gray-100 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="text-lg font-bold text-gray-900">{event.title}</h4>
                  <span className="text-xs font-semibold text-indigo-600 uppercase tracking-wider">{event.date}</span>
                </div>
                
                <div className="flex items-center space-x-3 mb-3">
                  <span className="px-2.5 py-1 bg-white border border-gray-200 text-gray-700 text-xs font-medium rounded-full">
                    {event.category}
                  </span>
                </div>
                
                <p className="text-sm font-medium text-gray-500">{event.details}</p>
              </div>
            </div>
          ))}
          
          {timelineEvents.length === 0 && (
            <div className="pl-6 text-gray-500 italic">
              No timeline events available yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
