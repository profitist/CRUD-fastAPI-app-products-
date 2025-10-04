import uuid

from fastapi import FastAPI, Request
from loguru import logger
from fastapi.responses import JSONResponse

from app.routers import categories, products, users, reviews

app = FastAPI(
    title='FastApi Интернет-магазин',
    version='0.1.0',
)


@app.middleware('http')
async def log_middleware(request: Request, call_next):
    log_id = str(uuid.uuid4())
    with logger.contextualize(log_id=log_id):
        try:
            response = await call_next(request)
            if response.status_code in [401, 404, 402, 403]:
                logger.warning(f"Request to {request.url.path} failed")
            else:
                logger.info(f"Request to {request.url.path} succeeded")
        except Exception as e:
            logger.error(f"Request to {request.url.path} failed: {e}")
            response = JSONResponse(content={"success": False}, status_code=500)
        return response


logger.add(
    "info.log",
    format="Log: [{extra[log_id]}:{time} - {level} - {message}]",
    level="INFO", enqueue=True
)


app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(reviews.router)


@app.get("/")
async def root():
    return {"message": "Добро пожаловать в API интернет-магазина!"}
