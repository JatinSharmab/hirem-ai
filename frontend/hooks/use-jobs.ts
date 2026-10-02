"use client";
import { useCallback, useEffect, useState } from "react";
import { useWorkspace } from "@/components/layout/workspace-provider";
import { api } from "@/lib/api/browser-client";
import { errorMessage } from "@/lib/errors";
import type { Job } from "@/types";
export function useJobs() {
  const { status, jobs, setJobs } = useWorkspace();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    if (status !== "ready") return;
    const controller = new AbortController();
    api<Job[]>("jobs", { signal: controller.signal })
      .then(setJobs)
      .catch((error) => {
        if (!controller.signal.aborted) setError(errorMessage(error));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [status, revision, setJobs]);
  return {
    jobs,
    loading,
    error,
    reload: useCallback(() => {
      setLoading(true);
      setError(null);
      setRevision((value) => value + 1);
    }, []),
  };
}
