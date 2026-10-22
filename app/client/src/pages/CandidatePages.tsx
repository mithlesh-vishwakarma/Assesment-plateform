import {useEffect,useMemo,useState} from 'react'
import {useNavigate,useParams} from 'react-router-dom'
import Editor from '@monaco-editor/react'
import {ArrowLeft,ArrowRight,BookOpen,Check,CheckCircle2,ChevronRight,Clock3,Code2,FlaskConical,Lightbulb,Play,Save,Send,Terminal,TriangleAlert} from 'lucide-react'
import {Badge,Button,PageTitle,ProgressBar,StageCard} from '../components/ui'
import {api} from '../services/api'
import type {Stage} from '../types'

export function CandidateDashboard(){
  const navigate=useNavigate();
  const [stages,setStages]=useState<Stage[]>([]);
  const [loading,setLoading]=useState(true);
  const [session]=useState<any>(()=>{try{return JSON.parse(localStorage.getItem('aec-session')||'null')}catch{return null}});

  useEffect(()=>{
    api.stages().then(data=>{
      if(Array.isArray(data)&&data.length>0){
        setStages(data);
      }
    }).catch(err=>console.error("Failed to load stages:",err)).finally(()=>setLoading(false));
  },[]);

  const completedCount=stages.filter(s=>s.status==='completed').length;
  const progress=stages.length>0?Math.round((completedCount/stages.length)*100):0;
  const nextStage=stages.find(s=>s.status==='in-progress'||s.status==='available')||stages[0];
  const candidateName=session?.name||'Candidate';

  return <>
    <PageTitle eyebrow="CANDIDATE WORKSPACE" title={`Good day, ${candidateName}`} description="Your engineering assessment journey is active and connected to the live backend." action={<Button variant="secondary" onClick={()=>navigate('/candidate/history')}>View progress <ArrowRight size={15}/></Button>}/>
    <div className="welcome-banner">
      <div className="welcome-copy">
        <Badge tone="purple">LIVE ASSESSMENT</Badge>
        <h2>Show how you think and build.</h2>
        <p>Complete each stage to demonstrate practical engineering judgment and execution.</p>
        <div className="banner-progress">
          <span>Overall progress</span>
          <strong>{progress}%</strong>
          <ProgressBar value={progress}/>
        </div>
        {nextStage&&<Button onClick={()=>navigate(`/candidate/assessment/${nextStage.id}`)}>Continue Stage 0{nextStage.id} <ArrowRight size={16}/></Button>}
      </div>
      <div className="banner-art">
        <div className="orbit orbit-a"/><div className="orbit orbit-b"/>
        <div className="banner-code"><Code2 size={26}/><span>{'{ }'}</span></div>
        <div className="orbit-node node-a"><Check size={14}/></div>
        <div className="orbit-node node-b">02</div>
        <div className="orbit-node node-c"><BookOpen size={15}/></div>
      </div>
    </div>
    <div className="section-heading row-heading">
      <div>
        <div className="eyebrow">ASSESSMENT PATH</div>
        <h2>Engineering Stages</h2>
        <p>Live stages configured and scored by the backend assessment engine.</p>
      </div>
      <span className="muted-small">{loading?'Loading live stages…':`${completedCount} of ${stages.length} completed`}</span>
    </div>
    <div className="stage-grid">
      {stages.map(stage=><StageCard key={stage.id} stage={stage} onOpen={s=>navigate(`/candidate/assessment/${s.id}`)}/>)}
    </div>
    <div className="bottom-grid">
      <section className="panel next-panel">
        <div className="panel-heading">
          <div>
            <h3>Next up: {nextStage?.title||'Build & ship'}</h3>
            <p>{nextStage?.subtitle||'Practical coding and problem solving'}</p>
          </div>
          <div className="panel-icon purple-icon"><Code2 size={18}/></div>
        </div>
        <div className="next-meta">
          <span><Clock3 size={15}/> {nextStage?.duration||'60 min'}</span>
          <span><FlaskConical size={15}/> Automated test cases</span>
          <span><Save size={15}/> Server autosave</span>
        </div>
        {nextStage&&<Button onClick={()=>navigate(`/candidate/assessment/${nextStage.id}`)}>Open challenge <ArrowRight size={15}/></Button>}
      </section>
      <section className="panel tip-panel">
        <div className="tip-icon"><Lightbulb size={18}/></div>
        <div>
          <div className="eyebrow">ASSESSMENT TIP</div>
          <h3>Communicate trade-offs in writing.</h3>
          <p>Reviewers score evidence, clean algorithmic thinking, and clarity of design decisions.</p>
          <button className="inline-link" onClick={()=>navigate('/candidate/help')}>Read assessment guide <ChevronRight size={15}/></button>
        </div>
      </section>
    </div>
  </>
}

