import express from 'express';
import multer from 'multer';
import fs from 'fs';
import path from 'path';
import Report from '../models/Report.js';

const router = express.Router();
const upload = multer();

const driftDir = path.join('uploads', 'ev_drift');
const expectationsDir = path.join('uploads', 'expectations');

// Ensure upload folders exist
[driftDir, expectationsDir].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Upload HTML reports
router.post('/upload', upload.single('file'), async (req, res) => {
  try {
    const { station_id, type } = req.body;
    const { originalname, buffer } = req.file;

    if (!station_id || !type || !buffer) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const folder = type === 'drift' ? driftDir : expectationsDir;
    const timestampedName = `${Date.now()}-${originalname}`;
    const fullPath = path.join(folder, timestampedName);

    fs.writeFileSync(fullPath, buffer);

    await Report.create({
      station_id,
      type,
      filename: timestampedName,
      path: fullPath,
    });

    res.status(200).json({ message: '✅ Report uploaded successfully!' });
  } catch (err) {
    console.error('❌ Upload Error:', err);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// List all uploaded reports
router.get('/list', async (req, res) => {
  try {
    const driftFiles = fs.readdirSync(driftDir);
    const expectationFiles = fs.readdirSync(expectationsDir);

    const driftReports = driftFiles.map(file => ({
      station_id: file.split('_')[0],
      type: 'drift',
      filename: file,
    }));

    const expectationReports = expectationFiles.map(file => ({
      station_id: file.split('_')[0],
      type: 'expectation',
      filename: file,
    }));

    res.json([...driftReports, ...expectationReports]);
  } catch (err) {
    console.error('❌ Listing Error:', err);
    res.status(500).json({ error: 'Failed to list reports' });
  }
});

export default router;
