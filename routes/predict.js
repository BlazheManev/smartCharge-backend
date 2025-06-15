import express from 'express';
import mongoose from 'mongoose';
import { GridFSBucket } from 'mongodb';
import { InferenceSession, Tensor } from 'onnxruntime-node';

const router = express.Router();
const db = mongoose.connection;

router.post('/predict', async (req, res) => {
    const { station_id, datetime } = req.body;

    if (!station_id || !datetime) {
        return res.status(400).json({ error: 'Missing station_id or timestamp' });
    }

    try {
        const filename = `model_ev_${station_id}.onnx`;
        const bucket = new GridFSBucket(db.db);
        const downloadStream = bucket.openDownloadStreamByName(filename);

        let chunks = [];
        downloadStream.on('data', chunk => chunks.push(chunk));
        downloadStream.on('error', err => {
            console.error('❌ GridFS error:', err);
            return res.status(500).json({ error: 'Model not found in GridFS' });
        });

        downloadStream.on('end', async () => {
            try {
                const buffer = Buffer.concat(chunks);
                const session = await InferenceSession.create(buffer);

                // TODO: Use real preprocessing here
                const dummyInput = new Tensor('float32', new Float32Array([0.5, 0.4, 0.6]), [1, 3, 1]);
                const output = await session.run({ input: dummyInput });
                const prediction = output.output.data[0];

                res.status(200).json({
                    station_id,
                    datetime,
                    prediction: prediction.toFixed(2),
                    status: prediction > 0.6
                        ? '✅ High chance it will be available'
                        : prediction > 0.3
                            ? '⚠️ Might be occupied'
                            : '🚫 Likely not available',
                });
            } catch (err) {
                console.error('❌ ONNX inference error:', err);
                res.status(500).json({ error: 'Prediction failed' });
            }
        });
    } catch (err) {
        console.error('❌ General error:', err);
        res.status(500).json({ error: 'Internal error' });
    }
});

export default router;
