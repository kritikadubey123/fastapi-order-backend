# Store Inventory & Order Management API

A high-performance REST API backend built with FastAPI and SQLAlchemy for managing retail inventory and processing customer orders. The application is fully containerized using Docker Compose for seamless, reproducible deployments across any environment.

## 🚀 Tech Stack
* **Framework:** FastAPI (Python 3.11)
* **ORM & Database:** SQLAlchemy, SQLite
* **Testing:** Pytest
* **DevOps:** Docker, Docker Compose
* **Documentation:** Swagger UI / OpenAPI (Auto-generated)

## ✨ Features
* **Inventory Management:** Create and retrieve product listings with real-time stock tracking.
* **Order Processing:** Place orders with automated inventory deduction and insufficient stock validation.
* **Containerized Infrastructure:** Isolated environment setup using Docker, ensuring zero local dependency conflicts.
* **Automated Testing:** Endpoint and business logic validation using Pytest.

## 🐳 Quick Start (Docker)

The easiest way to run this API is via Docker. Ensure Docker Desktop is running on your machine.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/fastapi-order-backend.git](https://github.com/yourusername/fastapi-order-backend.git)
   cd fastapi-order-backend