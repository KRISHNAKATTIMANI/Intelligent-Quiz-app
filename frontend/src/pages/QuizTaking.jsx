import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { quizAPI } from '../services/api';
import { ArrowLeft, Clock, CheckCircle, XCircle } from 'lucide-react';

export default function QuizTaking() {
  const { quizId } = useParams();
  const navigate = useNavigate();
  const { darkMode } = useTheme();
  
  const [quiz, setQuiz] = useState(null);
  const [attemptId, setAttemptId] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadQuiz();
  }, [quizId]);

  useEffect(() => {
    if (timeRemaining > 0) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            handleSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [timeRemaining]);

  const loadQuiz = async () => {
    try {
      // Start the quiz attempt
      const response = await quizAPI.start(quizId);
      console.log('Quiz start response:', response.data);
      
      setAttemptId(response.data.attempt_id);
      setQuiz(response.data.quiz);
      setQuestions(response.data.questions || []);
      setTimeRemaining(response.data.quiz.time_limit_minutes * 60);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load quiz:', err);
      setError(err.response?.data?.error || 'Failed to load quiz');
      setLoading(false);
    }
  };

  const handleAnswerSelect = (questionId, choiceId) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: choiceId
    }));
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    if (submitting) return;
    
    // Confirm submission
    if (!window.confirm('Are you sure you want to submit your quiz?')) {
      return;
    }

    setSubmitting(true);
    try {
      // Format answers for submission
      const formattedAnswers = Object.entries(answers).map(([questionId, choiceId]) => ({
        question_id: parseInt(questionId),
        selected_choice_id: choiceId
      }));

      const response = await quizAPI.submit(attemptId, formattedAnswers);
      console.log('Submit response:', response.data);
      
      // Navigate to results page
      navigate(`/results/${attemptId}`);
    } catch (err) {
      console.error('Submit error:', err);
      setError(err.response?.data?.error || 'Failed to submit quiz');
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>Loading quiz...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
        <div className={`card max-w-md text-center ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className={`text-xl font-bold mb-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>Error</h2>
          <p className={`mb-4 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>{error}</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-primary"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!quiz || questions.length === 0) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
        <div className={`card max-w-md text-center ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>No questions available</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-primary mt-4"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const currentQ = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;
  const answeredCount = Object.keys(answers).length;

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <header className={`${darkMode ? 'bg-gray-800' : 'bg-white'} shadow-sm sticky top-0 z-10`}>
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>{quiz.quiz_title}</h1>
            </div>
            
            {/* Timer */}
            <div className="flex items-center gap-2 bg-primary-50 px-4 py-2 rounded-lg">
              <Clock className="w-5 h-5 text-primary-600" />
              <span className={`font-mono font-semibold ${timeRemaining < 60 ? 'text-red-600' : 'text-primary-600'}`}>
                {formatTime(timeRemaining)}
              </span>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Question {currentQuestion + 1} of {questions.length}</span>
              <span>{answeredCount} answered</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Question Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className={`card ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
          {/* Question Text */}
          <div className="mb-6">
            <div className="flex items-start gap-3">
              <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-semibold">
                {currentQuestion + 1}
              </span>
              <p className={`text-lg font-medium pt-1 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                {currentQ.question_text}
              </p>
            </div>
          </div>

          {/* Answer Choices */}
          <div className="space-y-3 mb-8">
            {currentQ.choices && currentQ.choices.map((choice, index) => {
              const isSelected = answers[currentQ.question_id] === choice.choice_id;
              return (
                <button
                  key={choice.choice_id}
                  onClick={() => handleAnswerSelect(currentQ.question_id, choice.choice_id)}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    isSelected
                      ? 'border-primary-600 bg-primary-50'
                      : darkMode
                      ? 'border-gray-600 hover:border-primary-400 hover:bg-gray-700'
                      : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                      isSelected
                        ? 'border-primary-600 bg-primary-600'
                        : darkMode ? 'border-gray-500' : 'border-gray-300'
                    }`}>
                      {isSelected && (
                        <CheckCircle className="w-4 h-4 text-white" />
                      )}
                    </div>
                    <span className={`text-sm font-medium ${isSelected ? 'text-primary-900' : darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      {String.fromCharCode(65 + index)}.
                    </span>
                    <span className={isSelected ? 'text-gray-900 font-medium' : darkMode ? 'text-gray-200' : 'text-gray-700'}>
                      {choice.choice_text}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Navigation Buttons */}
          <div className={`flex items-center justify-between pt-6 ${darkMode ? 'border-gray-600' : 'border-gray-200'} border-t`}>
            <button
              onClick={handlePrevious}
              disabled={currentQuestion === 0}
              className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            <div className="flex gap-3">
              {currentQuestion === questions.length - 1 ? (
                <button
                  onClick={handleSubmit}
                  disabled={submitting}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? 'Submitting...' : 'Submit Quiz'}
                </button>
              ) : (
                <button
                  onClick={handleNext}
                  className="btn-primary"
                >
                  Next Question
                </button>
              )}
            </div>
          </div>

          {/* Question Navigator */}
          <div className={`mt-6 pt-6 ${darkMode ? 'border-gray-600' : 'border-gray-200'} border-t`}>
            <p className={`text-sm mb-3 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Quick Navigation:</p>
            <div className="grid grid-cols-10 gap-2">
              {questions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentQuestion(idx)}
                  className={`w-10 h-10 rounded-lg text-sm font-semibold transition-all ${
                    idx === currentQuestion
                      ? 'bg-primary-600 text-white'
                      : answers[q.question_id]
                      ? 'bg-green-100 text-green-700 hover:bg-green-200'
                      : darkMode
                      ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {idx + 1}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
