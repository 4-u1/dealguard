// Relay for Docker containers that have no egress: forwards http://<bind>:<port>/* to https://openrouter.ai/*
// through the session HTTPS proxy (run with NODE_USE_ENV_PROXY=1). The proxy injects the real API key,
// so callers send a placeholder Authorization header. Streams responses (SSE) through unchanged.
import http from "node:http";
import { Readable } from "node:stream";

const BIND = process.env.RELAY_BIND || "172.17.0.1";
const PORT = Number(process.env.RELAY_PORT || 8788);
const UPSTREAM = "https://openrouter.ai";
const HOP = new Set(["host", "connection", "content-length", "transfer-encoding", "keep-alive", "accept-encoding"]);

http.createServer(async (req, res) => {
  try {
    const headers = {};
    for (const [k, v] of Object.entries(req.headers)) if (!HOP.has(k)) headers[k] = v;
    const body = ["GET", "HEAD"].includes(req.method) ? undefined : Readable.toWeb(req);
    const up = await fetch(UPSTREAM + req.url, { method: req.method, headers, body, duplex: "half" });
    const out = {};
    up.headers.forEach((v, k) => { if (!HOP.has(k) && k !== "content-encoding") out[k] = v; });
    res.writeHead(up.status, out);
    if (up.body) Readable.fromWeb(up.body).pipe(res); else res.end();
  } catch (e) {
    res.writeHead(502, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: { message: "relay: " + (e.cause?.code || e.message) } }));
  }
}).listen(PORT, BIND, () => console.log(`llm-relay on http://${BIND}:${PORT} -> ${UPSTREAM}`));
