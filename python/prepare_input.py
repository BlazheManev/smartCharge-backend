# python/prepare_input.py

import sys
import numpy as np
import pickle
from io import BytesIO
from pymongo import MongoClient
import gridfs  # ✅ same as your example

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
    fs = gridfs.GridFS(db)  # ✅ THIS is the correct way
except Exception:
    print("ERROR_DB_CONNECT")
    sys.exit(1)

# ✅ Step 3: Get last `window_size` availability records
col = db["ev_station_availability"]
try:
    cursor = col.find({"station_id": station_id}).sort("timestamp", -1).limit(window_size)
    records = list(cursor)
except Exception:
    print("ERROR_DB_QUERY")
    sys.exit(1)

#if len(records) < window_size:
    #print("ERROR_NOT_ENOUGH_DATA")
 #   sys.exit(1)

records.reverse()
available = np.array([rec["available"] for rec in records]).reshape(-1, 1)

# ✅ Step 4: Load pipeline from GridFS
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

# ✅ Step 5: Transform data using pipeline
try:
    X, _ = pipeline.transform(available)
except Exception:
    print("ERROR_PIPELINE_FAILED")
    sys.exit(1)

# ✅ Step 6: Output ONNX-ready input
input_array = X[-1].flatten()
print(",".join(str(x) for x in input_array))
