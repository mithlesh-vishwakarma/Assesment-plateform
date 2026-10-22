import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import {
  Activity, Bell, BookOpen, Boxes, BriefcaseBusiness, CheckSquare,
  ChevronDown, CircleHelp, Code2, FileText, Flag, Gauge, GitBranch,
  LayoutDashboard, LogOut, Menu, MessageSquareText, Search, Settings2,
  ShieldCheck, Users, X, Command
} from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Brand } from './ui'
import { clearAuthToken } from '../services/api'

const candidateLinks = [
  { to: '/candidate', label: 'Overview', icon: LayoutDashboard, end: true },
  { to: '/candidate/assessment', label: 'My assessment', icon: Code2 },
  { to: '/candidate/history', label: 'Progress history', icon: GitBranch },
  { to: '/candidate/reasoning', label: 'Written reasoning', icon: FileText },
  { to: '/candidate/help', label: 'Help & guidelines', icon: CircleHelp }
]

const adminLinks = [
  { to: '/admin', label: 'Overview', icon: Gauge, end: true },
  { to: '/admin/candidates', label: 'Candidates', icon: Users },
  { to: '/admin/campaigns', label: 'Campaigns', icon: BriefcaseBusiness },
  { to: '/admin/stages', label: 'Stage builder', icon: Boxes },
  { to: '/admin/questions', label: 'Question bank', icon: BookOpen },
  { to: '/admin/rubrics', label: 'Evaluation rubrics', icon: CheckSquare },
  { to: '/admin/integrity', label: 'Integrity review', icon: ShieldCheck },
  { to: '/admin/comparison', label: 'Candidate comparison', icon: Activity }
]

const reviewerLinks = [
  { to: '/reviewer', label: 'Review queue', icon: LayoutDashboard, end: true },
  { to: '/reviewer/scorecards', label: 'Scorecards', icon: FileText },
  { to: '/reviewer/integrity', label: 'Integrity events', icon: Flag }
]

