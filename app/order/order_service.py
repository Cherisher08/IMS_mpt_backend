from app.config import database
from app.order.order_repository import OrderRepository
from app.product.product_repository import ProductRepository


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository = None,
    ):
        self.repository = order_repository
        self.product_repository = product_repository or ProductRepository(database=database)
    
    def process_purchase_products(self, purchase_products: list):
        """Process products in a purchase order. 
        If product has an ID, increment its quantity.
        If product doesn't have an ID, create a new product.
        
        Args:
            purchase_products: List of PurchaseOrderProduct objects
        """
        for product in purchase_products:
            product_id = product.id
            quantity = int(product.quantity)
            
            if product_id:
                # Product exists, increment quantity
                self.product_repository.increment_product_quantity(
                    product_id=str(product_id),
                    quantity=quantity
                )
            else:
                # New product, create it
                self.product_repository.create_product_from_purchase(
                    name=product.name,
                    product_code=product.product_code,
                    category_id=str(product.category.id),
                    unit_id=str(product.unit.id),
                    type_str=product.type.value,
                    rent_per_unit=float(product.rent_per_unit),
                    quantity=quantity,
                    price=float(product.price)
                )
    
    def process_purchase_products_update(self, old_products: list, new_products: list):
        """Process product quantity changes during purchase order update.
        Compare old and new products to calculate quantity deltas.
        
        Args:
            old_products: List of old product dicts from existing purchase order
            new_products: List of new PurchaseOrderProduct objects
        """
        # Create a map of old product IDs to quantities
        old_product_map = {}
        for old_product in old_products:
            product_id = str(old_product.get("_id") or old_product.get("id"))
            if product_id:
                old_product_map[product_id] = int(old_product.get("quantity", 0))
        
        # Process new products
        for new_product in new_products:
            product_id = str(new_product.id) if new_product.id else None
            new_quantity = int(new_product.quantity)
            
            if product_id:
                old_quantity = old_product_map.get(product_id, 0)
                quantity_delta = new_quantity - old_quantity
                
                if quantity_delta > 0:
                    # Increase quantity
                    self.product_repository.increment_product_quantity(
                        product_id=product_id,
                        quantity=quantity_delta
                    )
                elif quantity_delta < 0:
                    # Decrease quantity
                    self.product_repository.increment_product_quantity(
                        product_id=product_id,
                        quantity=quantity_delta
                    )
                # If delta is 0, no change needed
            else:
                # New product, create it
                self.product_repository.create_product_from_purchase(
                    name=new_product.name,
                    product_code=new_product.product_code,
                    category_id=str(new_product.category.id),
                    unit_id=str(new_product.unit.id),
                    type_str=new_product.type.value,
                    rent_per_unit=float(new_product.rent_per_unit),
                    quantity=new_quantity,
                    price=float(new_product.price)
                )


def get_order_service():
    order_repository = OrderRepository(database=database)
    svc = OrderService(
        order_repository=order_repository,
    )
    return svc
