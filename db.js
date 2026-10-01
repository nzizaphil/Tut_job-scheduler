/**
 * db.js - ACTIVITY 8: MongoDB connection + the Run model (Mongoose).
 * One document per scheduler run, with every job and its logs embedded.
 */
const mongoose = require('mongoose');

const jobSchema = new mongoose.Schema(
  {
    jobId: { type: Number, required: true },
    type: String,
    description: String,
    status: { type: String, enum: ['pending', 'running', 'completed', 'failed'] },
    priority: Number,
    maxRetries: Number,
    startOffset: Number, // seconds after the run started (for the timeline)
    duration: Number,    // seconds
    logs: [String],
  },
  { _id: false }
);

const runSchema = new mongoose.Schema(
  {
    summary: { pending: Number, completed: Number, failed: Number },
    wallTime: Number,
    totalJobTime: Number,
    jobs: [jobSchema],
    console: [String],
  },
  { timestamps: true } // adds createdAt / updatedAt automatically
);

const Run = mongoose.model('Run', runSchema);

async function connectDB(uri) {
  if (!uri) {
    console.warn('MONGODB_URI is not set: /api routes will return 503 (GET / still works).');
    return;
  }
  try {
    await mongoose.connect(uri);
    console.log('Connected to MongoDB');
  } catch (err) {
    console.error('MongoDB connection failed:', err.message);
  }
}

const isConnected = () => mongoose.connection.readyState === 1;

module.exports = { Run, connectDB, isConnected };
