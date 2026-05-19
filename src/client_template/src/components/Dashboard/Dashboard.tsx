import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Dashboard.css';

interface ApiKey {
  id: number;
  name: string;
  key_hash: string;
  is_active: boolean;
  created_at: string;
}

interface UsageRecord {
  id: number;
  prompt: string;
  story: string | null;
  tokens_used: number | null;
  cost_credits: number;
  created_at: string;
}

const Dashboard: React.FC = () => {
  const { user, logout, token } = useAuth();
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [usage, setUsage] = useState<UsageRecord[]>([]);
  const [credits, setCredits] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [showCreateKey, setShowCreateKey] = useState(false);
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<string | null>(null);
  const [selectedStory, setSelectedStory] = useState<UsageRecord | null>(null);
  const [showStoryModal, setShowStoryModal] = useState(false);
  const navigate = useNavigate();

  // ==== TODO: BACKEND API INTEGRATION - Fetch API Keys ====
  // Implement function to fetch user's API keys:
  // 1. Make GET request to 'http://localhost:8000/api-keys'
  // 2. Include 'Authorization: Bearer {token}' header
  // 3. On success, update apiKeys state with response data
  const fetchApiKeys = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api-keys', {
        headers: {
          'Authorization': 'Bearer ${token}',
        },
      });
      if (response.ok) {
        const data = await response.json()
        setApiKeys(data);
      }
    } catch (error) {
      console.error('Error fetching API keys:', error);
    }
  }, [token]);

  // ==== TODO: BACKEND API INTEGRATION - Create New API Key ====
  // Implement function to create a new API key:
  // 1. Make POST request to 'http://localhost:8000/api-keys'
  // 2. Include 'Authorization: Bearer {token}' header
  // 3. Send { name: newKeyName } in request body
  // 4. On success, extract api_key from response and store in newlyCreatedKey
  // 5. Refresh the API keys list by calling fetchApiKeys()
  const createApiKey = async () => {
    if (!newKeyName.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api-keys', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer ${token}',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({name: newKeyName})
      });
      if (response.ok) {
        const data = await response.json();
        setNewlyCreatedKey(data.api_key); // Store the newly created API key
        setNewKeyName('');
        setShowCreateKey(false);
        fetchApiKeys();
      }
    } catch (error) {
      console.error('Error creating API key:', error);
    }
    setLoading(false);
  };

  // ==== TODO: BACKEND API INTEGRATION - Deactivate API Key ====
  // Implement function to delete an API key:
  // 1. Show confirmation dialog first
  // 2. Make DELETE request to 'http://localhost:8000/api-keys/{keyId}'
  // 3. Include 'Authorization: Bearer {token}' header
  // 4. On success, refresh API keys list and show success message
  // 5. On error, show error message
  const deactivateApiKey = async (keyId: number, keyName: string) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete the API key "${keyName}"? This action cannot be undone.`
    );

    if (!confirmed) return;

    try {
      const response = await fetch('http://localhost:8000/api-keys/${keyId}', {
        method: 'DELETE',
        headers: {
          'Authorization': 'Bearer ${token}',
        },
      });
      if (response.ok) {
        fetchApiKeys();
        alert('API key deleted successfully!');
      } else {
        alert('Failed to delete API key. Please try again.');
      }
    } catch (error) {
      console.error('Error deactivating API key:', error);
      alert('Error deleting API key. Please try again.');
    }
  };

  // ==== TODO: BACKEND API INTEGRATION - Fetch Usage History ====
  // Implement function to fetch user's usage history:
  // 1. Make GET request to 'http://localhost:8000/auth/me/usage?limit=20'
  // 2. Include 'Authorization: Bearer {token}' header
  // 3. On success, update usage state with response data
  // 4. Handle case when token is not available
  const fetchUsage = useCallback(async () => {
    try {
          if (!token) {
            console.log('No auth token available for fetching usage');
            setUsage([]);
            return;
          }
          const response = await fetch('http://localhost:8000/auth/me/usage?limit=20', {
            headers: {
              'Authorization': 'Bearer ${token}',
              'Content-Type': 'application/json',
          },
        });
        if (response.ok) {
          const data = await response.json();
          console.log('Fetched usage history:', data);
          setUsage(data);
        } else {
          console.error('Failed to fetch usage history:', response.status, response.statusText);
          setUsage([]);
        }
    } catch (error) {
      console.error('Error fetching usage history:', error);
      setUsage([]);
    }
  }, [token]);

  // ==== TODO: BACKEND API INTEGRATION - Fetch Current Credits ====
  // Note: This endpoint requires an API key (not JWT token)
  // For now, using user data from context as fallback
  // To implement: Make GET request to 'http://localhost:8000/v1/me/credits'
  // with 'Authorization: Bearer {api_key}' header
  const fetchCredits = useCallback(async () => {
    // Using user context data as placeholder
    // TODO: Implement API call to GET /v1/me/credits with API key
    setCredits(user?.credits || 0);
  }, [user?.credits]);

  useEffect(() => {
    fetchApiKeys();
    fetchCredits();
    fetchUsage();
  }, [fetchApiKeys, fetchCredits, fetchUsage]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleViewStory = (record: UsageRecord) => {
    setSelectedStory(record);
    setShowStoryModal(true);
  };

  const handleCopyStory = (story: string) => {
    navigator.clipboard.writeText(story);
    alert('Story copied to clipboard!');
  };

  const closeStoryModal = () => {
    setShowStoryModal(false);
    setSelectedStory(null);
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-background"></div>
      <div className="dashboard-content">
        <header className="dashboard-header">
          <h1>Story Generation Dashboard</h1>
          <div className="user-info">
            <span>Credits: {credits}</span>
            <span>{user?.email}</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </header>

        <div className="dashboard-grid">
          <div className="card">
            <h2>Generate Stories</h2>
            <p>Create amazing stories using AI</p>
            <Link to="/generate" className="primary-btn">
              Start Generating
            </Link>
          </div>

          <div className="card">
            <h2>Credits</h2>
            <div className="credits-display">
              <span className="credits-number">{credits}</span>
              <span className="credits-label">remaining</span>
            </div>
            <p>Each story generation costs 1 credit</p>
          </div>

          <div className="card api-keys-card">
            <div className="card-header">
              <h2>API Keys</h2>
              <button
                onClick={() => setShowCreateKey(!showCreateKey)}
                className="create-key-btn"
              >
                Create New Key
              </button>
            </div>

            {showCreateKey && (
              <div className="create-key-form">
                <input
                  type="text"
                  placeholder="API Key Name"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                />
                <div className="form-buttons">
                  <button onClick={createApiKey} disabled={loading}>
                    {loading ? 'Creating...' : 'Create'}
                  </button>
                  <button onClick={() => setShowCreateKey(false)}>
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {newlyCreatedKey && (
              <div className="new-key-display">
                <h4>🎉 New API Key Created!</h4>
                <p className="warning-text">⚠️ Copy this key now - it won't be shown again!</p>
                <div className="key-copy-container">
                  <code className="new-key-value">{newlyCreatedKey}</code>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(newlyCreatedKey);
                      alert('API key copied to clipboard!');
                    }}
                    className="copy-key-btn"
                  >
                    Copy
                  </button>
                </div>
                <button
                  onClick={() => setNewlyCreatedKey(null)}
                  className="dismiss-btn"
                >
                  I've saved it safely
                </button>
              </div>
            )}

            <div className="api-keys-list">
              {apiKeys.length === 0 ? (
                <p className="no-keys">No API keys created yet</p>
              ) : (
                apiKeys.map((key) => (
                  <div key={key.id} className="api-key-item">
                    <div className="key-info">
                      <h4>{key.name}</h4>
                      <code className="key-value">{key.key_hash}</code>
                      <small>Created: {new Date(key.created_at).toLocaleDateString()}</small>
                    </div>
                    <button
                      onClick={() => deactivateApiKey(key.id, key.name)}
                      className="delete-btn"
                      disabled={!key.is_active}
                      title={key.is_active ? 'Delete this API key' : 'This API key is already inactive'}
                    >
                      {key.is_active ? '🗑️ Delete' : 'Inactive'}
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="card usage-card">
            <h2>Recent Usage</h2>
            <div className="usage-list">
              {usage.length === 0 ? (
                <p className="no-usage">No stories generated yet</p>
              ) : (
                usage.map((record) => (
                  <div key={record.id} className="usage-item">
                    <div className="usage-content">
                      <div className="usage-prompt">
                        <strong>Prompt:</strong> {record.prompt}
                      </div>
                      {record.story && (
                        <div className="story-preview">
                          {record.story.length > 100
                            ? `${record.story.substring(0, 100)}...`
                            : record.story
                          }
                        </div>
                      )}
                      <div className="usage-meta">
                        <span>Credits used: {record.cost_credits}</span>
                        <span>{new Date(record.created_at).toLocaleDateString()}</span>
                        {record.tokens_used && <span>Tokens: {record.tokens_used}</span>}
                      </div>
                    </div>
                    {record.story && (
                      <div className="usage-actions">
                        <button
                          onClick={() => handleViewStory(record)}
                          className="view-story-btn"
                        >
                          View Full Story
                        </button>
                        <button
                          onClick={() => handleCopyStory(record.story!)}
                          className="copy-story-btn"
                        >
                          Copy
                        </button>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Story Modal */}
        {showStoryModal && selectedStory && (
          <div className="modal-overlay" onClick={closeStoryModal}>
            <div className="story-modal" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Generated Story</h3>
                <button onClick={closeStoryModal} className="close-modal-btn">×</button>
              </div>
              <div className="modal-content">
                <div className="story-details">
                  <p><strong>Prompt:</strong> {selectedStory.prompt}</p>
                  <p><strong>Generated on:</strong> {new Date(selectedStory.created_at).toLocaleDateString()}</p>
                  <p><strong>Credits used:</strong> {selectedStory.cost_credits}</p>
                  {selectedStory.tokens_used && <p><strong>Tokens:</strong> {selectedStory.tokens_used}</p>}
                </div>
                <div className="story-full-text">
                  {selectedStory.story}
                </div>
                <div className="modal-actions">
                  <button
                    onClick={() => handleCopyStory(selectedStory.story!)}
                    className="copy-full-story-btn"
                  >
                    Copy Story
                  </button>
                  <button onClick={closeStoryModal} className="close-btn">
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;