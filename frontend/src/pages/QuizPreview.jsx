import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Clock, BookOpen, AlertCircle } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function QuizPreview() {
  const navigate = useNavigate();
  const location = useLocation();
  const { darkMode } = useTheme();
  
  const [quizDetails, setQuizDetails] = useState(null);
  const [difficulty, setDifficulty] = useState('MEDIUM');
  const [timerOption, setTimerOption] = useState('whole'); // 'whole' or 'each'
  const [totalTime, setTotalTime] = useState('');
  const [perQuestionTime, setPerQuestionTime] = useState('');
  const [instructions, setInstructions] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get quiz details from location state
    const { category, subcategory, numQuestions, categoryName, subcategoryName } = location.state || {};
    
    if (!category || !subcategory || !numQuestions) {
      navigate('/quiz-section');
      return;
    }

    setQuizDetails({
      category,
      subcategory,
      numQuestions,
      categoryName,
      subcategoryName
    });
    setLoading(false);
  }, [location, navigate]);

  const handleStartQuiz = async () => {
    if (timerOption === 'whole' && !totalTime) {
      alert('Please set time for whole quiz');
      return;
    }
    if (timerOption === 'each' && !perQuestionTime) {
      alert('Please set time for each quiz');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      
      // Generate quiz with AI
      const response = await fetch('http://127.0.0.1:5000/api/quiz/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          subcategory_id: quizDetails.subcategory,
          num_questions: parseInt(quizDetails.numQuestions),
          difficulty_level: difficulty,
          timer_option: timerOption,
          total_time: timerOption === 'whole' ? parseInt(totalTime) : null,
          per_question_time: timerOption === 'each' ? parseInt(perQuestionTime) : null,
          instructions: instructions,
          use_ai: true  // Enable AI question generation
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to generate quiz');
      }

      const data = await response.json();
      
      // Navigate to quiz taking page with quiz ID
      navigate(`/quiz/${data.quiz_id}`, {
        state: {
          quizData: data,
          timerOption,
          totalTime: timerOption === 'whole' ? parseInt(totalTime) * 60 : null, // Convert to seconds
          perQuestionTime: timerOption === 'each' ? parseInt(perQuestionTime) * 60 : null
        }
      });
    } catch (error) {
      console.error('Error generating quiz:', error);
      alert(error.message || 'Failed to generate quiz. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className={`min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} flex items-center justify-center`}>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} py-8 px-4`}>
      <div className="max-w-4xl mx-auto">
        <h1 className={`text-3xl font-bold text-center mb-8 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
          QUIZ PREVIEW
        </h1>

        <div className={`${darkMode ? 'bg-gray-800' : 'bg-white'} rounded-2xl shadow-xl p-8`}>
          {/* Quiz Details */}
          <div className="mb-6">
            <h2 className={`text-xl font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              QUIZ DETAILS:
            </h2>
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
              <p className={`mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                <span className="font-semibold">Category:</span> {quizDetails?.categoryName}
              </p>
              <p className={`mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                <span className="font-semibold">Subcategory:</span> {quizDetails?.subcategoryName}
              </p>
              <p className={`${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                <span className="font-semibold">Number of Questions:</span> {quizDetails?.numQuestions}
              </p>
            </div>
          </div>

          {/* Select Difficulty Level */}
          <div className="mb-6">
            <h2 className={`text-lg font-semibold mb-3 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              Select quiz level
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {['EASY', 'MEDIUM', 'HARD', 'ADVANCE'].map((level) => (
                <button
                  key={level}
                  onClick={() => setDifficulty(level)}
                  className={`px-4 py-3 rounded-lg font-medium transition-all ${
                    difficulty === level
                      ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                      : darkMode
                      ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          {/* Timer Settings */}
          <div className="mb-6">
            <h2 className={`text-lg font-semibold mb-3 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              TIMER
            </h2>
            <div className="space-y-4">
              {/* Whole Quiz Timer */}
              <div className={`p-4 rounded-lg border-2 ${
                timerOption === 'whole'
                  ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                  : darkMode ? 'border-gray-600' : 'border-gray-200'
              }`}>
                <label className="flex items-center cursor-pointer mb-3">
                  <input
                    type="radio"
                    name="timer"
                    value="whole"
                    checked={timerOption === 'whole'}
                    onChange={(e) => setTimerOption(e.target.value)}
                    className="mr-3"
                  />
                  <span className={`font-medium ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                    Set time for whole quiz
                  </span>
                </label>
                {timerOption === 'whole' && (
                  <input
                    type="number"
                    min="1"
                    placeholder="Enter minutes (e.g., 30)"
                    value={totalTime}
                    onChange={(e) => setTotalTime(e.target.value)}
                    className={`w-full px-4 py-2 rounded-lg border ${
                      darkMode
                        ? 'bg-gray-700 border-gray-600 text-white'
                        : 'bg-white border-gray-300 text-gray-900'
                    }`}
                  />
                )}
              </div>

              {/* Per Question Timer */}
              <div className={`p-4 rounded-lg border-2 ${
                timerOption === 'each'
                  ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                  : darkMode ? 'border-gray-600' : 'border-gray-200'
              }`}>
                <label className="flex items-center cursor-pointer mb-3">
                  <input
                    type="radio"
                    name="timer"
                    value="each"
                    checked={timerOption === 'each'}
                    onChange={(e) => setTimerOption(e.target.value)}
                    className="mr-3"
                  />
                  <span className={`font-medium ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                    Set time for each quiz
                  </span>
                </label>
                {timerOption === 'each' && (
                  <input
                    type="number"
                    min="1"
                    placeholder="Enter minutes per question (e.g., 2)"
                    value={perQuestionTime}
                    onChange={(e) => setPerQuestionTime(e.target.value)}
                    className={`w-full px-4 py-2 rounded-lg border ${
                      darkMode
                        ? 'bg-gray-700 border-gray-600 text-white'
                        : 'bg-white border-gray-300 text-gray-900'
                    }`}
                  />
                )}
              </div>
            </div>
          </div>

          {/* Instructions */}
          <div className="mb-8">
            <h2 className={`text-lg font-semibold mb-3 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              ADD INSTRUCTIONS
            </h2>
            <textarea
              placeholder="Enter special instructions for the quiz (optional)"
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              rows="4"
              className={`w-full px-4 py-3 rounded-lg border ${
                darkMode
                  ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400'
                  : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
              }`}
            />
          </div>

          {/* Start Button */}
          <div className="flex justify-center">
            <button
              onClick={handleStartQuiz}
              className={`px-16 py-4 rounded-lg text-lg font-bold transition-all transform hover:scale-105 ${
                darkMode
                  ? 'bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800'
                  : 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700'
              } text-white shadow-lg`}
            >
              Start
            </button>
          </div>
        </div>

        {/* Back Button */}
        <div className="mt-6 text-center">
          <button
            onClick={() => navigate('/quiz-section')}
            className={`px-6 py-2 rounded-lg ${
              darkMode 
                ? 'bg-gray-700 text-white hover:bg-gray-600' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            } border ${darkMode ? 'border-gray-600' : 'border-gray-300'} transition-colors`}
          >
            Back to Quiz Section
          </button>
        </div>
      </div>
    </div>
  );
}
