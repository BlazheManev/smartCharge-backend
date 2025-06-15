import express from 'express';
import mongoose from 'mongoose';
import { GridFSBucket } from 'mongodb';

const router = express.Router();

const db = mongoose.connection;
const MLModels = db.collection('ml_models');

router.get('/ml-models', async (_req, res) => {
  try {
    const models = await MLModels.find({}).toArray();
    res.status(200).json(models);
  } catch (err) {
    console.error('❌ Error fetching ML models:', err);
    res.status(500).json({ error: 'Failed to fetch ML models' });
  }
});


export default router;
