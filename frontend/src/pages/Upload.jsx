import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { fileAPI } from '../services/api';
import { ArrowLeft, Upload as UploadIcon, File, CheckCircle, AlertCircle } from 'lucide-react';

export default function Upload() {
  const navigate = useNavigate();
  const { darkMode } = useTheme();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [error, setError] = useState('');
  const [uploadedFileId, setUploadedFileId] = useState(null);
  const [numQuestions, setNumQuestions] = useState(10);
  const [generating, setGenerating] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const allowedTypes = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           'text/plain'];
      
      if (!allowedTypes.includes(selectedFile.type)) {
        setError('Please upload a PDF, DOC, DOCX, or TXT file');
        return;
      }

      // Validate file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      setFile(selectedFile);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
      setError('You must be logged in to upload files');
      return;
    }

    setUploading(true);
    setError('');
    setUploadStatus(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      console.log('Uploading file:', file.name);
      console.log('Token exists:', !!token);
      const response = await fileAPI.upload(formData);
      console.log('Upload response:', response.data);
      
      // Store file ID and show question count input
      setUploadedFileId(response.data.file_id);
      setUploadStatus('uploaded');

    } catch (err) {
      console.error('Upload error:', err);
      console.error('Error response:', err.response);
      console.error('Error data:', err.response?.data);
      setError(err.response?.data?.error || err.response?.data?.msg || err.message || 'Failed to upload file');
      setUploadStatus('error');
    } finally {
      setUploading(false);
    }
  };

  const handleGenerateQuiz = async () => {
    if (!uploadedFileId || numQuestions < 1 || numQuestions > 50) {
      setError('Please enter a valid number of questions (1-50)');
      return;
    }

    setGenerating(true);
    setError('');

    try {
      const response = await fileAPI.generateQuiz(uploadedFileId, { num_questions: numQuestions });
      console.log('Quiz generation response:', response.data);
      
      if (response.data.quiz_id) {
        // Navigate to quiz taking page
        navigate(`/quiz/${response.data.quiz_id}`);
      } else {
        setUploadStatus('quiz_generated');
      }
    } catch (err) {
      console.error('Quiz generation error:', err);
      setError(err.response?.data?.error || 'Failed to generate quiz from file');
    } finally {
      setGenerating(false);
    }
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
            <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Upload Study Material</h1>
          </div>
        </div>
      </header>

      <div className="max-w-3xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className={`card ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-100 mb-4">
              <UploadIcon className="w-8 h-8 text-primary-600" />
            </div>
            <h2 className={`text-xl font-bold mb-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              Generate Quiz from Your Materials
            </h2>
            <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>
              Upload your study materials and let AI generate custom quiz questions
            </p>
          </div>

          {/* Upload Area */}
          <div className="mb-6">
            <label className="block">
              <div className={`border-2 border-dashed rounded-lg p-8 text-center hover:border-primary-500 transition-colors cursor-pointer ${darkMode ? 'border-gray-600' : 'border-gray-300'}`}>
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf,.doc,.docx,.txt"
                  onChange={handleFileChange}
                  disabled={uploading}
                />
                {file ? (
                  <div className="flex items-center justify-center gap-3">
                    <File className="w-8 h-8 text-primary-600" />
                    <div className="text-left">
                      <p className={`font-medium ${darkMode ? 'text-white' : 'text-gray-900'}`}>{file.name}</p>
                      <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                ) : (
                  <>
                    <UploadIcon className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <p className={`font-medium mb-1 ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>
                      Click to upload or drag and drop
                    </p>
                    <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                      PDF, DOC, DOCX, or TXT (Max 10MB)
                    </p>
                  </>
                )}
              </div>
            </label>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {/* Success Message - File Uploaded */}
          {uploadStatus === 'uploaded' && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start gap-3 mb-4">
                <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-blue-700 font-medium">File analyzed successfully!</p>
                  <p className="text-blue-600 text-sm">Now specify how many questions you want</p>
                </div>
              </div>
              
              {/* Question Count Input */}
              <div className={`rounded-lg p-4 border ${darkMode ? 'bg-gray-700 border-blue-400' : 'bg-white border-blue-200'}`}>
                <label className="block mb-2">
                  <span className={`font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>Number of MCQ questions:</span>
                  <div className="mt-2 flex items-center gap-3">
                    <input
                      type="number"
                      min="1"
                      max="50"
                      value={numQuestions}
                      onChange={(e) => setNumQuestions(parseInt(e.target.value) || 1)}
                      className="form-input w-24 text-center"
                      disabled={generating}
                    />
                    <span className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-500'}`}>(1-50 questions)</span>
                  </div>
                </label>
                
                <button
                  onClick={handleGenerateQuiz}
                  disabled={generating}
                  className="btn-primary w-full mt-4 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {generating ? 'Generating Quiz...' : 'Generate Quiz & Start'}
                </button>
              </div>
            </div>
          )}

          {uploadStatus === 'success' && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-green-700 font-medium">File uploaded successfully!</p>
                <p className="text-green-600 text-sm">Generating quiz questions...</p>
              </div>
            </div>
          )}

          {uploadStatus === 'quiz_generated' && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-green-700 font-medium">Quiz generated successfully!</p>
                <p className="text-green-600 text-sm">You can now take the quiz</p>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4">
            {file && !uploadStatus && (
              <button
                onClick={() => {
                  setFile(null);
                  setError('');
                }}
                className="btn-secondary flex-1"
                disabled={uploading}
              >
                Clear
              </button>
            )}
            {uploadStatus !== 'uploaded' && (
              <button
                onClick={handleUpload}
                disabled={!file || uploading || uploadStatus === 'uploaded'}
                className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? 'Uploading...' : 'Upload & Analyze File'}
              </button>
            )}
          </div>

          {/* Info Section */}
          <div className={`mt-8 pt-8 ${darkMode ? 'border-gray-600' : 'border-gray-200'} border-t`}>
            <h3 className={`font-semibold mb-3 ${darkMode ? 'text-white' : 'text-gray-900'}`}>How it works:</h3>
            <ol className={`space-y-2 text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              <li className="flex gap-2">
                <span className="font-semibold text-primary-600">1.</span>
                Upload your study material (notes, textbook excerpts, etc.)
              </li>
              <li className="flex gap-2">
                <span className="font-semibold text-primary-600">2.</span>
                Our AI extracts key concepts and generates quiz questions
              </li>
              <li className="flex gap-2">
                <span className="font-semibold text-primary-600">3.</span>
                Review and approve the generated questions
              </li>
              <li className="flex gap-2">
                <span className="font-semibold text-primary-600">4.</span>
                Take the quiz and track your progress
              </li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
