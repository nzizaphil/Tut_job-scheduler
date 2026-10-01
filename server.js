/**
 * server.js - Express API for the job scheduler.
 *
 *   GET  /                    run app.py, return plain text (unchanged, used by CI)
 *   POST /api/runs            ACTIVITY 8: run app.py --json and save the run to MongoDB
 *   GET  /api/runs            ACTIVITY 8: list recent runs (summaries only)
 *   GET  /api/runs/:id        ACTIVITY 8: one run, with every job and its logs
 *   GET  /api/runs/:id/logs   ACTIVITY 8: just the logs (optional ?status=failed)
 *   GET  /dashboard/          ACTIVITY 8: the frontend dashboard (public/index.html)
 */
require('dotenv').config({ quiet: true });
const express = require('express');
const { exec, execFile } = require('child_process');
const cors = require('cors');
const path = require('path');
const mongoose = require('mongoose');
const { Run, connectDB, isConnected } = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;
const PY = process.env.PYTHON || 'python3';
const BACKEND = path.join(__dirname, 'backend');

app.use(cors());
app.use(express.json());
app.use('/dashboard', express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    exec(`${PY} app.py`, { cwd: BACKEND }, (error, stdout) => {
        if (error) return res.status(500).send('Error running Python script');
        res.type('text/plain').send(stdout.trim());
    });
});

// ACTIVITY 8: every /api route needs the database, so check it once here.
app.use('/api', (req, res, next) => {
    if (!isConnected()) {
        return res.status(503).json({
            error: 'Database not connected. Check MONGODB_URI in .env and restart the server.',
        });
    }
    next();
});

// Runs `python3 app.py --json` and parses its output.
// execFile (not exec) passes arguments directly, with no shell involved.
function runSchedulerJson() {
    return new Promise((resolve, reject) => {
        execFile(PY, ['app.py', '--json'], { cwd: BACKEND, maxBuffer: 10 * 1024 * 1024 },
            (error, stdout, stderr) => {
                if (error) return reject(new Error(stderr.trim() || error.message));
                try {
                    resolve(JSON.parse(stdout));
                } catch {
                    reject(new Error('app.py did not return valid JSON'));
                }
            });
    });
}

app.post('/api/runs', async (req, res) => {
    const report = await runSchedulerJson();
    const run = await Run.create(report);
    res.status(201).json(run);
});

app.get('/api/runs', async (req, res) => {
    const limit = Math.min(parseInt(req.query.limit, 10) || 20, 100);
    const runs = await Run.find({}, { jobs: 0, console: 0 }) // summaries only: smaller response
        .sort({ createdAt: -1 })
        .limit(limit);
    res.json(runs);
});

async function findRun(req, res) {
    if (!mongoose.isValidObjectId(req.params.id)) {
        res.status(400).json({ error: 'Invalid run id' });
        return null;
    }
    const run = await Run.findById(req.params.id);
    if (!run) res.status(404).json({ error: 'Run not found' });
    return run;
}

app.get('/api/runs/:id', async (req, res) => {
    const run = await findRun(req, res);
    if (run) res.json(run);
});

app.get('/api/runs/:id/logs', async (req, res) => {
    const run = await findRun(req, res);
    if (!run) return;
    const jobs = req.query.status ? run.jobs.filter((j) => j.status === req.query.status) : run.jobs;
    res.json(jobs.map(({ jobId, status, logs }) => ({ jobId, status, logs })));
});

// Express 5 forwards errors from async routes here automatically.
app.use((err, req, res, next) => {
    console.error(err);
    res.status(500).json({ error: err.message });
});

connectDB(process.env.MONGODB_URI).finally(() => {
    app.listen(PORT, () => {
        console.log(`Node server running at http://localhost:${PORT}`);
        console.log(`Dashboard: http://localhost:${PORT}/dashboard/`);
    });
});