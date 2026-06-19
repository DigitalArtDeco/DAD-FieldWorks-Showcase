(function () {
  "use strict";

  function normalizeFramePath(manifestUrl, framePath) {
    if (/^(?:https?:)?\/\//i.test(framePath) || framePath.startsWith("/")) {
      return framePath;
    }

    const base = new URL(manifestUrl, window.location.href);
    return new URL(framePath, window.location.origin + window.location.pathname.replace(/[^/]*$/, "")).href || new URL(framePath, base).href;
  }

  function createPlayer(figure) {
    const image = figure.querySelector("img");
    const manifestPath = figure.getAttribute("data-frame-manifest");

    if (!image || !manifestPath) {
      return;
    }

    fetch(manifestPath)
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Frame manifest unavailable");
        }
        return response.json();
      })
      .then(function (manifest) {
        const frames = Array.isArray(manifest.Frames) ? manifest.Frames : [];
        if (frames.length < 2) {
          return;
        }

        const urls = frames
          .map(function (frame) {
            return normalizeFramePath(manifestPath, frame.ImagePath || "");
          })
          .filter(Boolean);

        if (urls.length < 2) {
          return;
        }

        const interval = Number(manifest.FrameIntervalMs) > 0 ? Number(manifest.FrameIntervalMs) : 80;
        let frameIndex = 0;
        let lastTime = 0;
        let active = true;

        urls.forEach(function (url) {
          const preload = new Image();
          preload.decoding = "async";
          preload.src = url;
        });

        function step(timestamp) {
          if (!active) {
            window.requestAnimationFrame(step);
            return;
          }

          if (!lastTime || timestamp - lastTime >= interval) {
            frameIndex = (frameIndex + 1) % urls.length;
            image.src = urls[frameIndex];
            lastTime = timestamp;
          }

          window.requestAnimationFrame(step);
        }

        document.addEventListener("visibilitychange", function () {
          active = !document.hidden;
        });

        window.requestAnimationFrame(step);
      })
      .catch(function () {
        figure.classList.add("frame-player-fallback");
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-frame-manifest]").forEach(createPlayer);
  });
})();
