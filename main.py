from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import engine, get_db

# Create database tables automatically on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Store Inventory & Order Management API",
    version="1.0.0",
    description="A high-performance REST API backend built with FastAPI and SQLAlchemy."
)

# --- Pydantic Schemas for Request/Response Validation ---
class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int

class ProductResponse(ProductCreate):
    id: int
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    product_id: int
    quantity: int

class OrderResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    total_price: float
    status: str
    class Config:
        from_attributes = True

# --- Product Endpoints ---
@app.post("/products/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Add a new product to the inventory catalog."""
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=list[ProductResponse])
def get_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Retrieve all products with pagination support."""
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

# --- Order Endpoints ---
@app.post("/orders/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Place an order, verifying stock availability and calculating total price."""
    product = db.query(models.Product).filter(models.Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < order.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock available")
    
    # Deduct stock and calculate total cost
    product.stock -= order.quantity
    total = product.price * order.quantity
    
    new_order = models.Order(
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=total,
        status="Confirmed"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@app.get("/orders/", response_model=list[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    """Retrieve all customer orders."""
    return db.query(models.Order).all()