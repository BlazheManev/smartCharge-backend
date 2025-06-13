# 🪼 SmartCharge EV Backend

Node.js + Express backend for SmartCharge AI — an intelligent electric vehicle (EV) infrastructure system. It handles data ingestion, report uploads, model metadata, and exposes REST APIs for the frontend.

---

## 🚀 Features

* 📊 Exposes EV station availability via `/api/ev-data`
* 🧠 Serves ML model metadata via `/api/ml-models`
* 🔄 Supports uploading HTML reports (drift, expectations)
* 📂 Stores all report metadata and HTML in MongoDB
* 📡 Integrated with React frontend and DVC ML pipeline

---

## 🧱 Tech Stack

* ✨ **Node.js** + **Express.js**
* 📃 MongoDB (with Mongoose)
* 📁 Multer for file uploads
* ✨ Deployed on Render (or Docker-ready)

---

## 🗜️ Project Structure

```
EV-BACKEND/
├── models/             # Mongoose model (Report.js)
├── routes/             # Express route handlers
│   ├── evData.js       # GET /api/ev-data
│   ├── mlModels.js     # GET /api/ml-models
│   └── upload.js       # POST /reports/upload, GET /reports/view
├── uploads/            # Uploaded HTML report files
├── .env                # MONGO_URI goes here
├── Dockerfile          # Docker config
├── server.js           # Express entry point
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

### 3. Add your `.env` file

Create a `.env` file in the root with:

```env
MONGO_URI=mongodb+srv://<your-uri>
```

### 4. Start the server

```bash
node server.js
```

Server runs on [http://localhost:5000](http://localhost:3000)

---

## 📂 Docker

### Build image

```bash
docker build -t blazhe/smartcharge-backend:latest .
```

### Run container

```bash
docker run -p 3000:3000 \
  -e MONGO_URI="mongodb+srv://..." \
  blazhe/smartcharge-backend:latest
```

---

## 🔗 API Endpoints

* `GET /api/ev-data` → Returns latest station availability
* `GET /api/ml-models` → Returns MLflow-extracted model info
* `POST /reports/upload` → Uploads drift/expectation HTML reports
* `GET /reports/view/:id` → Fetches HTML string for a report
* `GET /reports/raw/:id` → Returns HTML as `text/html`
* `GET /reports/list` → Lists all uploaded reports

---

## 📍 Deployment

* Backend deployed via **Render** or Docker
* MongoDB Atlas cloud-hosted instance used

---

## 👨‍💻 Author

Blazhe Manev

---

