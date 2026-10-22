import type { Candidate, Stage } from '../types'
export const stages:Stage[]=[
{id:1,title:'Engineering fundamentals',subtitle:'DSA & problem solving',category:'CORE',duration:'45 min',questions:3,status:'completed',score:86},
{id:2,title:'Build & ship',subtitle:'Frontend or backend challenge',category:'PRACTICAL',duration:'60 min',questions:2,status:'in-progress'},
{id:3,title:'Systems thinking',subtitle:'Architecture & trade-offs',category:'DESIGN',duration:'35 min',questions:4,status:'available'},
{id:4,title:'Engineering judgment',subtitle:'Written reasoning',category:'REASONING',duration:'25 min',questions:5,status:'locked'}]
export const candidates:Candidate[]=[
{id:'AEC-2048',name:'Aarav Shah',email:'aarav.shah@example.com',role:'Frontend Engineer',status:'Needs review',score:88,updated:'12 min ago'},
{id:'AEC-2047',name:'Meera Patel',email:'meera.patel@example.com',role:'Full Stack Engineer',status:'Submitted',score:82,updated:'38 min ago'},
{id:'AEC-2046',name:'Dev Mehta',email:'dev.mehta@example.com',role:'Backend Engineer',status:'In progress',score:null,updated:'1 hr ago'},
{id:'AEC-2045',name:'Riya Desai',email:'riya.desai@example.com',role:'Full Stack Engineer',status:'Selected',score:94,updated:'Yesterday'},
{id:'AEC-2044',name:'Kabir Joshi',email:'kabir.joshi@example.com',role:'DevOps Engineer',status:'Submitted',score:76,updated:'Yesterday'}]
