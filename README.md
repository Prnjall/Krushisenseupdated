# KrushiSense

## Smart Crop Recommendation, Yield Intelligence and Digital Agriculture Platform

## Overview

Agricultural decisions depend heavily on soil health, environmental conditions, and weather patterns. Unfortunately, agricultural information is often fragmented, leaving farmers to rely on guesswork or delayed expert advice. Selecting the wrong crop or missing early signs of plant disease can lead to significant financial loss and reduced yield. Furthermore, as digital agriculture expands, systems struggle to share data because they use incompatible schemas.

**KrushiSense** is a comprehensive, data-driven digital agriculture platform designed to solve these problems. It empowers farmers with instant, localized intelligence by combining machine learning, real-time satellite/weather data, AI advisory services, and a unified interoperability schema.

## Key Features

- **AI Crop Recommendation**: Evaluates soil NPK, pH, and climate data to recommend the most suitable crops.
- **Yield Prediction / Estimated Yield Index**: Provides baseline yield expectations for informed agricultural planning.
- **Regenerative Agricultural Heuristics**: Highlights crops that naturally improve soil health based on the current context.
- **Weather Integration**: Live weather data and 7-day precipitation/risk forecasts via Open-Meteo.
- **Satellite NDVI Monitoring**: Historical vegetation index analysis using Sentinel/Copernicus satellite data.
- **AI-Assisted Disease Detection**: Vision-based disease screening using a custom ONNX model (MobileNetV3).
- **AI Disease Advisory**: Graceful, uncertain-aware agricultural advisory using Google Gemini with an OpenAI fallback.
- **Multilingual Support**: Fully localized static UI in English, Hindi, and Marathi.
- **KVK Explorer**: Interactive directory of the India-wide Krishi Vigyan Kendra (KVK) network.
- **Interoperability / Canonical Schema**: A BRICS-ready, standardized schema for agricultural data exchange between partner platforms.
- **Privacy-Aware Architecture**: GPS coordinates are never sent to external AI providers.
- **Responsive UI**: Accessible, farmer-oriented interface with dark and light mode support.

## System Architecture

KrushiSense operates on a decoupled client-server architecture:

1. **Frontend (Vercel)**: Collects farmer input, handles static localization locally, and interacts with the API.
2. **Backend (Render)**: Django-based REST APIs coordinate ML inference and external services.
3. **ML Inference Layer**: Loads pre-trained models (`.pkl` and `.onnx`) to compute crop suitability, yield indices, and disease classifications locally.
4. **External Services**: The backend queries Open-Meteo for weather, Sentinel Hub for NDVI, and Gemini/OpenAI for conversational advisory.
5. **Data Layer**: An SQLite database holds normalized KVK discovery data, allowing the frontend to filter and map official agricultural centers.
6. **Interoperability Layer**: Normalizes proprietary internal data structures into a canonical JSON schema for external partner consumption.

## Technology Stack

**Frontend**
- React 19
- TypeScript
- Vite
- Tailwind CSS v4
- Leaflet / React Leaflet

**Backend**
- Python 3
- Django 5
- Django REST Framework / Custom API Views
- Gunicorn (Production Server)
- SQLite (Production Database)

**Machine Learning & AI**
- scikit-learn
- Joblib
- ONNX Runtime
- MobileNetV3 (Disease detection architecture)
- Google Gemini (Primary AI)
- OpenAI (Fallback AI)

**External APIs**
- Open-Meteo
- Sentinel Hub / Copernicus

## ML Models

- **Crop Recommendation**: A Random Forest classifier trained on local soil/climate conditions to predict the most biologically suitable crop.
- **Yield Prediction**: A regressor model estimating standard yield indices based on optimal NPK matching and historical baseline performance.
- **Disease Detection**: A quantized MobileNetV3 ONNX model fine-tuned for early-stage disease classification on 4 specific crops (Apple, Maize, Grapes, Rice).

## Disease Safety

To prevent dangerous misdiagnosis, the disease detection pipeline includes strict safety guardrails:
- **Image Validation**: Enforces 5MB size limits and standard image formats.
- **Preprocessing**: Applies ImageNet normalization and strict 224x224 CHW tensor layouts.
- **Crop Compatibility**: Rejects unsupported crops before inference.
- **Confidence Handling**: Low-confidence predictions explicitly trigger "Uncertain" workflows.
- **AI-Assisted Assessment**: Results are explicitly marked as "AI-assisted screening" rather than definitive diagnoses.

## KVK Explorer

The KVK Explorer provides access to the official Indian Council of Agricultural Research (ICAR) network:
- **726 Official Records**: The deployed database contains 726 KVK records encompassing all of India.
- **Official Source Provenance**: Data is strictly preserved from official records.
- **Verified Coordinates**: 4 KVKs have manually verified, exact map coordinates for precise Leaflet mapping.
- **Address Search**: The remaining 722 records are fully filterable by State and District and display their official textual addresses.
- **No Fabricated Data**: We do not inject fake coordinates or unsupported soil-testing prices into official records.

## Interoperability

KrushiSense implements a canonical agricultural schema to solve data fragmentation. By mapping internal, proprietary representations (like numeric IDs or legacy database columns) into a standardized JSON structure, KrushiSense can share:
- Normalized agricultural context
- Data provenance and freshness timestamps
- Model outputs (separated from ground truth)
- Explicit representations of unavailable data
This architecture ensures KrushiSense is ready to integrate with external state, national, or BRICS partner systems.

