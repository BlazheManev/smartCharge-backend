import express from 'express';
import mongoose from 'mongoose';

const router = express.Router();

// Define schema dynamically if you don't have a model already
const StationAvailability = mongoose.connection.collection('ev_station_availability');

router.get('/ev-data', async (_req, res) => {
  try {
    const cursor = StationAvailability.find({});
    const results = await cursor.toArray();

    res.status(200).json({ results });
  } catch (err) {
    console.error('❌ Error fetching EV data:', err);
    res.status(500).json({ error: 'Failed to fetch EV data' });
  }
});

export default router;
