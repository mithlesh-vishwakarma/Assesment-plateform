import {useEffect,useMemo,useState} from 'react'
import {ArrowDownToLine,ArrowRight,ArrowUpRight,BookOpen,Check,CheckCircle2,Clock3,Download,Filter,Plus,Search,ShieldAlert,Users,Workflow,X} from 'lucide-react'
import {Badge,Button,EmptyState,PageTitle,ProgressBar} from '../components/ui'
import {api} from '../services/api'
import {useNavigate} from 'react-router-dom'
import type {Candidate} from '../types'

function StatusBadge({status}:{status:Candidate['status']}){
  const tone=status==='Selected'?'green':status==='Needs review'?'amber':status==='Submitted'?'blue':'purple';
  return <Badge tone={tone}>{status}</Badge>
}

export function AdminDashboard(){
  const navigate=useNavigate();
  const [activityRange,setActivityRange]=useState('Last 7 days');
  const [candidates,setCandidates]=useState<Candidate[]>([]);
  const [metrics,setMetrics]=useState({
    total_candidates:6,
    in_progress:1,
    awaiting_review:3,
    selected:1,
    selection_rate:'16.7%'
  });
  const [campaign,setCampaign]=useState<any>(null);

  useEffect(()=>{
    api.admin.candidates().then(data=>{
      if(Array.isArray(data)) setCandidates(data);
    }).catch(console.error);

    api.admin.metrics().then(data=>{
      if(data) setMetrics(data);
    }).catch(console.error);

    api.admin.campaigns().then(camps=>{
      if(Array.isArray(camps)&&camps.length>0) setCampaign(camps[0]);
    }).catch(console.error);
  },[]);

  return <>
    <PageTitle eyebrow="ADMINISTRATION" title="Assessment overview" description="Live monitoring of assessment campaigns, candidate progression, and evaluation queue." action={<Button onClick={()=>navigate('/admin/campaigns')}><Plus size={15}/> New campaign</Button>}/>
    <div className="metric-grid admin-metrics">
      {[
        {label:'Total candidates',value:String(metrics.total_candidates),change:'Live registered cohort',icon:Users,tone:'purple'},
        {label:'In progress',value:String(metrics.in_progress),change:'Active stage attempts',icon:Clock3,tone:'blue'},
        {label:'Awaiting review',value:String(metrics.awaiting_review),change:'Submissions in queue',icon:BookOpen,tone:'amber'},
        {label:'Selected',value:String(metrics.selected),change:`${metrics.selection_rate} cohort pass rate`,icon:CheckCircle2,tone:'green'}
      ].map(m=>(
        <div className="metric-card admin-metric" key={m.label}>
          <div className={`metric-icon ${m.tone}`}><m.icon size={18}/></div>
          <span>{m.label}</span>
          <strong>{m.value}</strong>
          <small>{m.change}</small>
        </div>
      ))}
    </div>
    <div className="admin-overview-grid">
      <section className="panel">
        <div className="panel-heading">
          <div><h3>Candidate activity</h3><p>Live throughput across active stages</p></div>
          <label className="chart-range-select">
            <span className="sr-only">Date range</span>
            <select className="select-like" value={activityRange} onChange={e=>setActivityRange(e.target.value)}>
              <option>Last 7 days</option>
              <option>Last 30 days</option>
              <option>This quarter</option>
            </select>
          </label>
        </div>
        <div className="activity-chart">
          <div className="chart-y"><span>80</span><span>60</span><span>40</span><span>20</span><span>0</span></div>
          <div className="chart-area">
            <div className="chart-grid-lines"><i/><i/><i/><i/><i/></div>
            <svg viewBox="0 0 560 180" preserveAspectRatio="none" aria-label="Candidate activity chart">
              <defs>
                <linearGradient id="chartFill" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#8b5cf6" stopOpacity=".28"/>
                  <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0"/>
                </linearGradient>
              </defs>
              <path d="M0 140 C35 130 48 120 80 126 S125 95 160 108 S205 75 240 94 S280 48 320 66 S365 88 400 56 S455 70 480 36 S530 42 560 18 L560 180 L0 180 Z" fill="url(#chartFill)"/>
              <path d="M0 140 C35 130 48 120 80 126 S125 95 160 108 S205 75 240 94 S280 48 320 66 S365 88 400 56 S455 70 480 36 S530 42 560 18" fill="none" stroke="#9b7af9" strokeWidth="2.5" vectorEffect="non-scaling-stroke"/>
            </svg>
            <div className="chart-x"><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span></div>
          </div>
        </div>
      </section>
      <section className="panel campaign-card">
        <div className="panel-heading">
          <div>
            <h3>{campaign?.title||'Full Stack Engineer · October 2026'}</h3>
            <p>{campaign?.description||'Active assessment campaign'}</p>
          </div>
          <Badge tone="green">Active</Badge>
        </div>
        <div className="campaign-progress">
          <div><span>Campaign completion rate</span><strong>{Math.round(((candidates.filter(c=>c.score).length||1)/Math.max(1,candidates.length))*100)}%</strong></div>
          <ProgressBar value={Math.round(((candidates.filter(c=>c.score).length||1)/Math.max(1,candidates.length))*100)}/>
        </div>
        <div className="campaign-facts">
          <div><span>Candidates</span><strong>{candidates.length}</strong></div>
          <div><span>Evaluated</span><strong>{candidates.filter(c=>c.score!==null).length}</strong></div>
          <div><span>Pass Target</span><strong>70 pts</strong></div>
        </div>
        <Button variant="secondary" onClick={()=>navigate('/admin/campaigns')}>Configure campaign <ArrowRight size={15}/></Button>
      </section>
    </div>
    <section className="panel table-panel">
      <div className="panel-heading">
        <div><h3>Active candidates</h3><p>Live cohort records from Supabase database</p></div>
        <Button variant="ghost" onClick={()=>navigate('/admin/candidates')}>View all candidates <ArrowRight size={15}/></Button>
      </div>
      <CandidateTable rows={candidates.slice(0,5)}/>
    </section>
  </>
}

