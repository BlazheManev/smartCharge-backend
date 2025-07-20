# python/prepare_input.py

import sys
import pymongo
import gridfs
import numpy as np
import joblib
import pickle
from io import BytesIO

# ✅ Step 1: Read CLI arguments
if len(sys.argv) != 3:
    print("ERROR_BAD_ARGS")
    sys.exit(1)

station_id = sys.argv[1]
window_size = int(sys.argv[2])

# ✅ Step 2: Connect to MongoDB
MONGO_URI = "mongodb+srv://blazhe:Feri123feri@cluster0.j4co85k.mongodb.net/EV-AI?retryWrites=true&w=majority"
client = pymongo.MongoClient(MONGO_URI)
db = client["EV-AI"]
fs = gridfs.GridFS(db)

# ✅ Step 3: Get last `window_size` availability records
col = db["ev_station_availability"]
cursor = col.find({"station_id": station_id}).sort("timestamp", -1).limit(window_size)
records = list(cursor)

if len(records) < window_size:
    print("ERROR_NOT_ENOUGH_DATA")
    sys.exit(1)

records.reverse()  # oldest → newest
available = np.array([rec["available"] for rec in records]).reshape(-1, 1)

# ✅ Step 4: Load pipeline from GridFS
pipeline_filename = f"pipeline_ev_{station_id}.pkl"
pipeline_file = fs.find_one({"filename": pipeline_filename})

if not pipeline_file:
    print("ERROR_PIPELINE_NOT_FOUND")
    sys.exit(1)

pipeline_data = pipeline_file.read()
pipeline = pickle.load(BytesIO(pipeline_data))

# ✅ Step 5: Transform data using pipeline
try:
    X, _ = pipeline.transform(available)
except Exception as e:
    print("ERROR_PIPELINE_FAILED")
    sys.exit(1)

# ✅ Step 6: Output ONNX-ready input
input_array = X[-1].flatten()
print(",".join(str(x) for x in input_array))
