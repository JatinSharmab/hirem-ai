"use client";
import { useCallback, useRef, useState } from "react";
import { errorMessage } from "@/lib/errors";

/** Mutations are deliberate and never automatically retried. */
export function useTask() {
  const lock = useRef(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const run = useCallback(async (work: () => Promise<void>) => {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError(null);
    try {
      await work();
    } catch (error) {
      setError(errorMessage(error));
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }, []);
  return { busy, error, run, clearError: () => setError(null) };
}
