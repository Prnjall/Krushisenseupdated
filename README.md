# 🌾 KrushiSense — Smart Agricultural Intelligence for Maharashtra Farmers

KrushiSense is a data-driven web application that helps farmers choose the right crop based on their soil and environmental conditions, find the nearest Krishi Vigyan Kendra (KVK), and access agricultural support — all in English, Hindi, and Marathi.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🌱 **Crop Prediction** | Enter soil NPK, pH, temperature, humidity, and rainfall to get the top 3 recommended crops |
| 🗺️ **KVK Map** | Interactive map of all 33 official ICAR Krishi Vigyan Kendras across Maharashtra with distances, soil testing info, and Google Maps directions |
| 🌐 **Multi-language** | Full UI in English, Hindi, and Marathi with static + dynamic translation |
| 🌙 **Dark / Light Mode** | System-aware theme with persistent user preference |
| 📬 **Contact Support** | Integrated contact form via Formspree |
| 📄 **Legal Pages** | Privacy Policy and Terms of Service |

---

## 🛠 Tech Stack

**Frontend**
- [Vite](https://vitejs.dev/) + [React 19](https://react.dev/) + TypeScript
- [Tailwind CSS v4](https://tailwindcss.com/)
- [React Router v7](https://reactrouter.com/)
- [React Leaflet](https://react-leaflet.js.org/) + [Leaflet](https://leafletjs.com/) — KVK map
- [Framer Motion / motion](https://motion.dev/) — animations
- [Lucide React](https://lucide.dev/) — icons
- [Formspree](https://formspree.io/) — contact form backend

**Backend**
- [Python 3](https://www.python.org/) + [Django 5](https://www.djangoproject.com/)
- Machine learning prediction via scikit-learn
- SQLite database

**Data Sources**
- Maharashtra crop dataset (Kaggle / ICAR)
- KVK location data — [ICAR Official Network](https://kvk.icar.gov.in/)
- Map tiles — OpenStreetMap via Leaflet (no API key required)

---

## 📁 Project Structure

```
Agri Analysis/
├── backend/                       # Django backend
│   ├── backend/                   # Django project settings, URLs
│   ├── ml/                        # ML training scripts & dataset
│   │   └── data/crop_merged.csv
│   └── predictions/               # Django app: ML inference API
├── frontend/                      # Vite + React frontend
│   ├── public/
│   │   └── data/crop_merged.csv   # Served statically for frontend prediction
│   └── src/
│       ├── components/            # Page & feature components
│       │   └── ui/                # Reusable UI primitives (button, map)
│       ├── contexts/              # React contexts (Language, Theme)
│       ├── data/                  # cropData.ts — static crop metadata
│       └── lib/                   # Utility functions (future)
├── scripts/                       # One-off data update scripts
├── .env.example                   # Safe to commit — lists required variables
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Running Locally

### 1. Clone the repository

```sh
git clone <repo-url>
cd "Agri Analysis"
```

### 2. Backend Setup

```sh
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate         # Windows
# source .venv/bin/activate    # macOS / Linux

# Install Python dependencies
pip install -r requirements.txt

# Run migrations
cd backend
python manage.py migrate

# Start Django server
python manage.py runserver
```

Backend runs at: **http://127.0.0.1:8000/**

### 3. Frontend Setup

```sh
cd frontend

# Install Node dependencies
npm install

# Set up environment variables
copy .env.example .env.local
# Edit .env.local and fill in your VITE_FORMSPREE_ID

# Start dev server
npm run dev
```

Frontend runs at: **http://localhost:3000/**

---

## 🔑 Environment Variables

Copy `frontend/.env.example` to `frontend/.env.local` and fill in your values.

| Variable | Required | Description |
|---|---|---|
| `VITE_FORMSPREE_ID` | Yes | Formspree form endpoint ID for the Contact page |
| `VITE_APP_URL` | No | Base URL of the app (default: `http://localhost:3000`) |
| `DJANGO_SECRET_KEY` | Prod only | Django secret key — insecure dev key used automatically in dev |

> `.env.local` is gitignored and must never be committed.

---

## 📊 Data Sources

- **Crop dataset**: Maharashtra agricultural dataset (ICAR) — soil NPK, pH, temperature, humidity, rainfall, region, district, soil colour, fertilizer
- **KVK data**: 33 Krishi Vigyan Kendras across Maharashtra from [ICAR Official Directory](https://kvk.icar.gov.in/)
- **Map tiles**: OpenStreetMap (via Leaflet, no API key required)

---

## 📜 License

MIT — Free to use, modify, and distribute.

---

*Built for Maharashtra farmers. Made with ❤️ using open data.*
