import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { Clock, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function QuizTakingNew() {
  const { quizId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { darkMode } = useTheme();
  
  const [quiz, setQuiz] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [timerOption, setTimerOption] = useState('whole');
  const [totalTime, setTotalTime] = useState(null);
  const [perQuestionTime, setPerQuestionTime] = useState(null);
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [results, setResults] = useState(null);

  useEffect(() => {
    loadQuiz();
  }, [quizId]);

  // Timer for whole quiz or per question
  useEffect(() => {
    if (timeRemaining !== null && timeRemaining > 0 && !showResults) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            if (timerOption === 'each' && currentQuestion < questions.length - 1) {
              // Move to next question
              handleNextQuestion();
              return perQuestionTime;
            } else {
              // Time's up - submit quiz
              handleSubmit();
              return 0;
            }
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [timeRemaining, showResults, timerOption, currentQuestion]);

  const loadQuiz = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Get quiz data from location state or fetch from API
      const quizData = location.state?.quizData;
      const timerOpt = location.state?.timerOption || 'whole';
      const totalT = location.state?.totalTime;
      const perQT = location.state?.perQuestionTime;
      
      if (quizData) {
        // Convert backend question format to frontend format
        const formattedQuestions = quizData.questions.map(q => {
          if (q.choices && q.choices.length > 0) {
            // Backend format with choices array
            const choiceLetters = ['A', 'B', 'C', 'D'];
            const formatted = {
              id: q.question_id,
              question_text: q.question_text,
              difficulty: q.difficulty_level
            };
            
            q.choices.forEach((choice, index) => {
              const letter = choiceLetters[index] || String.fromCharCode(65 + index);
              formatted[`option_${letter.toLowerCase()}`] = choice.choice_text;
            });
            
            return formatted;
          } else {
            // Already in frontend format
            return {
              id: q.id || q.question_id,
              question_text: q.question_text,
              option_a: q.option_a,
              option_b: q.option_b,
              option_c: q.option_c,
              option_d: q.option_d,
              difficulty: q.difficulty
            };
          }
        });
        
        setQuiz(quizData);
        setQuestions(formattedQuestions);
        setTimerOption(timerOpt);
        setTotalTime(totalT);
        setPerQuestionTime(perQT);
        
        // Set initial timer
        if (timerOpt === 'whole' && totalT) {
          setTimeRemaining(totalT);
        } else if (timerOpt === 'each' && perQT) {
          setTimeRemaining(perQT);
        }
      } else {
        // Fetch from API
        const response = await fetch(`http://127.0.0.1:5000/api/quiz/${quizId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to load quiz');
        }
        
        const data = await response.json();
        
        // Convert backend format to frontend format
        const formattedQuestions = data.questions.map(q => {
          const choiceLetters = ['A', 'B', 'C', 'D'];
          const formatted = {
            id: q.question_id,
            question_text: q.question_text,
            difficulty: q.difficulty_level
          };
          
          if (q.choices && q.choices.length > 0) {
            q.choices.forEach((choice, index) => {
              const letter = choiceLetters[index] || String.fromCharCode(65 + index);
              formatted[`option_${letter.toLowerCase()}`] = choice.choice_text;
            });
          }
          
          return formatted;
        });
        
        setQuiz(data);
        setQuestions(formattedQuestions);
        setTimerOption(data.timer_option || 'whole');
        
        if (data.timer_option === 'whole' && data.time_limit_minutes) {
          setTotalTime(data.time_limit_minutes * 60);
          setTimeRemaining(data.time_limit_minutes * 60);
        } else if (data.timer_option === 'each' && data.per_question_time) {
          setPerQuestionTime(data.per_question_time);
          setTimeRemaining(data.per_question_time);
        }
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error loading quiz:', error);
      alert('Failed to load quiz. Please try again.');
      navigate('/quiz-section');
    }
  };

  const handleAnswerSelect = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
      
      // Reset timer for next question if per-question timing
      if (timerOption === 'each' && perQuestionTime) {
        setTimeRemaining(perQuestionTime);
        setQuestionStartTime(Date.now());
      }
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    if (submitting) return;
    
    setSubmitting(true);
    
    try {
      const token = localStorage.getItem('token');
      const totalTimeTaken = totalTime ? totalTime - timeRemaining : 0;
      
      const response = await fetch(`http://127.0.0.1:5000/api/quiz/${quizId}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          answers: answers,
          time_taken: totalTimeTaken
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit quiz');
      }
      
      const data = await response.json();
      setResults(data);
      setShowResults(true);
      setTimeRemaining(0);
    } catch (error) {
      console.error('Error submitting quiz:', error);
      alert('Failed to submit quiz. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    if (seconds === null) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimerColor = () => {
    if (timeRemaining === null) return darkMode ? 'text-gray-400' : 'text-gray-600';
    if (timeRemaining < 60) return 'text-red-500';
    if (timeRemaining < 300) return 'text-yellow-500';
    return darkMode ? 'text-green-400' : 'text-green-600';
  };

  if (loading) {
    return (
      <div className={`min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} flex items-center justify-center`}>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (showResults) {
    return (
      <div className={`min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} py-8 px-4`}>
        <div className="max-w-4xl mx-auto">
          <div className={`${darkMode ? 'bg-gray-800' : 'bg-white'} rounded-2xl shadow-xl p-8`}>
            <h1 className={`text-3xl font-bold text-center mb-8 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
              Quiz Results
            </h1>
            
            <div className="text-center mb-8">
              <div className={`text-6xl font-bold mb-4 ${
                results.score >= 70 ? 'text-green-500' : results.score >= 40 ? 'text-yellow-500' : 'text-red-500'
              }`}>
                {results.score.toFixed(1)}%
              </div>
              <p className={`text-xl ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                {results.correct_count} out of {results.total_questions} correct
              </p>
              <p className={`text-lg ${darkMode ? 'text-gray-400' : 'text-gray-600'} mt-2`}>
                Time taken: {formatTime(results.time_taken)}
              </p>
            </div>

            <div className="space-y-4 mb-8">
              {results.results?.map((result, index) => (
                <div
                  key={result.question_id}
                  className={`p-4 rounded-lg border-2 ${
                    result.is_correct
                      ? darkMode ? 'border-green-600 bg-green-900/20' : 'border-green-300 bg-green-50'
                      : darkMode ? 'border-red-600 bg-red-900/20' : 'border-red-300 bg-red-50'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {result.is_correct ? (
                      <CheckCircle2 className="text-green-500 flex-shrink-0 mt-1" size={20} />
                    ) : (
                      <AlertCircle className="text-red-500 flex-shrink-0 mt-1" size={20} />
                    )}
                    <div className="flex-1">
                      <p className={`font-medium mb-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                        {index + 1}. {result.question_text}
                      </p>
                      <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                        Your answer: <span className={result.is_correct ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                          {result.user_answer || 'Not answered'}
                        </span>
                      </p>
                      {!result.is_correct && (
                        <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-700'} mt-1`}>
                          Correct answer: <span className="text-green-600 font-medium">{result.correct_answer}</span>
                        </p>
                      )}
                      {result.explanation && (
                        <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'} mt-2 italic`}>
                          {result.explanation}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-center gap-4">
              <button
                onClick={() => navigate('/quiz-section')}
                className={`px-6 py-3 rounded-lg font-medium ${
                  darkMode
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-blue-500 hover:bg-blue-600 text-white'
                } transition-colors`}
              >
                Take Another Quiz
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className={`px-6 py-3 rounded-lg font-medium ${
                  darkMode
                    ? 'bg-gray-700 hover:bg-gray-600 text-white'
                    : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
                } transition-colors`}
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const currentQ = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} py-8 px-4`}>
      <div className="max-w-4xl mx-auto">
        {/* Header with Timer */}
        <div className={`${darkMode ? 'bg-gray-800' : 'bg-white'} rounded-2xl shadow-xl p-6 mb-6`}>
          <div className="flex justify-between items-center">
            <div>
              <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                {quiz?.title}
              </h1>
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'} mt-1`}>
                Question {currentQuestion + 1} of {questions.length}
              </p>
            </div>
            
            {timeRemaining !== null && (
              <div className="flex items-center gap-2">
                <Clock className={getTimerColor()} size={24} />
                <span className={`text-2xl font-bold ${getTimerColor()}`}>
                  {formatTime(timeRemaining)}
                </span>
              </div>
            )}
          </div>
          
          {/* Progress Bar */}
          <div className={`mt-4 h-2 ${darkMode ? 'bg-gray-700' : 'bg-gray-200'} rounded-full overflow-hidden`}>
            <div 
              className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Instructions */}
        {quiz?.instructions && (
          <div className={`${darkMode ? 'bg-blue-900/20 border-blue-600' : 'bg-blue-50 border-blue-300'} border-2 rounded-lg p-4 mb-6`}>
            <p className={`${darkMode ? 'text-blue-300' : 'text-blue-800'} font-medium`}>
              Instructions: {quiz.instructions}
            </p>
          </div>
        )}

        {/* Question Card */}
        <div className={`${darkMode ? 'bg-gray-800' : 'bg-white'} rounded-2xl shadow-xl p-8 mb-6`}>
          <h2 className={`text-xl font-semibold mb-6 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            {currentQ?.question_text}
          </h2>
          
          <div className="space-y-3">
            {['A', 'B', 'C', 'D'].map((option) => {
              const optionKey = `option_${option.toLowerCase()}`;
              const isSelected = answers[currentQ?.id] === option;
              
              return (
                <button
                  key={option}
                  onClick={() => handleAnswerSelect(currentQ?.id, option)}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    isSelected
                      ? darkMode
                        ? 'border-blue-500 bg-blue-900/30'
                        : 'border-blue-500 bg-blue-50'
                      : darkMode
                      ? 'border-gray-600 hover:border-gray-500 bg-gray-700'
                      : 'border-gray-300 hover:border-gray-400 bg-white'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                      isSelected
                        ? 'bg-blue-500 text-white'
                        : darkMode
                        ? 'bg-gray-600 text-gray-300'
                        : 'bg-gray-200 text-gray-700'
                    }`}>
                      {option}
                    </div>
                    <span className={darkMode ? 'text-gray-200' : 'text-gray-800'}>
                      {currentQ?.[optionKey]}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between">
          <button
            onClick={handlePreviousQuestion}
            disabled={currentQuestion === 0}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              currentQuestion === 0
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : darkMode
                ? 'bg-gray-700 hover:bg-gray-600 text-white'
                : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
            }`}
          >
            Previous
          </button>
          
          {currentQuestion === questions.length - 1 ? (
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className={`px-8 py-3 rounded-lg font-bold transition-all ${
                submitting
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 transform hover:scale-105'
              } text-white shadow-lg`}
            >
              {submitting ? 'Submitting...' : 'Submit Quiz'}
            </button>
          ) : (
            <button
              onClick={handleNextQuestion}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                darkMode
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-blue-500 hover:bg-blue-600 text-white'
              }`}
            >
              Next
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
