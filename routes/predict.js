import express from "express";
import mongoose from "mongoose";
import { GridFSBucket } from "mongodb";
import { InferenceSession, Tensor } from "onnxruntime-node";
import { spawn } from "child_process";

const router = express.Router();
const db = mongoose.connection;

router.post("/predict", async (req, res) => {
  const { station_id, datetime } = req.body;
  const windowSize = 24;

  if (!station_id || !datetime) {
    return res.status(400).json({ error: "Missing station_id or datetime" });
  }

  try {
    // 1. Load ONNX model from GridFS
    const bucket = new GridFSBucket(db.db);
    const onnxFilename = `model_ev_${station_id}.onnx`;

    const modelBuffer = await new Promise((resolve, reject) => {
      const chunks = [];
      const stream = bucket.openDownloadStreamByName(onnxFilename);
      stream.on("data", (chunk) => chunks.push(chunk));
      stream.on("end", () => resolve(Buffer.concat(chunks)));
      stream.on("error", reject);
    });

    const session = await InferenceSession.create(modelBuffer);

    // 2. Call Python script to prepare input using the .pkl pipeline
    const python = spawn("python3", ["python/prepare_input.py", station_id, String(windowSize)]);

    let result = "";
    let errorOutput = "";

    python.stdout.on("data", (data) => (result += data.toString()));
    python.stderr.on("data", (data) => (errorOutput += data.toString()));

    python.on("close", async (code) => {
      if (errorOutput || result.includes("ERROR")) {
        console.error("❌ Python error:", errorOutput || result);
        return res.status(500).json({ error: "Failed to prepare input data." });
      }

      // Parse Python output into ONNX input tensor
      const inputValues = result.trim().split(",").map(parseFloat);
      const inputTensor = new Tensor("float32", Float32Array.from(inputValues), [1, windowSize, 1]);

      // 3. Run ONNX inference
      const output = await session.run({ input: inputTensor });
      const prediction = output.output.data[0];

      // 4. Format response
      const status =
        prediction < 0.3
          ? "✅ High chance it will be available"
          : prediction < 0.6
          ? "⚠️ Might be occupied"
          : "🚫 Likely occupied";

      return res.json({
        station_id,
        datetime,
        prediction: prediction.toFixed(2),
        probability: `${(prediction * 100).toFixed(1)}%`,
        status,
      });
    });
  } catch (err) {
    console.error("❌ Prediction error:", err);
    res.status(500).json({ error: "Prediction failed" });
  }
});

export default router;
