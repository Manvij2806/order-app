from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from routers import products, orders, auth
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    products.seed_products(db)
    db.close()
    print("\n" + "="*50)
    print("API is running!")
    print("Swagger UI is available at: http://127.0.0.1:8000/docs")
    print("="*50 + "\n")
    yield

tags_metadata = [
    {"name": "Auth"},
    {"name": "Products"},
    {"name": "Cart"},
]

app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
