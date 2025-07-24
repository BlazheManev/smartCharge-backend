import sys
import json
import joblib
import gridfs
import onnxruntime as ort
from pymongo import MongoClient
from datetime import datetime
from bson import json_util
import pandas as pd
from io import BytesIO

# ——— CONFIG —————————————————————————————
MONGO_URI = "mongodb+srv://blazhe:Feri123feri@cluster0.j4co85k.mongodb.net/EV-AI?retryWrites=true&w=majority"
DB_NAME = "EV-AI"
COLL_AVAIL = "ev_station_availability"

# ——— HELPERS —————————————————————————————
def fetch_recent_data(db, station_id, window_size):
    col = db[COLL_AVAIL]
    cursor = col.find({
        "station_id": station_id
    }).sort("fetched_at", -1).limit(window_size)
    
    records = list(cursor)
    if len(records) < window_size:
        sys.stderr.write(f"❌ Not enough data. Found: {len(records)}\n")
        sys.exit("ERROR_NO_DATA")

    records.reverse() 
    df = pd.DataFrame([{
        "timestamp": rec["fetched_at"],
        "available": rec.get("available", rec.get("availability", [{}])[0] if isinstance(rec.get("availability"), list) else 0)
    } for rec in records])

    return df

def load_from_gridfs(fs, filename):
    file_doc = fs.find_one({"filename": filename})
    if not file_doc:
        sys.stderr.write(f"❌ {filename} not found in GridFS\n")
        sys.exit("ERROR_MODEL_NOT_FOUND")
    return BytesIO(file_doc.read())

# ——— MAIN —————————————————————————————————————
def main():
    if len(sys.argv) != 4:
        sys.stderr.write("Usage: python prepare_input.py <station_id> <window_size> <timestamp>\n")
        sys.exit(1)

    station_id, window_size_str, ts_str = sys.argv[1], sys.argv[2], sys.argv[3]
    try:
        window_size = int(window_size_str)
        timestamp = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except Exception as e:
        sys.stderr.write(f"❌ Bad arguments: {e}\n")
        sys.exit(1)

    sys.stderr.write(f"📦 Predicting for station={station_id}, time={timestamp}, window={window_size}\n")

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    fs = gridfs.GridFS(db)

    pipe_name = f"pipeline_ev_{station_id}.pkl"
    model_name = f"model_ev_{station_id}.onnx"

    pipeline = joblib.load(load_from_gridfs(fs, pipe_name))
    sess = ort.InferenceSession(load_from_gridfs(fs, model_name).getvalue())

    df = fetch_recent_data(db, station_id, window_size)
    X, _ = pipeline.transform(df[["available"]])

    input_name = sess.get_inputs()[0].name
    pred = sess.run(None, {input_name: X.astype("float32")})[0]

    sys.stdout.write(json.dumps({
        "station_id": station_id,
        "timestamp": timestamp.isoformat(),
        "predicted": float(pred[-1][0])
    }, default=json_util.default))

if __name__ == "__main__":
    main()
