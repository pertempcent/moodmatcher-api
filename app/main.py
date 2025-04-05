import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from app.api.v1.routes import router as api_v1_router

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',  
    handlers=[
        logging.FileHandler("app.log"),  
        logging.StreamHandler() 
    ]
)

app = FastAPI()

limiter = Limiter(key_func=lambda request: request.client.host)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for evaluation — restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RateLimitExceeded)
async def ratelimit_error(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded, please try again later."}
    )

app.include_router(api_v1_router, prefix="/api/v1")
