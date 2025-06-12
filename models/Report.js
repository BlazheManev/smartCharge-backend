import mongoose from 'mongoose';

const ReportSchema = new mongoose.Schema({
  type: { type: String, required: true },
  station_id: { type: String, required: true },
  filename: { type: String, required: true },
  originalName: String,
  createdAt: { type: Date, default: Date.now },
});

export default mongoose.model('Report', ReportSchema);
