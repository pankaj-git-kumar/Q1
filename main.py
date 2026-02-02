from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json

app = FastAPI()

# Enable CORS for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load your telemetry bundle once on startup
df = pd.read_json("telemetry_data.json") 

@app.post("/metrics")
async def get_metrics(request: Request):
    params = await request.json()
    regions = params.get("regions", [])
    threshold = params.get("threshold_ms", 180)
    
    results = {}

    for region in regions:
        # Filter data for the specific region
        region_df = df[df['region'] == region]
        
        if region_df.empty:
            continue

        # Calculate metrics
        avg_latency = region_df['latency'].mean()
        p95_latency = region_df['latency'].quantile(0.95)
        avg_uptime = region_df['uptime'].mean()
        breaches = int((region_df['latency'] > threshold).sum())

        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 4),
            "breaches": breaches
        }

    return results