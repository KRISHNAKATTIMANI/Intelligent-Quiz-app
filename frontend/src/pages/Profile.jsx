import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { ArrowLeft, Camera, User, ChevronDown, ChevronUp } from 'lucide-react';

// Built-in avatar options
const BUILT_IN_AVATARS = [
  { id: 'male1', src: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix&backgroundColor=b6e3f4', label: 'Male 1' },
  { id: 'male2', src: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Aneka&backgroundColor=b6e3f4', label: 'Male 2' },
  { id: 'male3', src: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Max&backgroundColor=b6e3f4', label: 'Male 3' },
  { id: 'female1', src: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Lucy&backgroundColor=ffdfbf', label: 'Female 1' },
  { id: 'female2', src: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Bella&backgroundColor=ffdfbf', label: 'Female 2' },
  { id: 'female3', src: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sophie&backgroundColor=ffdfbf', label: 'Female 3' },
  { id: 'neutral1', src: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Charlie&backgroundColor=c0aede', label: 'Avatar 1' },
  { id: 'neutral2', src: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sam&backgroundColor=c0aede', label: 'Avatar 2' },
];

export default function Profile() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { darkMode } = useTheme();
  const [avatar, setAvatar] = useState(null);
  const [selectedBuiltIn, setSelectedBuiltIn] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showAvatarOptions, setShowAvatarOptions] = useState(false);

  useEffect(() => {
    // Load saved avatar from localStorage
    const savedAvatar = localStorage.getItem('userAvatar');
    if (savedAvatar) {
      setAvatar(savedAvatar);
      const builtIn = BUILT_IN_AVATARS.find(a => a.src === savedAvatar);
      if (builtIn) {
        setSelectedBuiltIn(builtIn.id);
      } else {
        setUploadedImage(savedAvatar);
      }
    }
  }, []);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file');
      return;
    }

    // Validate file size (1000KB = 1000 * 1024 bytes)
    if (file.size > 1000 * 1024) {
      setError('Image must be less than 1000KB (1MB)');
      return;
    }

    // Convert to base64
    const reader = new FileReader();
    reader.onload = (event) => {
      const imageData = event.target.result;
      setUploadedImage(imageData);
      setAvatar(imageData);
      setSelectedBuiltIn(null);
      setError('');
      setSuccess('Image uploaded successfully!');
      
      // Save to localStorage
      localStorage.setItem('userAvatar', imageData);
      
      setTimeout(() => setSuccess(''), 3000);
    };
    reader.readAsDataURL(file);
  };

  const handleBuiltInSelect = (builtInAvatar) => {
    setSelectedBuiltIn(builtInAvatar.id);
    setAvatar(builtInAvatar.src);
    setUploadedImage(null);
    setError('');
    setSuccess('Avatar selected successfully!');
    
    // Save to localStorage
    localStorage.setItem('userAvatar', builtInAvatar.src);
    
    setTimeout(() => setSuccess(''), 3000);
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <header className={`${darkMode ? 'bg-gray-800' : 'bg-white'} shadow-sm`}>
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className={`p-2 rounded-lg ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
            >
              <ArrowLeft className={`w-5 h-5 ${darkMode ? 'text-gray-300' : ''}`} />
            </button>
            <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Profile Settings</h1>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* User Info Card */}
        <div className={`card mb-6 ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <div className="flex items-center gap-6">
            <div className="relative">
              {avatar ? (
                <img
                  src={avatar}
                  alt="Avatar"
                  className="w-24 h-24 rounded-full object-cover border-4 border-primary-200"
                />
              ) : (
                <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center">
                  <User className="w-12 h-12 text-gray-400" />
                </div>
              )}
            </div>
            <div className="flex-1">
              <h2 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>{user?.full_name || 'User'}</h2>
              <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>{user?.username || 'username'}</p>
              <p className={`text-sm mt-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>{user?.email || 'email@example.com'}</p>
            </div>
          </div>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
            {success}
          </div>
        )}

        {/* Avatar Settings Toggle */}
        <div className={`card mb-6 ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <button
            onClick={() => setShowAvatarOptions(!showAvatarOptions)}
            className="w-full flex items-center justify-between text-left"
          >
            <div>
              <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Avatar Settings</h3>
              <p className={`text-sm mt-1 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                {showAvatarOptions ? 'Click to hide options' : 'Click to upload or choose an avatar'}
              </p>
            </div>
            {showAvatarOptions ? (
              <ChevronUp className={`w-6 h-6 ${darkMode ? 'text-gray-400' : 'text-gray-400'}`} />
            ) : (
              <ChevronDown className={`w-6 h-6 ${darkMode ? 'text-gray-400' : 'text-gray-400'}`} />
            )}
          </button>
        </div>

        {/* Avatar Options (Collapsible) */}
        {showAvatarOptions && (
          <>
            {/* Upload Custom Avatar */}
            <div className={`card mb-6 ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
              <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>Upload Custom Avatar</h3>
              <p className={`text-sm mb-4 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                Upload your own image (max 1MB, JPG/PNG/GIF)
              </p>
              
              <label className="block">
                <div className={`border-2 border-dashed rounded-lg p-6 text-center hover:border-primary-500 transition-colors cursor-pointer ${darkMode ? 'border-gray-600' : 'border-gray-300'}`}>
                  <input
                    type="file"
                    className="hidden"
                    accept="image/*"
                    onChange={handleFileUpload}
                  />
                  <Camera className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className={`font-medium mb-1 ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
                    Click to upload
                  </p>
                  <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                    Maximum size: 1MB
                  </p>
                </div>
              </label>

              {uploadedImage && (
                <div className="mt-4 flex items-center gap-3">
                  <img src={uploadedImage} alt="Uploaded" className="w-16 h-16 rounded-full object-cover" />
                  <span className="text-sm text-green-600">✓ Custom image uploaded</span>
                </div>
              )}
            </div>

            {/* Built-in Avatars */}
            <div className={`card ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
              <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>Choose from Built-in Avatars</h3>
              <p className={`text-sm mb-4 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                Select one of our pre-made avatars
              </p>
              
              <div className="grid grid-cols-4 gap-4">
                {BUILT_IN_AVATARS.map((builtInAvatar) => (
                  <button
                    key={builtInAvatar.id}
                    onClick={() => handleBuiltInSelect(builtInAvatar)}
                    className={`p-2 rounded-lg border-2 transition-all ${
                      selectedBuiltIn === builtInAvatar.id
                        ? 'border-primary-600 bg-primary-50'
                        : darkMode ? 'border-gray-600 hover:border-primary-400' : 'border-gray-200 hover:border-primary-300'
                    }`}
                  >
                    <img
                      src={builtInAvatar.src}
                      alt={builtInAvatar.label}
                      className="w-full aspect-square rounded-lg"
                    />
                    <p className={`text-xs text-center mt-2 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>{builtInAvatar.label}</p>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Statistics */}
        <div className={`card mt-6 ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>Your Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className={`text-center p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
              <p className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>0</p>
              <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Quizzes Taken</p>
            </div>
            <div className={`text-center p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
              <p className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>0%</p>
              <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Average Score</p>
            </div>
            <div className={`text-center p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
              <p className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>0</p>
              <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Current Streak</p>
            </div>
            <div className={`text-center p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
              <p className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>0h</p>
              <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Time Spent</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
