import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000/api'

function App() {
  const [health, setHealth] = useState({ status: 'checking', message: 'Checking backend...' })
  const [assessments, setAssessments] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [newTitle, setNewTitle] = useState('')
  const [newDesc, setNewDesc] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const fetchHealth = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/health/`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setHealth(data)
      setError(null)
    } catch (err) {
      setHealth({ status: 'offline', message: 'Backend not reachable' })
      setError(err.message)
    }
  }

  const fetchAssessments = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE_URL}/assessments/`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setAssessments(data)
    } catch (err) {
      console.error('Failed to fetch assessments:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHealth()
    fetchAssessments()
  }, [])

  const handleCreateAssessment = async (e) => {
    e.preventDefault()
    if (!newTitle.trim()) return

    setSubmitting(true)
    try {
      const res = await fetch(`${API_BASE_URL}/assessments/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle.trim(),
          description: newDesc.trim(),
          is_active: true
        })
      })

      if (!res.ok) throw new Error(`Failed to create assessment (HTTP ${res.status})`)
      const created = await res.json()
      setAssessments((prev) => [created, ...prev])
      setNewTitle('')
      setNewDesc('')
    } catch (err) {
      alert(`Error creating assessment: ${err.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  const isConnected = health.status === 'success' || health.status === 'ok'

  return (
    <div className="starter-container">
      {/* Top Navbar */}
      <header className="navbar">
        <div className="brand">
          <div className="brand-badge">PRO</div>
          <span className="brand-title">Assessment Platform Starter</span>
        </div>
        <div className="status-pill">
          <span className={`status-dot ${isConnected ? 'dot-online' : 'dot-offline'}`} />
          <span className="status-text">
            {isConnected ? 'Django DRF Connected' : 'Django DRF Offline'}
          </span>
          <button 
            type="button" 
            className="refresh-btn" 
            onClick={() => { fetchHealth(); fetchAssessments(); }}
            title="Refresh status"
          >
            ↻
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="tech-stack-pills">
          <div className="tech-badge">
            <img src={viteLogo} className="tech-icon" alt="Vite" />
            <span>Vite</span>
          </div>
          <span className="plus">+</span>
          <div className="tech-badge">
            <img src={reactLogo} className="tech-icon react-spin" alt="React" />
            <span>React</span>
          </div>
          <span className="plus">+</span>
          <div className="tech-badge py-badge">
            <span className="py-icon">🐍</span>
            <span>Django REST</span>
          </div>
        </div>

        <h1 className="hero-title">
          React <span className="gradient-text">&</span> Django REST API Starter
        </h1>
        <p className="hero-subtitle">
          A full-stack scaffolding ready for development. The client is built with React + Vite, 
          and the server is powered by Python Django REST Framework with CORS configured.
        </p>
      </section>

      {/* Main Grid */}
      <main className="content-grid">
        {/* Left Column: Backend API Demo */}
        <div className="card">
          <div className="card-header">
            <h2>Live REST API Integration</h2>
            <span className={`tag ${isConnected ? 'tag-success' : 'tag-warning'}`}>
              {isConnected ? '200 OK' : 'Waiting for Server'}
            </span>
          </div>

          <div className="api-status-box">
            <div className="status-row">
              <span className="status-label">API Health Endpoint:</span>
              <code>GET /api/health/</code>
            </div>
            <div className="status-row">
              <span className="status-label">Status:</span>
              <span className="status-val">{health.message || 'Connecting...'}</span>
            </div>
            {error && (
              <p className="notice-error">
                Start the backend server on port 8000 to enable communication.
              </p>
            )}
          </div>

          {/* Create Assessment Form */}
          <form className="create-form" onSubmit={handleCreateAssessment}>
            <h3>Create New Assessment (POST /api/assessments/)</h3>
            <div className="form-group">
              <input
                type="text"
                placeholder="Assessment title (e.g., Python Backend Test)"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <textarea
                placeholder="Description or test instructions..."
                rows="2"
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
              />
            </div>
            <button
              type="submit"
              className="submit-btn"
              disabled={submitting || !newTitle.trim()}
            >
              {submitting ? 'Creating...' : '+ Create Assessment'}
            </button>
          </form>

          {/* Assessments List */}
          <div className="assessments-list-section">
            <div className="list-header">
              <h3>Existing Assessments ({assessments.length})</h3>
              {loading && <span className="loading-spinner">Loading...</span>}
            </div>

            {assessments.length === 0 && !loading ? (
              <p className="empty-text">No assessments found. Create your first one above!</p>
            ) : (
              <ul className="assessments-list">
                {assessments.map((item) => (
                  <li key={item.id} className="assessment-item">
                    <div className="item-main">
                      <strong className="item-title">{item.title}</strong>
                      <p className="item-desc">{item.description || 'No description provided.'}</p>
                    </div>
                    <span className={`badge ${item.is_active ? 'badge-active' : 'badge-inactive'}`}>
                      {item.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Right Column: Quick Start Commands & Architecture */}
        <div className="card">
          <div className="card-header">
            <h2>Development Commands</h2>
            <span className="tag tag-info">Quick Guide</span>
          </div>

          <div className="guide-block">
            <h4>1. Start Django Backend Server</h4>
            <p className="guide-sub">Run from <code>app/server/</code>:</p>
            <div className="code-card">
              <code>.\venv\Scripts\python manage.py runserver</code>
            </div>
            <p className="guide-caption">Runs the REST API at <code>http://127.0.0.1:8000/api/</code></p>
          </div>

          <div className="guide-block">
            <h4>2. Start React + Vite Client</h4>
            <p className="guide-sub">Run from <code>app/client/</code>:</p>
            <div className="code-card">
              <code>npm run dev</code>
            </div>
            <p className="guide-caption">Runs the frontend at <code>http://localhost:5173/</code></p>
          </div>

          <div className="guide-block">
            <h4>3. Configured Endpoints</h4>
            <ul className="endpoints-list">
              <li>
                <span className="method get">GET</span>
                <code>/api/health/</code>
                <span className="desc">Server Health Check</span>
              </li>
              <li>
                <span className="method get">GET</span>
                <code>/api/assessments/</code>
                <span className="desc">List All Assessments</span>
              </li>
              <li>
                <span className="method post">POST</span>
                <code>/api/assessments/</code>
                <span className="desc">Create Assessment</span>
              </li>
              <li>
                <span className="method admin">ADMIN</span>
                <code>/admin/</code>
                <span className="desc">Django Admin Portal</span>
              </li>
            </ul>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>Assessment Platform • React Vite + Django REST Framework Starter</p>
      </footer>
    </div>
  )
}

export default App
