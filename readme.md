# Create README.md
@"
# 🌍 World Monitor - Real-Time Global Conflict & Disaster Tracker

A real-time web application that monitors global conflicts, wars, natural disasters, and critical events worldwide. Built with FastAPI (Python) backend and React (TypeScript) frontend.

## 🚀 Features

- **Real-time Conflict Tracking**: Monitors active war zones including Ukraine-Russia, Israel-Gaza, Sudan, Myanmar, and more
- **Live Disaster Alerts**: Earthquake, flood, storm, and wildfire tracking from GDACS
- **Interactive World Map**: Visualize events with color-coded markers based on severity
- **Casualty Tracking**: Military and civilian casualty estimates with sources
- **Filtering & Search**: Filter by conflict type, threat level, region, and time range
- **Live Statistics**: Active conflicts count, total casualties, and hotspot identification
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **AIOHTTP** - Async HTTP client for API calls
- **GDACS API** - Natural disaster data
- **Custom War Collectors** - Real-time conflict data

### Frontend
- **React 18** with TypeScript
- **Material-UI (MUI)** - Component library
- **Leaflet** - Interactive maps
- **Axios** - HTTP client
- **date-fns** - Date formatting

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

## 🔧 Installation

### Clone the repository
\`\`\`bash
git clone https://github.com/YOUR_USERNAME/world-monitor.git
cd world-monitor
\`\`\`

### Backend Setup
\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

### Frontend Setup
\`\`\`bash
cd frontend
npm install
npm start
\`\`\`

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/events` | GET | Get events within bounding box |
| `/api/v1/events/stats` | GET | Get event statistics |
| `/api/docs` | GET | Interactive API documentation |

## 🗺️ Active Conflicts Tracked

- **Ukraine-Russia War**: Multiple front lines (Bakhmut, Avdiivka, Kherson)
- **Israel-Gaza Conflict**: Gaza Strip, West Bank
- **Sudan Civil War**: Khartoum, Darfur
- **Myanmar Civil War**: Kachin State, Shan State
- **DR Congo Conflict**: North Kivu, Ituri
- **Ethiopia Conflicts**: Tigray, Amhara
- **Sahel Region**: Mali, Burkina Faso, Niger
- **Haiti Gang Violence**: Port-au-Prince

## 📊 Data Sources

- **GDACS** - Natural disasters
- **USGS** - Earthquakes
- **Custom War Collectors** - Real-time conflict data
- **NewsAPI** - Breaking news (optional)

## 🎯 Roadmap

- [ ] User authentication
- [ ] Custom alerts via email/SMS
- [ ] Historical data analysis
- [ ] Mobile app (React Native)
- [ ] AI-powered threat prediction
- [ ] Social media integration

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines.

## 📄 License

MIT License - see LICENSE file

## ⚠️ Disclaimer

This application is for informational purposes only. Casualty estimates are based on available sources and may not be fully accurate. Always verify critical information through official channels.

## 🙏 Acknowledgments

- GDACS for disaster data
- USGS for earthquake data
- All open-source contributors

---
Made with ❤️ for global awareness
"@ | Out-File -FilePath README.md -Encoding UTF8