from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/runs", tags=["runs"])


@router.get("/{run_id}")
async def get_run(run_id: str) -> dict[str, object]:
    raise HTTPException(status_code=404, detail="Persistent workflow traces are not implemented")
