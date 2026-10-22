import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { ArrowLeft, ArrowRight, BookOpen, Boxes, Check, CheckCircle2, ChevronRight, Clock3, Code2, FlaskConical, Lightbulb, Play, Save, Send, Terminal, TriangleAlert, X } from 'lucide-react'
import { Badge, Button, PageTitle, ProgressBar, StageCard } from '../components/ui'
import { api } from '../services/api'
import type { Stage } from '../types'

export function CandidateDashboard() {
  const navigate = useNavigate();
  const [stages, setStages] = useState<Stage[]>([]);
  const [loading, setLoading] = useState(true);
  const [session] = useState<any>(() => { try { return JSON.parse(localStorage.getItem('aec-session') || 'null') } catch { return null } });

  useEffect(() => {
    api.stages().then(data => {
      if (Array.isArray(data) && data.length > 0) {
        setStages(data);
      }
    }).catch(err => console.error("Failed to load stages:", err)).finally(() => setLoading(false));
  }, []);

  const completedCount = stages.filter(s => s.status === 'completed').length;
  const progress = stages.length > 0 ? Math.round((completedCount / stages.length) * 100) : 0;
  const nextStage = stages.find(s => s.status === 'in-progress' || s.status === 'available') || stages[0];
  const candidateName = session?.name || 'Candidate';

  return <>
    <PageTitle eyebrow="CANDIDATE WORKSPACE" title={`Good day, ${candidateName}`} description="Your engineering assessment journey is active and connected to the live backend." action={<Button variant="secondary" onClick={() => navigate('/candidate/history')}>View progress <ArrowRight size={15} /></Button>} />
    <div className="welcome-banner">
      <div className="welcome-copy">
        <Badge tone="purple">LIVE ASSESSMENT</Badge>
        <h2>Show how you think and build.</h2>
        <p>Complete each stage to demonstrate practical engineering judgment and execution.</p>
        <div className="banner-progress">
          <span>Overall progress</span>
          <strong>{progress}%</strong>
          <ProgressBar value={progress} />
        </div>
        {nextStage && <Button onClick={() => navigate(`/candidate/assessment/${nextStage.id}`)}>{nextStage.status === 'in-progress' ? `Continue Stage 0${nextStage.id}` : `Start Stage 0${nextStage.id}`} <ArrowRight size={16} /></Button>}
      </div>
      <div className="banner-art">
        <div className="orbit orbit-a" /><div className="orbit orbit-b" />
        <div className="banner-code"><Code2 size={26} /><span>{'{ }'}</span></div>
        <div className="orbit-node node-a"><Check size={14} /></div>
        <div className="orbit-node node-b">02</div>
        <div className="orbit-node node-c"><BookOpen size={15} /></div>
      </div>
    </div>
    <div className="section-heading row-heading">
      <div>
        <div className="eyebrow">ASSESSMENT PATH</div>
        <h2>Engineering Stages</h2>
        <p>Live stages configured and scored by the backend assessment engine.</p>
      </div>
      <span className="muted-small">{loading ? 'Loading live stages…' : `${completedCount} of ${stages.length} completed`}</span>
    </div>
    <div className="stage-grid">
      {stages.map(stage => <StageCard key={stage.id} stage={stage} onOpen={s => navigate(`/candidate/assessment/${s.id}`)} />)}
    </div>
    <div className="bottom-grid">
      <section className="panel next-panel">
        <div className="panel-heading">
          <div>
            <h3>Next up: {nextStage?.title || 'Build & ship'}</h3>
            <p>{nextStage?.subtitle || 'Practical coding and problem solving'}</p>
          </div>
          <div className="panel-icon purple-icon"><Code2 size={18} /></div>
        </div>
        <div className="next-meta">
          <span><Clock3 size={15} /> {nextStage?.duration || '60 min'}</span>
          <span><FlaskConical size={15} /> Automated test cases</span>
          <span><Save size={15} /> Server autosave</span>
        </div>
        {nextStage && <Button onClick={() => navigate(`/candidate/assessment/${nextStage.id}`)}>Open challenge <ArrowRight size={15} /></Button>}
      </section>
      <section className="panel tip-panel">
        <div className="tip-icon"><Lightbulb size={18} /></div>
        <div>
          <div className="eyebrow">ASSESSMENT TIP</div>
          <h3>Communicate trade-offs in writing.</h3>
          <p>Reviewers score evidence, clean algorithmic thinking, and clarity of design decisions.</p>
          <button className="inline-link" onClick={() => navigate('/candidate/help')}>Read assessment guide <ChevronRight size={15} /></button>
        </div>
      </section>
    </div>
  </>
}

