/* Read-only, visit-triggered startup checks. No account, API key or AI calls. */
(() => {
  "use strict";
  const card = document.querySelector("#connection");
  const title = document.querySelector("#connection-title");
  const copy = document.querySelector("#connection-copy");
  const announcement = document.querySelector("#announcement");
  const retry = document.querySelector("#retry");
  card.hidden = false;
  const services = [
    { id: "ui", label: "Workspace", url: "/status/ui", ready: false },
    { id: "api", label: "Career tools", url: "/status/api", ready: false },
  ];
  const maxWait = 120000;
  let deadline = 0;
  let timer;
  let running = false;
  let finished = false;
  const controllers = new Set();

  function message(heading, description, state) {
    title.textContent = heading;
    copy.textContent = description;
    card.dataset.state = state;
    announcement.textContent = `${heading}. ${description}`;
  }

  async function check(service) {
    if (service.ready) return;
    const controller = new AbortController();
    controllers.add(controller);
    const timeout = setTimeout(
      () => controller.abort(), Math.min(12000, Math.max(1, deadline - Date.now())),
    );
    try {
      const response = await fetch(service.url, {
        method: "GET", cache: "no-store", credentials: "omit", signal: controller.signal,
      });
      if (!response.ok) return;
      // HTML gateway/loading pages must never be mistaken for a ready service.
      if (service.id === "ui") {
        service.ready = (await response.text()).trim().toLowerCase() === "ok";
      } else {
        service.ready = (await response.json()).status === "ready";
      }
      if (service.ready) document.querySelector(`#${service.id}-status`).textContent = `${service.label}: ready`;
    } catch (_) {
      // Transient gateway errors are expected while a free instance starts.
    } finally {
      clearTimeout(timeout);
      controllers.delete(controller);
    }
  }

  function finishIfExpired() {
    if (Date.now() < deadline) return false;
    finished = true;
    message("The workspace is taking longer to start", "You can open the app directly or check again in a moment. This page stays available.", "waiting");
    retry.hidden = false;
    return true;
  }

  async function tick() {
    if (running || finished || document.hidden || finishIfExpired()) return;
    running = true;
    // Wake both services together instead of waiting for the UI to wake the API.
    await Promise.all(services.map(check));
    running = false;
    if (document.hidden) return;
    if (services.every(service => service.ready)) {
      finished = true;
      message("Your workspace is ready", "Open HireMe AI whenever you’re ready. Start with your resume and review your evidence.", "ready");
    } else if (!finishIfExpired()) {
      timer = setTimeout(tick, 5000);
    }
  }

  function start() {
    clearTimeout(timer);
    finished = false;
    retry.hidden = true;
    deadline = Date.now() + maxWait;
    services.forEach(service => {
      service.ready = false;
      document.querySelector(`#${service.id}-status`).textContent = `${service.label}: connecting`;
    });
    message("Preparing your workspace", "The app is starting in the background. Take a look around while it connects.", "starting");
    void tick();
  }

  function pause() {
    clearTimeout(timer);
    controllers.forEach(controller => controller.abort());
  }

  retry.addEventListener("click", start);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) pause();
    else if (!finished) void tick();
  });
  window.addEventListener("pagehide", pause);
  window.addEventListener("pageshow", event => { if (event.persisted) start(); });
  start();
})();
