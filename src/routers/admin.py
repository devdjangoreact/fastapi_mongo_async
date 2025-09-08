from fastapi import APIRouter, Depends, HTTPException

from ..core.auth import get_api_key
from ..core.logger import log
from ..services.scheduler import scheduler_service

router = APIRouter()


@router.post("/parse/products")
async def force_parse_products(api_key: str = Depends(get_api_key)):
    """Force immediate product parsing"""
    try:
        await scheduler_service.force_parse_products()
        return {"message": "Product parsing started successfully"}
    except Exception as e:
        log.error(f"Failed to force product parsing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse/news")
async def force_parse_news(api_key: str = Depends(get_api_key)):
    """Force immediate news parsing"""
    try:
        await scheduler_service.force_parse_news()
        return {"message": "News parsing started successfully"}
    except Exception as e:
        log.error(f"Failed to force news parsing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduler/status")
async def get_scheduler_status(api_key: str = Depends(get_api_key)):
    """Get scheduler status"""
    return {
        "running": scheduler_service.scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "next_run_time": job.next_run_time,
                "trigger": str(job.trigger),
            }
            for job in scheduler_service.scheduler.get_jobs()
        ],
    }
