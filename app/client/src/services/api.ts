import type { ApiError, Candidate, Stage } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api'

export function getAuthToken(): string | null {
    return localStorage.getItem('token') || localStorage.getItem('aec-token')
}

export function setAuthToken(token: string) {
    localStorage.setItem('token', token)
    localStorage.setItem('aec-token', token)
}

export function clearAuthToken() {
    localStorage.removeItem('token')
    localStorage.removeItem('aec-token')
    localStorage.removeItem('aec-session')
    localStorage.removeItem('aec-active-role')
}

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const token = getAuthToken()
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Token ${token}` } : {}),
        ...((init?.headers as Record<string, string>) ?? {}),
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...init,
        headers,
        credentials: 'include',
    })

    if (!response.ok) {
        let payload: ApiError = {}
        try {
            payload = await response.json()
        } catch {
            // non-JSON response
        }
        const errorMsg =
            payload.detail ??
            payload.message ??
            (payload as any).error ??
            (payload.errors ? Object.values(payload.errors).flat().join(', ') : undefined) ??
            `Request failed with status ${response.status}`
        throw new Error(errorMsg)
    }

    if (response.status === 204) return undefined as T
    return response.json() as Promise<T>
}

export const api = {
    // 1. System Health
    health: () =>
        request<{
            status: string
            message: string
            version: string
            active_models?: string[]
        }>('/health/'),

    // 2. Authentication
    auth: {
        login: (credentials: { username?: string; email?: string; password: string }) =>
            request<{ token: string; user: any }>('/auth/login/', {
                method: 'POST',
                body: JSON.stringify(credentials),
            }),

        register: (payload: { name?: string; username?: string; email: string; password: string; role?: string }) =>
            request<{ token: string; user: any }>('/auth/register/', {
                method: 'POST',
                body: JSON.stringify(payload),
            }),

        logout: () =>
            request<{ message: string }>('/auth/logout/', {
                method: 'POST',
            }),

        me: () => request<any>('/auth/me/'),
    },

    // 3. Candidate Operations
    candidate: {
        campaigns: () => request<any[]>('/candidate/campaigns/'),
        status: (campaignId: number) => request<any>(`/candidate/status/${campaignId}/`),
        startStage: (stageId: number) =>
            request<{ stage_attempt_id: number; deadline: string; remaining_seconds: number }>(
                `/candidate/stages/${stageId}/start/`,
                { method: 'POST' }
            ),
        questions: (stageId: number) => request<any[]>(`/candidate/stages/${stageId}/questions/`),
        autosaveDraft: (payload: {
            stage_attempt_id: number
            question_id?: number
            code?: string
            language?: string
            written_response?: string
        }) =>
            request<{ status: string; saved_at: string }>('/candidate/submissions/autosave/', {
                method: 'POST',
                body: JSON.stringify(payload),
            }),
        finalizeSubmission: (payload: { stage_attempt_id: number }) =>
            request<{ status: string; submitted_at: string }>('/candidate/submissions/finalize/', {
                method: 'POST',
                body: JSON.stringify(payload),
            }),
        runSample: (payload: { stage_question_id?: number; code: string; language: string; stdin?: string }) =>
            request<{
                stdout: string
                stderr?: string
                status: string
                time?: string
                memory?: number
            }>('/candidate/execution/run-sample/', {
                method: 'POST',
                body: JSON.stringify(payload),
            }),
        recordIntegrity: (payload: { stage_attempt_id: number; event_type: string; event_data?: any }) =>
            request<{ status: string }>('/candidate/integrity/events/', {
                method: 'POST',
                body: JSON.stringify(payload),
            }),
    },

    // 4. Admin Operations
    admin: {
        candidates: () => request<Candidate[]>('/admin/candidates/'),
        metrics: () => request<{
            total_candidates: number
            in_progress: number
            awaiting_review: number
            selected: number
            selection_rate: string
        }>('/admin/overview-metrics/'),
        campaigns: () => request<any[]>('/admin/campaigns/'),
        stages: () => request<any[]>('/admin/stages/'),
        questions: () => request<any[]>('/admin/questions/'),
        selections: () => request<any[]>('/admin/selections/'),
        auditLogs: () => request<any[]>('/admin/audit-logs/'),
        campaignSummary: (campaignId: number) =>
            request<any>(`/admin/reports/campaign-summary/${campaignId}/`),
    },

    // 5. Reviewer Operations
    reviewer: {
        assignments: () => request<any[]>('/reviewer/assignments/'),
        evaluation: (stageAttemptId: number) =>
            request<any>(`/reviewer/evaluations/${stageAttemptId}/`),
        submitScores: (stageAttemptId: number, scores: any) =>
            request<{ status: string }>(`/reviewer/evaluations/${stageAttemptId}/score/`, {
                method: 'POST',
                body: JSON.stringify(scores),
            }),
    },

    // Backwards compatibility shortcuts
    stages: () => request<Stage[]>('/candidate/stages/'),
    candidates: () => request<Candidate[]>('/admin/candidates/'),
}