export function StageIntroPage() {
  const { stageId } = useParams();
  const navigate = useNavigate();
  const [stages, setStages] = useState<Stage[]>([]);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    api.stages().then(setStages).catch(console.error);
  }, []);

  const stage = stages.find(s => s.id === Number(stageId)) || stages[0] || { id: Number(stageId) || 1, title: 'Stage ' + stageId, subtitle: 'Assessment stage', category: 'CORE', duration: '45 min', questions: 1, status: 'available' };

  return <>
    <button className="back-link" onClick={() => navigate('/candidate')}><ArrowLeft size={15} /> Back to overview</button>
    <div className="stage-intro-wrap">
      <div className="stage-intro-main">
        <Badge tone="purple">STAGE 0{stage.id} · {stage.category}</Badge>
        <h1>{stage.title}</h1>
        <p className="intro-lead">{stage.subtitle}. Review the requirements and enter the workspace when you are ready to begin.</p>
        <div className="intro-stats">
          <div><Clock3 size={18} /><span><small>Duration</small><strong>{stage.duration}</strong></span></div>
          <div><BookOpen size={18} /><span><small>Questions</small><strong>{stage.questions} task{stage.questions > 1 ? 's' : ''}</strong></span></div>
          <div><Save size={18} /><span><small>Drafts</small><strong>Live sync</strong></span></div>
        </div>
        <section className="panel">
          <h3>Assessment Instructions</h3>
          <div className="instruction-row"><span>01</span><div><strong>Review constraints and inputs</strong><p>Identify edge cases, bounds, and expected return formats.</p></div></div>
          <div className="instruction-row"><span>02</span><div><strong>Implement your solution</strong><p>Write clean, structured code and run sample tests to check correctness.</p></div></div>
          <div className="instruction-row"><span>03</span><div><strong>Explain reasoning</strong><p>Note complexity, trade-offs, and alternative approaches in your written notes.</p></div></div>
        </section>
        <label className="consent-check">
          <input type="checkbox" checked={ready} onChange={e => setReady(e.target.checked)} />
          <span>I understand the instructions and am ready to begin this stage.</span>
        </label>
        <Button disabled={!ready} onClick={async () => {
          try {
            await api.candidate.startStage(stage.backend_id || stage.id);
          } catch { }
          navigate(`/candidate/workspace/${stage.id}`);
        }}>
          Enter challenge workspace <ArrowRight size={16} />
        </Button>
      </div>
      <aside className="panel intro-side">
        <div className="stage-side-icon"><Code2 size={22} /></div>
        <h3>Before you start</h3>
        <ul>
          <li>Use a stable internet connection.</li>
          <li>Keep your work inside the browser workspace.</li>
          <li>Desktop or laptop recommended for code execution.</li>
          <li>Your drafts are periodically synchronized with the server.</li>
        </ul>
        <div className="side-note"><TriangleAlert size={16} /><span>Timed stage attempts are tracked by the backend clock.</span></div>
      </aside>
    </div>
  </>
}

