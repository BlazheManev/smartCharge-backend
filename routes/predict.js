import path from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const scriptPath = path.join(__dirname, "../python/prepare_input.py");

router.get("/predict", async (req, res) => {
  const { stationId, windowSize } = req.query;

  if (!stationId || !windowSize) {
    return res.status(400).json({ error: "Missing stationId or windowSize." });
  }

  const pythonCmd = process.platform === "win32" ? "python" : "python3";
  const py = spawn(pythonCmd, [scriptPath, stationId, String(windowSize)]);

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
      console.error("❌ PYTHON STDERR:", errorOutput);
      res.status(500).json({ error: "Failed to prepare input data." });
    }
  });

  py.on("error", (err) => {
    console.error("❌ Failed to spawn Python:", err);
    res.status(500).json({ error: "Python execution error." });
  });
});
