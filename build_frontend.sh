# Building the frontend for production
cd frontend
npm install
npm run build
cd ..

echo "Frontend built. To start the app:"
echo "  cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001"