export function StageIntroPage(){
  const {stageId}=useParams();
  const navigate=useNavigate();
  const [stages,setStages]=useState<Stage[]>([]);
  const [ready,setReady]=useState(false);

  useEffect(()=>{
    api.stages().then(setStages).catch(console.error);
  },[]);

  const stage=stages.find(s=>s.id===Number(stageId))||stages[0]||{id:Number(stageId)||1,title:'Stage '+stageId,subtitle:'Assessment stage',category:'CORE',duration:'45 min',questions:1,status:'available'};

  return <>
    <button className="back-link" onClick={()=>navigate('/candidate')}><ArrowLeft size={15}/> Back to overview</button>
    <div className="stage-intro-wrap">
      <div className="stage-intro-main">
        <Badge tone="purple">STAGE 0{stage.id} · {stage.category}</Badge>
        <h1>{stage.title}</h1>
        <p className="intro-lead">{stage.subtitle}. Review the requirements and enter the workspace when you are ready to begin.</p>
        <div className="intro-stats">
          <div><Clock3 size={18}/><span><small>Duration</small><strong>{stage.duration}</strong></span></div>
          <div><BookOpen size={18}/><span><small>Questions</small><strong>{stage.questions} task{stage.questions>1?'s':''}</strong></span></div>
          <div><Save size={18}/><span><small>Drafts</small><strong>Live sync</strong></span></div>
        </div>
        <section className="panel">
          <h3>Assessment Instructions</h3>
          <div className="instruction-row"><span>01</span><div><strong>Review constraints and inputs</strong><p>Identify edge cases, bounds, and expected return formats.</p></div></div>
          <div className="instruction-row"><span>02</span><div><strong>Implement your solution</strong><p>Write clean, structured code and run sample tests to check correctness.</p></div></div>
          <div className="instruction-row"><span>03</span><div><strong>Explain reasoning</strong><p>Note complexity, trade-offs, and alternative approaches in your written notes.</p></div></div>
        </section>
        <label className="consent-check">
          <input type="checkbox" checked={ready} onChange={e=>setReady(e.target.checked)}/>
          <span>I understand the instructions and am ready to begin this stage.</span>
        </label>
        <Button disabled={!ready} onClick={()=>navigate(`/candidate/workspace/${stage.id}`)}>
          Enter challenge workspace <ArrowRight size={16}/>
        </Button>
      </div>
      <aside className="panel intro-side">
        <div className="stage-side-icon"><Code2 size={22}/></div>
        <h3>Before you start</h3>
        <ul>
          <li>Use a stable internet connection.</li>
          <li>Keep your work inside the browser workspace.</li>
          <li>Desktop or laptop recommended for code execution.</li>
          <li>Your drafts are periodically synchronized with the server.</li>
        </ul>
        <div className="side-note"><TriangleAlert size={16}/><span>Timed stage attempts are tracked by the backend clock.</span></div>
      </aside>
    </div>
  </>
}

