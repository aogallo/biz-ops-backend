from app.domain.entities.product import ProductCreate
from app.domain.entities.user import User
from app.services.product_service import ProductService


class TestProducts:
    """Test products."""

    def test_create_product(self):
        """Test creating a product."""
        product_service = ProductService(
            current_user=User(
                auth_id="auth0|test123",
                permissions=["create:product"],
            )
        )
        product_data = ProductCreate(
            name="Test Product",
            description="A test product",
            price=99.99,
            stock=10,
        )
        product = product_service.create_product(product_request=product_data)

        assert product.id is not None
        assert product.name == "Test Product"
        assert product.description == "A test product"
        assert product.price == 99.99
