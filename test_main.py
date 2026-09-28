import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

# Use an in-memory SQLite database for fast, isolated testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop them afterward."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_product():
    """Test successful product creation."""
    response = client.post(
        "/products/",
        json={"name": "Wireless Mouse", "description": "Ergonomic mouse", "price": 25.50, "stock": 10}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Wireless Mouse"
    assert "id" in data

def test_get_products():
    """Test retrieving product listings with pagination."""
    client.post(
        "/products/",
        json={"name": "Mechanical Keyboard", "description": "RGB switches", "price": 75.0, "stock": 5}
    )
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Mechanical Keyboard"

def test_create_order_success():
    """Test placing an order successfully and verifying stock deduction."""
    # Step 1: Create a product
    prod_resp = client.post(
        "/products/",
        json={"name": "Gaming Monitor", "description": "144Hz 1080p", "price": 200.0, "stock": 4}
    )
    prod_id = prod_resp.json()["id"]

    # Step 2: Place order for 2 units
    response = client.post(
        "/orders/",
        json={"product_id": prod_id, "quantity": 2}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["total_price"] == 400.0
    assert data["status"] == "Confirmed"

def test_create_order_insufficient_stock():
    """Test ordering more than available stock raises a 400 error."""
    prod_resp = client.post(
        "/products/",
        json={"name": "USB-C Hub", "description": "Multiport adapter", "price": 30.0, "stock": 1}
    )
    prod_id = prod_resp.json()["id"]

    # Try ordering 3 units when stock is only 1
    response = client.post(
        "/orders/",
        json={"product_id": prod_id, "quantity": 3}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient stock available"