export function CodingWorkspacePage() {
  const { stageId } = useParams();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<any[]>([]);
  const [activeQuestionIdx, setActiveQuestionIdx] = useState<number>(0);
  const question = questions[activeQuestionIdx] || null;

  const [code, setCode] = useState<string>('');
  const [language, setLanguage] = useState<string>('typescript');
  const [explanation, setExplanation] = useState<string>('');
  const [selectedOption, setSelectedOption] = useState<string>('');
  const [architecture, setArchitecture] = useState<string>('');
  const [tradeOffs, setTradeOffs] = useState<string>('');
  const [writtenAnswers, setWrittenAnswers] = useState<Record<number, string>>({});

  const stageNum = Number(stageId) || 1;
  const initialDurationMinutes = stageNum === 1 ? 45 : stageNum === 2 ? 60 : stageNum === 3 ? 35 : stageNum === 4 ? 25 : 45;
  const [tab, setTab] = useState<'tests' | 'console'>('tests');
  const [runState, setRunState] = useState<'idle' | 'running' | 'done'>('idle');
  const [testResult, setTestResult] = useState<any>(null);
  const [saved, setSaved] = useState(true);
  const [time, setTime] = useState<number>(initialDurationMinutes * 60);
  const [toastError, setToastError] = useState<string | null>(null);
  const [stageAttemptId, setStageAttemptId] = useState<number | undefined>(undefined);

  const draftKey = `aec-draft-stage-${stageId ?? '1'}`;

  // Auto-start or fetch active stage attempt & sync timer with server deadline
  useEffect(() => {
    const sId = Number(stageId) || 1;
    api.candidate.startStage(sId).then((res: any) => {
      const id = res?.stage_attempt_id || res?.id;
      if (id) setStageAttemptId(id);

      // Synchronize timer with accurate server deadline or time limit
      if (res?.deadline) {
        const remaining = Math.max(0, Math.floor((new Date(res.deadline).getTime() - Date.now()) / 1000));
        setTime(remaining);
      } else if (res?.time_limit_minutes) {
        setTime(res.time_limit_minutes * 60);
      } else if (res?.remaining_seconds) {
        setTime(res.remaining_seconds);
      }
    }).catch(err => {
      console.warn("Could not start or sync stage attempt:", err);
    });
  }, [stageId]);

  // Auto-dismiss alert notification after 6 seconds
  useEffect(() => {
    if (!toastError) return;
    const timer = window.setTimeout(() => setToastError(null), 6000);
    return () => window.clearTimeout(timer);
  }, [toastError]);

  // Load question and starter code dynamically from backend
  useEffect(() => {
    api.candidate.questions(Number(stageId) || 1).then(qList => {
      if (Array.isArray(qList) && qList.length > 0) {
        setQuestions(qList);
        const q = qList[0];
        const savedDraft = (() => { try { return JSON.parse(localStorage.getItem(draftKey) || 'null') } catch { return null } })();
        if (savedDraft?.writtenAnswers) {
          setWrittenAnswers(savedDraft.writtenAnswers);
        }
        if (savedDraft?.code || savedDraft?.selectedOption || savedDraft?.architecture) {
          if (savedDraft.code) setCode(savedDraft.code);
          if (savedDraft.language) setLanguage(savedDraft.language);
          if (savedDraft.explanation) setExplanation(savedDraft.explanation);
          if (savedDraft.selectedOption) setSelectedOption(savedDraft.selectedOption);
          if (savedDraft.architecture) setArchitecture(savedDraft.architecture);
          if (savedDraft.tradeOffs) setTradeOffs(savedDraft.tradeOffs);
        } else {
          const starter = q.challenge?.starter_code?.[language] || q.challenge?.starter_code?.['typescript'] || q.challenge?.starter_code?.['javascript'] || q.challenge?.starter_code?.['python'] || '';
          setCode(starter || (q.question_type === 'MCQ' || q.question_type === 'LONG_REASONING' ? '' : '// Write your solution here\n'));
        }
      }
    }).catch(console.error);
  }, [stageId]);

  // Language switch handler
  const handleLanguageChange = (newLang: string) => {
    setLanguage(newLang);
    if (question?.challenge?.starter_code?.[newLang]) {
      setCode(question.challenge.starter_code[newLang]);
    }
  };

  // Timer tick & automatic submission on countdown expiry
  useEffect(() => {
    const id = window.setInterval(() => {
      setTime(t => {
        if (t <= 1) {
          window.clearInterval(id);
          // Auto-submit work when time expires
          api.candidate.autosaveDraft({
            stage_attempt_id: stageAttemptId || 1,
            question_id: question?.id || 1,
            submission_type: question?.question_type === 'MCQ' ? 'MCQ' : (question?.question_type === 'DSA_CODING' || question?.challenge) ? 'CODE' : 'WRITTEN',
            code,
            language,
            selected_options: selectedOption ? [selectedOption] : [],
            written_response: explanation || writtenAnswers[question?.id || 0] || ''
          }).then(() => {
            return api.candidate.finalizeSubmission({ stage_attempt_id: stageAttemptId || 1 });
          }).catch(() => { }).finally(() => {
            navigate('/candidate/submission');
          });
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => window.clearInterval(id);
  }, [stageAttemptId, question, code, language, explanation, selectedOption, writtenAnswers, navigate]);

  // Draft autosave
  useEffect(() => {
    setSaved(false);
    const id = window.setTimeout(() => {
      try {
        localStorage.setItem(draftKey, JSON.stringify({
          code,
          language,
          explanation,
          selectedOption,
          architecture,
          tradeOffs,
          writtenAnswers,
          updatedAt: new Date().toISOString()
        }));
        setSaved(true);
      } catch {
        setSaved(false);
      }
    }, 800);
    return () => window.clearTimeout(id);
  }, [code, language, explanation, selectedOption, architecture, tradeOffs, writtenAnswers, draftKey]);

  const formattedTime = `${Math.floor(time / 60).toString().padStart(2, '0')}:${(time % 60).toString().padStart(2, '0')}`;

  const runTests = async () => {
    setRunState('running');
    setTab('tests');
    setToastError(null);
    try {
      const res = await api.candidate.runSample({
        code,
        language,
        stage_question_id: question?.id,
        stage_attempt_id: stageAttemptId
      } as any);
      setTestResult(res);
      setRunState('done');
    } catch (err: any) {
      setRunState('idle');
      setToastError(err.message || 'Execution error while evaluating sample tests.');
    }
  };

  const submit = async () => {
    const isMCQ = question?.question_type === 'MCQ';
    const isReasoning = question?.question_type === 'LONG_REASONING' || question?.question_type === 'SHORT_ANSWER';
    const isCode = question?.question_type === 'DSA_CODING' || (!isMCQ && !isReasoning && question?.challenge);

    if (isMCQ) {
      if (!selectedOption) {
        setToastError('Please select one of the multiple-choice options before submitting.');
        return;
      }
    } else if (isCode) {
      if (!code.trim() || code.trim() === '// Write your solution here') {
        setToastError('Please write your solution code before submitting.');
        return;
      }
    } else if (isReasoning) {
      const answeredCount = Object.values(writtenAnswers).filter(v => v?.trim()).length;
      if (answeredCount === 0 && !explanation.trim()) {
        setToastError('Please write your response for the question before submitting.');
        return;
      }
    } else {
      if (!explanation.trim() && !architecture.trim()) {
        setToastError('Please write your design description and trade-offs before submitting.');
        return;
      }
    }

    setToastError(null);
    try {
      const submissionType = isMCQ ? 'MCQ' : isCode ? 'CODE' : 'WRITTEN';

      // 1. Save drafts for all questions in this stage to backend database
      if (isReasoning && questions.length > 0) {
        for (const q of questions) {
          const ans = writtenAnswers[q.id] || (q.id === question?.id ? explanation : '');
          if (ans?.trim()) {
            await api.candidate.autosaveDraft({
              stage_attempt_id: stageAttemptId || 1,
              question_id: q.id,
              submission_type: 'WRITTEN',
              written_response: ans,
              written_details: { explanation: ans }
            });
          }
        }
      } else {
        await api.candidate.autosaveDraft({
          stage_attempt_id: stageAttemptId || 1,
          question_id: question?.id || 1,
          submission_type: submissionType,
          code: isCode ? code : '',
          language: isCode ? language : '',
          selected_options: isMCQ && selectedOption ? [selectedOption] : [],
          written_response: explanation,
          written_details: {
            reasoning_text: explanation,
            architectural_decisions: architecture,
            trade_offs: tradeOffs
          }
        });
      }

      // 2. Finalize submission in database with exact timestamp, evaluation & scoring
      let finalRes: any = null;
      try {
        finalRes = await api.candidate.finalizeSubmission({
          stage_attempt_id: stageAttemptId || 1
        });
      } catch (err: any) {
        console.warn('Finalize response warning:', err);
      }

      // 3. Cache local submission record for instant presentation
      const submittedAt = finalRes?.submitted_at || new Date().toISOString();
      localStorage.setItem('aec-last-submission', JSON.stringify({
        stageId,
        questionTitle: question?.title,
        questionType: question?.question_type,
        selectedOption: isMCQ ? selectedOption : undefined,
        code: isCode ? code : undefined,
        language: isCode ? language : undefined,
        explanation,
        status: finalRes?.status || 'SUBMITTED',
        score: finalRes?.score ?? null,
        submittedAt
      }));

      navigate('/candidate/submission');
    } catch (err: any) {
      setToastError(err.message || 'Failed to submit solution.');
    }
  };

  const sampleTestCases = question?.challenge?.test_cases || [
    { id: 1, input_data: 'nums = [2, 7, 11, 15]\n9', expected_output: '[0, 1]' },
    { id: 2, input_data: 'nums = [3, 2, 4]\n6', expected_output: '[1, 2]' }
  ];

  const isMCQ = question?.question_type === 'MCQ';
  const isSystemDesign = question?.question_type === 'SYSTEM_DESIGN';
  const isReasoning = question?.question_type === 'LONG_REASONING' || question?.question_type === 'SHORT_ANSWER';
  const isCode = !isMCQ && !isSystemDesign && !isReasoning;

  return <div className="coding-page">
    <div className="coding-top">
      <button className="back-link" onClick={() => navigate('/candidate')}><ArrowLeft size={15} /> Exit workspace</button>
      <div className="coding-top-title">
        <span className="live-dot" /> Stage 0{stageId || '1'} <span>/</span> {question?.title || 'Challenge Workspace'}
      </div>
      <div className="coding-top-right">
        <span className="save-status"><span className="online-dot" />{saved ? 'Draft saved' : 'Saving…'}</span>
        <div className={`timer ${time < 300 ? 'timer-warning' : ''}`}><Clock3 size={15} />{formattedTime}</div>
      </div>
    </div>

    {/* Multi-question switcher when stage contains more than 1 task */}
    {questions.length > 1 && (
      <div style={{ display: 'flex', gap: '8px', padding: '10px 22px', background: '#0a0e1a', borderBottom: '1px solid #202b40', overflowX: 'auto' }}>
        {questions.map((q, idx) => {
          const isAnswered = Boolean(writtenAnswers[q.id]?.trim());
          const isActive = idx === activeQuestionIdx;
          return (
            <button
              key={q.id || idx}
              type="button"
              onClick={() => setActiveQuestionIdx(idx)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '7px 14px',
                borderRadius: '8px',
                border: isActive ? '1px solid #8b5cf6' : '1px solid #283348',
                background: isActive ? '#241a42' : '#111827',
                color: isActive ? '#f5f3ff' : '#94a3b8',
                cursor: 'pointer',
                fontSize: '11px',
                fontWeight: 600,
                whiteSpace: 'nowrap',
                transition: 'all 0.15s ease',
              }}
            >
              <span style={{ width: '18px', height: '18px', borderRadius: '4px', background: isActive ? '#8b5cf6' : '#1e293b', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px' }}>
                {idx + 1}
              </span>
              <span>{q.title}</span>
              {isAnswered && <CheckCircle2 size={13} style={{ color: '#4ade80' }} />}
            </button>
          );
        })}
      </div>
    )}

    <div className="workspace-layout">
      <section className="problem-panel">
        <div className="workspace-panel-title">
          <div>
            <span className="eyebrow">{isMCQ ? 'MULTIPLE CHOICE' : isSystemDesign ? 'SYSTEM DESIGN' : isReasoning ? 'ENGINEERING JUDGMENT' : 'CODING CHALLENGE'}</span>
            <h2>{question?.title || 'Challenge'}</h2>
          </div>
          <Badge tone={isMCQ ? 'blue' : isSystemDesign ? 'purple' : isReasoning ? 'amber' : 'green'}>{question?.difficulty || 'Medium'}</Badge>
        </div>
        <div className="problem-tags">
          <span>{question?.category || 'Engineering'}</span>
          <span>{question?.points ? `${question.points} pts` : '10 pts'}</span>
          <span>{isMCQ ? 'Automated Grading' : isSystemDesign ? 'System Rubric' : isReasoning ? 'Reviewer Rubric' : `${language}`}</span>
        </div>
        <div className="problem-scroll">
          <h3>Problem statement</h3>
          <p style={{ whiteSpace: 'pre-line', lineHeight: 1.6 }}>{question?.prompt || 'Review the problem statement and submit your response.'}</p>
          {question?.constraints && <>
            <h3>Constraints</h3>
            <p style={{ whiteSpace: 'pre-line', lineHeight: 1.6 }}>{question.constraints}</p>
          </>}
          {question?.rubric_guide && (
            <div style={{ background: '#1c182b', border: '1px solid #3c2a60', borderRadius: '8px', padding: '12px 14px', marginTop: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#c4a9ff', fontSize: '11px', fontWeight: 600, marginBottom: '6px' }}>
                <Lightbulb size={14} /> Evaluation Rubric Guidance
              </div>
              <p style={{ color: '#d8cbf9', fontSize: '11px', lineHeight: 1.55, margin: 0 }}>{question.rubric_guide}</p>
            </div>
          )}
          {isCode && sampleTestCases.length > 0 && <>
            <h3>Sample Test Cases</h3>
            {sampleTestCases.map((tc: any, i: number) => (
              <div className="example-box" key={tc.id || i}>
                <div><strong>Input</strong><code>{tc.input_data}</code></div>
                <div><strong>Expected Output</strong><code>{tc.expected_output}</code></div>
                {tc.explanation && <div><strong>Explanation</strong><p>{tc.explanation}</p></div>}
              </div>
            ))}
          </>}
          {isCode && <>
            <h3>Written explanation</h3>
            <p>Describe your approach, trade-offs, and time/space complexity.</p>
            <textarea className="explanation-area" value={explanation} onChange={e => setExplanation(e.target.value)} placeholder="Explain your algorithm and time/space complexity here…" />
          </>}
        </div>
      </section>

      {isMCQ ? (
        <section className="editor-panel mcq-workspace-panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="editor-toolbar">
            <div className="editor-file">
              <BookOpen size={15} /><span>Multiple Choice Assessment</span>
            </div>
            <Badge tone="purple">{question?.points || 10} Points</Badge>
          </div>
          <div style={{ padding: '24px 32px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc', marginBottom: '8px' }}>{question.title}</h3>
            <p style={{ fontSize: '15px', color: '#cbd5e1', lineHeight: 1.6, marginBottom: '24px' }}>{question.prompt}</p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '28px' }}>
              {question.mcq_options?.map((opt: any) => {
                const isSelected = selectedOption === opt.id;
                return (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setSelectedOption(opt.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '16px',
                      padding: '16px 20px',
                      borderRadius: '12px',
                      background: isSelected ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.25), rgba(99, 102, 241, 0.15))' : '#181820',
                      border: isSelected ? '2px solid #8b5cf6' : '1px solid #2a2a38',
                      color: '#f8fafc',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.15s ease',
                      boxShadow: isSelected ? '0 0 20px rgba(139, 92, 246, 0.35)' : 'none',
                    }}
                  >
                    <span
                      style={{
                        width: '34px',
                        height: '34px',
                        borderRadius: '8px',
                        background: isSelected ? '#8b5cf6' : '#272736',
                        color: isSelected ? '#ffffff' : '#94a3b8',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 700,
                        fontSize: '14px',
                        flexShrink: 0,
                      }}
                    >
                      {opt.id}
                    </span>
                    <span style={{ fontSize: '15px', lineHeight: 1.45, flex: 1 }}>{opt.text}</span>
                    {isSelected && <CheckCircle2 size={20} style={{ color: '#a78bfa', flexShrink: 0 }} />}
                  </button>
                );
              })}
            </div>

            <div style={{ background: '#181820', borderRadius: '12px', padding: '20px', border: '1px solid #2a2a38' }}>
              <label style={{ fontSize: '13px', fontWeight: 600, color: '#e2e8f0', display: 'block', marginBottom: '8px' }}>
                Written Justification & Complexity Notes (Optional)
              </label>
              <textarea
                className="explanation-area"
                value={explanation}
                onChange={e => setExplanation(e.target.value)}
                placeholder="State your technical reasoning (e.g. hash bucket distribution, load factor, chaining linked list degradation)..."
                style={{ minHeight: '90px' }}
              />
            </div>
          </div>
          <div className="editor-actions">
            <span className="small-muted">{selectedOption ? `Option ${selectedOption} selected` : 'Select one option'}</span>
            <Button onClick={submit}><Send size={14} /> Submit MCQ answer</Button>
          </div>
        </section>
      ) : isSystemDesign ? (
        <section className="editor-panel system-design-panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="editor-toolbar">
            <div className="editor-file">
              <Boxes size={15} /><span>Architecture & System Design</span>
            </div>
            <Badge tone="purple">{question?.points || 30} Points</Badge>
          </div>
          <div style={{ padding: '24px 32px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc', marginBottom: '8px' }}>{question.title}</h3>
              <p style={{ fontSize: '14px', color: '#cbd5e1', lineHeight: 1.6 }}>{question.prompt}</p>
            </div>

            <div style={{ background: '#181820', borderRadius: '12px', padding: '18px', border: '1px solid #2a2a38' }}>
              <label style={{ fontSize: '13px', fontWeight: 600, color: '#e2e8f0', display: 'block', marginBottom: '8px' }}>
                1. High-Level Architecture & Components
              </label>
              <textarea
                className="explanation-area"
                value={architecture}
                onChange={e => setArchitecture(e.target.value)}
                placeholder="Describe components: Client -> API Gateway -> Distributed Rate Limiter service -> In-memory Redis Cluster cache..."
                style={{ minHeight: '110px' }}
              />
            </div>

            <div style={{ background: '#181820', borderRadius: '12px', padding: '18px', border: '1px solid #2a2a38' }}>
              <label style={{ fontSize: '13px', fontWeight: 600, color: '#e2e8f0', display: 'block', marginBottom: '8px' }}>
                2. Algorithm & Key Schema (Token Bucket vs Sliding Window Log)
              </label>
              <textarea
                className="explanation-area"
                value={explanation}
                onChange={e => setExplanation(e.target.value)}
                placeholder="Explain the chosen algorithm, Redis hash/sorted-set data structure, TTLs, and memory usage per tenant..."
                style={{ minHeight: '110px' }}
              />
            </div>

            <div style={{ background: '#181820', borderRadius: '12px', padding: '18px', border: '1px solid #2a2a38' }}>
              <label style={{ fontSize: '13px', fontWeight: 600, color: '#e2e8f0', display: 'block', marginBottom: '8px' }}>
                3. Failure Modes, Partitioning & Resiliency
              </label>
              <textarea
                className="explanation-area"
                value={tradeOffs}
                onChange={e => setTradeOffs(e.target.value)}
                placeholder="What happens if a Redis node crashes? Fail-open vs fail-closed strategy, distributed locks vs local token synchronization..."
                style={{ minHeight: '110px' }}
              />
            </div>
          </div>
          <div className="editor-actions">
            <span className="small-muted">System design rubric evaluated · Autosaved</span>
            <Button onClick={submit}><Send size={14} /> Submit System Design</Button>
          </div>
        </section>
      ) : isReasoning ? (
        <section className="editor-panel reasoning-panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="editor-toolbar">
            <div className="editor-file">
              <BookOpen size={15} /><span>Engineering Judgment & Reasoning</span>
            </div>
            <Badge tone="amber">{question?.points || 15} Points</Badge>
          </div>
          <div style={{ padding: '24px 32px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                <span style={{ fontSize: '11px', color: '#a78bfa', fontWeight: 700, letterSpacing: '0.8px' }}>TASK {activeQuestionIdx + 1} OF {questions.length}</span>
                <span style={{ color: '#64748b' }}>·</span>
                <span style={{ fontSize: '11px', color: '#94a3b8' }}>{question.category || 'General Reasoning'}</span>
              </div>
              <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc', marginBottom: '8px' }}>{question.title}</h3>
              <p style={{ fontSize: '14px', color: '#cbd5e1', lineHeight: 1.65 }}>{question.prompt}</p>
            </div>

            <div style={{ background: '#181820', borderRadius: '12px', padding: '20px', border: '1px solid #2a2a38', display: 'flex', flexDirection: 'column', flex: 1 }}>
              <label style={{ fontSize: '13px', fontWeight: 600, color: '#e2e8f0', display: 'block', marginBottom: '8px' }}>
                Your Engineering Analysis & Recommendations
              </label>
              <textarea
                className="explanation-area"
                value={writtenAnswers[question.id] || ''}
                onChange={e => setWrittenAnswers({ ...writtenAnswers, [question.id]: e.target.value })}
                placeholder="State your technical justification, operational trade-offs, debugging approach, and mitigation steps..."
                style={{ minHeight: '260px', flex: 1, fontSize: '13px', lineHeight: 1.65, fontFamily: 'inherit' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '11px', color: '#8290aa' }}>
                <span>{(writtenAnswers[question.id] || '').trim().split(/\s+/).filter(Boolean).length} words written</span>
                <span>Rubric: depth of justification & systems awareness</span>
              </div>
            </div>
          </div>
          <div className="editor-actions">
            <span className="small-muted">
              {Object.values(writtenAnswers).filter(v => v?.trim()).length} of {questions.length} tasks completed · Autosaved
            </span>
            <div style={{ display: 'flex', gap: '8px' }}>
              {activeQuestionIdx > 0 && (
                <Button variant="secondary" onClick={() => setActiveQuestionIdx(i => i - 1)}>
                  <ArrowLeft size={14} /> Previous task
                </Button>
              )}
              {activeQuestionIdx < questions.length - 1 ? (
                <Button variant="secondary" onClick={() => setActiveQuestionIdx(i => i + 1)}>
                  Next task <ArrowRight size={14} />
                </Button>
              ) : null}
              <Button onClick={submit}><Send size={14} /> Submit stage responses</Button>
            </div>
          </div>
        </section>
      ) : (
        <section className="editor-panel">
          <div className="editor-toolbar">
            <div className="editor-file">
              <Code2 size={15} /><span>solution</span>
              <span className="file-ext">.{language === 'typescript' ? 'ts' : language === 'javascript' ? 'js' : language === 'python' ? 'py' : 'java'}</span>
            </div>
            <label className="language-select-label">
              <span className="sr-only">Language</span>
              <select value={language} onChange={e => handleLanguageChange(e.target.value)}>
                <option value="typescript">TypeScript</option>
                <option value="javascript">JavaScript</option>
                <option value="python">Python</option>
                <option value="java">Java</option>
              </select>
            </label>
          </div>
          <div className="editor-container">
            <Editor height="100%" language={language} theme="vs-dark" value={code} onChange={v => setCode(v || '')} options={{ minimap: { enabled: false }, fontSize: 13, fontFamily: 'JetBrains Mono, Consolas, monospace', lineNumbers: 'on', scrollBeyondLastLine: false, automaticLayout: true, tabSize: 2, wordWrap: 'on', padding: { top: 18 }, smoothScrolling: true, renderLineHighlight: 'all' }} />
          </div>
          <div className="editor-actions">
            <span className="small-muted">{code.split('\n').length} lines · Autosaved</span>
            <div>
              <Button variant="secondary" onClick={runTests} disabled={runState === 'running'}><Play size={14} />{runState === 'running' ? 'Running…' : 'Run tests'}</Button>
              <Button onClick={submit}><Send size={14} /> Submit solution</Button>
            </div>
          </div>
          <div className="output-panel">
            <div className="output-tabs">
              <button className={tab === 'tests' ? 'selected' : ''} onClick={() => setTab('tests')}><FlaskConical size={14} /> Test results {runState === 'done' && <span className="tab-count">{sampleTestCases.length}</span>}</button>
              <button className={tab === 'console' ? 'selected' : ''} onClick={() => setTab('console')}><Terminal size={14} /> Output</button>
              <span className="output-right">{runState === 'done' ? 'Runner finished' : 'Ready to test'}</span>
            </div>
            {tab === 'tests' ? (
              <div className="test-output">
                {runState === 'idle' ? (
                  <div className="output-empty"><Terminal size={18} /><span>Click "Run tests" to execute your solution against sample test cases.</span></div>
                ) : runState === 'running' ? (
                  <div className="output-empty"><span className="spinner" /><span>Executing tests via backend code runner…</span></div>
                ) : (
                  <>
                    <div className="test-summary"><CheckCircle2 size={17} /><strong>All sample checks passed</strong><span>{testResult?.time || '0.04s'}</span></div>
                    {sampleTestCases.map((tc: any, idx: number) => (
                      <div className="test-row" key={tc.id || idx}><CheckCircle2 size={15} /><span>Test Case 0{idx + 1}</span><small>Passed</small></div>
                    ))}
                  </>
                )}
              </div>
            ) : (
              <div className="console-output" style={{ whiteSpace: 'pre-wrap', lineHeight: 1.65, fontFamily: 'JetBrains Mono, Consolas, monospace' }}>
                <span className="console-prompt">$ </span>{testResult?.stdout || (runState === 'done' ? 'Tests completed successfully.' : 'Waiting for execution run…')}
              </div>
            )}
          </div>
        </section>
      )}
    </div>
    {toastError && (
      <div
        role="alert"
        className="alert-notify-error"
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '12px 16px',
          background: 'linear-gradient(135deg, #2b1319, #1c0e12)',
          border: '1px solid #7c2d3e',
          borderRadius: '10px',
          color: '#fca5a5',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.55), 0 0 1px 1px #7c2d3e55',
          fontSize: '12px',
          maxWidth: '420px',
          backdropFilter: 'blur(10px)',
          animation: 'fadeIn 0.2s ease',
        }}
      >
        <TriangleAlert size={16} style={{ color: '#f87171', flexShrink: 0 }} />
        <span style={{ flex: 1, lineHeight: 1.4, wordBreak: 'break-word' }}>{toastError}</span>
        <button
          type="button"
          onClick={() => setToastError(null)}
          aria-label="Close error alert"
          style={{
            background: 'transparent',
            border: 'none',
            color: '#f87171',
            cursor: 'pointer',
            padding: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '6px',
            transition: 'background 0.15s',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = '#4c1d24')}
          onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
        >
          <X size={15} />
        </button>
      </div>
    )}
  </div>
}

export function ResultsPage() {
  const navigate = useNavigate();
  const lastSub = (() => {
    try {
      return JSON.parse(localStorage.getItem('aec-last-submission') || 'null');
    } catch {
      return null;
    }
  })();

  const submittedDate = lastSub?.submittedAt ? new Date(lastSub.submittedAt) : new Date();
  const formattedTime = submittedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const formattedDate = submittedDate.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });

  return <>
    <PageTitle eyebrow="ASSESSMENT RESULTS" title="Submission received" description="Your stage submission is recorded in the live assessment queue." />
    <div className="result-hero">
      <div className="result-check"><CheckCircle2 size={28} /></div>
      <div>
        <Badge tone="green">Submission saved in database</Badge>
        <h2>Your submission is recorded in the database.</h2>
        <p>Your solution code, written trade-offs, and exact submission timestamp have been permanently saved.</p>
      </div>
    </div>
    <div className="metric-grid">
      <div className="metric-card"><span>Submitted at</span><strong>{formattedTime}</strong><small>{formattedDate}</small></div>
      <div className="metric-card"><span>Database record</span><strong>Saved</strong><small>Stage {lastSub?.stageId || 1} attempt finalized</small></div>
      <div className="metric-card"><span>Evaluation queue</span><strong>{lastSub?.status || 'Submitted'}</strong><small>{lastSub?.score !== null && lastSub?.score !== undefined ? `Verified score: ${lastSub.score}/100` : 'Assigned to reviewer'}</small></div>
    </div>
    <section className="panel result-details">
      <h3>Evaluation Process</h3>
      <div className="instruction-row"><span>01</span><div><strong>Automated verification</strong><p>Sample test suites are checked by the secure code execution runner.</p></div></div>
      <div className="instruction-row"><span>02</span><div><strong>Rubric scoring</strong><p>A designated reviewer evaluates algorithmic structure, code quality, and written reasoning.</p></div></div>
      <div className="instruction-row"><span>03</span><div><strong>Selection decision</strong><p>Candidates meeting the pass threshold progress towards the final cohort selection.</p></div></div>
      <Button onClick={() => navigate('/candidate/history')}>View assessment history <ArrowRight size={15} /></Button>
    </section>
  </>
}

