// ═══════════════════════════════════════════════════════════════
// stores/appStore.ts — Global Zustand state (Phase 2 extended)
// ═══════════════════════════════════════════════════════════════
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Language, ExperimentStatus, ComplexityMode } from '@/types';

interface AppState {
  // ── Layout ──────────────────────────────────────────────────
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (value: boolean) => void;
  toggleSidebar: () => void;
  focusModeEnabled: boolean;
  setFocusModeEnabled: (value: boolean) => void;
  toggleFocusMode: () => void;

  // ── Language ────────────────────────────────────────────────
  language: Language;
  setLanguage: (lang: Language) => void;

  // ── Complexity Mode ─────────────────────────────────────────
  complexityMode: ComplexityMode;
  setComplexityMode: (mode: ComplexityMode) => void;
  toggleComplexityMode: () => void;

  // ── Cinematic Effects ──────────────────────────────────────────
  cinematicEffectsEnabled: boolean;
  setCinematicEffectsEnabled: (value: boolean) => void;
  toggleCinematicEffects: () => void;

  // ── System status ────────────────────────────────────────────
  systemStatus: 'online' | 'processing' | 'idle';
  setSystemStatus: (status: 'online' | 'processing' | 'idle') => void;

  // ── Active experiment ────────────────────────────────────────
  activeExperimentStatus: ExperimentStatus;
  setActiveExperimentStatus: (status: ExperimentStatus) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Layout
      sidebarCollapsed: false,
      setSidebarCollapsed: (value) => set({ sidebarCollapsed: value }),
      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      focusModeEnabled: false,
      setFocusModeEnabled: (value) => set({ focusModeEnabled: value }),
      toggleFocusMode: () =>
        set((state) => ({ focusModeEnabled: !state.focusModeEnabled })),

      // Language
      language: 'en',
      setLanguage: (lang) => set({ language: lang }),

      // Complexity mode
      complexityMode: 'simple',
      setComplexityMode: (mode) => set({ complexityMode: mode }),
      toggleComplexityMode: () =>
        set((state) => ({
          complexityMode: state.complexityMode === 'simple' ? 'advanced' : 'simple',
        })),

      // Cinematic Effects (Disabled by default for CPU/GPU efficiency in dev)
      cinematicEffectsEnabled: false,
      setCinematicEffectsEnabled: (value) => set({ cinematicEffectsEnabled: value }),
      toggleCinematicEffects: () =>
        set((state) => ({ cinematicEffectsEnabled: !state.cinematicEffectsEnabled })),

      // System status
      systemStatus: 'online',
      setSystemStatus: (status) => set({ systemStatus: status }),

      // Experiment
      activeExperimentStatus: 'idle',
      setActiveExperimentStatus: (status) =>
        set({ activeExperimentStatus: status }),
    }),
    {
      name: 'neurosymbolic-app-store',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        focusModeEnabled: state.focusModeEnabled,
        language: state.language,
        complexityMode: state.complexityMode,
        cinematicEffectsEnabled: state.cinematicEffectsEnabled,
      }),
    }
  )
);
