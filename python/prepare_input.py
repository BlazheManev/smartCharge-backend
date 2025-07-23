import sys
import numpy as np
import pickle
from io import BytesIO
from pymongo import MongoClient
import gridfs

# ✅ Step 1: Read CLI arguments
if len(sys.argv) != 3:
    print("ERROR_BAD_ARGS")
    sys.exit(1)

station_id = sys.argv[1]
window_size = int(sys.argv[2])

# ✅ Step 2: Connect to MongoDB
MONGO_URI = "mongodb+srv://blazhe:Feri123feri@cluster0.j4co85k.mongodb.net/EV-AI?retryWrites=true&w=majority"
try:
    client = MongoClient(MONGO_URI)
    db = client.get_default_database()
    fs = gridfs.GridFS(db)
except Exception:
    print("ERROR_DB_CONNECT")
    sys.exit(1)

# ✅ Step 3: Fetch availability data
col = db["ev_station_availability"]
try:
    cursor = col.find({"station_id": station_id}).sort("timestamp", -1).limit(window_size)
    records = list(cursor)
except Exception:
    print("ERROR_DB_QUERY")
    sys.exit(1)

if not records:
    print("ERROR_NO_DATA")
    sys.exit(1)

records.reverse()
available = [rec["available"] for rec in records]

# ✅ Step 4: Pad data if not enough records
if len(available) < window_size:
    first_value = available[0]
    padding = [first_value] * (window_size - len(available))
    available = padding + available  # pad at start

available = np.array(available).reshape(-1, 1)

# ✅ Step 5: Load pipeline from GridFS
pipeline_filename = f"pipeline_ev_{station_id}.pkl"
pipeline_file = fs.find_one({"filename": pipeline_filename})

if not pipeline_file:
    print("ERROR_PIPELINE_NOT_FOUND")
    sys.exit(1)

try:
    pipeline_data = pipeline_file.read()
    pipeline = pickle.load(BytesIO(pipeline_data))
except Exception:
    print("ERROR_PIPELINE_LOAD")
    sys.exit(1)

# ✅ Step 6: Transform input
try:
    X, _ = pipeline.transform(available)
except Exception:
    print("ERROR_PIPELINE_FAILED")
    sys.exit(1)

# ✅ Step 7: Output last transformed row (as CSV string)
input_array = X[-1].flatten()
print(",".join(str(x) for x in input_array))