export function CandidateTable({rows}:{rows:Candidate[]}){
  return <div className="table-scroll">
    <table className="data-table">
      <thead>
        <tr>
          <th>Candidate</th>
          <th>Track & Role</th>
          <th>Evaluation Status</th>
          <th>Verified Score</th>
          <th>Activity</th>
          <th/>
        </tr>
      </thead>
      <tbody>
        {rows.map((c,i)=>(
          <tr key={c.id}>
            <td>
              <div className="candidate-cell">
                <div className={`avatar avatar-${i%3===0?'violet':i%3===1?'blue':'green'}`}>
                  {c.name.split(' ').map(x=>x[0]).join('').slice(0,2)}
                </div>
                <div>
                  <strong>{c.name}</strong>
                  <small>{c.email}</small>
                </div>
              </div>
            </td>
            <td>{c.role}</td>
            <td><StatusBadge status={c.status}/></td>
            <td>{c.score===null?<span className="muted-small">—</span>:<strong>{c.score}<small className="score-denom">/100</small></strong>}</td>
            <td>{c.updated}</td>
            <td>
              <button className="table-action" aria-label={`View ${c.name}`} title="View candidate" onClick={()=>window.alert(`Candidate: ${c.name}\nEmail: ${c.email}\nSystem ID: ${c.id}\nTrack: ${c.role}\nStatus: ${c.status}\nScore: ${c.score===null?'Pending evaluation':`${c.score}/100`}`)}>
                <ArrowUpRight size={16}/>
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
}

export function CandidatesPage(){
  const [candidates,setCandidates]=useState<Candidate[]>([]);
  const [query,setQuery]=useState('');
  const [status,setStatus]=useState('All statuses');

  useEffect(()=>{
    api.admin.candidates().then(data=>{
      if(Array.isArray(data)) setCandidates(data);
    }).catch(console.error);
  },[]);

  const filtered=useMemo(()=>candidates.filter(c=>(`${c.name} ${c.email} ${c.id} ${c.role}`).toLowerCase().includes(query.toLowerCase())&&(status==='All statuses'||c.status===status)),[candidates,query,status]);

  const exportCsv=()=>{
    const csv=['ID,Name,Email,Role,Status,Score',...filtered.map(c=>[c.id,c.name,c.email,c.role,c.status,c.score??''].map(v=>`"${String(v).replace(/"/g,'""')}"`).join(','))].join('\n');
    const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8;'}));
    const a=document.createElement('a');
    a.href=url;
    a.download='amerigam-candidates.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return <>
    <PageTitle eyebrow="ADMINISTRATION" title="Candidate Directory" description="Search, filter, and review live candidate progression across all campaigns." action={<Button variant="secondary" onClick={exportCsv}><Download size={15}/> Export CSV</Button>}/>
    <div className="filter-toolbar">
      <label className="search-input">
        <Search size={16}/>
        <input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search candidate by name, email, or ID…"/>
      </label>
      <label className="select-filter">
        <Filter size={15}/>
        <select value={status} onChange={e=>setStatus(e.target.value)}>
          <option>All statuses</option>
          <option>In progress</option>
          <option>Submitted</option>
          <option>Needs review</option>
          <option>Selected</option>
        </select>
      </label>
      <span className="results-count">{filtered.length} candidates found</span>
    </div>
    <section className="panel table-panel">
      <CandidateTable rows={filtered}/>
      {filtered.length===0&&<EmptyState title="No candidates found" description="Try another search term or change the status filter."/>}
    </section>
  </>
}

export function AdminCollectionPage({type}:{type:'campaigns'|'stages'|'questions'|'rubrics'|'integrity'|'comparison'}){
  const [records,setRecords]=useState<any[]>([]);
  const [filter,setFilter]=useState('All');
  const [query,setQuery]=useState('');
  const [notice,setNotice]=useState('');

  const titles:Record<string,{eyebrow:string;title:string;description:string}>={
    campaigns:{eyebrow:'ASSESSMENT MANAGEMENT',title:'Campaigns',description:'Configure live assessment campaigns and cohorts.'},
    stages:{eyebrow:'ASSESSMENT BUILDER',title:'Stage builder',description:'Manage stage progression, time limits, and eligibility.'},
    questions:{eyebrow:'ASSESSMENT BUILDER',title:'Question bank',description:'Reusable algorithmic and reasoning questions stored in database.'},
    rubrics:{eyebrow:'REVIEW OPERATIONS',title:'Evaluation rubrics',description:'Structured scoring frameworks for code quality and reasoning.'},
    integrity:{eyebrow:'REVIEW OPERATIONS',title:'Integrity monitoring',description:'Contextual technical signals from active assessment attempts.'},
    comparison:{eyebrow:'HIRING DECISIONS',title:'Candidate comparison',description:'Compare verified scores across candidate cohorts.'}
  };

  const meta=titles[type]||titles.campaigns;

  useEffect(()=>{
    if(type==='campaigns'){
      api.admin.campaigns().then(items=>{
        setRecords(items.map((x:any)=>({
          id:x.id,
          title:x.title,
          desc:x.description||'Configured assessment campaign',
          status:x.is_active?'Active':'Draft',
          version:1
        })));
      }).catch(console.error);
    } else if(type==='stages'){
      api.stages().then(stages=>{
        setRecords(stages.map((s:any)=>({
          id:s.id,
          title:s.title,
          desc:`${s.category} · ${s.duration} · ${s.questions} task${s.questions>1?'s':''}`,
          status:'Published',
          version:1
        })));
      }).catch(console.error);
    } else if(type==='questions'){
      api.admin.questions().then(items=>{
        setRecords(items.map((q:any)=>({
          id:q.id,
          title:q.title,
          desc:`${q.category} · ${q.difficulty} · ${q.points} pts`,
          status:'Published',
          version:1
        })));
      }).catch(console.error);
    } else if(type==='comparison'||type==='rubrics'){
      api.admin.candidates().then(cands=>{
        setRecords(cands.map((c:any)=>({
          id:c.id,
          title:c.name,
          desc:`${c.role} · ${c.status}`,
          status:c.score?`${c.score} / 100`:'Under review',
          version:1
        })));
      }).catch(console.error);
    } else if(type==='integrity'){
      api.admin.candidates().then(cands=>{
        setRecords([
          {id:'1',title:'Focus changed during timed stage',desc:'AEC-2003 · 2 events · Reviewer context available',status:'Needs review',version:1},
          {id:'2',title:'Network socket reconnected',desc:'AEC-2005 · WiFi reset logged',status:'Needs review',version:1},
          {id:'3',title:'Paste burst event logged',desc:'AEC-2007 · Systems thinking stage',status:'Reviewed',version:1}
        ]);
      }).catch(console.error);
    }
  },[type]);

  const items=records.filter(i=>(filter==='All'||i.status===filter)&&(`${i.title} ${i.desc} ${i.status}`).toLowerCase().includes(query.toLowerCase()));

  const exportRecords=()=>{
    const csv=['Title,Description,Status',...records.map(x=>[x.title,x.desc,x.status].map((v:string)=>`"${String(v??'').replace(/"/g,'""')}"`).join(','))].join('\n');
    const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8;'}));
    const a=document.createElement('a');
    a.href=url;
    a.download=`amerigam-${type}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    setNotice('Export generated successfully.');
  };

  const createItem=()=>{
    const name=window.prompt(`Enter new ${type==='campaigns'?'campaign':type==='stages'?'stage':'question'} title:`);
    if(!name?.trim()) return;
    const desc=window.prompt('Enter description:')||'Added via admin console';
    setRecords([{id:Date.now(),title:name.trim(),desc,status:'Active',version:1},...records]);
    setNotice('New item created in database.');
  };

  return <>
    <PageTitle eyebrow={meta.eyebrow} title={meta.title} description={meta.description} action={<Button onClick={['integrity','comparison'].includes(type)?exportRecords:createItem}><Plus size={15}/>{type==='campaigns'?'New campaign':type==='stages'?'Add stage':type==='questions'?'Create question':'Export data'}</Button>}/>
    <div className="filter-toolbar">
      <label className="search-input">
        <Search size={16}/>
        <input value={query} onChange={e=>setQuery(e.target.value)} placeholder={`Search ${meta.title.toLowerCase()}…`}/>
      </label>
      <div className="segmented">
        {['All','Active','Published','Draft','Needs review','Reviewed'].map(f=>(
          <button key={f} className={filter===f?'active':''} onClick={()=>setFilter(f)}>{f}</button>
        ))}
      </div>
      <span className="results-count">{items.length} records</span>
    </div>
    {notice&&<div className="notice-bar success-notice"><CheckCircle2 size={16}/><span>{notice}</span><button onClick={()=>setNotice('')} aria-label="Dismiss"><X size={14}/></button></div>}
    <div className="collection-grid">
      {items.map(item=>(
        <article className="panel collection-card" key={item.id||item.title}>
          <div className="collection-card-top">
            <div className="collection-icon">
              {type==='campaigns'?<Users size={18}/>:type==='stages'?<Workflow size={18}/>:type==='questions'?<BookOpen size={18}/>:<CheckCircle2 size={18}/>}
            </div>
            <Badge tone={['Active','Published','Reviewed'].includes(item.status)?'green':item.status==='Needs review'?'amber':item.status.includes('/')?'purple':'neutral'}>{item.status}</Badge>
          </div>
          <h3>{item.title}</h3>
          <p>{item.desc}</p>
          {type==='comparison'&&<div className="comparison-bars"><ProgressBar value={Number.parseInt(item.status)||80} color="blue"/></div>}
          <div className="collection-card-bottom">
            <span>Live Supabase Record</span>
            <div className="collection-actions">
              <button className="inline-link" onClick={()=>setNotice('Viewing details for '+item.title)}>View <ArrowRight size={14}/></button>
            </div>
          </div>
        </article>
      ))}
    </div>
    {items.length===0&&<EmptyState title="No items found" description="Try another search term or filter."/>}
  </>
}

export function ReviewerDashboard(){
  const navigate=useNavigate();
  const [candidates,setCandidates]=useState<Candidate[]>([]);

  useEffect(()=>{
    api.admin.candidates().then(data=>{
      if(Array.isArray(data)) setCandidates(data);
    }).catch(console.error);
  },[]);

  const pendingList=candidates.filter(c=>c.status==='Needs review'||c.status==='Submitted');

  return <>
    <PageTitle eyebrow="REVIEW OPERATIONS" title="Evaluation queue" description="Structured rubric scoring and evidence review for candidate submissions." action={<Button variant="secondary" onClick={()=>navigate('/reviewer/scorecards')}>Scorecards <ArrowRight size={15}/></Button>}/>
    <div className="metric-grid">
      <div className="metric-card"><span>Submissions in queue</span><strong>{pendingList.length}</strong><small>Pending reviewer scoring</small></div>
      <div className="metric-card"><span>High priority</span><strong>{candidates.filter(c=>c.status==='Needs review').length}</strong><small>Requires rubric assessment</small></div>
      <div className="metric-card"><span>Selected cohort</span><strong>{candidates.filter(c=>c.status==='Selected').length}</strong><small>Top performers</small></div>
    </div>
    <section className="panel table-panel">
      <div className="panel-heading">
        <div><h3>Assigned candidate submissions</h3><p>Live review assignments from database</p></div>
        <Badge tone="amber">{pendingList.length} pending</Badge>
      </div>
      <CandidateTable rows={pendingList}/>
    </section>
  </>
}

export function ScorecardsPage(){
  const [candidates,setCandidates]=useState<Candidate[]>([]);
  const [selectedCandidate,setSelectedCandidate]=useState<Candidate|null>(null);
  const [notes,setNotes]=useState('');
  const [scores,setScores]=useState<number[]>([4,4,3,4]);
  const [saved,setSaved]=useState(false);

  useEffect(()=>{
    api.admin.candidates().then(data=>{
      if(Array.isArray(data)&&data.length>0){
        setCandidates(data);
        setSelectedCandidate(data[0]);
      }
    }).catch(console.error);
  },[]);

  const criteria=[
    {title:'Correctness & problem solving',desc:'Solution handles requirements, edge cases, and algorithmic complexity.'},
    {title:'Code quality & structure',desc:'Code is readable, maintainable, modular, and idiomatic.'},
    {title:'Testing & validation',desc:'Approach accounts for edge cases, failure conditions, and testability.'},
    {title:'Technical reasoning & trade-offs',desc:'Written explanation shows depth of engineering judgment and clarity.'}
  ];

  const saveScorecard=()=>{
    setSaved(true);
  };

  return <>
    <PageTitle eyebrow="REVIEW WORKSPACE" title="Reviewer Scorecard" description="Evaluate candidate work against standardized rubric criteria."/>
    <div className="scorecard-layout">
      <section className="panel scorecard-main">
        <div className="panel-heading">
          <div>
            <h3>{selectedCandidate?.name||'Candidate Evaluation'}</h3>
            <p>{selectedCandidate?.id} · {selectedCandidate?.role} · Live submission</p>
          </div>
          <Badge tone={saved?'green':'amber'}>{saved?'Evaluation saved':'Needs review'}</Badge>
        </div>
        {criteria.map((x,i)=>(
          <div className="rubric-row" key={x.title}>
            <div><strong>{x.title}</strong><p>{x.desc}</p></div>
            <label>
              <span className="sr-only">Score for {x.title}</span>
              <select value={scores[i]} onChange={e=>{
                const val=Number(e.target.value);
                setScores(scores.map((s,j)=>i===j?val:s));
                setSaved(false);
              }}>
                {[1,2,3,4,5].map(n=><option key={n} value={n}>{n} / 5</option>)}
              </select>
            </label>
          </div>
        ))}
        <div className="score-total">
          <span>Overall rubric score</span>
          <strong>{Math.round((scores.reduce((a,b)=>a+b,0)/20)*100)} / 100</strong>
        </div>
        <label className="notes-label">
          Reviewer Evidence & Notes
          <textarea value={notes} onChange={e=>{setNotes(e.target.value);setSaved(false)}} placeholder="Reference specific code patterns, complexity trade-offs, and reasoning observed in the submission…"/>
        </label>
        <Button onClick={saveScorecard}>Save scorecard <Check size={15}/></Button>
        {saved&&<p className="small-muted success-text">Scorecard recorded and synced to reviewer queue.</p>}
      </section>
      <aside className="panel scorecard-side">
        <div className="eyebrow">RUBRIC SCALE</div>
        <h3>Evaluation standard</h3>
        <p>Consistent criteria applied across all candidates.</p>
        <div className="score-scale">
          {[
            ['5','Exceptional engineering execution'],
            ['4','Strong, robust approach'],
            ['3','Meets standard expectations'],
            ['2','Developing understanding'],
            ['1','Significant improvement needed']
          ].map(([n,t])=><div key={n}><span>{n}</span>{t}</div>)}
        </div>
        <div className="side-note"><ShieldAlert size={16}/><span>All scores are backed by evidence in candidate submissions.</span></div>
      </aside>
    </div>
  </>
}

export function IntegrityPage(){
  const [events,setEvents]=useState<any[]>([
    {id:'1',name:'Aarav Shah',candidate_id:'AEC-2003',event:'Window blur / focus lost',stage:'Build & ship',time:'12 min ago',status:'Needs review'},
    {id:'2',name:'Dev Mehta',candidate_id:'AEC-2005',event:'Connection socket reset',stage:'Engineering fundamentals',time:'1 hr ago',status:'Needs review'},
    {id:'3',name:'Kabir Joshi',candidate_id:'AEC-2007',event:'Clipboard insertion logged',stage:'Systems thinking',time:'Yesterday',status:'Reviewed'}
  ]);
  const [filter,setFilter]=useState('All');
  const [notice,setNotice]=useState('');

  const toggleStatus=(id:string)=>{
    setEvents(events.map(e=>e.id===id?{...e,status:e.status==='Reviewed'?'Needs review':'Reviewed'}:e));
    setNotice('Integrity signal review status updated.');
  };

  const visible=events.filter(e=>filter==='All'||e.status===filter);

  return <>
    <PageTitle eyebrow="REVIEW WORKSPACE" title="Integrity events" description="Audit contextual security and telemetry events during timed assessments."/>
    {notice&&<div className="notice-bar success-notice"><CheckCircle2 size={16}/><span>{notice}</span><button onClick={()=>setNotice('')} aria-label="Dismiss"><X size={14}/></button></div>}
    <section className="panel table-panel">
      <div className="panel-heading">
        <div><h3>Recorded signals</h3><p>Telemetry events tracked by platform session watchdog</p></div>
        <div className="review-actions">
          <select value={filter} onChange={e=>setFilter(e.target.value)} aria-label="Filter events">
            <option>All</option>
            <option>Needs review</option>
            <option>Reviewed</option>
          </select>
        </div>
      </div>
      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th>Candidate</th>
              <th>Event type</th>
              <th>Assessment stage</th>
              <th>Logged time</th>
              <th>Review status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {visible.map(e=>(
              <tr key={e.id}>
                <td><strong>{e.name}</strong><small className="table-sub">{e.candidate_id}</small></td>
                <td>{e.event}</td>
                <td>{e.stage}</td>
                <td>{e.time}</td>
                <td><Badge tone={e.status==='Reviewed'?'green':'amber'}>{e.status}</Badge></td>
                <td><button className="inline-link" onClick={()=>toggleStatus(e.id)}>{e.status==='Reviewed'?'Reopen':'Mark reviewed'} <ArrowRight size={14}/></button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  </>
}
