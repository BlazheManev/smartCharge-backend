import sys
import numpy as np
import pickle
from io import BytesIO
from pymongo import MongoClient
import gridfs

# ✅ Step 1: Parse CLI arguments
if len(sys.argv) != 3:
    sys.stderr.write("ERROR_BAD_ARGS\n")
    sys.exit(1)

station_id = sys.argv[1]
window_size = int(sys.argv[2])

# ✅ Step 2: Connect to MongoDB
MONGO_URI = "mongodb+srv://blazhe:Feri123feri@cluster0.j4co85k.mongodb.net/EV-AI?retryWrites=true&w=majority"
try:
    client = MongoClient(MONGO_URI)
    db = client.get_default_database()
    fs = gridfs.GridFS(db)
except Exception as e:
    sys.stderr.write(f"ERROR_DB_CONNECT: {e}\n")
    sys.exit(1)

# ✅ Step 3: Look up the pipeline filename from ml_models
model_doc = db.ml_models.find_one({"params.station": station_id})
if not model_doc:
    sys.stderr.write(f"ERROR_MODEL_NOT_FOUND for station: {station_id}\n")
    sys.exit(1)

filename = f"pipeline_ev_{model_doc['params']['station']}.pkl"
sys.stderr.write(f"📁 Loading pipeline: {filename}\n")

# ✅ Step 4: Get availability records
try:
    col = db["ev_station_availability"]
    cursor = col.find({"station_id": station_id}).sort("timestamp", -1).limit(window_size)
    records = list(cursor)
except Exception as e:
    sys.stderr.write(f"ERROR_DB_QUERY: {e}\n")
    sys.exit(1)

if not records:
    sys.stderr.write("ERROR_NO_DATA\n")
    sys.exit(1)

records.reverse()
available = [rec["available"] for rec in records]

# ✅ Pad if too few records
if len(available) < window_size:
    first_val = available[0]
    padding = [first_val] * (window_size - len(available))
    available = padding + available

available = np.array(available).reshape(-1, 1)

# ✅ Step 5: Load pipeline from GridFS
pipeline_file = fs.find_one({"filename": filename})
if not pipeline_file:
    sys.stderr.write("ERROR_PIPELINE_NOT_FOUND\n")
    sys.exit(1)

try:
    pipeline_data = pipeline_file.read()
    pipeline = pickle.load(BytesIO(pipeline_data))
except Exception as e:
    sys.stderr.write(f"ERROR_PIPELINE_LOAD: {e}\n")
    sys.exit(1)

# ✅ Step 6: Transform input
try:
    X, _ = pipeline.transform(available)
except Exception as e:
    sys.stderr.write(f"ERROR_PIPELINE_FAILED: {e}\n")
    sys.exit(1)

# ✅ Step 7: Output ONNX-ready input
input_array = X[-1].flatten()
print(",".join(str(x) for x in input_array))
