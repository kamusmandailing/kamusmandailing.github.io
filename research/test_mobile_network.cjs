#!/usr/bin/env node
"use strict";

// Synthetic mobile performance smoke for the lightweight online page.
// This is a browser/network emulation, not a physical-phone measurement.
const fs = require("node:fs");
const http = require("node:http");
const os = require("node:os");
const path = require("node:path");
const zlib = require("node:zlib");
const { spawn } = require("node:child_process");

const ROOT = path.resolve(__dirname, "..");
const OUTPUT = path.join(ROOT, "qa", "phase10-mobile-simulation.json");
const PROFILE = { viewport: "390x844", latencyMs: 150, downloadKbps: 400, uploadKbps: 400, cpuSlowdown: 4 };
const buildManifest = JSON.parse(fs.readFileSync(path.join(ROOT, "data/bank-online-shards/manifest.json"), "utf8"));
const firstViewByteBudget = buildManifest.chunkSize <= 512 ? 55_000 : 90_000;
const firstViewTimeBudget = buildManifest.chunkSize <= 512 ? 8_000 : 10_000;
const browserCandidates = [
  process.env.CHROME_BIN,
  ...["google-chrome", "chromium", "chromium-browser"].map(name => {
    const { execFileSync } = require("node:child_process");
    try { return execFileSync("which", [name], { encoding: "utf8" }).trim(); } catch { return null; }
  }),
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
].filter(Boolean);
const browser = browserCandidates.find(candidate => fs.existsSync(candidate));
if (!browser) throw new Error("Chrome/Chromium is required for the synthetic mobile test.");

const requests = [];
const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
};
const server = http.createServer((request, response) => {
  const pathname = decodeURIComponent(new URL(request.url, "http://localhost").pathname);
  const file = path.resolve(ROOT, `.${pathname}`);
  if (file !== ROOT && !file.startsWith(ROOT + path.sep)) {
    response.writeHead(403).end("Forbidden");
    return;
  }
  requests.push(pathname);
  let body;
  try { body = fs.readFileSync(file); }
  catch { response.writeHead(404).end("Not found"); return; }
  const compressible = /\.(html|json|js|css|svg)$/.test(file);
  const useGzip = compressible && /\bgzip\b/.test(request.headers["accept-encoding"] || "");
  if (useGzip) body = zlib.gzipSync(body, { level: 9, mtime: 0 });
  const headers = {
    "Content-Type": contentTypes[path.extname(file)] || "application/octet-stream",
    "Content-Length": body.length,
    "Cache-Control": "no-store",
    "Timing-Allow-Origin": "*",
  };
  if (useGzip) headers["Content-Encoding"] = "gzip";
  response.writeHead(200, headers).end(body);
});

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function waitFor(predicate, description, timeoutMs = 20_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const result = await predicate();
    if (result) return result;
    await sleep(100);
  }
  throw new Error(`Timed out waiting for ${description}.`);
}