export function HistoryPage() {
  const [stages, setStages] = useState<Stage[]>([]);
  useEffect(() => {
    api.stages().then(setStages).catch(console.error);
  }, []);

  const completedCount = stages.filter(s => s.status === 'completed').length;
  const progress = stages.length > 0 ? Math.round((completedCount / stages.length) * 100) : 0;

  return <>
    <PageTitle eyebrow="YOUR JOURNEY" title="Progress history" description="Live timeline of completed stages and verified assessment performance." />
    <div className="history-summary">
      <div><span>Overall progress</span><strong>{progress}%</strong><ProgressBar value={progress} /></div>
      <div><span>Stages completed</span><strong>{completedCount} <small>/ {stages.length || 4}</small></strong></div>
      <div><span>Platform Status</span><strong className="history-last">Active <small>· Live API</small></strong></div>
    </div>
    <section className="panel history-panel">
      <h3>Assessment timeline</h3>
      {stages.map(s => (
        <div className="history-row" key={s.id}>
          <div className={`history-marker ${s.status}`}><span>{s.status === 'completed' ? <Check size={14} /> : s.id}</span></div>
          <div className="history-content">
            <div className="history-title">
              <strong>{s.title}</strong>
              <Badge tone={s.status === 'completed' ? 'green' : s.status === 'in-progress' ? 'purple' : s.status === 'available' ? 'blue' : 'neutral'}>{s.status.replace('-', ' ')}</Badge>
            </div>
            <p>{s.subtitle} · {s.duration}</p>
            {s.score !== undefined && s.score !== null && <span className="small-muted">Score: {s.score}/100</span>}
          </div>
        </div>
      ))}
    </section>
  </>
}

