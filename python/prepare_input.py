# python/prepare_input.py

import sys
import pymongo
import numpy as np
import joblib
import pickle
from io import BytesIO

# 1. Read args
if len(sys.argv) != 3:
    print("ERROR_BAD_ARGS")
    sys.exit(1)

station_id = sys.argv[1]
window_size = int(sys.argv[2])

# 2. Connect to MongoDB
MONGO_URI = "mongodb+srv://blazhe:Feri123feri@cluster0.j4co85k.mongodb.net/EV-AI?retryWrites=true&w=majority"
client = pymongo.MongoClient(MONGO_URI)
db = client["EV-AI"]
fs = pymongo.database.GridFS(db)

# 3. Get last N availability entries for the station
col = db["ev_station_availability"]
cursor = col.find({"station_id": station_id}).sort("timestamp", -1).limit(window_size)
records = list(cursor)

if len(records) < window_size:
    print("ERROR_NOT_ENOUGH_DATA")
    sys.exit(1)

# 4. Extract and sort chronologically
records.reverse()  # sort oldest → newest
available = np.array([rec["available"] for rec in records]).reshape(-1, 1)  # shape: (window_size, 1)

# 5. Load pipeline from GridFS
pipeline_filename = f"pipeline_ev_{station_id}.pkl"
pipeline_file = fs.find_one({"filename": pipeline_filename})

if not pipeline_file:
    print("ERROR_PIPELINE_NOT_FOUND")
    sys.exit(1)

pipeline_data = pipeline_file.read()
pipeline = pickle.load(BytesIO(pipeline_data))

# 6. Run pipeline transform
try:
    X, _ = pipeline.transform(available)
except Exception as e:
    print("ERROR_PIPELINE_FAILED")
    sys.exit(1)

# 7. Return last input window as comma-separated floats
input_array = X[-1].flatten()
output_str = ",".join(str(x) for x in input_array)
print(output_str)
