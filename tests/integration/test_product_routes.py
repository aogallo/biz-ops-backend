"""Integration tests for product routes."""

import pytest
from fastapi.testclient import TestClient

from app.internal.product.entity import Product


@pytest.mark.integration
class TestProductRoutes:
    """Integration tests for /products endpoints."""

    API_PREFIX = "/api/v1"

    def test_read_products_unauthorized(self, client: TestClient):
        """Test that reading products without auth token fails."""
        # client fixture has NO auth - should get 403
        response = client.get(f"{self.API_PREFIX}/products")

        print(f"\nUnauthorized test - Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]

    def test_create_product_success(
        self,
        authenticated_client: TestClient,
    ):
        """Test creating a product with valid authentication."""
        # Use a unique name for each test run
        import time

        unique_name = f"Test Laptop {time.time()}"

        # Create a product via API
        product_data = {
            "name": unique_name,
            "description": "A test laptop product",
            "price": 1299.99,
            "stock": 5,
        }

        response = authenticated_client.post(
            f"{self.API_PREFIX}/products",
            json=product_data,
        )

        print(f"\nCreate product - Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}\n"
            f"Response: {response.text}"
        )

        data = response.json()
        assert data["name"] == unique_name
        assert data["price"] == 1299.99
        assert data["stock"] == 5
        assert "id" in data

    def test_read_products_success(
        self,
        authenticated_client: TestClient,
        engine,  # Need engine to create product
    ):
        """Test reading products with valid authentication."""
        # Create a product directly in the database
        from sqlmodel import Session

        with Session(engine) as session:
            product = Product(
                name="Test Product",
                description="A test product",
                price=99.99,
                stock=10,
                created_by="auth0|test123",
            )
            session.add(product)
            session.commit()
            session.refresh(product)

        # Now read products via API
        response = authenticated_client.get(f"{self.API_PREFIX}/products")

        print(f"\nAuthenticated test - Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}\n"
            f"Response: {response.text}"
        )

        data = response.json()

        # Verify response structure
        assert "products" in data, (
            f"Expected 'products' key in response: {data}"
        )
        assert "pagination" in data, (
            f"Expected 'pagination' key in response: {data}"
        )

        # Verify pagination metadata
        pagination = data["pagination"]
        assert pagination["total"] >= 1
        assert pagination["pageSize"] == 10
        assert pagination["pageIndex"] == 0

        # Verify product data
        products = data["products"]
        assert isinstance(products, list)
        assert len(products) >= 1, (
            f"Expected at least 1 product, got {len(products)}"
        )

        # Verify product structure (check any product in the list)
        first_product = products[0]
        assert "name" in first_product
        assert "price" in first_product
        assert "stock" in first_product
        assert isinstance(first_product["name"], str)
        assert isinstance(first_product["price"], int | float)
        assert isinstance(first_product["stock"], int)
