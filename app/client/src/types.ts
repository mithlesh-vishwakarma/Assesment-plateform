export type Role = 'candidate' | 'admin' | 'reviewer'
export type StageStatus = 'completed' | 'in-progress' | 'locked' | 'available'
export interface Stage { id:number; backend_id?:number; title:string; subtitle:string; category:string; duration:string; questions:number; status:StageStatus; score?:number }
export interface Candidate { id:string; name:string; email:string; role:string; status:'In progress'|'Submitted'|'Needs review'|'Selected'; score:number|null; updated:string }
export interface ApiError { detail?:string; message?:string; errors?:Record<string,string[]> }