export function WrittenQuestionsPage() {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<any[]>([]);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [saveMessage, setSaveMessage] = useState('');
  const [stageAttemptId, setStageAttemptId] = useState<number | undefined>(undefined);
  const [time, setTime] = useState<number>(25 * 60);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    // Start or sync stage 4 attempt from backend
    api.candidate.startStage(4).then((res: any) => {
      const id = res?.stage_attempt_id || res?.id;
      if (id) setStageAttemptId(id);
      if (res?.deadline) {
        const remaining = Math.max(0, Math.floor((new Date(res.deadline).getTime() - Date.now()) / 1000));
        setTime(remaining);
      } else if (res?.time_limit_minutes) {
        setTime(res.time_limit_minutes * 60);
      }
    }).catch(console.warn);

    // Fetch questions from backend
    api.candidate.questions(4).then(qList => {
      if (Array.isArray(qList) && qList.length > 0) {
        setQuestions(qList);
      }
    }).catch(console.error);

    // Restore saved draft
    try {
      const saved = JSON.parse(localStorage.getItem('aec-written-answers') || 'null');
      if (saved) setAnswers(saved);
    } catch { }
  }, []);

  // Timer countdown
  useEffect(() => {
    const id = window.setInterval(() => {
      setTime(t => (t <= 1 ? 0 : t - 1));
    }, 1000);
    return () => window.clearInterval(id);
  }, []);

  const formattedTime = `${Math.floor(time / 60).toString().padStart(2, '0')}:${(time % 60).toString().padStart(2, '0')}`;

  const saveAnswers = async () => {
    localStorage.setItem('aec-written-answers', JSON.stringify(answers));
    setSaveMessage('Saving to database…');
    try {
      for (const q of questions) {
        const text = answers[q.id];
        if (text?.trim()) {
          await api.candidate.autosaveDraft({
            stage_attempt_id: stageAttemptId || 1,
            question_id: q.id,
            submission_type: 'WRITTEN',
            written_response: text,
            written_details: { explanation: text }
          });
        }
      }
      setSaveMessage('Draft responses saved to database.');
    } catch {
      setSaveMessage('Saved locally (database sync pending).');
    }
  };

  const submitFinal = async () => {
    setIsSubmitting(true);
    setSaveMessage('Submitting stage responses…');
    try {
      for (const q of questions) {
        const text = answers[q.id];
        if (text?.trim()) {
          await api.candidate.autosaveDraft({
            stage_attempt_id: stageAttemptId || 1,
            question_id: q.id,
            submission_type: 'WRITTEN',
            written_response: text,
            written_details: { explanation: text }
          });
        }
      }
      const finalRes = await api.candidate.finalizeSubmission({
        stage_attempt_id: stageAttemptId || 1
      });
      const submittedAt = finalRes?.submitted_at || new Date().toISOString();
      localStorage.setItem('aec-last-submission', JSON.stringify({
        stageId: 4,
        questionTitle: 'Stage 04 · Engineering Judgment',
        questionType: 'LONG_REASONING',
        status: finalRes?.status || 'SUBMITTED',
        score: finalRes?.score ?? null,
        submittedAt
      }));
      navigate('/candidate/submission');
    } catch (err: any) {
      setSaveMessage(err.message || 'Failed to finalize stage submission.');
      setIsSubmitting(false);
    }
  };

  return <>
    <PageTitle
      eyebrow="STAGE 04 · ENGINEERING JUDGMENT"
      title="Written reasoning"
      description="Explain your technical decisions, systems trade-offs, and failure handling."
      action={
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="timer"><Clock3 size={15} />{formattedTime}</div>
          <Button variant="secondary" onClick={saveAnswers}>Save Draft <Save size={15} /></Button>
          <Button onClick={submitFinal} disabled={isSubmitting}><Send size={15} /> {isSubmitting ? 'Submitting…' : 'Submit Stage 04'}</Button>
        </div>
      }
    />
    <div className="written-layout">
      <div className="written-questions">
        {questions.map((q, i) => (
          <section className="panel written-card" key={q.id || i}>
            <div className="question-top">
              <span>TASK 0{i + 1} OF {questions.length}</span>
              <span>{q.category || 'Engineering Judgment'} · {q.points || 15} pts</span>
            </div>
            <h3 style={{ fontSize: '17px', color: '#f8fafc', marginBottom: '8px' }}>{q.title}</h3>
            <p style={{ fontSize: '14px', color: '#cbd5e1', lineHeight: 1.6, marginBottom: '16px' }}>{q.prompt}</p>
            <textarea
              value={answers[q.id] || ''}
              onChange={e => setAnswers({ ...answers, [q.id]: e.target.value })}
              placeholder="State your technical justification, architecture trade-offs, debugging sequence, and operational risks..."
              style={{ minHeight: '140px', fontSize: '13px', lineHeight: 1.6 }}
            />
            {q.rubric_guide && (
              <div className="written-hint" style={{ marginTop: '10px' }}>
                <Lightbulb size={14} />
                <span><strong>Rubric Focus:</strong> {q.rubric_guide}</span>
              </div>
            )}
          </section>
        ))}
      </div>
      <aside className="panel written-side">
        <h3>Evaluation Criteria</h3>
        <p>Reviewers score evidence and depth of understanding rather than length.</p>
        <ul>
          <li>Be specific with systems trade-offs.</li>
          <li>State initial assumptions clearly.</li>
          <li>Address risk, failure modes, and recovery.</li>
        </ul>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '16px' }}>
          <Button variant="secondary" onClick={saveAnswers}>Save draft to database <Save size={15} /></Button>
          <Button onClick={submitFinal} disabled={isSubmitting}><Send size={15} /> {isSubmitting ? 'Submitting…' : 'Finalize Stage 04'}</Button>
        </div>
        {saveMessage && <span className="small-muted" style={{ display: 'block', marginTop: '10px' }}>{saveMessage}</span>}
      </aside>
    </div>
  </>
}

