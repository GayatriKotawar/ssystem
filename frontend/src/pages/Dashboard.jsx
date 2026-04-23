import { useState, useEffect, useCallback } from 'react';
import { FileText, DollarSign, AlertCircle, Calendar, Filter, Tag, RefreshCw } from 'lucide-react';
import api from '../api';

// Category colour map
const CAT_STYLES = {
  Medical:   { bg: 'bg-red-50',     text: 'text-red-700',     dot: 'bg-red-400',     icon: '🏥' },
  Bills:     { bg: 'bg-yellow-50',  text: 'text-yellow-700',  dot: 'bg-yellow-400',  icon: '⚡' },
  Insurance: { bg: 'bg-blue-50',    text: 'text-blue-700',    dot: 'bg-blue-400',    icon: '🛡️' },
  Banking:   { bg: 'bg-green-50',   text: 'text-green-700',   dot: 'bg-green-400',   icon: '🏦' },
  Education: { bg: 'bg-purple-50',  text: 'text-purple-700',  dot: 'bg-purple-400',  icon: '🎓' },
  Legal:     { bg: 'bg-orange-50',  text: 'text-orange-700',  dot: 'bg-orange-400',  icon: '⚖️' },
  Receipts:  { bg: 'bg-teal-50',    text: 'text-teal-700',    dot: 'bg-teal-400',    icon: '🧾' },
  Others:    { bg: 'bg-gray-100',   text: 'text-gray-600',    dot: 'bg-gray-400',    icon: '📄' },
};

