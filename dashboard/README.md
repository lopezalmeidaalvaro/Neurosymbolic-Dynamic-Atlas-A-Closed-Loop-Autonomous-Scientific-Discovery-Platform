# Neurosymbolic Atlas Dashboard

Next.js 16 App Router frontend for the Neurosymbolic Dynamic Atlas.

## Routes

- `/en/dashboard` and `/es/dashboard`: cinematic scientific overview.
- `/en/learn` and `/es/learn`: educational UX with Simple/Advanced explanations.
- `/en/discoveries` and `/es/discoveries`: scientific storytelling, findings, evidence, hypotheses, open questions, and literature memory.
- `/en/dashboard/benchmark`: benchmark comparison against DTW and ROCKET.
- `/en/dashboard/scientific-log`: scientific log view.
- `/en/dashboard/timeline`: research timeline.
- `/en/dashboard/roadmap`: roadmap.

Root redirects:

- `/learn` -> `/en/learn`
- `/discoveries` -> `/en/discoveries`

## Data Layers

All files in `data/` are static and JSON-serializable TypeScript objects. They must not contain JSX, hooks, runtime persistence, or non-serializable values.

- `learningData.ts`: educational concepts and guided learning steps.
- `researchFindings.ts`: validated, observed, uncertain, rejected, and hypothesis-state findings.
- `hypotheses.ts`: active research hypotheses.
- `openQuestions.ts`: unresolved scientific questions.
- `scientificMemory.ts`: narrative memory and literature references.

## UI Systems

- `components/cinematic`: ambient scientific background.
- `components/educational`: explainability and learning components.
- `components/scientific`: equations, discovery cards, evidence panels, hypotheses, and research narrative.
- `components/motion`: reveal, scroll, and counter motion primitives.
- `components/ui`: glass surfaces, panels, controls, and shared visual primitives.

## Commands

```bash
npm install
npm run dev
npm run build
npm run start
```

## Validation

Use `npm run build` for type and production build validation. For visual checks, run the app and inspect `/en/discoveries`, `/es/discoveries`, `/en/learn`, and `/es/learn` across desktop and mobile viewports.
