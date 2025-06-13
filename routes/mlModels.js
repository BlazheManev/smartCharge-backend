import express from 'express';
import mongoose from 'mongoose';

const router = express.Router();

const MLModels = mongoose.connection.collection('ml_models');

// GET all ML models
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
