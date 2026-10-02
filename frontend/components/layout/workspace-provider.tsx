"use client";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { api } from "@/lib/api/browser-client";
import { errorMessage } from "@/lib/errors";
import type {
  BackendState,
  Candidate,
  Job,
  Match,
  Requirements,
  RuntimeSettings,
  SavedVersion,
} from "@/types";

type Workspace = {
  status: BackendState;
  statusError: string | null;
  retry: () => void;
  expiresAt: string | null;
  settings: RuntimeSettings | null;
  candidate: Candidate | null;
  setCandidate: (value: Candidate | null) => void;
  jobs: Job[];
  setJobs: (value: Job[]) => void;
  refreshJobs: () => Promise<void>;
  selectedJob: string;
  selectJob: (id: string) => void;
  requirements: Record<string, Requirements>;
  rememberRequirements: (id: string, value: Requirements) => void;
  match: Match | null;
  setMatch: (value: Match | null) => void;
  versions: SavedVersion[];
  addVersion: (value: SavedVersion) => void;
  bookmarks: string[];
  toggleBookmark: (id: string) => void;
  applicationsRevision: number;
  applicationsChanged: () => void;
  reset: () => void;
};
const Context = createContext<Workspace | null>(null);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<BackendState>("checking");
  const [statusError, setStatusError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [expiresAt, setExpiresAt] = useState<string | null>(null);
  const [settings, setSettings] = useState<RuntimeSettings | null>(null);
  const [candidate, updateCandidate] = useState<Candidate | null>(null);
  const [jobs, updateJobs] = useState<Job[]>([]);
  const [selectedJob, updateSelectedJob] = useState("");
  const [requirements, setRequirements] = useState<
    Record<string, Requirements>
  >({});
  const [match, setMatch] = useState<Match | null>(null);
  const [versions, setVersions] = useState<SavedVersion[]>([]);
  const [bookmarks, setBookmarks] = useState<string[]>([]);
  const [applicationsRevision, setApplicationsRevision] = useState(0);
  const epoch = useRef(0);
  const [generation, setGeneration] = useState(0);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const reset = useCallback(() => {
    epoch.current += 1;
    setGeneration(epoch.current);
    updateCandidate(null);
    updateJobs([]);
    updateSelectedJob("");
    setRequirements({});
    setMatch(null);
    setVersions([]);
    setBookmarks([]);
    setApplicationsRevision((value) => value + 1);
  }, []);
  const setJobs = useCallback(
    (value: Job[]) => {
      if (generation === epoch.current) updateJobs(value);
    },
    [generation],
  );
  const refreshJobs = useCallback(async () => {
    setJobs(await api<Job[]>("jobs"));
  }, [setJobs]);
  useEffect(() => {
    const controller = new AbortController();
    let stopped = false;
    const signal = AbortSignal.any([
      controller.signal,
      AbortSignal.timeout(120000),
    ]);
    // At most eight checks or two minutes, whichever comes first.
    async function start() {
      setStatus("checking");
      setStatusError(null);
      try {
        const session = await api<{ expiresAt: string }>("workspace", {
          method: "POST",
          signal,
        });
        if (stopped) return;
        setExpiresAt(session.expiresAt);
      } catch (error) {
        if (!stopped) {
          setStatus("error");
          setStatusError(errorMessage(error));
        }
        return;
      }
      for (let index = 0; index < 8 && !stopped; index++) {
        try {
          await api("health", { signal });
          const config = await api<RuntimeSettings>("settings", { signal });
          if (stopped) return;
          setSettings(config);
          setStatus("ready");
          return;
        } catch (error) {
          if (stopped) return;
          if (index === 7 || signal.aborted) {
            setStatus("error");
            setStatusError(
              signal.aborted
                ? "The backend did not become ready within two minutes. You can retry when you are ready."
                : errorMessage(error),
            );
            return;
          }
          setStatus("waking");
          await new Promise<void>((resolve) => {
            timer.current = setTimeout(
              resolve,
              Math.min(2000 * (index + 1), 8000),
            );
            signal.addEventListener("abort", () => resolve(), { once: true });
          });
        }
      }
    }
    void start();
    return () => {
      stopped = true;
      controller.abort();
      clearTimeout(timer.current);
    };
  }, [attempt]);
  useEffect(() => {
    if (!expiresAt) return;
    const expiryTimer = setTimeout(
      () => {
        reset();
        setStatus("error");
        setStatusError(
          "Your temporary session expired. Start a new session to continue.",
        );
      },
      Math.max(0, Date.parse(expiresAt) - Date.now()),
    );
    return () => clearTimeout(expiryTimer);
  }, [expiresAt, reset]);
  return (
    <Context.Provider
      value={{
        status,
        statusError,
        retry: () => setAttempt((value) => value + 1),
        expiresAt,
        settings,
        candidate,
        setCandidate: (value) => {
          if (generation !== epoch.current) return;
          updateCandidate(value);
          setMatch(null);
        },
        jobs,
        setJobs,
        refreshJobs,
        selectedJob,
        selectJob: (id) => {
          updateSelectedJob(id);
          setMatch(null);
        },
        requirements,
        rememberRequirements: (id, value) => {
          if (generation === epoch.current)
            setRequirements((previous) => ({ ...previous, [id]: value }));
        },
        match,
        setMatch: (value) => {
          if (generation === epoch.current) setMatch(value);
        },
        versions,
        addVersion: (value) => {
          if (generation === epoch.current)
            setVersions((previous) => [value, ...previous]);
        },
        bookmarks,
        applicationsRevision,
        applicationsChanged: () => {
          if (generation === epoch.current)
            setApplicationsRevision((value) => value + 1);
        },
        toggleBookmark: (id) =>
          setBookmarks((previous) =>
            previous.includes(id)
              ? previous.filter((value) => value !== id)
              : [...previous, id],
          ),
        reset,
      }}
    >
      {children}
    </Context.Provider>
  );
}
export function useWorkspace() {
  const value = useContext(Context);
  if (!value) throw new Error("Workspace provider is missing");
  return value;
}