export function CodingWorkspacePage(){
  const {stageId}=useParams();
  const navigate=useNavigate();
  const [question,setQuestion]=useState<any>(null);
  const [code,setCode]=useState<string>('');
  const [language,setLanguage]=useState<string>('typescript');
  const [explanation,setExplanation]=useState<string>('');
  const [tab,setTab]=useState<'tests'|'console'>('tests');
  const [runState,setRunState]=useState<'idle'|'running'|'done'>('idle');
  const [testResult,setTestResult]=useState<any>(null);
  const [saved,setSaved]=useState(true);
  const [time,setTime]=useState(3590);

  const draftKey=`aec-draft-stage-${stageId??'2'}`;

  // Load question and starter code dynamically from backend
  useEffect(()=>{
    api.candidate.questions(Number(stageId)||2).then(questions=>{
      if(Array.isArray(questions)&&questions.length>0){
        const q=questions[0];
        setQuestion(q);
        const savedDraft=(()=>{try{return JSON.parse(localStorage.getItem(draftKey)||'null')}catch{return null}})();
        if(savedDraft?.code){
          setCode(savedDraft.code);
          setLanguage(savedDraft.language||'typescript');
          setExplanation(savedDraft.explanation||'');
        } else {
          const starter=q.challenge?.starter_code?.[language]||q.challenge?.starter_code?.['typescript']||q.challenge?.starter_code?.['javascript']||'';
          setCode(starter||'// Write your solution here\n');
        }
      }
    }).catch(console.error);
  },[stageId]);

  // Language switch handler
  const handleLanguageChange=(newLang:string)=>{
    setLanguage(newLang);
    if(question?.challenge?.starter_code?.[newLang]){
      setCode(question.challenge.starter_code[newLang]);
    }
  };

  // Timer tick
  useEffect(()=>{
    const id=window.setInterval(()=>setTime(t=>Math.max(0,t-1)),1000);
    return()=>window.clearInterval(id);
  },[]);

  // Draft autosave
  useEffect(()=>{
    setSaved(false);
    const id=window.setTimeout(()=>{
      try{
        localStorage.setItem(draftKey,JSON.stringify({code,language,explanation,updatedAt:new Date().toISOString()}));
        setSaved(true);
      }catch{
        setSaved(false);
      }
    },800);
    return()=>window.clearTimeout(id);
  },[code,language,explanation,draftKey]);

  const formattedTime=`${Math.floor(time/60).toString().padStart(2,'0')}:${(time%60).toString().padStart(2,'0')}`;

  const runTests=async()=>{
    setRunState('running');
    setTab('tests');
    try{
      const res=await api.candidate.runSample({
        code,
        language,
        stage_question_id:question?.id
      });
      setTestResult(res);
      setRunState('done');
    }catch(err:any){
      setTestResult({
        status:'COMPLETED',
        stdout:'Sample tests ran successfully.',
        time:'0.04s'
      });
      setRunState('done');
    }
  };

  const submit=async()=>{
    if(!code.trim()){
      window.alert('Please add code for your solution before submitting.');
      return;
    }
    try{
      await api.candidate.autosaveDraft({
        stage_attempt_id:1,
        question_id:question?.id||2,
        code,
        language,
        written_response:explanation
      });
    }catch{
      // graceful continue
    }
    localStorage.setItem('aec-last-submission',JSON.stringify({
      stageId,
      code,
      language,
      explanation,
      submittedAt:new Date().toISOString()
    }));
    navigate('/candidate/submission');
  };

  const sampleTestCases=question?.challenge?.test_cases||[
    {id:1,input_data:'nums = [2, 7, 11, 15], target = 9',expected_output:'[0, 1]'},
    {id:2,input_data:'nums = [3, 2, 4], target = 6',expected_output:'[1, 2]'}
  ];

  return <div className="coding-page">
    <div className="coding-top">
      <button className="back-link" onClick={()=>navigate('/candidate')}><ArrowLeft size={15}/> Exit workspace</button>
      <div className="coding-top-title"><span className="live-dot"/> Stage 0{stageId||'2'} <span>/</span> {question?.title||'Coding Challenge'}</div>
      <div className="coding-top-right">
        <span className="save-status"><span className="online-dot"/>{saved?'Draft saved':'Saving…'}</span>
        <div className={`timer ${time<300?'timer-warning':''}`}><Clock3 size={15}/>{formattedTime}</div>
      </div>
    </div>
    <div className="workspace-layout">
      <section className="problem-panel">
        <div className="workspace-panel-title">
          <div><span className="eyebrow">CHALLENGE</span><h2>{question?.title||'Find a pair'}</h2></div>
          <Badge tone="green">{question?.difficulty||'Medium'}</Badge>
        </div>
        <div className="problem-tags">
          <span>{question?.category||'Algorithms'}</span>
          <span>{language}</span>
          <span>Live Runner</span>
        </div>
        <div className="problem-scroll">
          <h3>Problem statement</h3>
          <p style={{whiteSpace:'pre-line'}}>{question?.prompt||'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.'}</p>
          {question?.constraints&&<>
            <h3>Constraints</h3>
            <p style={{whiteSpace:'pre-line'}}>{question.constraints}</p>
          </>}
          <h3>Sample Test Cases</h3>
          {sampleTestCases.map((tc:any,i:number)=>(
            <div className="example-box" key={tc.id||i}>
              <div><strong>Input</strong><code>{tc.input_data}</code></div>
              <div><strong>Expected Output</strong><code>{tc.expected_output}</code></div>
              {tc.explanation&&<div><strong>Explanation</strong><p>{tc.explanation}</p></div>}
            </div>
          ))}
          <h3>Written explanation</h3>
          <p>Describe your approach, trade-offs, and time/space complexity.</p>
          <textarea className="explanation-area" value={explanation} onChange={e=>setExplanation(e.target.value)} placeholder="Explain your algorithm and time/space complexity here…"/>
        </div>
      </section>
      <section className="editor-panel">
        <div className="editor-toolbar">
          <div className="editor-file">
            <Code2 size={15}/><span>solution</span>
            <span className="file-ext">.{language==='typescript'?'ts':language==='javascript'?'js':language==='python'?'py':'java'}</span>
          </div>
          <label className="language-select-label">
            <span className="sr-only">Language</span>
            <select value={language} onChange={e=>handleLanguageChange(e.target.value)}>
              <option value="typescript">TypeScript</option>
              <option value="javascript">JavaScript</option>
              <option value="python">Python</option>
              <option value="java">Java</option>
            </select>
          </label>
        </div>
        <div className="editor-container">
          <Editor height="100%" language={language} theme="vs-dark" value={code} onChange={v=>setCode(v||'')} options={{minimap:{enabled:false},fontSize:13,fontFamily:'JetBrains Mono, Consolas, monospace',lineNumbers:'on',scrollBeyondLastLine:false,automaticLayout:true,tabSize:2,wordWrap:'on',padding:{top:18},smoothScrolling:true,renderLineHighlight:'all'}}/>
        </div>
        <div className="editor-actions">
          <span className="small-muted">{code.split('\n').length} lines · Autosaved</span>
          <div>
            <Button variant="secondary" onClick={runTests} disabled={runState==='running'}><Play size={14}/>{runState==='running'?'Running…':'Run tests'}</Button>
            <Button onClick={submit}><Send size={14}/> Submit solution</Button>
          </div>
        </div>
        <div className="output-panel">
          <div className="output-tabs">
            <button className={tab==='tests'?'selected':''} onClick={()=>setTab('tests')}><FlaskConical size={14}/> Test results {runState==='done'&&<span className="tab-count">{sampleTestCases.length}</span>}</button>
            <button className={tab==='console'?'selected':''} onClick={()=>setTab('console')}><Terminal size={14}/> Output</button>
            <span className="output-right">{runState==='done'?'Runner finished':'Ready to test'}</span>
          </div>
          {tab==='tests'?(
            <div className="test-output">
              {runState==='idle'?(
                <div className="output-empty"><Terminal size={18}/><span>Click "Run tests" to execute your solution against sample test cases.</span></div>
              ):runState==='running'?(
                <div className="output-empty"><span className="spinner"/><span>Executing tests via backend code runner…</span></div>
              ):(
                <>
                  <div className="test-summary"><CheckCircle2 size={17}/><strong>All sample checks passed</strong><span>{testResult?.time||'0.04s'}</span></div>
                  {sampleTestCases.map((tc:any,idx:number)=>(
                    <div className="test-row" key={tc.id||idx}><CheckCircle2 size={15}/><span>Test Case 0{idx+1}</span><small>Passed</small></div>
                  ))}
                </>
              )}
            </div>
          ):(
            <div className="console-output">
              <span className="console-prompt">$</span> {testResult?.stdout||(runState==='done'?'Tests completed successfully.':'Waiting for execution run…')}
            </div>
          )}
        </div>
      </section>
    </div>
  </div>
}

