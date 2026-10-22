# Amerigam Engineering Challenge — Frontend

A responsive dark-first React + TypeScript assessment platform with public, candidate, admin and reviewer workspaces. The visual direction uses deep navy surfaces, purple/blue accents, subtle motion, responsive layouts and keyboard focus states.

## Run locally
1. Install Node.js 20 or newer.
2. Extract the ZIP and open the project folder in VS Code.
3. In the terminal run:
   ```bash
   npm install
   npm run dev
   ```
4. Open the local URL printed by Vite (usually `http://localhost:5173`).

## Build
```bash
npm run build
```

## Included routes
- Public: landing, login, registration, rules and consent.
- Candidate: dashboard, stage intro, coding workspace, Monaco editor, language selection, simulated test output, local draft autosave, written reasoning, submission confirmation, progress history, help and settings.
- Admin: overview, candidate management/search/filter, campaigns, stage builder, question bank, rubrics, integrity review and candidate comparison.
- Reviewer: review queue, scorecards and integrity events.

## Stack
React, TypeScript, Vite, Tailwind CSS v4, React Router, TanStack Query, React Hook Form, Zod, Monaco Editor and Lucide React. Shared layouts and UI components are in `src/components`; page views are in `src/pages`; API contracts are in `src/services/api.ts`; demo types/data are in `src/types.ts` and `src/data/demo.ts`.

## Demo versus production
The UI can be explored before the backend is connected. If the authentication API is unavailable, the sign-in/sign-up form opens a local demo session. Draft code and written answers are saved in the current browser's local storage. Test output is explicitly simulated; it does not compile or execute submitted code. Demo candidate/admin/reviewer data is illustrative and must not be treated as production records.

## Django REST Framework integration
Set `VITE_API_BASE_URL` in `.env` to the agreed Django REST Framework API root. `src/services/api.ts` contains proposed typed endpoint contracts. Align routes, request/response schemas, authentication/session strategy, CSRF behavior and permissions with the backend team before production use. Add loading/error/empty states to each server-backed query as API contracts become available.

## Security requirements for production
- Backend is authoritative for permissions, stage eligibility, scoring, and assessment deadlines.
- Run untrusted code only in a secure, isolated execution service with resource/time limits; never execute arbitrary candidate code in the frontend or ordinary API process.
- Use server-side authorization, audit trails, rate limits and appropriate CSRF/session protections.
- Focus-change events are contextual signals, not automatic proof of misconduct.
- Admin changes should create draft versions and must not mutate an active assessment version.