function CategoryBadge({ category }) {
  const style = CAT_STYLES[category] || CAT_STYLES.Others;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${style.bg} ${style.text}`}>
      <span>{style.icon}</span>
      {category}
    </span>
  );
}

const ALL_CATEGORIES = ['All', ...Object.keys(CAT_STYLES)];

export default function Dashboard({ user }) {
  const [documents, setDocuments] = useState([]);
  const [alerts, setAlerts]       = useState([]);
  const [loading, setLoading]     = useState(true);
  const [filter, setFilter]       = useState('All');
  const [fixing, setFixing]       = useState(false);
  const [fixMsg, setFixMsg]       = useState('');

  const fetchDashboardData = useCallback(async () => {
    try {
      const [docsRes, alertsRes] = await Promise.all([
        api.get(`/documents/${user.id}`),
        api.get(`/alerts/${user.id}`),
      ]);
      setDocuments(docsRes.data.documents);
      setAlerts(alertsRes.data.alerts);
    } catch (err) {
      console.error('Failed to fetch dashboard data', err);
    } finally {
      setLoading(false);
    }
  }, [user.id]);

  useEffect(() => {
    if (user?.id) fetchDashboardData();
  }, [fetchDashboardData]);

  const handleFixCategories = async () => {
    setFixing(true);
    setFixMsg('');
    try {
      const res = await api.post(`/recategorize/${user.id}`);
      setFixMsg(res.data.message);
      await fetchDashboardData(); // refresh the list
    } catch (e) {
      setFixMsg('Re-categorization failed.');
    } finally {
      setFixing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
      </div>
    );
  }

  // ── Metrics ────────────────────────────────────────────────────────────
  const totalDocs = documents.length;

  const totalExpenses = documents.reduce((acc, doc) => {
    try {
      const data = typeof doc.extracted_data === 'string'
        ? JSON.parse(doc.extracted_data)
        : doc.extracted_data;
      const amtStr = String(data?.amount || '0').replace(/[,₹$\s]/g, '');
      const num = parseFloat(amtStr);
      return acc + (isNaN(num) ? 0 : num);
    } catch { return acc; }
  }, 0);

  const expiringCount = alerts.filter(a =>
    a.message?.toLowerCase().includes('expir')
  ).length;

  // ── Category breakdown ─────────────────────────────────────────────────
  const catCounts = documents.reduce((acc, doc) => {
    const cat = doc.document_category || 'Others';
    acc[cat] = (acc[cat] || 0) + 1;
    return acc;
  }, {});

  // ── Filtered list ──────────────────────────────────────────────────────
  const filtered = filter === 'All'
    ? documents
    : documents.filter(d => (d.document_category || 'Others') === filter);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Welcome back, {user.name}. Here's what's happening today.
          </p>
        </div>
        {/* Fix Categories button — shown when any doc is 'Others' */}
        {documents.some(d => (d.document_category || 'Others') === 'Others') && (
          <div className="flex flex-col items-end gap-1">
            <button
              onClick={handleFixCategories}
              disabled={fixing}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-xl shadow hover:bg-indigo-700 disabled:opacity-60 transition-all"
            >
              <RefreshCw className={`w-4 h-4 ${fixing ? 'animate-spin' : ''}`} />
              {fixing ? 'Fixing…' : 'Fix Categories'}
            </button>
            {fixMsg && <p className="text-xs text-green-700 font-medium">{fixMsg}</p>}
          </div>
        )}
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-orange-500" /> Action Required
          </h2>
          <div className="space-y-3">
            {alerts.map((alert, idx) => (
              <div key={idx} className={`p-4 rounded-xl flex items-start gap-3 ${alert.type === 'error' ? 'bg-red-50 text-red-800' : 'bg-orange-50 text-orange-800'}`}>
                <span className="text-xl">{alert.type === 'error' ? '🚨' : '⚠️'}</span>
                <p className="font-medium text-sm">{alert.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Total Documents</p>
            <p className="text-2xl font-bold text-gray-900">{totalDocs}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-green-50 text-green-600 rounded-xl">
            <DollarSign className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Tracked Expenses</p>
            <p className="text-2xl font-bold text-gray-900">₹{totalExpenses.toLocaleString()}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-orange-50 text-orange-600 rounded-xl">
            <Calendar className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Upcoming Expiries</p>
            <p className="text-2xl font-bold text-gray-900">{expiringCount}</p>
          </div>
        </div>
      </div>

      {/* Category Breakdown */}
      {totalDocs > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Tag className="w-4 h-4 text-indigo-500" /> Documents by Category
          </h2>
          <div className="flex flex-wrap gap-3">
            {Object.entries(catCounts).map(([cat, count]) => {
              const style = CAT_STYLES[cat] || CAT_STYLES.Others;
              return (
                <button
                  key={cat}
                  onClick={() => setFilter(filter === cat ? 'All' : cat)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl border-2 transition-all text-sm font-semibold
                    ${filter === cat
                      ? `${style.bg} ${style.text} border-current`
                      : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
                    }`}
                >
                  <span className={`w-2 h-2 rounded-full ${style.dot}`} />
                  {style.icon} {cat}
                  <span className={`ml-1 px-1.5 py-0.5 rounded-full text-xs ${style.bg} ${style.text}`}>
                    {count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Document List */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-100 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            {filter === 'All' ? 'All Documents' : `${filter} Documents`}
            <span className="ml-2 text-sm font-normal text-gray-400">({filtered.length})</span>
          </h3>
          {filter !== 'All' && (
            <button
              onClick={() => setFilter('All')}
              className="text-xs text-indigo-600 hover:underline font-medium"
            >
              Clear filter
            </button>
          )}
        </div>

        <div className="divide-y divide-gray-50">
          {filtered.slice(0, 10).map(doc => {
            const cat = doc.document_category || 'Others';
            const style = CAT_STYLES[cat] || CAT_STYLES.Others;
            let extractedData = {};
            try {
              extractedData = typeof doc.extracted_data === 'string'
                ? JSON.parse(doc.extracted_data)
                : (doc.extracted_data || {});
            } catch {}

            const summary = extractedData.summary || extractedData.plain_language || '';
            const name = extractedData.name || '';
            const amount = extractedData.amount || '';

            return (
              <div key={doc.id} className="px-6 py-4 flex items-start justify-between gap-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start gap-4 min-w-0">
                  <div className={`mt-0.5 p-2 ${style.bg} rounded-lg flex-shrink-0 text-base`}>
                    {style.icon}
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-gray-900 truncate">{doc.file_name}</p>
                    {summary && (
                      <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{summary}</p>
                    )}
                    <div className="flex items-center gap-3 mt-1">
                      <p className="text-xs text-gray-400">
                        {new Date(doc.upload_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                      </p>
                      {name && <p className="text-xs text-gray-400">👤 {name}</p>}
                      {amount && <p className="text-xs font-medium text-green-700">₹{amount}</p>}
                    </div>
                  </div>
                </div>
                <div className="flex-shrink-0">
                  <CategoryBadge category={cat} />
                </div>
              </div>
            );
          })}

          {filtered.length === 0 && (
            <div className="p-10 text-center text-gray-400">
              <FileText className="w-10 h-10 mx-auto mb-3 opacity-30" />
              <p className="text-sm font-medium">
                {filter === 'All'
                  ? 'No documents yet. Go to Upload Document to get started.'
                  : `No ${filter} documents found.`}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
