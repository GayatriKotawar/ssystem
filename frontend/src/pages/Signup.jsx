import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { FileText, ArrowRight, Mail, Lock, User, AlertTriangle, CheckCircle } from 'lucide-react';
import api, { getApiErrorMessage } from '../api';

const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
const backendConfigured = !isProduction || !!import.meta.env.VITE_API_BASE_URL;

export default function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    setLoading(true);
    setError('');

    try {
      await api.post('/auth/signup', { name, email, password });
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Registration failed. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex text-gray-900 bg-white">
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="flex justify-center text-indigo-600 mb-6">
              <FileText className="w-12 h-12" />
            </div>
            <h2 className="text-3xl font-extrabold tracking-tight">Create your account</h2>
            <p className="mt-2 text-sm text-gray-500">Start organizing your life automatically</p>
          </div>

          {/* Backend not configured warning — only shown on production without env var */}
          {!backendConfigured && (
            <div className="p-4 rounded-lg bg-amber-50 border border-amber-200 flex gap-3">
              <AlertTriangle className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-amber-800">
                <p className="font-semibold mb-1">Backend not connected</p>
                <p>The API backend is not configured for this Netlify site. To fix this:</p>
                <ol className="list-decimal list-inside mt-2 space-y-1">
                  <li>Deploy the backend to <strong>Render.com</strong> using <code className="bg-amber-100 px-1 rounded">render.yaml</code></li>
                  <li>Copy your Render service URL</li>
                  <li>In <strong>Netlify → Site settings → Environment variables</strong>, set:<br />
                    <code className="bg-amber-100 px-1 rounded text-xs">VITE_API_BASE_URL = https://your-app.onrender.com</code>
                  </li>
                  <li>Redeploy this Netlify site</li>
                </ol>
              </div>
            </div>
          )}

          {success ? (
            <div className="p-4 rounded-lg bg-green-50 border border-green-200 flex gap-3 items-center">
              <CheckCircle className="h-6 w-6 text-green-500 flex-shrink-0" />
              <div className="text-sm text-green-800">
                <p className="font-semibold">Account created successfully!</p>
                <p>Redirecting you to login…</p>
              </div>
            </div>
          ) : (
            <form className="mt-8 space-y-6" onSubmit={handleSignup}>
              {error && (
                <div className="p-3 rounded-lg bg-red-50 text-red-700 text-sm">{error}</div>
              )}

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                      <User className="h-5 w-5" />
                    </div>
                    <input
                      name="name"
                      type="text"
                      required
                      className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition-all outline-none"
                      placeholder="John Doe"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email address</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                      <Mail className="h-5 w-5" />
                    </div>
                    <input
                      name="email"
                      type="email"
                      required
                      className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition-all outline-none"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                      <Lock className="h-5 w-5" />
                    </div>
                    <input
                      name="password"
                      type="password"
                      required
                      minLength={6}
                      className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-600 focus:border-transparent transition-all outline-none"
                      placeholder="Min. 6 characters"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-xl text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all shadow-sm shadow-indigo-200 disabled:opacity-70"
              >
                {loading ? 'Creating account…' : 'Create account'}
                {!loading && <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />}
              </button>

              <p className="text-center text-sm text-gray-600 mt-4">
                Already have an account?{' '}
                <Link to="/login" className="font-semibold text-indigo-600 hover:text-indigo-500">
                  Sign in
                </Link>
              </p>
            </form>
          )}
        </div>
      </div>

      <div className="hidden lg:flex lg:flex-1 bg-indigo-50 items-center justify-center p-12">
        <div className="max-w-lg text-center">
          <img src="https://illustrations.popsy.co/amber/student-going-to-school.svg" alt="Launch" className="w-full max-w-md mx-auto mb-8 drop-shadow-xl" />
          <h3 className="text-2xl font-bold text-gray-900 mb-4">Secure &amp; Private</h3>
          <p className="text-gray-600 text-lg">Your documents are isolated and your passwords are bcrypt hashed. We value your privacy.</p>
        </div>
      </div>
    </div>
  );
}
