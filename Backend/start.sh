#!/bin/bash
# Install dependencies is handled by Render's build command usually, but we ensure uvicorn is ready.
# Run Database Init (if we had migrations, we would run them here)
# For now, just start the app
echo "Starting TalentTalk Pro Backend..."
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
