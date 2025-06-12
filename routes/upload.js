import express from 'express';
import multer from 'multer';
import fs from 'fs';
import path from 'path';
import Report from '../models/Report.js';
import mongoose from 'mongoose';

const router = express.Router();
const upload = multer();

// Directories
const driftDir = path.join('uploads', 'ev_drift');
const expectationsDir = path.join('uploads', 'expectations');

// Ensure folders exist
[driftDir, expectationsDir].forEach((dir) => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// 🔼 Upload report
router.post('/upload', upload.single('file'), async (req, res) => {
  try {
    const { station_id, type } = req.body;
    const { originalname, buffer } = req.file || {};

    if (!station_id || !type || !buffer) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const folder = type === 'drift' ? driftDir : expectationsDir;
    const timestampedName = `${Date.now()}-${originalname}`;
    const fullPath = path.join(folder, timestampedName);

    // 🧹 Delete previous entries for this station and type
    const oldEntries = await Report.find({ station_id, type });
    for (const entry of oldEntries) {
      if (fs.existsSync(entry.path)) {
        fs.unlinkSync(entry.path);
      }
    }
    await Report.deleteMany({ station_id, type });

    // 📝 Save new file
    fs.writeFileSync(fullPath, buffer);

    // 💾 Save metadata (and HTML string for frontend use)
    await Report.create({
      station_id,
      type,
      filename: timestampedName,
      path: fullPath,
      html: buffer.toString(),
      uploaded_at: new Date(),
    });

    res.status(200).json({ message: '✅ Report uploaded successfully!' });
  } catch (err) {
    console.error('❌ Upload Error:', err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// 📄 List reports
router.get('/list', async (_req, res) => {
  try {
    const reports = await Report.find({}, '-__v -html').sort({ uploaded_at: -1 });
    res.json(reports);
  } catch (err) {
    console.error('❌ Listing Error:', err);
    res.status(500).json({ error: 'Failed to list reports' });
  }
});

// 📄 Serve HTML by ID
router.get('/view/:id', async (req, res) => {
  try {
    const report = await Report.findById(req.params.id).lean();
    if (!report) return res.status(404).json({ error: 'Not found' });

    res.status(200).json(report); // Includes HTML as a string
  } catch (err) {
    console.error('❌ Error fetching report:', err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

router.get('/raw/:id', async (req, res) => {
  const report = await Report.findById(req.params.id).lean();
  if (!report) return res.status(404).send('Not found');
  
  res.setHeader('Content-Type', 'text/html');
  res.send(report.html);
});

export default router;
