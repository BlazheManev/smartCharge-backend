import sys
import numpy as np
import pickle
from io import BytesIO
from pymongo import MongoClient
import gridfs

# ✅ Step 1: Read CLI arguments
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

# ✅ Step 3: Fetch availability records
try:
    sys.stderr.write(f"📦 Fetching records for station: {station_id}, window: {window_size}\n")
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

# ✅ Step 4: Pad if not enough records
if len(available) < window_size:
    first_val = available[0]
    padding = [first_val] * (window_size - len(available))
    available = padding + available

available = np.array(available).reshape(-1, 1)

# ✅ Step 5: Load pipeline from GridFS
pipeline_filename = f"pipeline_ev_{station_id}.pkl"
sys.stderr.write(f"🔍 Looking for pipeline: {pipeline_filename}\n")
pipeline_file = fs.find_one({"filename": pipeline_filename})

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

# ✅ Step 7: Output last transformed row
input_array = X[-1].flatten()
print(",".join(str(x) for x in input_array))
