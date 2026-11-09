import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { spawn, spawnSync } from "child_process";
import { readFileSync, writeFileSync, existsSync } from "fs";
import { createServer as createViteServer } from "vite";
import dotenv from "dotenv";

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = parseInt(process.env.PORT || "4002");
const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY;

app.use(express.json({ limit: "5mb" }));

// ── Python runner ────────────────────────────────────────────────────────────
function findPython(): string {
  // Try real Python installs before Windows Store stubs
  const candidates = [
    path.join(process.env.LOCALAPPDATA || "", "Programs/Python/Python313/python.exe"),
    path.join(process.env.LOCALAPPDATA || "", "Programs/Python/Python312/python.exe"),
    "python3",
    "python",
  ];
  for (const c of candidates) {
    try {
      const result = spawnSync(c, ["--version"], { timeout: 3000 });
      if (result.status === 0) return c;
    } catch {}
  }
  return "python"; // fallback
}

const PYTHON_EXE = findPython();

function runPython(args: string[]): Promise<string> {
  return new Promise((resolve, reject) => {
    const pythonDir = path.join(process.cwd(), "python");
    const py = spawn(PYTHON_EXE, args, { cwd: pythonDir });
    let out = "";
    let err = "";
    py.stdout.on("data", (d: Buffer) => { out += d.toString(); });
    py.stderr.on("data", (d: Buffer) => { err += d.toString(); });
    py.on("close", (code) => {
      if (code === 0) resolve(out.trim());
      else reject(new Error(err || `Python exited ${code}`));
    });
  });
}

// ── DeepSeek — factual analysis note only ────────────────────────────────────
async function getAnalysis(numbers: number[], reversal: number[], drawTime: string): Promise<string> {
  if (!DEEPSEEK_API_KEY) return "";
  try {
    const res = await fetch("https://api.deepseek.com/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${DEEPSEEK_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "deepseek-chat",
        messages: [
          {
            role: "system",
            content: "You are a statistical analyst reviewing lottery draw data. State what the data shows in 2 sentences. No mystical language, no hype. Plain factual English only.",
          },
          {
            role: "user",
            content: `Draw slot: ${drawTime}. Engine top picks: ${numbers.join(", ")}. Reversal (lowest confidence): ${reversal.join(", ")}. Summarise what pattern this reflects.`,
          },
        ],
        max_tokens: 120,
      }),
    });
    if (!res.ok) return "";
    const data = await res.json() as any;
    return data.choices?.[0]?.message?.content?.trim() ?? "";
  } catch {
    return "";
  }
}

// ── GET /api/recent-draws — serve last 120 draws from the data file ──────────
app.get("/api/recent-draws", (req, res) => {
  try {
    const dataPath = path.join(process.cwd(), "python", "cash_pot_results.json");
    const raw = readFileSync(dataPath, "utf-8");
    const all: any[] = JSON.parse(raw);
    // Normalise field names to match frontend Draw interface
    const draws = all.slice(0, 120).map((d: any) => ({
      id: String(d.draw_number ?? d.id ?? Math.random()),
      index: d.draw_number ?? d.index ?? 0,
      drawTime: d.draw_name ?? d.drawTime ?? "Unknown",
      winningNumber: d.number ?? d.winningNumber ?? 0,
      date: d.date_display ?? d.date ?? "",
    }));
    res.json(draws);
  } catch (e: any) {
    res.status(500).json({ error: "Could not load draw data." });
  }
});

// ── GET /api/health ──────────────────────────────────────────────────────────
app.get("/api/health", (req, res) => {
  try {
    const dataPath = path.join(process.cwd(), "python", "cash_pot_results.json");
    const raw = readFileSync(dataPath, "utf-8");
    const all: any[] = JSON.parse(raw);
    const first = all[all.length - 1]; // oldest (sorted newest-first)
    const last = all[0]; // newest
    res.json({
      status: "ok", uptime: process.uptime(), ai: !!DEEPSEEK_API_KEY,
      dataRange: { first: first?.date ?? "?", last: last?.date ?? "?", total: all.length },
    });
  } catch {
    res.json({ status: "ok", uptime: process.uptime(), ai: !!DEEPSEEK_API_KEY, dataRange: null });
  }
});

