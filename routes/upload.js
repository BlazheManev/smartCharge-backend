import express from 'express';
import multer from 'multer';
import fs from 'fs';
import path from 'path';
import Report from '../models/Report.js';

const router = express.Router();
const upload = multer();

const driftDir = path.join('uploads', 'ev_drift');
const expectationsDir = path.join('uploads', 'ev_expectations');

[driftDir, expectationsDir].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

router.post('/upload', upload.single('file'), async (req, res) => {
  try {
    const { station_id, type } = req.body;
    const { originalname, buffer } = req.file;

    if (!station_id || !type || !buffer) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const folder = type === 'drift' ? driftDir : expectationsDir;
    const fullPath = path.join(folder, `${Date.now()}-${originalname}`);

    fs.writeFileSync(fullPath, buffer);

    await Report.create({
      station_id,
      type,
      filename: originalname,
      path: fullPath,
    });

    res.status(200).json({ message: '✅ Report uploaded successfully!' });
  } catch (err) {
    console.error('❌ Upload Error:', err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

export default router;
