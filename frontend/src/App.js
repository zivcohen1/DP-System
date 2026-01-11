import axios from 'axios';
import { useEffect, useState } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [query, setQuery] = useState('');
  const [userId, setUserId] = useState('default_user');
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [budget, setBudget] = useState(null);
  const [examples, setExamples] = useState([]);
  const [tables, setTables] = useState([]);
  const [budgetHistory, setBudgetHistory] = useState([]);
  const [expandedTables, setExpandedTables] = useState({});

  useEffect(() => {
    loadExamples();
    loadTables();
    loadBudget();
    loadBudgetHistory();
  }, [userId]);

  const loadExamples = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/examples`);
      setExamples(response.data.examples);
    } catch (err) {
      console.error('Failed to load examples:', err);
    }
  };

  const loadTables = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tables`);
      setTables(response.data.tables);
    } catch (err) {
      console.error('Failed to load tables:', err);
    }
  };

  const loadBudget = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/budget/${userId}`);
      setBudget(response.data);
    } catch (err) {
      console.error('Failed to load budget:', err);
    }
  };

  const loadBudgetHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/budget/${userId}/history`);
      setBudgetHistory(response.data.history || []);
    } catch (err) {
      console.error('Failed to load budget history:', err);
    }
  };

  const executeQuery = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, {
        query: query,
        user_id: userId
      });

      if (response.data.success) {
        setResults(response.data);
        setBudget(response.data.budget);
        loadBudgetHistory(); // Reload history after query
      } else {
        setError(response.data.error);
        setBudget(response.data.budget);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to execute query');
    } finally {
      setLoading(false);
    }
  };

  const resetBudget = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/budget/${userId}/reset`);
      setBudget(response.data.budget);
      setBudgetHistory([]);
      setResults(null);
      setError(null);
    } catch (err) {
      setError('Failed to reset budget');
    }
  };

  const loadExample = (exampleQuery) => {
    setQuery(exampleQuery);
    setError(null);
    setResults(null);
  };

  const toggleTableColumns = (tableName) => {
    setExpandedTables(prev => ({
      ...prev,
      [tableName]: !prev[tableName]
    }));
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔒 DP System</h1>
        <p className="subtitle">Differential Privacy Query System</p>
      </header>

      <div className="container">
        {/* Sidebar with User Info, Budget, and Tables */}
        <div className="sidebar">
          {/* User Info */}
          <div className="user-section">
            <h3>👤 User Info</h3>
            <label>
              User ID:
              <input
                type="text"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                placeholder="Enter user ID"
              />
            </label>
          </div>

          {/* Budget Display */}
          {budget && (
            <div className="budget-display">
              <h3>💰 Privacy Budget</h3>
              <div className="budget-info">
                <span className="budget-label">Used:</span>
                <span className={`budget-value ${budget.remaining < 2 ? 'low' : ''}`}>
                  ε = {(budget.max - budget.remaining).toFixed(2)} / {budget.max.toFixed(2)}
                </span>
                <span className="budget-label">Remaining:</span>
                <span className={`budget-value ${budget.remaining < 2 ? 'low' : ''}`}>
                  ε = {budget.remaining.toFixed(2)}
                </span>
              </div>
              <button onClick={resetBudget} className="reset-button">
                Reset Budget
              </button>
            </div>
          )}

          {/* Database Tables */}
          <div className="info-section">
            <h3>📊 Database Tables</h3>
            <div className="tables-list">
              {tables.map(table => (
                <div key={table.name} className="table-detail">
                  <div className="table-header">
                    <span className="table-name">{table.name}</span>
                    <span className="table-rows">{table.row_count?.toLocaleString()} rows</span>
                  </div>
                  <div className="table-columns">
                    {table.columns?.slice(0, expandedTables[table.name] ? table.columns.length : 5).map((col, idx) => (
                      <span key={idx} className="column-tag" title={col.type}>
                        {col.name}
                      </span>
                    ))}
                    {table.columns?.length > 5 && (
                      <span 
                        className="column-tag more" 
                        onClick={() => toggleTableColumns(table.name)}
                        style={{cursor: 'pointer'}}
                      >
                        {expandedTables[table.name] 
                          ? 'Show less' 
                          : `+${table.columns.length - 5} more`}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Budget History Tracker */}
          {budgetHistory.length > 0 && (
            <div className="info-section">
              <h3>📈 Budget Usage History</h3>
              <div className="budget-history">
                {budgetHistory.slice(-5).reverse().map((entry, idx) => (
                  <div key={idx} className="history-entry">
                    <span className="history-cost">ε = {entry.cost?.toFixed(2) || '0.00'}</span>
                    <span className="history-query">{entry.query?.substring(0, 40)}...</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="main-content">
          {/* Query Editor */}
          <div className="query-section">
            <h3>✍️ Write Your Query</h3>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Example: SELECT AVG(PRIVATE Salary OF [1.0]) FROM employees LIMIT 10"
              rows="6"
              className="query-input"
            />
            <button 
              onClick={executeQuery} 
              disabled={loading}
              className="execute-button"
            >
              {loading ? 'Executing...' : '🚀 Execute Query'}
            </button>
          </div>

          {/* Example Queries */}
          <div className="examples-section">
            <h3>📝 Example Queries</h3>
            <div className="examples-grid">
              {examples.map((example, idx) => (
                <div key={idx} className="example-card" onClick={() => loadExample(example.query)}>
                  <h4>{example.title}</h4>
                  <code>{example.query}</code>
                  <p className="example-description">{example.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Results Section */}
          {error && (
            <div className="error-section">
              <h3>❌ Error</h3>
              <pre className="error-message">{error}</pre>
            </div>
          )}

          {results && results.success && (
            <div className="results-section">
              <h3>✅ Results ({results.row_count} rows)</h3>
              {results.data.length > 0 ? (
                <div className="table-container">
                  <table className="results-table">
                    <thead>
                      <tr>
                        {Object.keys(results.data[0]).map(key => (
                          <th key={key}>{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {results.data.map((row, idx) => (
                        <tr key={idx}>
                          {Object.values(row).map((value, i) => (
                            <td key={i}>{typeof value === 'number' ? value.toFixed(2) : value}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p>No results returned</p>
              )}
            </div>
          )}
        </div>
      </div>

      <footer className="App-footer">
        <p>Protected by Differential Privacy | HIPAA Compliant</p>
      </footer>
    </div>
  );
}

export default App;