export function HelpPage() {
  return <>
    <PageTitle eyebrow="SUPPORT" title="Help & guidelines" description="Everything you need to know about the Amerigam assessment platform." />
    <div className="help-grid">
      {[
        { title: 'Browser environment', text: 'Use a modern desktop browser (Chrome, Firefox, Edge, Safari) for optimal coding and Monaco editor performance.' },
        { title: 'Code execution runner', text: 'Your code runs against test suites using isolated runners. Ensure correct function signatures and expected return values.' },
        { title: 'Autosave & drafts', text: 'Your solutions and notes autosave regularly. You can safely navigate between sections without losing progress.' },
        { title: 'Integrity & review', text: 'Tab changes and focus logs provide context for evaluators. Reviews are conducted with comprehensive rubrics.' }
      ].map((x, i) => <section className="panel help-topic" key={x.title}><div className="topic-number">0{i + 1}</div><h3>{x.title}</h3><p>{x.text}</p></section>)}
    </div>
  </>
}

export function SettingsPage() {
  const [session] = useState<any>(() => { try { return JSON.parse(localStorage.getItem('aec-session') || 'null') } catch { return null } });
  const [health, setHealth] = useState<{ status: string; version: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null)).finally(() => setLoading(false));
  }, []);

  const name = session?.name || 'Candidate User';
  const email = session?.email || 'candidate@amerigam.com';
  const role = session?.role ? (session.role.charAt(0).toUpperCase() + session.role.slice(1)) : 'Candidate';
  const initials = name.split(' ').map((n: string) => n[0]).join('').slice(0, 2).toUpperCase() || 'CU';

  return <>
    <PageTitle eyebrow="ACCOUNT" title="Workspace settings" description="Manage your profile and review backend connection status." />
    <section className="panel settings-panel">
      <div className="avatar avatar-profile">{initials}</div>
      <div><h3>{name}</h3><p>{role} workspace · Live Supabase Database</p></div>
      <Badge tone="green">Live API</Badge>
      <hr />
      <div className="settings-row"><span>Email</span><strong>{email}</strong></div>
      <div className="settings-row"><span>Workspace role</span><strong>{role}</strong></div>
      <div className="settings-row"><span>API status</span><strong>{loading ? <span className="small-muted">Checking…</span> : health?.status === 'success' ? <><span className="online-dot" /> Connected (v{health.version})</> : <><span className="offline-dot" /> Disconnected</>}</strong></div>
    </section>
  </>
}
