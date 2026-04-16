from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List
from .lineage_tracer import tracer
from .hash_chain_ledger import ledger

app = FastAPI(title="Sovereign Provenance Events API")

@app.get("/events/trace/{trace_id}")
async def get_trace_history(trace_id: str) -> Dict[str, Any]:
    """Retrieve the complete ordered trace history for a given trace_id."""
    try:
        result = tracer.get_trace_history(trace_id)
        if not result["events"]:
            raise HTTPException(status_code=404, detail=f"No events found for trace_id: {trace_id}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/recent")
async def get_recent_traces(limit: int = 10) -> List[Dict[str, Any]]:
    """Get the most recent traces."""
    try:
        return tracer.get_recent_traces(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/verify")
async def verify_chain_integrity() -> Dict[str, bool]:
    """Verify the integrity of the entire provenance chain."""
    try:
        is_valid = ledger.verify_chain_integrity()
        return {"chain_valid": is_valid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/stats")
async def get_chain_stats() -> Dict[str, Any]:
    """Get statistics about the provenance chain."""
    try:
        length = ledger.get_chain_length()
        return {
            "chain_length": length,
            "total_events": length - 1  # Subtract genesis block
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)