## Multilingual Support

The application is fully usable in **English**, **Hindi**, and **Marathi**.
To ensure maximum performance and accessibility on low-end devices, all static UI translations (navigation, buttons, state/district names, badges) are bundled locally. Language switching happens immediately without blocking network requests. AI-generated advisory content is translated asynchronously in the background.

## Privacy and Security

- **Server-side Secrets**: API keys (Gemini, OpenAI, Sentinel) remain safely on the backend.
- **GPS Privacy**: Precise latitude/longitude coordinates are used for weather/NDVI retrieval but are stripped before sending prompts to LLM providers.
- **Production Hardening**: `DEBUG=False`, strict `ALLOWED_HOSTS`, and restricted `CORS` headers protect the Render deployment.
- **Input Validation**: All incoming API requests are validated against strict type and range constraints.

## API Endpoints

The following production routes are implemented under `/api/`:

- `GET /api/health` - System health and ML model status.
- `POST /api/predict-crop/` - Returns top-3 recommended crops and yield index based on soil data.
- `GET /api/weather/` - Retrieves current weather, 7-day forecast, and agricultural risk signals.
- `GET /api/satellite-ndvi/` - Retrieves historical NDVI imagery and vegetation indices.
- `POST /api/agri-advisory/` - Generates localized LLM agricultural advice based on canonical context.
- `POST /api/disease-detection/` - Performs ONNX vision inference on crop leaves.
- `POST /api/disease-advisory/` - Generates LLM treatment advisory for detected diseases.
- `POST /api/v1/interop/advisory/` - Accepts canonical schema requests from external partner systems.
- `GET /api/v1/kvks/` - Paginated, filterable directory of KVKs.
- `GET /api/v1/kvks/nearest/` - Locates the nearest KVKs using geospatial logic.

## Project Structure

```text
Agri Analysis/
├── backend/
│   ├── backend/             # Django settings, root URLs, WSGI
│   ├── data/                # KVK import scripts & seed artifacts
│   ├── predictions/         # ML inference APIs, Views, Models
│   │   ├── models/          # .pkl and .onnx model files
│   │   └── interoperability/# Canonical schema implementations
│   └── requirements.txt
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/      # React components (Home, PredictCrop, NearbyKendras)
│       ├── contexts/        # Language and Theme providers
│       ├── lib/             # API utilities and routing
│       └── index.css        # Tailwind v4 configuration
└── README.md
```

## Installation

### Backend Setup
Requires Python 3.10+
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
pip install -r requirements.txt
cp .env.example .env       # Configure required keys
python manage.py migrate
python data/kvk/import_kvk.py # Initialize KVK dataset
python manage.py runserver
```

### Frontend Setup
Requires Node.js 18+
```bash
cd frontend
npm install
cp .env.example .env.local # Configure VITE_API_BASE_URL if needed
npm run dev
```

## Environment Variables

**Backend (`backend/.env`)**
- `DJANGO_SECRET_KEY`: Security key for Django
- `GEMINI_API_KEY`: Primary AI provider key
- `OPENAI_API_KEY`: Fallback AI provider key
- `SENTINEL_HUB_CLIENT_ID`: Copernicus satellite credentials
- `SENTINEL_HUB_CLIENT_SECRET`: Copernicus satellite credentials
- `CORS_ALLOWED_ORIGIN_REGEXES`: Allowed frontend origins

**Frontend (`frontend/.env.local`)**
- `VITE_FORMSPREE_ID`: Contact form endpoint ID
- `VITE_API_BASE_URL`: Production backend URL (leave empty for local dev proxy)

## Production Deployment

- **Frontend**: Deployed to Vercel via standard Vite build (`npm run build`).
- **Backend**: Deployed to Render as a Python Web Service.
The verified Render Start Command is:
```bash
python manage.py migrate && python data/kvk/import_kvk.py && gunicorn backend.wsgi
```
*Note: Because SQLite on Render operates on an ephemeral disk, migrations and the safe KVK importer must run automatically at startup.*

## Testing

- **Backend**: Automated tests run via `pytest`. The suite currently comprises **141 passing tests** covering ML loading, API endpoints, error handling, and schema validation.
- **Frontend**: Enforces strict TypeScript checks (`npm run lint`) and Vite production builds.

## Limitations

- **Yield Estimation**: The Yield prediction is provided as a relative statistical index, not an absolute tonnage guarantee.
- **KVK Geolocation**: While 726 KVKs are searchable, only 4 have verified exact map coordinates. We prioritize data integrity over automated, unverified geocoding.
- **AI Availability**: AI advisory workflows depend directly on external Gemini/OpenAI API quotas.
- **Disease Inference**: The vision model is an AI-assisted screening tool; it does not replace laboratory pathology.
- **Satellite Data**: Sentinel NDVI relies on recent cloud-free passes; data may be temporarily unavailable depending on weather patterns.

## Future Scope

- Expanding verified KVK geospatial coverage through crowdsourced regional validation.
- Integration with live national agricultural market pricing APIs (e.g., e-NAM).
- Expanded disease dataset coverage for more regional staple crops.
- Support for additional BRICS languages via the canonical interoperability schema.

## License

MIT License. Free to use, modify, and distribute.
