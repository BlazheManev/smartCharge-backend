import sys
import numpy as np
import pickle
from io import BytesIO
from pymongo import MongoClient
import gridfs

# ✅ Step 1: Parse CLI args
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

# ✅ Step 3: Look up ml_models for pipeline match
model_doc = db.ml_models.find_one({"params.station": station_id})
if not model_doc:
    sys.stderr.write(f"ERROR_MODEL_NOT_FOUND for station: {station_id}\n")
    sys.exit(1)

# Extract actual pipeline filename from GridFS
pipeline_file = None
pipeline_cursor = fs.find({})
for file in pipeline_cursor:
    if file.filename.endswith(".pkl") and model_doc["run_id"] in file.filename:
        pipeline_file = file
        break

if not pipeline_file:
    sys.stderr.write("ERROR_PIPELINE_NOT_FOUND\n")
    sys.exit(1)

sys.stderr.write(f"✅ Using pipeline: {pipeline_file.filename}\n")

# ✅ Step 4: Fetch station availability data
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

# ✅ Pad if too short
if len(available) < window_size:
    padding = [available[0]] * (window_size - len(available))
    available = padding + available

available = np.array(available).reshape(-1, 1)

# ✅ Step 5: Load and apply pipeline
try:
    pipeline = pickle.load(BytesIO(pipeline_file.read()))
    X, _ = pipeline.transform(available)
except Exception as e:
    sys.stderr.write(f"ERROR_PIPELINE_FAILED: {e}\n")
    sys.exit(1)

# ✅ Step 6: Output final input
input_array = X[-1].flatten()
print(",".join(str(x) for x in input_array))
