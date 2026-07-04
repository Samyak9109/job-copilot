# Job Copilot — Frontend (React + Vite + Tailwind)

## Run
```bash
npm install
cp .env.example .env    # VITE_API_BASE_URL=http://localhost:8000/api
npm run dev             # http://localhost:5173
```

## Stack
React 18 · React Router 6 · Axios · Tailwind CSS · lucide-react icons · Plus Jakarta Sans.

## Structure
```
src/
  api/client.js         axios instance (JWT interceptor + error helper)
  auth/                 AuthContext + ProtectedRoute
  components/           Layout, Sidebar, Toast, ui atoms (StatCard, Chip, Field…)
  pages/                Login, Register, Dashboard, UploadMemory, MemoryLibrary,
                        Generate, SkillGap, InterviewPrep, Jobs, JobDetail, Lifecycle, Settings
  styles/index.css      Tailwind layers + component classes
```

## Design
Clean light-theme SaaS dashboard — violet (`#7C3AED`) primary, pink accent, rounded-2xl
cards, soft shadows, sidebar nav. Accessible focus states, `prefers-reduced-motion`
respected, responsive from 375px up. SVG icons only (no emoji).
