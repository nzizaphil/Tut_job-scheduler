/**
* server.js — Minimal Express API that runs backend/app.py and returns
stdout.
*/
const express = require('express');
const { exec } = require('child_process');
const cors = require('cors');
const path = require('path');
const app = express();
const PORT = 3000;
app.use(cors());
app.get('/', (req, res) => {
    const cwd = path.join(__dirname, 'backend');
    const PY = 'python3';
    exec(`${PY} app.py`, { cwd }, (error, stdout, stderr) => {
        if (error) return res.status(500).send('Error running Python script');
        res.type('text/plain').send(stdout.trim());
    });
});
app.listen(PORT, () => {
    console.log(`Node server running at http://localhost:${PORT}`);
});