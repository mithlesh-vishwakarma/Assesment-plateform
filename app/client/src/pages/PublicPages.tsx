import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { ArrowRight, ArrowUpRight, Braces, Check, ChevronRight, Code2, GitBranch, KeyRound, LockKeyhole, ShieldCheck, Sparkles, Terminal, Trophy, Zap } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Brand, Button, Badge } from '../components/ui'
import { api, setAuthToken } from '../services/api'
const authSchema = z.object({ name: z.string().optional(), email: z.string().email('Enter a valid email address'), password: z.string().min(8, 'Use at least 8 characters') })
type AuthValues = z.infer<typeof authSchema>
export function LandingPage() { const navigate = useNavigate(); return <div className="landing-page"><header className="landing-nav"><Brand /><nav><a href="#how-it-works">How it works</a><a href="#disciplines">Disciplines</a><a href="#principles">Our principles</a></nav><div className="landing-actions"><Link to="/login" className="nav-login">Log in</Link><Button onClick={() => navigate('/register')}>Get started <ArrowRight size={16} /></Button></div></header><section className="hero"><div className="hero-grid" /><div className="hero-copy"><Badge tone="purple"><Sparkles size={12} /> ENGINEERING, EVALUATED</Badge><h1>Show us how<br />you <span>think.</span></h1><p className="hero-description">A practical engineering challenge built to understand how you solve problems, write code, and make technical decisions.</p><div className="hero-actions"><Button onClick={() => navigate('/register')}>Start your assessment <ArrowRight size={17} /></Button><a href="#how-it-works" className="text-link">Explore the process <ChevronRight size={16} /></a></div><div className="hero-trust"><div className="trust-avatars"><span>JS</span><span>RK</span><span>MP</span><span>+</span></div><div><strong>Skills over signals</strong><small>Real engineering. Thoughtful evaluation.</small></div></div></div><div className="hero-visual"><div className="glow glow-one" /><div className="code-window"><div className="window-bar"><div className="window-dots"><i /><i /><i /></div><span>challenge.ts</span><span className="window-status"><i /> Ready</span></div><div className="code-content"><div className="code-line"><span className="line-no">1</span><span><b>function</b> <em>findPair</em>(nums: <i>number[]</i>, target: <i>number</i>) {'{'}</span></div><div className="code-line"><span className="line-no">2</span><span className="indent"><b>const</b> seen = <em>new</em> Map();</span></div><div className="code-line"><span className="line-no">3</span><span className="indent"><b>for</b> (<b>let</b> i = <u>0</u>; i &lt; nums.length; i++) {'{'}</span></div><div className="code-line"><span className="line-no">4</span><span className="indent2"><b>const</b> complement = target - nums[i];</span></div><div className="code-line"><span className="line-no">5</span><span className="indent2"><b>if</b> (seen.has(complement)) {'{'}</span></div><div className="code-line"><span className="line-no">6</span><span className="indent3"><b>return</b> [seen.get(complement), i];</span></div><div className="code-line"><span className="line-no">7</span><span className="indent2">{'}'}</span></div><div className="code-line"><span className="line-no">8</span><span className="indent2">seen.set(nums[i], i);</span></div><div className="code-line"><span className="line-no">9</span><span className="indent">{'}'}</span></div><div className="code-line"><span className="line-no">10</span><span>{'}'}</span></div><div className="code-line"><span className="line-no">11</span><span className="muted-code">// Your reasoning matters, too.</span></div></div><div className="terminal-panel"><div className="terminal-heading"><Terminal size={13} /> TEST RESULTS <span>3 passed</span></div><div className="terminal-result"><Check size={13} /><span>Example case</span><small>2 ms</small></div><div className="terminal-result"><Check size={13} /><span>Edge case: duplicates</span><small>1 ms</small></div><div className="terminal-result"><Check size={13} /><span>Large input</span><small>8 ms</small></div></div></div><div className="floating-score"><div className="score-icon"><Trophy size={17} /></div><div><small>Problem solving</small><strong>Strong signal <span>↗</span></strong></div><div className="score-bars"><i /><i /><i /><i /><i /></div></div><div className="floating-secure"><ShieldCheck size={17} /><span>Fair, structured evaluation</span></div></div></section><section className="stats-strip"><div><strong>4</strong><span>Assessment stages</span></div><div><strong>10<span>+</span></strong><span>Engineering disciplines</span></div><div><strong>100%</strong><span>Skills-focused evaluation</span></div><div><strong>1:1</strong><span>Structured review</span></div></section><section className="section-block" id="how-it-works"><div className="section-heading"><div className="eyebrow">THE PROCESS</div><h2>One challenge. A clearer picture.</h2><p>A structured journey that gives you room to demonstrate how you approach engineering.</p></div><div className="process-grid">{[{ n: '01', icon: ShieldCheck, title: 'Get oriented', text: 'Review the guidelines, understand the expectations, and start with confidence.' }, { n: '02', icon: Braces, title: 'Solve real problems', text: 'Work in an in-browser coding workspace with tests and a focused environment.' }, { n: '03', icon: GitBranch, title: 'Explain your thinking', text: 'Share trade-offs, reasoning, and how you would improve your solution.' }, { n: '04', icon: Trophy, title: 'Get reviewed fairly', text: 'Your work is evaluated using a consistent, structured rubric.' }].map(item => <article className="process-card" key={item.n}><div className="process-top"><span>{item.n}</span><item.icon size={20} /></div><h3>{item.title}</h3><p>{item.text}</p></article>)}</div></section><section className="section-block discipline-section" id="disciplines"><div className="section-heading"><div className="eyebrow">BUILT FOR ENGINEERING</div><h2>More than a coding test.</h2><p>Evaluate the skills that make engineers effective in real teams.</p></div><div className="discipline-grid">{[{ icon: Code2, title: 'DSA & algorithms' }, { icon: Braces, title: 'Frontend engineering' }, { icon: Terminal, title: 'Backend & APIs' }, { icon: Zap, title: 'Mobile development' }, { icon: LockKeyhole, title: 'Application security' }, { icon: GitBranch, title: 'Databases & DevOps' }].map(x => <div className="discipline-item" key={x.title}><x.icon size={19} /><span>{x.title}</span><ArrowUpRight size={15} /></div>)}</div></section><section className="cta-section" id="principles"><div><div className="eyebrow">YOUR NEXT CHALLENGE STARTS HERE</div><h2>Let your work speak.</h2><p>Thoughtful problems. Clear expectations. A fair review process.</p></div><Button onClick={() => navigate('/register')}>Create your account <ArrowRight size={16} /></Button></section><footer className="landing-footer"><Brand /><span>© 2026 Amerigam Engineering Challenge</span><div><a href="#principles">Privacy & fairness</a><a href="mailto:support@amerigam.example">Contact</a></div></footer></div> }
export function AuthPage({ mode }: { mode: 'login' | 'register' }) {
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<AuthValues>({ resolver: zodResolver(authSchema) });

  const onSubmit = async (data: AuthValues) => {
    setError('');
    const inferredRole = (data.email.toLowerCase().includes('admin') ? 'admin' : data.email.toLowerCase().includes('review') ? 'reviewer' : 'candidate') as 'admin' | 'reviewer' | 'candidate';

    const saveAndProceed = (user: any, token?: string) => {
      if (token) setAuthToken(token);
      const role = (user?.profile?.role?.toLowerCase() || inferredRole) as 'admin' | 'reviewer' | 'candidate';
      const displayName = user?.first_name || data.name || user?.username || data.email.split('@')[0];
      localStorage.setItem('aec-session', JSON.stringify({ name: displayName, email: data.email, role, mode: token ? 'api' : 'demo' }));
      localStorage.setItem('aec-active-role', role);
      navigate(role === 'admin' ? '/admin' : role === 'reviewer' ? '/reviewer' : '/candidate');
    };

    try {
      if (mode === 'login') {
        const res = await api.auth.login({
          email: data.email,
          username: data.email,
          password: data.password,
        });
        saveAndProceed(res.user, res.token);
      } else {
        const res = await api.auth.register({
          name: data.name,
          email: data.email,
          password: data.password,
          role: inferredRole.toUpperCase(),
        });
        saveAndProceed(res.user, res.token);
      }
    } catch (err: any) {
      console.warn('API authentication error:', err.message);
      setError(err.message || 'Authentication failed. Please check your credentials.');
    }
  };

  return <div className="auth-page"><div className="auth-art"><div className="auth-art-grid" /><Brand /><div className="auth-art-content"><Badge tone="purple"><Sparkles size={12} /> ENGINEERING, EVALUATED</Badge><h1>Great engineering<br />starts with <span>curiosity.</span></h1><p>Show your process, not just your answer. A thoughtful way to demonstrate your engineering skills.</p><div className="auth-perks"><div><Check size={15} /> Clear assessment stages</div><div><Check size={15} /> Real coding workspace</div><div><Check size={15} /> Structured, fair review</div></div></div><div className="auth-art-bottom">AMERIGAM <span>·</span> ENGINEERING CHALLENGE</div></div><div className="auth-form-side"><div className="auth-mobile-brand"><Brand /></div><div className="auth-form-wrap"><Link className="back-home" to="/"><ChevronRight size={15} className="back-chevron" /> Back to home</Link><div className="eyebrow">{mode === 'login' ? 'WELCOME BACK' : 'GET STARTED'}</div><h2>{mode === 'login' ? 'Sign in to your workspace' : 'Create your account'}</h2><p className="auth-subtitle">{mode === 'login' ? 'Continue where you left off.' : 'Start your engineering assessment journey.'}</p><form onSubmit={handleSubmit(onSubmit)} className="auth-form">{mode === 'register' && <label>Full name<input {...register('name')} placeholder="e.g. Mithlesh Vishwakarma" />{errors.name && <small className="field-error">{errors.name.message}</small>}</label>}<label>Email address<input {...register('email')} type="email" placeholder="you@example.com" autoComplete="email" />{errors.email && <small className="field-error">{errors.email.message}</small>}</label><label>Password<div className="password-wrap"><input {...register('password')} type={showPassword ? 'text' : 'password'} placeholder="At least 8 characters" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} /><button type="button" onClick={() => setShowPassword(!showPassword)}>{showPassword ? 'Hide' : 'Show'}</button></div>{errors.password && <small className="field-error">{errors.password.message}</small>}</label>{mode === 'login' && <div className="forgot-row"><Link to="/forgot-password" style={{ color: '#b9a6ff' }}>Forgot password?</Link><a href="mailto:support@amerigam.com">Need help?</a></div>}{error && <div className="form-notice">{error}</div>}<Button type="submit" className="auth-submit" disabled={isSubmitting}>{isSubmitting ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'} <ArrowRight size={16} /></Button></form><div className="auth-switch">{mode === 'login' ? 'New to Amerigam?' : 'Already have an account?'} <Link to={mode === 'login' ? '/register' : '/login'}>{mode === 'login' ? 'Create an account' : 'Sign in'}</Link></div><div className="auth-legal"><LockKeyhole size={13} /> Your information is handled securely. <Link to="/rules">Assessment rules</Link></div></div></div></div> }
export function RulesPage() { const navigate = useNavigate(); const [accepted, setAccepted] = useState(false); return <div className="rules-page"><header className="landing-nav"><Brand /><Link to="/candidate" className="nav-login">Exit to dashboard</Link></header><main className="rules-content"><div className="eyebrow">BEFORE YOU BEGIN</div><h1>Assessment rules & consent</h1><p className="rules-intro">A few important details to help you have a fair, focused assessment experience.</p><div className="rule-list">{[{ n: '01', title: 'Work independently', text: 'Submit your own work. You may use only the resources allowed in the assessment instructions.' }, { n: '02', title: 'Manage your time', text: 'Each timed stage has a server-controlled deadline. Your progress and remaining time are confirmed by the platform.' }, { n: '03', title: 'Explain your reasoning', text: 'Some tasks ask you to describe trade-offs, complexity, assumptions, or what you would improve.' }, { n: '04', title: 'Respect the environment', text: 'The platform may record technical integrity signals, such as focus changes, for reviewer context. No single event automatically proves misconduct.' }, { n: '05', title: 'Know your screen requirements', text: 'Coding challenges are designed for desktop or laptop screens. Before starting a timed coding stage, use a supported desktop-sized viewport and a stable connection.' }].map(r => <article className="rule-card" key={r.n}><span>{r.n}</span><div><h3>{r.title}</h3><p>{r.text}</p></div></article>)}</div><label className="consent-check"><input type="checkbox" checked={accepted} onChange={e => setAccepted(e.target.checked)} /><span>I have read and understood the assessment rules and agree to proceed.</span></label><Button disabled={!accepted} onClick={() => navigate('/candidate')}>I agree and continue <ArrowRight size={16} /></Button><p className="rules-note">This demo consent is local UI state. Production consent must be recorded by the backend.</p></main></div> }

export function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialEmail = searchParams.get('email') || '';
  const initialToken = searchParams.get('token') || '';

  const [step, setStep] = useState<'request' | 'confirm' | 'success'>(
    initialToken ? 'confirm' : 'request'
  );
  const [email, setEmail] = useState(initialEmail);
  const [token, setToken] = useState(initialToken);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [infoMessage, setInfoMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleRequestToken = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setInfoMessage('');
    if (!email || !email.includes('@')) {
      setError('Please provide a valid email address.');
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await api.auth.passwordResetRequest(email.trim());
      if (res.reset_token) {
        setToken(res.reset_token);
        setInfoMessage('Reset token generated successfully! Enter your new password below.');
      } else {
        setInfoMessage(res.message || 'If an account exists for this email, reset instructions were generated.');
      }
      setStep('confirm');
    } catch (err: any) {
      setError(err.message || 'Failed to request password reset.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleConfirmReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!token.trim()) {
      setError('Password reset token is required.');
      return;
    }
    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await api.auth.passwordResetConfirm({
        email: email.trim(),
        token: token.trim(),
        new_password: newPassword,
      });
      if (res.token) {
        setAuthToken(res.token);
      }
      setStep('success');
    } catch (err: any) {
      setError(err.message || 'Password reset failed. Token may be invalid or expired.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-art">
        <div className="auth-art-grid" />
        <Brand />
        <div className="auth-art-content">
          <Badge tone="purple"><KeyRound size={12} /> ACCOUNT SECURITY</Badge>
          <h1>Secure recovery for your <span>workspace.</span></h1>
          <p>Reset your credentials safely using cryptographically verified single-use tokens.</p>
          <div className="auth-perks">
            <div><Check size={15} /> Instant cryptographic reset tokens</div>
            <div><Check size={15} /> Direct password encryption & update</div>
            <div><Check size={15} /> Works for Candidate, Reviewer & Admin accounts</div>
          </div>
        </div>
        <div className="auth-art-bottom">AMERIGAM <span>·</span> SECURITY PROTOCOL</div>
      </div>

      <div className="auth-form-side">
        <div className="auth-mobile-brand"><Brand /></div>
        <div className="auth-form-wrap">
          <Link className="back-home" to="/login">
            <ChevronRight size={15} className="back-chevron" /> Back to sign in
          </Link>

          {step === 'request' && (
            <>
              <div className="eyebrow">PASSWORD RECOVERY</div>
              <h2>Reset your password</h2>
              <p className="auth-subtitle">Enter your account email to receive your password reset token.</p>

              <form onSubmit={handleRequestToken} className="auth-form">
                <label>
                  Account email address
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@amerigam.com"
                    autoComplete="email"
                    required
                  />
                </label>

                {error && (
                  <div className="form-notice" style={{ borderColor: '#783044', background: '#301c22', color: '#ff9aa8' }}>
                    {error}
                  </div>
                )}

                <Button type="submit" className="auth-submit" disabled={isSubmitting}>
                  {isSubmitting ? 'Requesting token…' : 'Generate reset token'} <ArrowRight size={16} />
                </Button>
              </form>

              <div className="auth-switch">
                Remember your password? <Link to="/login">Sign in</Link>
              </div>
            </>
          )}

          {step === 'confirm' && (
            <>
              <div className="eyebrow">STEP 2 OF 2</div>
              <h2>Set new password</h2>
              <p className="auth-subtitle">
                Enter your reset token and new password for <strong>{email}</strong>
              </p>

              {infoMessage && (
                <div className="form-notice" style={{ borderColor: '#2b5042', background: '#132c25', color: '#7ce2a5', marginBottom: 16 }}>
                  {infoMessage}
                </div>
              )}

              <form onSubmit={handleConfirmReset} className="auth-form">
                <label>
                  Reset token
                  <input
                    type="text"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    placeholder="Enter or paste reset token"
                    required
                  />
                </label>

                <label>
                  New password
                  <div className="password-wrap">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="At least 8 characters"
                      autoComplete="new-password"
                      required
                    />
                    <button type="button" onClick={() => setShowPassword(!showPassword)}>
                      {showPassword ? 'Hide' : 'Show'}
                    </button>
                  </div>
                </label>

                <label>
                  Confirm new password
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Repeat new password"
                    autoComplete="new-password"
                    required
                  />
                </label>

                {error && (
                  <div className="form-notice" style={{ borderColor: '#783044', background: '#301c22', color: '#ff9aa8' }}>
                    {error}
                  </div>
                )}

                <Button type="submit" className="auth-submit" disabled={isSubmitting}>
                  {isSubmitting ? 'Updating password…' : 'Update password'} <ArrowRight size={16} />
                </Button>
              </form>

              <div className="auth-switch">
                Need to change email?{' '}
                <button
                  type="button"
                  onClick={() => { setStep('request'); setError(''); }}
                  style={{ background: 'none', border: 0, color: '#c1a7ff', cursor: 'pointer', fontWeight: 600, padding: 0 }}
                >
                  Try another email
                </button>
              </div>
            </>
          )}

          {step === 'success' && (
            <>
              <div className="eyebrow" style={{ color: '#7ce2a5' }}>SUCCESS</div>
              <h2>Password updated!</h2>
              <p className="auth-subtitle">Your password has been securely updated. You can now log in to your account with your new credentials.</p>

              <div className="panel" style={{ background: '#12251e', borderColor: '#24523d', textAlign: 'center', padding: '24px 20px', marginBottom: 20 }}>
                <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 48, height: 48, borderRadius: '50%', background: '#1c4232', color: '#6fe0a0', marginBottom: 12 }}>
                  <Check size={24} />
                </div>
                <h3 style={{ color: '#e8eaf3', marginBottom: 6 }}>Ready to sign in</h3>
                <p style={{ fontSize: 11, color: '#97d2b4', margin: 0 }}>All prior sessions have been invalidated for security.</p>
              </div>

              <Button onClick={() => navigate('/login')} className="auth-submit">
                Continue to sign in <ArrowRight size={16} />
              </Button>
            </>
          )}

          <div className="auth-legal">
            <LockKeyhole size={13} /> Secure recovery powered by Django cryptographic token generator.
          </div>
        </div>
      </div>
    </div>
  );
}