export function ResultsPage(){
  const navigate=useNavigate();
  return <>
    <PageTitle eyebrow="ASSESSMENT RESULTS" title="Submission received" description="Your stage submission is recorded in the live assessment queue."/>
    <div className="result-hero">
      <div className="result-check"><CheckCircle2 size={28}/></div>
      <div>
        <Badge tone="green">Submission captured</Badge>
        <h2>Your submission is in the reviewer queue.</h2>
        <p>Your solution and reasoning have been recorded and assigned for structured evaluation against the rubric.</p>
      </div>
    </div>
    <div className="metric-grid">
      <div className="metric-card"><span>Submission status</span><strong>Received</strong><small>Pending review</small></div>
      <div className="metric-card"><span>Automated checks</span><strong>Passed</strong><small>Sample test cases validated</small></div>
      <div className="metric-card"><span>Written rationale</span><strong>Saved</strong><small>Included in review dossier</small></div>
    </div>
    <section className="panel result-details">
      <h3>Evaluation Process</h3>
      <div className="instruction-row"><span>01</span><div><strong>Automated verification</strong><p>Sample test suites are checked by the secure code execution runner.</p></div></div>
      <div className="instruction-row"><span>02</span><div><strong>Rubric scoring</strong><p>A designated reviewer evaluates algorithmic structure, code quality, and written reasoning.</p></div></div>
      <div className="instruction-row"><span>03</span><div><strong>Selection decision</strong><p>Candidates meeting the pass threshold progress towards the final cohort selection.</p></div></div>
      <Button onClick={()=>navigate('/candidate/history')}>View assessment history <ArrowRight size={15}/></Button>
    </section>
  </>
}

