import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/Layouts'
import { PublicRoute, RoleProtectedRoute } from './components/RouteGuards'
import { AuthPage, LandingPage, RulesPage, ForgotPasswordPage } from './pages/PublicPages'
import {
  CandidateDashboard,
  CodingWorkspacePage,
  HelpPage,
  HistoryPage,
  ResultsPage,
  SettingsPage,
  StageIntroPage,
  WrittenQuestionsPage
} from './pages/CandidatePages'
import {
  AdminCollectionPage,
  AdminDashboard,
  CandidatesPage,
  IntegrityPage,
  ReviewerDashboard,
  ScorecardsPage
} from './pages/ManagementPages'

export default function App() {
  return (
    <Routes>
      {/* Public Pages: Blocked if already authenticated (redirects to workspace) */}
      <Route element={<PublicRoute />}>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<AuthPage mode="login" />} />
        <Route path="/register" element={<AuthPage mode="register" />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ForgotPasswordPage />} />
      </Route>

      {/* Rules Page: Viewable publicly or inside workspace */}
      <Route path="/rules" element={<RulesPage />} />

      {/* Candidate Workspace: Protected, Candidates & Admins only */}
      <Route element={<RoleProtectedRoute allowedRoles={['candidate']} />}>
        <Route element={<AppLayout role="candidate" />}>
          <Route path="/candidate" element={<CandidateDashboard />} />
          <Route path="/candidate/assessment" element={<Navigate to="/candidate/assessment/1" replace />} />
          <Route path="/candidate/assessment/:stageId" element={<StageIntroPage />} />
          <Route path="/candidate/workspace/:stageId" element={<CodingWorkspacePage />} />
          <Route path="/candidate/submission" element={<ResultsPage />} />
          <Route path="/candidate/results" element={<ResultsPage />} />
          <Route path="/candidate/reasoning" element={<WrittenQuestionsPage />} />
          <Route path="/candidate/history" element={<HistoryPage />} />
          <Route path="/candidate/help" element={<HelpPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Route>

      {/* Administrator Workspace: Strictly blocked for candidates and reviewers */}
      <Route element={<RoleProtectedRoute allowedRoles={['admin']} />}>
        <Route element={<AppLayout role="admin" />}>
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/candidates" element={<CandidatesPage />} />
          <Route path="/admin/campaigns" element={<AdminCollectionPage type="campaigns" />} />
          <Route path="/admin/stages" element={<AdminCollectionPage type="stages" />} />
          <Route path="/admin/questions" element={<AdminCollectionPage type="questions" />} />
          <Route path="/admin/rubrics" element={<AdminCollectionPage type="rubrics" />} />
          <Route path="/admin/integrity" element={<AdminCollectionPage type="integrity" />} />
          <Route path="/admin/comparison" element={<AdminCollectionPage type="comparison" />} />
        </Route>
      </Route>

      {/* Reviewer / Receiver Workspace: Evaluators and Admins only */}
      <Route element={<RoleProtectedRoute allowedRoles={['reviewer']} />}>
        <Route element={<AppLayout role="reviewer" />}>
          <Route path="/reviewer" element={<ReviewerDashboard />} />
          <Route path="/reviewer/scorecards" element={<ScorecardsPage />} />
          <Route path="/reviewer/integrity" element={<IntegrityPage />} />
        </Route>
      </Route>

      {/* Wildcard redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
