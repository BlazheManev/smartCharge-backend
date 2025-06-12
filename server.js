import express from 'express';
import multer from 'multer';
import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';
import Report from './models/Report.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const MONGO_URI = process.env.MONGO_URI;

// Connect to MongoDB
mongoose.connect(MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
}).then(() => console.log('✅ Connected to MongoDB'))
  .catch(err => console.error('❌ MongoDB connection error:', err));

// Set up multer to store files in 'uploads' folder
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/ev_drift');
  },
  filename: function (req, file, cb) {
    const uniqueName = `${Date.now()}-${file.originalname}`;
    cb(null, uniqueName);
  }
});
const upload = multer({ storage });

// Upload endpoint
app.post('/reports/upload', upload.single('file'), async (req, res) => {
  const { type, station_id } = req.body;
  const { filename, originalname } = req.file;

  const report = new Report({
    type,
    station_id,
    filename,
    originalName: originalname,
  });

  await report.save();
  res.json({ message: '✅ Report uploaded successfully' });
});

// Serve HTML file
app.get('/reports/:type/:station_id', async (req, res) => {
  const { type, station_id } = req.params;
  const report = await Report.findOne({ type, station_id }).sort({ createdAt: -1 });

  if (!report) return res.status(404).send('Report not found');

  const filePath = path.join('uploads/ev_drift', report.filename);
  if (!fs.existsSync(filePath)) return res.status(404).send('File not found');

  res.setHeader('Content-Type', 'text/html');
  fs.createReadStream(filePath).pipe(res);
});

// List report metadata
app.get('/reports/meta/:type', async (req, res) => {
  const reports = await Report.find({ type: req.params.type }).sort({ createdAt: -1 });
  res.json(reports);
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});
