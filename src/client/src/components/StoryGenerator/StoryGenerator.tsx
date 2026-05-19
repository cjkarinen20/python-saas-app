import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './StoryGenerator.css';

interface GeneratedStory {
  story: string;
  credits_used: number;
  remaining_credits: number;
}

const StoryGenerator: React.FC = () => {
  const { user, logout } = useAuth();
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState('fantasy');
  const [story, setStory] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [credits, setCredits] = useState(user?.credits ?? 0);

  // ==== TODO: BACKEND API INTEGRATION - Fetch Current Credits ====
  // Implement function to fetch user's current credit balance:
  // 1. Make GET request to 'http://localhost:8000/v1/me/credits'
  // 2. Include 'Authorization: Bearer {apiKey}' header (uses API key, not JWT token)
  // 3. On success, extract credits from response and update state
  const fetchCredits = useCallback(async () => {
    if (!apiKey) return;
    try {
      const response = await fetch('http://localhost:8000/v1/me/credits', {
        headers: {
          'Authorization': 'Bearer ${apiKey}',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setCredits(data.credits);
      }
    } catch (error) {
      console.error('Error fetching credits:', error);
    }

    console.log('Fetch credits called - API integration needed');
  }, [apiKey]);

  useEffect(() => {
    fetchCredits();
  }, [fetchCredits]);

  useEffect(() => {
    if (!apiKey) {
      setCredits(user?.credits ?? 0);
    }
  }, [apiKey, user?.credits]);


  // ==== TODO: BACKEND API INTEGRATION - Generate Story ====
  // Implement the main story generation function (costs 1 credit):
  // 1. Make POST request to 'http://localhost:8000/v1/story/generate'
  // 2. Include 'Authorization: Bearer {apiKey}' header (uses API key, not JWT)
  // 3. Send { prompt: prompt, style: style } in request body
  // 4. On success, extract story and remaining_credits from response
  // 5. Handle specific errors:
  //    - 402: Insufficient credits
  //    - 401: Invalid API key
  //    - Other: Display error message
  const generateStory = async () => {
    if (!prompt.trim() || !apiKey.trim()) {
      setError('Please provide both a prompt and API key');
      return;
    }

    setLoading(true);
    setError('');
    setStory('');

    try {
      const response = await fetch('http://localhost:8000/v1/story/generate', {
        method: 'POST', 
        headers: {
          'Authorization': 'Bearer ${apiKey}',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          style: style
        }),
      });
      if (response.ok) {
        const data: GeneratedStory = await response.json();
        setStory(data.story);
        setCredits(data.remaining_credits);
      } else if (response.status === 402) {
        setError('Insufficient credits to generate story.')
      } else if (response.status === 401) {
        setError('Invalid API key.');
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Failed to generate story');
      }
    } catch(error){
      setError('Network error. Please try again.');
      console.error('Story generation error:', error);
    }
    setLoading(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    generateStory();
  };

  return (
    <div className="story-generator-container">
      <div className="story-background"></div>
      <div className="story-content">
        <header className="story-header">
          <div>
            <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
            <h1>AI Story Generator</h1>
          </div>
          <div className="user-info">
            <span>Credits: {credits}</span>
            <span>{user?.email}</span>
            <button onClick={logout} className="logout-btn">Logout</button>
          </div>
        </header>

        <div className="generator-layout">
          <div className="input-section">
            <form onSubmit={handleSubmit} className="generator-form">
              <div className="form-group">
                <label htmlFor="apiKey">API Key</label>
                <input
                  id="apiKey"
                  type="text"
                  placeholder="sk_live_your_api_key_here"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="api-key-input"
                />
                <small>You can create API keys in your dashboard</small>
              </div>

              <div className="form-group">
                <label htmlFor="prompt">Story Prompt</label>
                <textarea
                  id="prompt"
                  placeholder="Describe the story you want to generate..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  rows={4}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="style">Style</label>
                <select
                  id="style"
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                >
                  <option value="fantasy">Fantasy</option>
                  <option value="sci-fi">Science Fiction</option>
                  <option value="mystery">Mystery</option>
                  <option value="romance">Romance</option>
                  <option value="adventure">Adventure</option>
                  <option value="horror">Horror</option>
                </select>
              </div>

              {error && <div className="error-message">{error}</div>}

              <button
                type="submit"
                disabled={loading || !prompt.trim() || !apiKey.trim()}
                className="generate-btn"
              >
                {loading ? 'Generating Story...' : 'Generate Story (1 Credit)'}
              </button>
            </form>
          </div>

          <div className="output-section">
            <h2>Generated Story</h2>
            {loading && (
              <div className="loading-animation">
                <div className="loading-spinner"></div>
                <p>Creating your story...</p>
              </div>
            )}
            {story && (
              <div className="story-output">
                <div className="story-text">{story}</div>
                <div className="story-actions">
                  <button
                    onClick={() => navigator.clipboard.writeText(story)}
                    className="copy-btn"
                  >
                    Copy Story
                  </button>
                </div>
              </div>
            )}
            {!story && !loading && (
              <div className="empty-output">
                <p>Your generated story will appear here</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StoryGenerator;