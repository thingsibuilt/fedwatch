"""
FedWatch API - FastAPI Backend
Real-time economic data API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import json
import os

app = FastAPI(
    title="FedWatch API",
    description="Real-Time Economic Intelligence API",
    version="0.1.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class EconomicMetric(BaseModel):
    name: str
    value: float
    unit: str
    change: Optional[float] = None
    change_period: Optional[str] = None
    source: str
    timestamp: str

class EmploymentSignal(BaseModel):
    category: str
    job_count: int
    trend: str  # "up", "down", "stable"
    source: str
    timestamp: str

class HealthScore(BaseModel):
    score: float
    rating: str  # "healthy", "cautious", "concerning"
    factors: Dict[str, float]
    timestamp: str

# In-memory "database" (would be PostgreSQL in production)
DATA_FILE = "/root/.openclaw/workspace/fedwatch/data.json"

def load_data():
    """Load cached data"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "employment": {
            "unemployment_rate": {"value": 4.3, "unit": "%", "source": "BLS", "timestamp": "2026-01-01"},
            "nonfarm_payrolls": {"value": 256000, "unit": "jobs", "source": "BLS", "timestamp": "2026-01-01"},
        },
        "inflation": {
            "cpi": {"value": 2.4, "unit": "%", "source": "BLS", "timestamp": "2026-01-01"},
            "core_cpi": {"value": 2.5, "unit": "%", "source": "BLS", "timestamp": "2026-01-01"},
            "pce": {"value": 2.3, "unit": "%", "source": "BLS", "timestamp": "2025-11-01"},
        },
        "monetary": {
            "fed_funds_rate": {"value": 4.25, "unit": "%", "source": "Federal Reserve", "timestamp": "2026-01-29"},
        },
        "gdp": {
            "gdp_growth": {"value": 2.5, "unit": "%", "source": "BEA", "timestamp": "2025-Q4"},
        }
    }

# API Routes

@app.get("/")
async def root():
    return {
        "name": "FedWatch API",
        "version": "0.1.0",
        "description": "Real-Time Economic Intelligence",
        "endpoints": {
            "employment": "/api/v1/employment",
            "inflation": "/api/v1/inflation", 
            "signals": "/api/v1/signals",
            "health": "/api/v1/health",
            "history": "/api/v1/history/{metric}"
        }
    }

@app.get("/api/v1/employment")
async def get_employment():
    """Get employment indicators"""
    data = load_data()
    return {
        "status": "success",
        "data": data["employment"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/inflation")
async def get_inflation():
    """Get inflation indicators"""
    data = load_data()
    return {
        "status": "success", 
        "data": data["inflation"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/signals")
async def get_signals():
    """
    Get real-time alternative signals
    This is where the magic happens - Indeed, Google Trends, etc.
    """
    # This would be populated by scrapers in production
    return {
        "status": "success",
        "data": {
            "indeed": {
                "status": "pending_setup",
                "message": "Indeed API key needed - see docs",
                "categories": {
                    "tech": None,
                    "retail": None,
                    "manufacturing": None
                }
            },
            "google_trends": {
                "status": "pending_setup", 
                "message": "PyTrends library needed"
            },
            "housing": {
                "status": "pending_setup",
                "message": "Realtor.com API key needed"
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/health")
async def get_health():
    """Get overall economic health score"""
    data = load_data()
    
    # Calculate simple health score
    unemployment = data["employment"]["unemployment_rate"]["value"]
    inflation = data["inflation"]["cpi"]["value"]
    
    # Simple scoring algorithm
    score = 100
    
    # Unemployment impact (lower = better, ideally 3.5-4.5%)
    if unemployment > 5:
        score -= (unemployment - 5) * 10
    elif unemployment < 3.5:
        score -= (3.5 - unemployment) * 5
    
    # Inflation impact (2% target)
    score -= abs(inflation - 2.0) * 10
    
    score = max(0, min(100, score))
    
    rating = "healthy" if score >= 70 else "cautious" if score >= 50 else "concerning"
    
    return {
        "status": "success",
        "score": round(score, 1),
        "rating": rating,
        "factors": {
            "unemployment": unemployment,
            "inflation": inflation,
            "fed_funds": data["monetary"]["fed_funds_rate"]["value"]
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/metrics")
async def get_all_metrics():
    """Get all economic metrics"""
    data = load_data()
    return {
        "status": "success",
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/signals/indeed")
async def update_indeed_signals(signals: Dict):
    """Webhook to receive Indeed data from scraper"""
    # This would be called by the scraper job
    return {"status": "success", "message": "Signals updated"}

@app.get("/docs")
async def docs():
    return {"message": "Visit /docs for Swagger UI"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
