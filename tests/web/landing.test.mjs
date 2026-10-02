import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const source = readFileSync(new URL("../../apps/landing/app.js", import.meta.url), "utf8");
const flush = async () => { for (let i = 0; i < 20; i++) await Promise.resolve(); };

function page(fetcher) {
  let now = 0;
  let nextId = 0;
  const elements = new Map();
  const timers = new Map();
  const documentEvents = new Map();
  const windowEvents = new Map();
  const calls = [];
  const document = {
    hidden: false,
    querySelector(id) {
      if (!elements.has(id)) elements.set(id, {
        textContent: "", dataset: {}, hidden: false, events: new Map(),
        addEventListener(event, handler) { this.events.set(event, handler); },
      });
      return elements.get(id);
    },
    addEventListener(event, handler) { documentEvents.set(event, handler); },
  };
  const sandbox = {
    document,
    window: { addEventListener(event, handler) { windowEvents.set(event, handler); } },
    Date: { now: () => now }, AbortController,
    setTimeout(fn, delay) { const id = ++nextId; timers.set(id, { fn, at: now + delay }); return id; },
    clearTimeout(id) { timers.delete(id); },
    fetch(url, options) { calls.push({ url, options }); return fetcher(url, options); },
  };
  vm.runInNewContext(source, sandbox);
  return {
    document, elements, calls, timers, windowEvents,
    async advance(ms) {
      const target = now + ms;
      for (;;) {
        await flush();
        const next = [...timers].sort((a, b) => a[1].at - b[1].at)[0];
        if (!next || next[1].at > target) break;
        now = next[1].at; timers.delete(next[0]); next[1].fn();
      }
      now = target;
      await flush();
    },
    visibility(hidden) { document.hidden = hidden; documentEvents.get("visibilitychange")(); },
    retry() { elements.get("#retry").events.get("click")(); },
  };
}

const healthy = url => Promise.resolve({
  ok: true, text: async () => "ok", json: async () => ({ status: "ready" }),
});

test("starts both read-only health checks together and stops once ready", async () => {
  const pending = [];
  const p = page((url, options) => new Promise(resolve => pending.push({ url, resolve })));
  assert.deepEqual(p.calls.map(c => c.url), ["/status/ui", "/status/api"]);
  assert.equal(p.elements.get("#connection").hidden, false);
  assert.equal(p.elements.get("#connection").dataset.state, "starting");
  for (const item of pending) item.resolve(await healthy(item.url));
  await flush();
  assert.equal(p.elements.get("#connection").dataset.state, "ready");
  assert.equal(p.elements.get("#ui-status").textContent, "Workspace: ready");
  await p.advance(300000);
  assert.equal(p.calls.length, 2);
  for (const { options } of p.calls) {
    assert.equal(options.method, "GET");
    assert.equal(options.credentials, "omit");
    assert.equal(options.cache, "no-store");
    assert.equal(options.headers, undefined);
  }
});

test("HTML loading pages and gateway failures never count as ready", async () => {
  let recovered = false;
  const p = page(url => recovered ? healthy(url) : Promise.resolve({
    ok: url.endsWith("ui"), text: async () => "<html>Loading</html>",
    json: async () => { throw new Error("not JSON"); },
  }));
  await flush();
  assert.equal(p.elements.get("#connection").dataset.state, "starting");
  recovered = true;
  await p.advance(5000);
  assert.equal(p.elements.get("#connection").dataset.state, "ready");
  assert.equal(p.calls.length, 4);
});

test("stops at the time limit and supports an explicit retry", async () => {
  let recovered = false;
  const p = page(url => recovered ? healthy(url) : Promise.reject(new Error("offline")));
  await p.advance(120000);
  assert.equal(p.elements.get("#connection").dataset.state, "waiting");
  assert.equal(p.elements.get("#retry").hidden, false);
  const count = p.calls.length;
  await p.advance(300000);
  assert.equal(p.calls.length, count);
  recovered = true;
  p.retry();
  await flush();
  assert.equal(p.elements.get("#connection").dataset.state, "ready");
});

test("aborts requests while hidden and resumes only inside the original time budget", async () => {
  const p = page((url, { signal }) => new Promise((resolve, reject) => {
    signal.addEventListener("abort", () => reject(new Error("aborted")));
  }));
  p.visibility(true);
  await flush();
  assert.ok(p.calls.every(c => c.options.signal.aborted));
  const count = p.calls.length;
  await p.advance(125000);
  assert.equal(p.calls.length, count);
  p.visibility(false);
  await flush();
  assert.equal(p.calls.length, count);
  assert.equal(p.elements.get("#connection").dataset.state, "waiting");
});

test("hanging requests are aborted and do not create an endless loop", async () => {
  const p = page((url, { signal }) => new Promise((resolve, reject) => {
    signal.addEventListener("abort", () => reject(new Error("timeout")));
  }));
  await p.advance(130000);
  assert.equal(p.elements.get("#connection").dataset.state, "waiting");
  assert.ok(p.calls.every(c => c.options.signal.aborted));
  assert.equal(p.timers.size, 0);
});
