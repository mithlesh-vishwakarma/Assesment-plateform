import type { ApiError, Candidate, Stage } from '../types'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'
async function request<T>(path:string, init?:RequestInit):Promise<T>{
 const response=await fetch(`${API_BASE_URL}${path}`,{...init,headers:{'Content-Type':'application/json',...(init?.headers??{})},credentials:'include'})
 if(!response.ok){let payload:ApiError={};try{payload=await response.json()}catch{/* non-JSON response */}throw new Error(payload.detail??payload.message??`Request failed (${response.status})`)}
 if(response.status===204)return undefined as T
 return response.json() as Promise<T>
}
/** Proposed DRF contract. Align paths and schemas with backend before production. */
export const api={
 health:()=>request<{status:string}>('/health/'),
 stages:()=>request<Stage[]>('/candidate/stages/'),
 candidates:()=>request<Candidate[]>('/admin/candidates/'),
 saveDraft:(payload:{assessmentId:string;answer:string})=>request<{savedAt:string}>('/candidate/drafts/',{method:'PUT',body:JSON.stringify(payload)}),
 submitAssessment:(payload:{assessmentId:string;answers:unknown})=>request<{submissionId:string;status:string}>('/candidate/submissions/',{method:'POST',body:JSON.stringify(payload)}),
 login:(payload:{email:string;password:string})=>request<{user:{id:string;name:string;role:string}}>('/auth/login/',{method:'POST',body:JSON.stringify(payload)}),
 register:(payload:{name:string;email:string;password:string})=>request<{id:string}>('/auth/register/',{method:'POST',body:JSON.stringify(payload)})
}