async function main() {
  await new Promise((resolve, reject) => server.listen(0, "127.0.0.1", resolve).once("error", reject));
  const base = `http://127.0.0.1:${server.address().port}`;
  const profileDir = fs.mkdtempSync(path.join(os.tmpdir(), "km-mobile-cdp-"));
  const chrome = spawn(browser, [
    "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
    "--remote-debugging-port=0", "--remote-allow-origins=*", `--user-data-dir=${profileDir}`, "about:blank",
  ], { stdio: "ignore" });
  let socket;
  try {
    const activeFile = path.join(profileDir, "DevToolsActivePort");
    const active = await waitFor(() => {
      if (chrome.exitCode !== null) throw new Error(`Chrome exited with ${chrome.exitCode}.`);
      try { return fs.readFileSync(activeFile, "utf8").trim().split("\n"); } catch { return null; }
    }, "Chrome DevTools endpoint");
    const debugPort = Number(active[0]);
    const targets = await (await fetch(`http://127.0.0.1:${debugPort}/json/list`)).json();
    const target = targets.find(item => item.type === "page");
    if (!target) throw new Error("Chrome did not create a page target.");

    socket = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((resolve, reject) => {
      socket.addEventListener("open", resolve, { once: true });
      socket.addEventListener("error", reject, { once: true });
    });
    let nextId = 0;
    const pending = new Map();
    socket.addEventListener("message", event => {
      const message = JSON.parse(event.data);
      if (!message.id || !pending.has(message.id)) return;
      const { resolve, reject, timer } = pending.get(message.id);
      clearTimeout(timer);
      pending.delete(message.id);
      if (message.error) reject(new Error(message.error.message));
      else resolve(message.result || {});
    });
    const command = (method, params = {}, timeoutMs = 90_000) => new Promise((resolve, reject) => {
      const id = ++nextId;
      const timer = setTimeout(() => { pending.delete(id); reject(new Error(`CDP timed out: ${method}`)); }, timeoutMs);
      pending.set(id, { resolve, reject, timer });
      socket.send(JSON.stringify({ id, method, params }));
    });
    const evaluate = async (expression, awaitPromise = false) => {
      const result = await command("Runtime.evaluate", { expression, awaitPromise, returnByValue: true }, 90_000);
      if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || "Browser evaluation failed.");
      return result.result?.value;
    };

    await command("Page.enable");
    await command("Runtime.enable");
    await command("Network.enable");
    await command("Network.setCacheDisabled", { cacheDisabled: true });
    await command("Network.emulateNetworkConditions", {
      offline: false,
      latency: PROFILE.latencyMs,
      downloadThroughput: PROFILE.downloadKbps * 1000 / 8,
      uploadThroughput: PROFILE.uploadKbps * 1000 / 8,
      connectionType: "cellular3g",
    });
    await command("Emulation.setDeviceMetricsOverride", {
      width: 390, height: 844, deviceScaleFactor: 1, mobile: true,
    });
    await command("Emulation.setCPUThrottlingRate", { rate: PROFILE.cpuSlowdown });
    await command("Page.navigate", { url: `${base}/online.html` });

    const initial = await waitFor(async () => {
      const value = await evaluate(`(() => ({
        ready: document.readyState === "complete" && !!window.HataOnlineAudit,
        count: document.querySelector("#curated-count")?.textContent || "",
        viewport: [innerWidth, innerHeight].join("x"),
        resources: performance.getEntriesByType("resource").map(entry => entry.name)
      }))()`);
      return value.ready ? value : null;
    }, "light page initialization", 40_000);
    const initialBankRequests = initial.resources.filter(name => name.includes("/data/bank-online-shards/"));
    if (!initial.count.includes("1.404") || initial.viewport !== PROFILE.viewport || initialBankRequests.length) {
      throw new Error(`Unexpected initial mobile page state: ${JSON.stringify(initial)}`);
    }
    const navigationTiming = await evaluate(`(() => {
      const nav = performance.getEntriesByType("navigation")[0];
      const paints = performance.getEntriesByType("paint");
      return { responseEndMs: nav?.responseEnd || null,
        domContentLoadedMs: nav?.domContentLoadedEventEnd || null,
        loadEventMs: nav?.loadEventEnd || null,
        firstContentfulPaintMs: paints.find(item => item.name === "first-contentful-paint")?.startTime || null };
    })()`);

    const firstBank = await evaluate(`(async () => {
      const start = performance.now();
      document.querySelector("#show-bank").click();
      const deadline = Date.now() + 40000;
      while (Date.now() < deadline && !window.HataOnlineAudit.bankLoaded())
        await new Promise(resolve => setTimeout(resolve, 50));
      if (!window.HataOnlineAudit.bankLoaded()) throw new Error("First Bank chunk did not load.");
      const assets = performance.getEntriesByType("resource")
        .filter(entry => entry.name.includes("/data/bank-online-shards/"))
        .map(entry => ({ file: new URL(entry.name).pathname.split("/").pop(), bytes: entry.encodedBodySize }));
      return { elapsedMs: performance.now() - start, loadedChunks: window.HataOnlineAudit.loadedChunkCount(), assets };
    })()`, true);
    const firstBankBytes = firstBank.assets.reduce((sum, asset) => sum + asset.bytes, 0);
    const expectedFirstFiles = new Set(firstBank.assets.map(asset => asset.file));
    if (firstBank.loadedChunks !== 1 || firstBank.assets.length !== 2 ||
        !expectedFirstFiles.has("manifest.json") || !expectedFirstFiles.has("chunk-000.json") ||
        firstBankBytes <= 0 || firstBankBytes >= firstViewByteBudget || firstBank.elapsedMs > firstViewTimeBudget) {
      throw new Error(`Unexpected first-page mobile result: ${JSON.stringify(firstBank)}`);
    }

    const fullSearch = await evaluate(`(async () => {
      const input = document.querySelector("#bank-search");
      const start = performance.now();
      input.value = "fish";
      input.dispatchEvent(new Event("input", { bubbles: true }));
      const deadline = Date.now() + 90000;
      while (Date.now() < deadline && !window.HataOnlineAudit.bankComplete())
        await new Promise(resolve => setTimeout(resolve, 50));
      if (!window.HataOnlineAudit.bankComplete()) throw new Error("Complete search did not load all Bank chunks.");
      return { elapsedMs: performance.now() - start,
        chunks: window.HataOnlineAudit.loadedChunkCount(),
        forms: document.querySelectorAll("#bank-results article").length,
        countText: document.querySelector("#bank-count").textContent };
    })()`, true);
    if (fullSearch.chunks !== buildManifest.chunks.length || !fullSearch.countText.includes("bentuk cocok dari 10.821")) {
      throw new Error(`Search did not return a complete mobile result: ${JSON.stringify(fullSearch)}`);
    }

    const fullBankAssets = await evaluate(`performance.getEntriesByType("resource")
      .filter(entry => entry.name.includes("/data/bank-online-shards/"))
      .reduce((sum, entry) => sum + entry.encodedBodySize, 0)`);
    const result = {
      schemaVersion: 1,
      testType: "Synthetic mobile browser/network simulation; not physical device measurement",
      profile: PROFILE,
      metrics: { ...navigationTiming, bankChunkSize: buildManifest.chunkSize,
        bankChunkCount: buildManifest.chunks.length, bankFirstViewEncodedBytes: firstBankBytes,
        bankFirstViewElapsedMs: Math.round(firstBank.elapsedMs), fullBankSearchElapsedMs: Math.round(fullSearch.elapsedMs),
        fullBankEncodedBytes: fullBankAssets,
        shardCount: fullSearch.chunks, bankSearchCount: fullSearch.countText },
      checks: { curatedEntriesRendered: initial.count.includes("1.404"),
        noBankDataBeforeRequest: initialBankRequests.length === 0,
        firstViewFetchedOnlyManifestAndFirstChunk: true, searchLoadedAllFormsBeforeResults: true },
      caveat: "Chrome emulation on a desktop host estimates one constrained mobile profile. Confirm Core Web Vitals, memory, and accessibility on physical phones before release.",
    };
    fs.mkdirSync(path.dirname(OUTPUT), { recursive: true });
    fs.writeFileSync(OUTPUT, JSON.stringify(result, null, 2) + "\n");
    process.stdout.write(JSON.stringify(result, null, 2) + "\n");
  } finally {
    if (socket) socket.close();
    if (chrome.exitCode === null && chrome.signalCode === null) {
      const exited = new Promise(resolve => chrome.once("exit", resolve));
      chrome.kill("SIGTERM");
      const stopped = await Promise.race([exited.then(() => true), sleep(3_000).then(() => false)]);
      if (!stopped) {
        chrome.kill("SIGKILL");
        await Promise.race([exited, sleep(1_000)]);
      }
    }
    await new Promise(resolve => server.close(resolve));
    fs.rmSync(profileDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
  }
}

main().catch(error => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exitCode = 1;
});
