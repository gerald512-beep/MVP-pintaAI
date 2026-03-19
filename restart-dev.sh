#!/bin/bash
echo "Stopping existing servers..."
taskkill /F /IM uvicorn.exe 2>/dev/null || true
taskkill /F /IM node.exe 2>/dev/null || true
sleep 1

echo "Clearing Vite cache..."
rm -rf frontend/node_modules/.vite

echo "Starting backend..."
cd backend && uvicorn main:app --reload --port 8000 &
cd ..

echo "Starting frontend..."
cd frontend && npm run dev -- --force