// ── POST /api/predict ─────────────────────────────────────────────────────────
// Body: { drawTime: string, strategy: "math"|"dream"|"hybrid", dreamText?: string }
app.post("/api/predict", async (req, res) => {
  try {
    const { drawTime = "Morning", strategy = "hybrid", dreamText = "" } = req.body;

    // Map strategy to day-of-week approach (python engine uses DOW bias)
    const now = new Date();
    const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
    const dow = days[now.getDay()];

    // Build python args with strategy + dream text
    const pyArgs = ["predictor.py", "json", "36", `--dow=${dow}`, `--strategy=${strategy}`];
    if (dreamText.trim()) pyArgs.push(`--dream=${dreamText.trim()}`);

    // Run full 36-number ranking
    const raw = await runPython(pyArgs);
    const parsed = JSON.parse(raw) as { predictions: Array<{ number: number; name: string; score: number; symbol?: string; reasons?: string[] }> };

    const ranked = parsed.predictions;
    const top = ranked.slice(0, 3);
    const bottom = ranked.slice(-3).reverse();

    const numbers = top.map(p => p.number);
    const names = top.map(p => p.name);
    const reversal = bottom.map(p => p.number);
    const reversalNames = bottom.map(p => p.name);

    const analysis = await getAnalysis(numbers, reversal, drawTime);

    res.json({
      numbers, names, reversal, reversalNames, analysis, drawTime,
      fullRanking: ranked.slice(0, 36),
      strategyMode: (parsed as any).strategyMode || "hybrid",
    });
  } catch (err: any) {
    console.error("[predict]", err.message);
    // Fallback — return static numbers so UI never breaks
    res.json({
      numbers: [7, 14, 25],
      names: ["Small Bird", "Hot Match", "Money"],
      reversal: [3, 18, 33],
      reversalNames: ["Dead", "Crow", "Big House"],
      analysis: "Python engine unavailable — showing static fallback.",
      drawTime: req.body.drawTime ?? "Morning",
      fallback: true,
    });
  }
});

// ── GET /api/strategies — per-strategy raw output for Chart dashboard ────────
app.get("/api/strategies", async (req, res) => {
  try {
    const now = new Date();
    const days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
    const dow = days[now.getDay()];
    const raw = await runPython(["predictor.py", "strategies", `--dow=${dow}`]);
    res.json(JSON.parse(raw));
  } catch (e: any) {
    console.error("[strategies]", e.message);
    res.json({ targetDow: "Unknown", strategies: [] });
  }
});

// ── GET /api/forecast?days=2 — N-step ahead predictions ──────────────────────
app.get("/api/forecast", async (req, res) => {
  try {
    const days = parseInt(req.query.days as string) || 2;
    const steps = days * 6;
    const now = new Date();
    const dows = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
    const dow = dows[now.getDay()];
    const raw = await runPython(["predictor.py", "forecast", String(steps), `--dow=${dow}`]);
    res.json(JSON.parse(raw));
  } catch (e: any) {
    console.error("[forecast]", e.message);
    res.json({ forecast: [] });
  }
});

// ── GET /api/accuracy — hit rate breakdown ──────────────────────────────────
app.get("/api/accuracy", async (req, res) => {
  try {
    const raw = await runPython(["predictor.py", "accuracy"]);
    res.json(JSON.parse(raw));
  } catch (e: any) {
    console.error("[accuracy]", e.message);
    res.json({ total_predictions: 0, total_hits: 0, hit_rate: 0 });
  }
});

// ── GET /api/moon — current moon phase + planetary data ─────────────────────
app.get("/api/moon", async (req, res) => {
  try {
    const raw = await runPython(["predictor.py", "moon"]);
    res.json(JSON.parse(raw));
  } catch (e: any) {
    console.error("[moon]", e.message);
    res.json({ moonPhase: "Unknown", planetaryRuler: "Unknown" });
  }
});

// ── GET /api/dev-status — background tasks heartbeat for UI footer ──────────
app.get("/api/dev-status", (req, res) => {
  try {
    const statusPath = "D:/cashpot_verification_logs/RUNNING_STATUS.json";
    if (existsSync(statusPath)) {
      const raw = readFileSync(statusPath, "utf-8");
      res.json(JSON.parse(raw));
    } else {
      // Also check for Python process marker
      const markerPath = path.join(process.cwd(), "python", ".running");
      res.json({
        running: existsSync(markerPath),
        task: existsSync(markerPath) ? "unknown (legacy marker)" : null,
        progress: null,
        updated: null,
      });
    }
  } catch {
    res.json({ running: false, task: null, progress: null });
  }
});

// ── POST /api/log-hit — record a correct prediction ─────────────────────────
app.post("/api/log-hit", async (req, res) => {
  try {
    const { draw, number, predicted } = req.body;
    const logPath = path.join(process.cwd(), "python", "predictions_log.json");
    let log = { predictions: [] };
    try {
      const existing = JSON.parse(readFileSync(logPath, "utf-8"));
      if (existing.predictions) log = existing;
    } catch {}
    log.predictions.push({
      timestamp: new Date().toISOString(),
      draw: draw || "Unknown",
      predicted: predicted || [],
      actual: number,
      hit: predicted ? predicted.includes(number) : false,
      strategies_that_hit: [],
    });
    writeFileSync(logPath, JSON.stringify(log, null, 2), "utf-8");
    res.json({ success: true });
  } catch (e: any) {
    console.error("[log-hit]", e.message);
    res.status(500).json({ success: false, error: e.message });
  }
});

// ── Start ────────────────────────────────────────────────────────────────────
async function start() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({ server: { middlewareMode: true }, appType: "spa" });
    app.use(vite.middlewares);
  } else {
    const dist = path.join(__dirname, "dist");
    app.use(express.static(dist));
    app.get("*", (req, res) => res.sendFile(path.join(dist, "index.html")));
  }
  app.listen(PORT, "0.0.0.0", () => {
    console.log(`[cashpot-engine] http://0.0.0.0:${PORT}`);
    console.log(`[cashpot-engine] AI analysis: ${DEEPSEEK_API_KEY ? "on" : "off"}`);
  });
}

start();
