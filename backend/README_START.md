# How to Start the Backend Server

## Quick Start

1. **Navigate to the backend directory:**
```bash
cd backend
```

2. **Install dependencies (if not already installed):**
```bash
pip install -r requirements.txt
```

3. **Start the server:**
```bash
python3 app.py
```

Or use the startup script:
```bash
./start_server.sh
```

The server will start on `http://localhost:5000`

## Verify it's working

Open a new terminal and test the health endpoint:
```bash
curl http://localhost:5000/api/health
```

You should see:
```json
{"status":"ok","message":"BioBoard API is running"}
```

## Troubleshooting

### Port 5000 already in use
If you get an error that port 5000 is already in use, you can:
1. Kill the process using port 5000:
```bash
lsof -ti:5000 | xargs kill -9
```

2. Or change the port in `app.py` (last line):
```python
app.run(debug=True, port=5001)  # Change to different port
```

And update `src/services/api.js` to use the new port:
```javascript
const API_BASE_URL = 'http://localhost:5001/api';
```

### Models not loading
If models fail to load, the server will use fallback calculations. This is fine - the API will still work, just using simpler calculations instead of ML models.

### Dependencies not installing
Make sure you're using Python 3:
```bash
python3 --version
```

If you have issues, try:
```bash
pip3 install -r requirements.txt
```

