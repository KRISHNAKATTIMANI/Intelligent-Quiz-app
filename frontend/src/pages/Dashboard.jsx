import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { dashboardAPI } from '../services/api';
import { Trophy, Target, TrendingUp, BookOpen, LogOut, Upload, Home, Menu, X, Sun, Moon, User, Search, ArrowRight } from 'lucide-react';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const { darkMode, toggleDarkMode } = useTheme();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [logoutMessage, setLogoutMessage] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResponse, setSearchResponse] = useState('');
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const token = localStorage.getItem('token');
      console.log('Dashboard - Token exists:', !!token);
      if (token) {
        console.log('Token preview:', token.substring(0, 20) + '...');
      }
      const response = await dashboardAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      console.error('Error response:', error.response);
      console.error('Error data:', error.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const handleAISearch = async () => {
    if (!searchQuery.trim()) return;
    
    setSearching(true);
    setSearchResponse('');
    
    try {
      const response = await fetch('http://127.0.0.1:5000/api/ai/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ query: searchQuery })
      });
      
      const data = await response.json();
      if (response.ok) {
        setSearchResponse(data.response);
      } else {
        setSearchResponse('Sorry, I could not process your request. Please try again.');
      }
    } catch (error) {
      console.error('AI Search error:', error);
      setSearchResponse('Error connecting to AI service. Please try again later.');
    } finally {
      setSearching(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAISearch();
    }
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} flex transition-colors duration-300`}>
      {/* Left Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-gray-900 text-white min-h-screen flex flex-col transition-all duration-300 overflow-hidden`}>
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center">
              <BookOpen className="w-6 h-6" />
            </div>
            <div>
              <h2 className="font-semibold whitespace-nowrap">Quiz App</h2>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4">
          <Link
            to="/profile"
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors mb-2"
          >
            <User className="w-5 h-5 flex-shrink-0" />
            <span className="whitespace-nowrap">Profile</span>
          </Link>

          <Link
            to="/categories"
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors mb-2"
          >
            <Search className="w-5 h-5 flex-shrink-0" />
            <span className="whitespace-nowrap">Search chats</span>
          </Link>

          <Link
            to="/upload"
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors mb-2"
          >
            <Upload className="w-5 h-5 flex-shrink-0" />
            <span className="whitespace-nowrap">Library</span>
          </Link>

          <Link
            to="/categories"
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors"
          >
            <ArrowRight className="w-5 h-5 flex-shrink-0" />
            <span className="whitespace-nowrap">Projects</span>
          </Link>
        </nav>

        <div className="p-4 border-t border-gray-700">
          <button
            onClick={() => {
              setLogoutMessage('Logged out successfully! Redirecting...');
              setTimeout(() => {
                logout();
                navigate('/login');
              }, 1500);
            }}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors"
          >
            <LogOut className="w-5 h-5 flex-shrink-0" />
            <span className="whitespace-nowrap">Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1">
        {/* Logout Success Message */}
        {logoutMessage && (
          <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 bg-green-50 border border-green-200 text-green-700 px-6 py-3 rounded-lg shadow-lg">
            {logoutMessage}
          </div>
        )}

        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                  aria-label="Toggle sidebar"
                >
                  {sidebarOpen ? (
                    <X className="w-6 h-6 text-gray-600" />
                  ) : (
                    <Menu className="w-6 h-6 text-gray-600" />
                  )}
                </button>
              </div>
              <h1 className="absolute left-1/2 transform -translate-x-1/2 text-4xl font-black text-gray-900" style={{ 
                fontFamily: 'Georgia, serif',
                textShadow: '3px 3px 0px #d4a574, -1px -1px 0px #d4a574, 1px -1px 0px #d4a574, -1px 1px 0px #d4a574, 1px 1px 0px #d4a574, 4px 4px 8px rgba(0,0,0,0.3)',
                letterSpacing: '0.05em',
                WebkitTextStroke: '1px #d4a574',
                color: '#1a1a1a'
              }}>
                QUIZ APP
              </h1>
              <div className="flex items-center gap-3">
                <button
                  onClick={toggleDarkMode}
                  className="p-2 rounded-full hover:bg-gray-100 transition-colors"
                  aria-label="Toggle dark mode"
                >
                  {darkMode ? (
                    <Sun className="w-6 h-6 text-yellow-500" />
                  ) : (
                    <Moon className="w-6 h-6 text-gray-600" />
                  )}
                </button>
                <span className="text-sm text-gray-600">Welcome, {user?.full_name}</span>
              </div>
            </div>
          </div>
        </header>

        <div className="px-4 py-8 sm:px-6 lg:px-8">
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className={`card ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Total Quizzes</p>
                  <p className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>{stats?.total_quizzes || 0}</p>
                </div>
                <Target className="w-8 h-8 text-primary-600" />
              </div>
            </div>

            <div className={`card ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Average Score</p>
                  <p className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>{stats?.average_score || 0}%</p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-600" />
              </div>
            </div>

            <div className={`card ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Current Streak</p>
                  <p className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>{stats?.current_streak || 0}</p>
                </div>
                <Trophy className="w-8 h-8 text-yellow-600" />
              </div>
            </div>

            <div className={`card ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Time Spent</p>
                  <p className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>{stats?.total_time || 0}h</p>
                </div>
                <BookOpen className="w-8 h-8 text-blue-600" />
              </div>
            </div>
          </div>

          {/* AI Search and Take Quiz */}
          <div className={`flex flex-col items-center justify-center min-h-[400px] ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} px-4`}>
            <h2 className={`text-2xl font-semibold ${darkMode ? 'text-white' : 'text-gray-900'} mb-4`}>Ready to test your knowledge?</h2>
            
            {/* Take Quiz Button - Prominent */}
            <Link 
              to="/quiz-section"
              className="mb-8 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold text-lg rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center gap-3"
            >
              <Trophy className="w-6 h-6" />
              Take Quiz Now
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
              </svg>
            </Link>

            {/* AI Search Bar */}
            <div className="w-full max-w-3xl">
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-3 text-center`}>Or ask me anything about your subjects</p>
              <div className="flex items-center gap-3 bg-gray-700 rounded-full p-3">
                <button className="flex items-center justify-center w-10 h-10 bg-gray-600 hover:bg-gray-500 rounded-full transition-colors">
                  <span className="text-white text-xl">+</span>
                </button>
                <input
                  type="text"
                  placeholder="Ask anything about your subjects..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={searching}
                  className="flex-1 bg-transparent border-none outline-none text-white placeholder-gray-400 px-4"
                />
                <button className="flex items-center justify-center w-10 h-10 hover:bg-gray-600 rounded-full transition-colors">
                  <svg className="w-5 h-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z"></path>
                  </svg>
                </button>
                <button 
                  onClick={handleAISearch}
                  disabled={searching || !searchQuery.trim()}
                  className="flex items-center justify-center w-10 h-10 bg-white rounded-full hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {searching ? (
                    <svg className="animate-spin w-5 h-5 text-gray-800" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : (
                    <svg className="w-5 h-5 text-gray-800" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
                    </svg>
                  )}
                </button>
              </div>

              {/* AI Response */}
              {searchResponse && (
                <div className={`mt-6 p-6 rounded-xl ${darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'} shadow-lg`}>
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center flex-shrink-0">
                      <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z"/>
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold mb-2">AI Assistant Response:</h3>
                      <p className={`text-sm leading-relaxed ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                        {searchResponse}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