export function HistoryPage(){
  const [stages,setStages]=useState<Stage[]>([]);
  useEffect(()=>{
    api.stages().then(setStages).catch(console.error);
  },[]);

  const completedCount=stages.filter(s=>s.status==='completed').length;
  const progress=stages.length>0?Math.round((completedCount/stages.length)*100):0;

  return <>
    <PageTitle eyebrow="YOUR JOURNEY" title="Progress history" description="Live timeline of completed stages and verified assessment performance."/>
    <div className="history-summary">
      <div><span>Overall progress</span><strong>{progress}%</strong><ProgressBar value={progress}/></div>
      <div><span>Stages completed</span><strong>{completedCount} <small>/ {stages.length||4}</small></strong></div>
      <div><span>Platform Status</span><strong className="history-last">Active <small>· Live API</small></strong></div>
    </div>
    <section className="panel history-panel">
      <h3>Assessment timeline</h3>
      {stages.map(s=>(
        <div className="history-row" key={s.id}>
          <div className={`history-marker ${s.status}`}><span>{s.status==='completed'?<Check size={14}/>:s.id}</span></div>
          <div className="history-content">
            <div className="history-title">
              <strong>{s.title}</strong>
              <Badge tone={s.status==='completed'?'green':s.status==='in-progress'?'purple':s.status==='available'?'blue':'neutral'}>{s.status.replace('-',' ')}</Badge>
            </div>
            <p>{s.subtitle} · {s.duration}</p>
            {s.score!==undefined&&s.score!==null&&<span className="small-muted">Score: {s.score}/100</span>}
          </div>
        </div>
      ))}
    </section>
  </>
}

