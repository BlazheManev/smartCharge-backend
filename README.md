# 🪼 SmartCharge EV Backend

Node.js + Express backend for **SmartCharge AI** — an intelligent electric vehicle (EV) infrastructure system. It handles station data ingestion, HTML report uploads, ONNX-based ML predictions, and serves metadata to the React frontend.

---

## 🚀 Features

- 📊 EV station availability via `/api/ev-data`
- 🧠 ML model metadata via `/api/ml-models`
- 📂 Upload & fetch HTML reports from MongoDB
- 🤖 ONNX prediction endpoint for EV availability
- 💾 Model binaries stored in MongoDB GridFS
- 🔌 Connected to ML training pipeline via DVC
- 🔐 Supports environment configs via `.env`

---

## 🧱 Tech Stack

- ⚙️ **Node.js** + **Express.js**
- 🧬 **MongoDB** (with GridFS + Mongoose)
- 🧠 **onnxruntime-node** for model inference
- 📦 **Multer** for file uploads
- 📤 Deployed on **Render** / Docker-ready

---

## 🗜️ Project Structure

```
EV-BACKEND/
├── models/               # Mongoose schema (e.g. Report.js)
├── routes/               # Express route handlers
│   ├── evData.js         # GET /api/ev-data
│   ├── mlModels.js       # GET /api/ml-models (and download)
│   ├── upload.js         # POST /reports/upload, GET /reports/view
│   └── predict.js        # POST /api/predict
├── uploads/              # Uploaded HTML files (served as static)
├── server.js             # Express server entry point
├── Dockerfile            # Docker build config
├── .env                  # Env vars like MONGO_URI, etc.
```

---

## 🛠️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/your-username/smartcharge-backend.git
cd smartcharge-backend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Add a `.env` file

```env
MONGO_URI=mongodb+srv://<your-uri>
```

_Optionally add:_  
```env
PORT=3000
```

### 4. Start the server

```bash
node server.js
```

Open: [http://localhost:3000](http://localhost:3000)

---

## 🐳 Docker Support

### Build Docker image

```bash
docker build -t blazhe/smartcharge-backend:latest .
```

### Run the container

```bash
docker run -p 3000:3000   -e MONGO_URI="mongodb+srv://..."   blazhe/smartcharge-backend:latest
```

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/ev-data` | Returns latest station availability |
| `GET` | `/api/ml-models` | Returns MLflow/metadata from MongoDB |
| `GET` | `/api/ml-models/file/:filename` | Downloads model ONNX/pkl file from GridFS |
| `POST` | `/api/predict` | Run ONNX model prediction for a station |
| `POST` | `/reports/upload` | Uploads drift/expectation HTML reports |
| `GET` | `/reports/view/:id` | Returns HTML string for rendering |
| `GET` | `/reports/raw/:id` | Returns raw HTML as text/html |
| `GET` | `/reports/list` | Lists all uploaded report documents |

---

## ✅ Required Environment Variables

In your `.env`:

```env
MONGO_URI=your-mongodb-uri
```

And optionally:

```env
PORT=3000
```

---

## 📍 Deployment Notes

- Connects to **MongoDB Atlas** (URI via `.env`)
- Models are stored via **GridFS**
- ONNX model inference happens live using stored model files
- Frontend (Vite + React) connects via `/api`

---

## 👨‍💻 Author

**Blazhe Manev**  

---
