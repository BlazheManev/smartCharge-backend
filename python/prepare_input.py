import sys
import numpy as np
import pickle
from io import BytesIO
from pymongo import MongoClient
import gridfs

if len(sys.argv) != 3:
    sys.stderr.write("ERROR_BAD_ARGS\n")
    sys.exit(1)

station_id = sys.argv[1]
window_size = int(sys.argv[2])

# ✅ Connect to MongoDB
MONGO_URI = "mongodb+srv://blazhe:Feri123feri@cluster0.j4co85k.mongodb.net/EV-AI?retryWrites=true&w=majority"
try:
    client = MongoClient(MONGO_URI)
    db = client.get_default_database()
    fs = gridfs.GridFS(db)
except Exception as e:
    sys.stderr.write(f"ERROR_DB_CONNECT: {e}\n")
    sys.exit(1)

# ✅ Fetch availability data
col = db["ev_station_availability"]
try:
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
if len(available) < window_size:
    padding = [available[0]] * (window_size - len(available))
    available = padding + available

available = np.array(available).reshape(-1, 1)

# ✅ Find pipeline in GridFS by metadata
pipeline_file = fs.find_one({
    "filename": {"$regex": r"^pipeline_ev_.*\.pkl$"},
    "metadata.station_id": station_id
})

if not pipeline_file:
    sys.stderr.write(f"ERROR_MODEL_NOT_FOUND for station: {station_id}\n")
    sys.exit(1)

try:
    pipeline = pickle.load(BytesIO(pipeline_file.read()))
    X, _ = pipeline.transform(available)
except Exception as e:
    sys.stderr.write(f"ERROR_PIPELINE_FAILED: {e}\n")
    sys.exit(1)

input_array = X[-1].flatten()
print(",".join(str(x) for x in input_array))