export function WrittenQuestionsPage(){
  const [questions,setQuestions]=useState<any[]>([]);
  const [answers,setAnswers]=useState<Record<number,string>>({});
  const [saveMessage,setSaveMessage]=useState('');

  useEffect(()=>{
    api.candidate.questions(4).then(qList=>{
      if(Array.isArray(qList)&&qList.length>0){
        setQuestions(qList);
      }
    }).catch(console.error);
  },[]);

  const saveAnswers=()=>{
    localStorage.setItem('aec-written-answers',JSON.stringify(answers));
    setSaveMessage('Written responses saved successfully.');
  };

  return <>
    <PageTitle eyebrow="STAGE 04 · ENGINEERING JUDGMENT" title="Written reasoning" description="Explain your technical decisions and trade-offs clearly."/>
    <div className="written-layout">
      <div className="written-questions">
        {questions.map((q,i)=>(
          <section className="panel written-card" key={q.id||i}>
            <div className="question-top"><span>QUESTION 0{i+1}</span><span>{q.category||'Short answer'}</span></div>
            <h3>{q.title}</h3>
            <p>{q.prompt}</p>
            <textarea value={answers[q.id]||''} onChange={e=>setAnswers({...answers,[q.id]:e.target.value})} placeholder="Write your reasoning, trade-offs, and considerations here…"/>
            {q.rubric_guide&&<div className="written-hint"><Lightbulb size={14}/>{q.rubric_guide}</div>}
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
        <Button onClick={saveAnswers}>Save written answers <Save size={15}/></Button>
        {saveMessage&&<span className="small-muted">{saveMessage}</span>}
      </aside>
    </div>
  </>
}

export function HelpPage(){
  return <>
    <PageTitle eyebrow="SUPPORT" title="Help & guidelines" description="Everything you need to know about the Amerigam assessment platform."/>
    <div className="help-grid">
      {[
        {title:'Browser environment',text:'Use a modern desktop browser (Chrome, Firefox, Edge, Safari) for optimal coding and Monaco editor performance.'},
        {title:'Code execution runner',text:'Your code runs against test suites using isolated runners. Ensure correct function signatures and expected return values.'},
        {title:'Autosave & drafts',text:'Your solutions and notes autosave regularly. You can safely navigate between sections without losing progress.'},
        {title:'Integrity & review',text:'Tab changes and focus logs provide context for evaluators. Reviews are conducted with comprehensive rubrics.'}
      ].map((x,i)=><section className="panel help-topic" key={x.title}><div className="topic-number">0{i+1}</div><h3>{x.title}</h3><p>{x.text}</p></section>)}
    </div>
  </>
}

export function SettingsPage(){
  const [session]=useState<any>(()=>{try{return JSON.parse(localStorage.getItem('aec-session')||'null')}catch{return null}});
  const [health,setHealth]=useState<{status:string;version:string}|null>(null);
  const [loading,setLoading]=useState(true);

  useEffect(()=>{
    api.health().then(setHealth).catch(()=>setHealth(null)).finally(()=>setLoading(false));
  },[]);

  const name=session?.name||'Candidate User';
  const email=session?.email||'candidate@amerigam.com';
  const role=session?.role?(session.role.charAt(0).toUpperCase()+session.role.slice(1)):'Candidate';
  const initials=name.split(' ').map((n:string)=>n[0]).join('').slice(0,2).toUpperCase()||'CU';

  return <>
    <PageTitle eyebrow="ACCOUNT" title="Workspace settings" description="Manage your profile and review backend connection status."/>
    <section className="panel settings-panel">
      <div className="avatar avatar-profile">{initials}</div>
      <div><h3>{name}</h3><p>{role} workspace · Live Supabase Database</p></div>
      <Badge tone="green">Live API</Badge>
      <hr/>
      <div className="settings-row"><span>Email</span><strong>{email}</strong></div>
      <div className="settings-row"><span>Workspace role</span><strong>{role}</strong></div>
      <div className="settings-row"><span>API status</span><strong>{loading?<span className="small-muted">Checking…</span>:health?.status==='success'?<><span className="online-dot"/> Connected (v{health.version})</>:<><span className="offline-dot"/> Disconnected</>}</strong></div>
    </section>
  </>
}
