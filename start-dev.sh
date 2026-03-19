#!/bin/bash
# Start backend (reload on file change)
cd backend && uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend dev server
cd ../frontend && npm run dev

# Kill backend when frontend exits
kill $BACKEND_PID 2>/dev/null
