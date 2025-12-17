import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { categoryAPI } from '../services/api';
import { ArrowLeft, Play } from 'lucide-react';

export default function CategoryDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { darkMode } = useTheme();
  const [category, setCategory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCategory();
  }, [id]);

  const loadCategory = async () => {
    try {
      const response = await categoryAPI.getById(id);
      setCategory(response.data);
    } catch (error) {
      console.error('Failed to load category:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
        <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>Loading...</p>
      </div>
    );
  }

  if (!category) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
        <div className="text-center">
          <p className={`mb-4 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Category not found</p>
          <button onClick={() => navigate('/categories')} className="btn-primary">
            Back to Categories
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <header className={`${darkMode ? 'bg-gray-800' : 'bg-white'} shadow-sm`}>
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/categories')}
              className={`p-2 rounded-lg ${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
            >
              <ArrowLeft className={`w-5 h-5 ${darkMode ? 'text-gray-300' : ''}`} />
            </button>
            <div className="flex items-center gap-3">
              <span className="text-3xl">{category.icon || '📚'}</span>
              <div>
                <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>{category.category_name}</h1>
                <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>{category.description}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {category.subcategories && category.subcategories.length > 0 ? (
          <div className="space-y-8">
            {category.subcategories.map((subcategory) => (
              <div key={subcategory.subcategory_id} className={`card ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
                <h2 className={`text-xl font-bold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                  {subcategory.subcategory_name}
                </h2>
                <p className={`mb-4 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>{subcategory.description}</p>

                {subcategory.topics && subcategory.topics.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {subcategory.topics.map((topic) => (
                      <div
                        key={topic.topic_id}
                        className={`p-4 border rounded-lg hover:border-primary-500 hover:shadow-md transition-all cursor-pointer group ${darkMode ? 'border-gray-600' : 'border-gray-200'}`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <h3 className={`font-semibold group-hover:text-primary-600 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                              {topic.topic_name}
                            </h3>
                            <p className={`text-sm mt-1 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>{topic.description}</p>
                            <p className={`text-xs mt-2 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                              {topic.question_count || 0} questions available
                            </p>
                          </div>
                          <Play className="w-5 h-5 text-gray-400 group-hover:text-primary-600" />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className={darkMode ? 'text-gray-400' : 'text-gray-500'}>No topics available yet</p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className={`card text-center ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
            <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>No subcategories available yet</p>
          </div>
        )}
      </div>
    </div>
  );
}
