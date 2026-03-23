<div align="center">
  <h1>🌍 World Conflict Monitor</h1>
  <p>Real-time global conflict and disaster tracking application</p>
</div>
Real-time global conflict and disaster tracking application

## 🚀 Live Demo
[Coming soon]

## 📋 Overview
This application provides real-time monitoring of:
- **Active Conflicts**: Ukraine-Russia, Israel-Gaza, Sudan, Myanmar, and more
- **Natural Disasters**: Earthquakes, floods, storms, wildfires
- **Casualty Tracking**: Military and civilian casualties
- **Geospatial Visualization**: Interactive world map with color-coded markers

## 🛠️ Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript
- **Maps**: Leaflet
- **UI**: Material-UI
- **Data Sources**: GDACS, USGS, custom war collectors

## 🏃‍♂️ Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend Setup
\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

### Frontend Setup
\`\`\`bash
cd frontend
npm install
npm start
\`\`\`

## 🌐 API Endpoints
- `GET /health` - Health check
- `GET /api/v1/events` - Get events within bounding box
- `GET /api/v1/events/stats` - Get event statistics
- `GET /api/docs` - Interactive API documentation

## 📊 Active Conflicts Tracked
- 🇺🇦 Ukraine-Russia War (multiple front lines)
- 🇮🇱🇵🇸 Israel-Gaza Conflict
- 🇸🇩 Sudan Civil War
- 🇲🇲 Myanmar Civil War
- 🇨🇩 DR Congo Conflict
- 🇪🇹 Ethiopia Conflicts
- 🌍 Sahel Region Conflicts
- 🇭🇹 Haiti Gang Violence

## 🤝 Contributing
Contributions are welcome! Please read our contributing guidelines.

## 📄 License
MIT License

## ⚠️ Disclaimer
This application is for informational purposes only. Casualty estimates are based on available sources and may not be fully accurate.

---
Made with ❤️ for global awareness
"@ | Out-File -FilePath README.md -Encoding UTF8
# Add badges to README
$readme = Get-Content README.md -Raw
$badges = @"
[![GitHub stars](https://img.shields.io/github/stars/Vaanar24/worldconflict-app)](https://github.com/Vaanar24/worldconflict-app/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Vaanar24/worldconflict-app)](https://github.com/Vaanar24/worldconflict-app/network)
[![GitHub issues](https://img.shields.io/github/issues/Vaanar24/worldconflict-app)](https://github.com/Vaanar24/worldconflict-app/issues)
[![License](https://img.shields.io/github/license/Vaanar24/worldconflict-app)](https://github.com/Vaanar24/worldconflict-app/blob/main/LICENSE)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)
![React](https://img.shields.io/badge/react-18.0+-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg)
