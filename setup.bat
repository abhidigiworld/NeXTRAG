@echo off
echo ========================================
echo SmartRAG AI - Quick Setup Script
echo ========================================
echo.

echo Step 1: Setting up Backend...
cd backend
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate
echo Installing Python dependencies...
pip install -r requirements.txt
echo.

echo Step 2: Copying environment template...
if not exist .env (
    copy .env.example .env
    echo .env file created! Please edit it with your API keys.
) else (
    echo .env file already exists.
)
echo.

cd ..

echo Step 3: Setting up Frontend...
cd frontend
echo Installing Node dependencies...
call npm install
echo.

cd ..

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit backend/.env with your API keys
echo 2. Run backend: cd backend ^&^& venv\Scripts\activate ^&^& python -m app.main
echo 3. Run frontend: cd frontend ^&^& npm run dev
echo 4. Open http://localhost:3000
echo.
pause
