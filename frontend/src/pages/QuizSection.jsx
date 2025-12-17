import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronDown, ChevronUp, Search } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function QuizSection() {
  const navigate = useNavigate();
  const { darkMode } = useTheme();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedCategory, setExpandedCategory] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedSubcategory, setSelectedSubcategory] = useState('');
  const [numQuestions, setNumQuestions] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchSuggestions, setSearchSuggestions] = useState([]);

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    if (searchQuery.trim()) {
      const suggestions = [];
      categories.forEach(category => {
        // Check if category name matches
        if (category.category_name.toLowerCase().includes(searchQuery.toLowerCase())) {
          suggestions.push({
            type: 'category',
            id: category.category_id,
            name: category.category_name,
            icon: category.icon
          });
        }
        
        // Check subcategories
        category.subcategories?.forEach(subcategory => {
          if (subcategory.subcategory_name.toLowerCase().includes(searchQuery.toLowerCase())) {
            suggestions.push({
              type: 'subcategory',
              id: subcategory.subcategory_id,
              categoryId: category.category_id,
              name: `${category.category_name} → ${subcategory.subcategory_name}`,
              icon: category.icon
            });
          }
        });
      });
      setSearchSuggestions(suggestions.slice(0, 10)); // Limit to 10 suggestions
    } else {
      setSearchSuggestions([]);
    }
  }, [searchQuery, categories]);

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/categories/all');

      if (!response.ok) {
        throw new Error('Failed to fetch categories');
      }

      const data = await response.json();
      setCategories(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryClick = (categoryId) => {
    if (expandedCategory === categoryId) {
      setExpandedCategory(null);
    } else {
      setExpandedCategory(categoryId);
    }
  };

  const handleCategorySelect = (categoryId, categoryName) => {
    setSelectedCategory(categoryId);
    setSelectedSubcategory('');
    setSearchQuery('');
    setExpandedCategory(null); // Collapse all categories after selection
  };

  const handleSubcategorySelect = (subcategoryId, subcategoryName) => {
    setSelectedSubcategory(subcategoryId);
    setSearchQuery('');
    setExpandedCategory(null); // Collapse all categories after selection
  };

  const handleSuggestionClick = (suggestion) => {
    if (suggestion.type === 'category') {
      handleCategorySelect(suggestion.id, suggestion.name);
      setExpandedCategory(suggestion.id);
      setSearchQuery('');
    } else if (suggestion.type === 'subcategory') {
      setSelectedCategory(suggestion.categoryId);
      setSelectedSubcategory(suggestion.id);
      setSearchQuery('');
      setExpandedCategory(null);
    }
  };

  const handleStartQuiz = () => {
    if (!selectedCategory) {
      alert('Please select a category');
      return;
    }
    if (!selectedSubcategory) {
      alert('Please select a subcategory');
      return;
    }
    if (!numQuestions || numQuestions < 1) {
      alert('Please enter a valid number of questions');
      return;
    }

    // Get category and subcategory names for display
    const selectedCategoryData = categories.find(cat => cat.id === selectedCategory);
    const selectedSubcategoryData = selectedCategoryData?.subcategories?.find(sub => sub.id === selectedSubcategory);

    // Navigate to quiz preview page with parameters
    navigate('/quiz-preview', {
      state: {
        category: selectedCategory,
        subcategory: selectedSubcategory,
        numQuestions: numQuestions,
        categoryName: selectedCategoryData?.name || '',
        subcategoryName: selectedSubcategoryData?.name || ''
      }
    });
  };

  if (loading) {
    return (
      <div className={`min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} flex items-center justify-center`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className={`mt-4 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Loading categories...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} flex items-center justify-center`}>
        <div className="text-center">
          <p className="text-red-600">Error: {error}</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} py-8 px-4`}>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className={`text-4xl font-bold mb-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            QUIZ SECTION
          </h1>
        </div>

        {/* Main Quiz Form */}
        <div className={`${darkMode ? 'bg-gray-800' : 'bg-white'} rounded-2xl shadow-xl p-8`}>
          {/* Category Dropdown with Integrated Search */}
          <div className="mb-6">
            <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
              SELECT CATEGORY
            </label>
            <div className={`border-2 rounded-lg ${darkMode ? 'border-gray-600' : 'border-gray-300'}`}>
              {/* Search/Select Button */}
              <button
                onClick={() => setExpandedCategory(expandedCategory ? null : 'all')}
                className={`w-full px-4 py-3 flex items-center justify-between ${
                  darkMode ? 'text-white hover:bg-gray-700' : 'text-gray-900 hover:bg-gray-50'
                } rounded-lg transition-colors`}
              >
                <span className="text-left font-medium">
                  {selectedCategory 
                    ? categories.find(c => c.category_id === selectedCategory)?.category_name 
                    : 'Choose a category...'}
                </span>
                {expandedCategory ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
              </button>

              {expandedCategory && (
                <div className={`border-t ${darkMode ? 'border-gray-600' : 'border-gray-300'}`}>
                  {/* Integrated Search Input */}
                  <div className="p-3 border-b border-gray-300 dark:border-gray-600">
                    <div className="relative">
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Type to search categories or subcategories..."
                        className={`w-full px-4 py-2 pl-10 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                            : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                        }`}
                        autoFocus
                      />
                      <Search className={`absolute left-3 top-2.5 w-4 h-4 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`} />
                    </div>
                  </div>

                  {/* Categories List with Search Results */}
                  <div className="max-h-96 overflow-y-auto">
                    {/* Show search results if searching */}
                    {searchQuery && searchSuggestions.length > 0 ? (
                      <div>
                        {searchSuggestions.map((suggestion, index) => (
                          <button
                            key={index}
                            onClick={() => handleSuggestionClick(suggestion)}
                            className={`w-full px-4 py-3 flex items-center gap-3 border-b ${
                              darkMode 
                                ? 'hover:bg-gray-700 border-gray-600 text-white' 
                                : 'hover:bg-gray-50 border-gray-100 text-gray-900'
                            } transition-colors`}
                          >
                            <span className="text-2xl">{suggestion.icon}</span>
                            <div className="text-left">
                              <p className="font-medium">{suggestion.name}</p>
                              <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                                {suggestion.type === 'category' ? 'Category' : 'Subcategory'}
                              </p>
                            </div>
                          </button>
                        ))}
                      </div>
                    ) : searchQuery && searchSuggestions.length === 0 ? (
                      <div className={`px-4 py-8 text-center ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        <p>No results found for "{searchQuery}"</p>
                      </div>
                    ) : (
                      // Show all categories when not searching
                      <div>
                        {categories.map((category) => (
                          <div key={category.category_id} className={`${darkMode ? 'border-b border-gray-600' : 'border-b border-gray-200'}`}>
                            <button
                              onClick={() => handleCategoryClick(category.category_id)}
                              className={`w-full px-4 py-3 flex items-center justify-between ${
                                selectedCategory === category.category_id
                                  ? darkMode ? 'bg-blue-900 text-white' : 'bg-blue-50 text-blue-900'
                                  : darkMode ? 'text-white hover:bg-gray-700' : 'text-gray-900 hover:bg-gray-50'
                              } transition-colors`}
                            >
                              <div className="flex items-center gap-3">
                                <span className="text-2xl">{category.icon}</span>
                                <span className="font-medium">{category.category_name}</span>
                              </div>
                              {expandedCategory === category.category_id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                            </button>

                            {/* Subcategories */}
                            {expandedCategory === category.category_id && category.subcategories && (
                              <div className={`${darkMode ? 'bg-gray-750' : 'bg-gray-50'}`}>
                                {category.subcategories.map((subcategory) => (
                                  <button
                                    key={subcategory.subcategory_id}
                                    onClick={() => {
                                      handleCategorySelect(category.category_id, category.category_name);
                                      handleSubcategorySelect(subcategory.subcategory_id, subcategory.subcategory_name);
                                    }}
                                    className={`w-full px-12 py-2.5 text-left ${
                                      selectedSubcategory === subcategory.subcategory_id
                                        ? darkMode ? 'bg-blue-800 text-white' : 'bg-blue-100 text-blue-900'
                                        : darkMode ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100'
                                    } transition-colors`}
                                  >
                                    <span className="text-sm">→ {subcategory.subcategory_name}</span>
                                  </button>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Subcategory Dropdown (shows selected) */}
          <div className="mb-6">
            <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
              SELECT SUB CATEGORY
            </label>
            <div className={`border-2 rounded-lg px-4 py-3 ${darkMode ? 'border-gray-600 bg-gray-700' : 'border-gray-300 bg-gray-50'}`}>
              <span className={`${darkMode ? 'text-white' : 'text-gray-900'} font-medium`}>
                {selectedSubcategory
                  ? categories
                      .find(c => c.category_id === selectedCategory)
                      ?.subcategories?.find(s => s.subcategory_id === selectedSubcategory)
                      ?.subcategory_name
                  : 'Choose a subcategory...'}
              </span>
            </div>
          </div>

          {/* Number of Questions */}
          <div className="mb-8">
            <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
              NUMBER OF QUIZ QUESTIONS
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={numQuestions}
              onChange={(e) => setNumQuestions(e.target.value)}
              placeholder="Enter number of questions (e.g., 10)"
              className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                darkMode 
                  ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                  : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
              }`}
            />
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-4 justify-center">
            <button
              onClick={handleStartQuiz}
              disabled={!selectedCategory || !selectedSubcategory || !numQuestions}
              className={`px-8 py-3 rounded-lg text-base font-medium transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none ${
                darkMode
                  ? 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white'
                  : 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white'
              } shadow-lg`}
            >
              generate QUIZ to enhance your knowledge
            </button>
            
            <button
              onClick={handleStartQuiz}
              disabled={!selectedCategory || !selectedSubcategory || !numQuestions}
              className={`px-8 py-3 rounded-lg text-base font-medium transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none ${
                darkMode
                  ? 'bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white'
                  : 'bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white'
              } shadow-lg`}
            >
              Generate quiz for class of members
            </button>
          </div>
        </div>

        {/* Back Button */}
        <div className="mt-6 text-center">
          <button
            onClick={() => navigate('/dashboard')}
            className={`px-6 py-2 rounded-lg ${
              darkMode 
                ? 'bg-gray-700 text-white hover:bg-gray-600' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            } border ${darkMode ? 'border-gray-600' : 'border-gray-300'} transition-colors`}
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}
