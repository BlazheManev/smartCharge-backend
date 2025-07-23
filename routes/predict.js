// routes/predict.js
import express from "express";
import { spawn } from "child_process";

const router = express.Router();

// 🚀 GET /api/predict?stationId=abc&windowSize=24
router.get("/", async (req, res) => {
  const { stationId, windowSize } = req.query;

  if (!stationId || !windowSize) {
    return res.status(400).json({ error: "Missing stationId or windowSize." });
  }

  const pythonCmd = process.platform === "win32" ? "python" : "python3";
  const py = spawn(pythonCmd, ["python/prepare_input.py", stationId, String(windowSize)]);

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
      res.json({ input: result.trim() });
    } else {
      console.error("❌ Python stderr:", errorOutput);
      res.status(500).json({ error: "Failed to prepare input data." });
    }
  });

  py.on("error", (err) => {
    console.error("❌ Failed to spawn Python:", err);
    res.status(500).json({ error: "Python execution error." });
  });
});

export default router;
