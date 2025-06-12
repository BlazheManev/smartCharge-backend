import mongoose from 'mongoose';

const reportSchema = new mongoose.Schema({
  station_id: String,
  type: String,
  filename: String,
  path: String,
  uploaded_at: { type: Date, default: Date.now }
});

export default mongoose.model('Report', reportSchema);