export function AppLayout({ role = 'candidate' }: { role?: 'candidate' | 'admin' | 'reviewer' }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [activeSearchIndex, setActiveSearchIndex] = useState(0)
  const [profileOpen, setProfileOpen] = useState(false)
  const [notificationsOpen, setNotificationsOpen] = useState(false)

  const [session] = useState<any>(() => {
    try {
      return JSON.parse(localStorage.getItem('aec-session') || 'null')
    } catch {
      return null
    }
  })

  const location = useLocation()
  const navigate = useNavigate()
  const links = role === 'admin' ? adminLinks : role === 'reviewer' ? reviewerLinks : candidateLinks
  const roleLabel = role === 'admin' ? 'Administrator' : role === 'reviewer' ? 'Reviewer' : 'Candidate'

  const userName = session?.name || ''
  const defaultInitials = role === 'admin' ? 'AD' : role === 'reviewer' ? 'RV' : 'CD'
  const initials = useMemo(() => {
    if (!userName || !userName.trim()) return defaultInitials
    const parts = userName.trim().split(/\s+/)
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
    }
    return parts[0].slice(0, 2).toUpperCase()
  }, [userName, defaultInitials])

  const pageLabel = links.find(link => link.end ? location.pathname === link.to : location.pathname.startsWith(link.to))?.label ?? 'Workspace'
  const allLinks = [...candidateLinks, ...adminLinks, ...reviewerLinks]
  const matches = useMemo(() => allLinks.filter(x => x.label.toLowerCase().includes(search.toLowerCase())), [search])

  useEffect(() => {
    const fn = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setSearchOpen(v => !v)
      }
      if (e.key === 'Escape') {
        setSearchOpen(false)
        setProfileOpen(false)
        setNotificationsOpen(false)
      }
    }
    window.addEventListener('keydown', fn)
    return () => window.removeEventListener('keydown', fn)
  }, [])

  const logout = () => {
    clearAuthToken()
    setProfileOpen(false)
    navigate('/login', { replace: true })
  }

  return (
    <div className="app-shell">
      {mobileOpen && (
        <button className="mobile-scrim" aria-label="Close navigation" onClick={() => setMobileOpen(false)} />
      )}

      <aside className={`sidebar ${mobileOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-brand">
          <Brand />
          <button className="mobile-close" onClick={() => setMobileOpen(false)} aria-label="Close menu">
            <X size={18} />
          </button>
        </div>

        <div className="workspace-label">WORKSPACE</div>

        <nav className="side-nav" aria-label={`${roleLabel} navigation`}>
          {links.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={'end' in item ? item.end : false}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
              {item.label === 'Integrity review' && <span className="nav-count">3</span>}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon"><MessageSquareText size={17} /></div>
            <strong>Need a hand?</strong>
            <p>Find answers and assessment guidance.</p>
            <button onClick={() => navigate(role === 'candidate' ? '/candidate/help' : '/reviewer/integrity')}>
              Visit help center <span>↗</span>
            </button>
          </div>

          <div className="sidebar-user">
            <div className="avatar avatar-violet">{initials}</div>
            <div className="user-info">
              <strong title={userName || roleLabel}>
                {userName || (role === 'candidate' ? 'Candidate workspace' : role === 'admin' ? 'Admin workspace' : 'Reviewer workspace')}
              </strong>
              <span>{session?.email || roleLabel}</span>
            </div>
            <button className="icon-button" title="Account menu" onClick={() => navigate('/settings')}>
              <ChevronDown size={17} />
            </button>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button className="mobile-menu icon-button" onClick={() => setMobileOpen(true)} aria-label="Open navigation">
              <Menu size={20} />
            </button>
            <div className="breadcrumb">
              Workspace <span>/</span> <strong>{pageLabel}</strong>
            </div>
          </div>

          <div className="topbar-actions">
            <button className="search-pill" onClick={() => setSearchOpen(true)} aria-label="Search workspace">
              <Search size={15} />
              <span>Search anything</span>
              <kbd><Command size={11} /> K</kbd>
            </button>

            <div className="popover-anchor">
              <button
                className="icon-button notification-button"
                aria-label="Notifications"
                onClick={() => setNotificationsOpen(v => !v)}
              >
                <Bell size={18} />
                <i />
              </button>
              {notificationsOpen && (
                <div className="mini-popover">
                  <strong>Notifications</strong>
                  <p>Platform notifications active.</p>
                  <button onClick={() => setNotificationsOpen(false)}>Mark as read</button>
                </div>
              )}
            </div>

            <div className="topbar-divider" />

            <div className="popover-anchor">
              <button className="role-switch" onClick={() => setProfileOpen(v => !v)} title="Account menu">
                <div className="avatar avatar-small">{initials}</div>
                <ChevronDown size={14} />
              </button>
              {profileOpen && (
                <div className="mini-popover account-popover">
                  <div style={{ paddingBottom: '8px', marginBottom: '4px', borderBottom: '1px solid var(--border)' }}>
                    <strong>{userName || roleLabel}</strong>
                    {session?.email && (
                      <p style={{ margin: '3px 0 0', fontSize: '11px', color: 'var(--muted)', wordBreak: 'break-all' }}>
                        {session.email}
                      </p>
                    )}
                  </div>
                  <button onClick={() => { setProfileOpen(false); navigate('/settings'); }}>
                    <Settings2 size={15} /> Account settings
                  </button>
                  <button className="logout-action" onClick={logout}>
                    <LogOut size={15} /> Log out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <div className="content-wrap">
          <Outlet />
        </div>

        <footer className="app-footer">
          <span>© 2026 Amerigam Engineering Challenge</span>
          <div>
            <span><i className="online-dot" /> Live connected</span>
            <a href="mailto:support@amerigam.example">Support</a>
            <a href={role === 'candidate' ? '/candidate/help' : '/admin'}>Documentation</a>
            <button onClick={logout}>Log out</button>
          </div>
        </footer>
      </main>

      {searchOpen && (
        <div
          className="modal-backdrop search-backdrop"
          role="presentation"
          onMouseDown={e => { if (e.target === e.currentTarget) setSearchOpen(false) }}
        >
          <section className="global-search panel" role="dialog" aria-modal="true" aria-label="Search workspace">
            <div className="global-search-input">
              <Search size={18} />
              <input
                autoFocus
                value={search}
                onChange={e => { setSearch(e.target.value); setActiveSearchIndex(0); }}
                onKeyDown={e => {
                  if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    setActiveSearchIndex(i => Math.min(matches.length - 1, i + 1));
                  } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    setActiveSearchIndex(i => Math.max(0, i - 1));
                  } else if (e.key === 'Enter' && matches[activeSearchIndex]) {
                    navigate(matches[activeSearchIndex].to);
                    setSearchOpen(false);
                    setSearch('');
                  }
                }}
                placeholder="Search pages and workspaces…"
              />
              <kbd>ESC</kbd>
            </div>
            <div className="global-search-results">
              <span className="eyebrow">NAVIGATION</span>
              {matches.map((item, index) => (
                <button
                  key={item.to}
                  className={index === activeSearchIndex ? 'search-active' : ''}
                  onMouseEnter={() => setActiveSearchIndex(index)}
                  onClick={() => {
                    navigate(item.to);
                    setSearchOpen(false);
                    setSearch('');
                  }}
                >
                  <item.icon size={17} />
                  <span>{item.label}</span>
                  <span className="search-result-group">Open page ↗</span>
                </button>
              ))}
              {matches.length === 0 && (
                <p className="empty-search">No matching pages. Try “candidate”, “question”, or “scorecard”.</p>
              )}
            </div>
            <div className="search-footer">Use ↑ and ↓ to browse · Enter to open · Esc to close</div>
          </section>
        </div>
      )}
    </div>
  )
}
