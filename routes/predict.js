import express from "express";
import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const router = express.Router();
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const scriptPath = path.join(__dirname, "../python/prepare_input.py");

router.get("/predict", async (req, res) => {
  const { stationId, windowSize, datetime } = req.query;

  if (!stationId || !windowSize || !datetime) {
    return res.status(400).json({ error: "Missing stationId, windowSize, or datetime." });
  }

  const pythonCmd = process.platform === "win32" ? "python" : "python3";
  const py = spawn(pythonCmd, [scriptPath, stationId, String(windowSize), datetime]);

  let result = "";
  let errorOutput = "";

  py.stdout.on("data", (data) => {
    result += data.toString();
  });

  py.stderr.on("data", (data) => {
    errorOutput += data.toString();
  });

  py.on("close", (code) => {
    if (code === 0) {
      try {
        const parsed = JSON.parse(result);
        res.json({ input: parsed.predicted });
      } catch (err) {
        console.error("❌ JSON parse failed:", err);
        res.status(500).json({ error: "Invalid output from Python." });
      }
    } else {
      console.error("❌ Python exited with code:", code);
      console.error("❌ Python stderr:", errorOutput || "(empty)");
      res.status(500).json({ error: errorOutput || "Python script failed." });
    }
  });

  py.on("error", (err) => {
    console.error("❌ Failed to spawn Python:", err);
    res.status(500).json({ error: "Python execution error." });
  });
});

export default router;
