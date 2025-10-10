from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import auth, customers, products, employees, suppliers, prescriptions, batches, sales, reports, purchases

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pharmacy Management System API",
    description="API for managing pharmacy operations including inventory, sales, and prescriptions",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

 # Include routers
app.include_router(auth, prefix="/api", tags=["auth"])
app.include_router(customers, prefix="/api", tags=["customers"])
app.include_router(products, prefix="/api", tags=["products"])
app.include_router(employees, prefix="/api", tags=["employees"])
app.include_router(suppliers, prefix="/api", tags=["suppliers"])
app.include_router(prescriptions, prefix="/api", tags=["prescriptions"])
app.include_router(batches, prefix="/api", tags=["batches"])
app.include_router(sales, prefix="/api", tags=["sales"])
app.include_router(reports, prefix="/api", tags=["reports"])
app.include_router(purchases, prefix="/api", tags=["purchases"])