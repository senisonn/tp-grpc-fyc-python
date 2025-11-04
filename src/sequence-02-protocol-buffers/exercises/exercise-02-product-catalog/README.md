# Exercise 02: Product Catalog

## Objective
Create a Protocol Buffers schema for an e-commerce product catalog using collections (repeated fields and maps).

## Duration
20-25 minutes

## Learning Goals
- Use repeated fields for lists
- Use map fields for key-value pairs
- Work with nested messages
- Model real-world data structures

## Task Description

Create a `product.proto` file that models an e-commerce product catalog with the following requirements:

### Product Message
Create a `Product` message with these fields:
- `id` (integer) - unique product identifier
- `name` (string) - product name
- `description` (string) - product description
- `price` (float) - product price
- `currency` (string) - currency code (e.g., "USD", "EUR")
- `in_stock` (boolean) - availability status
- `stock_quantity` (integer) - number of items in stock
- `categories` (repeated string) - list of category names
- `tags` (repeated string) - list of product tags
- `attributes` (map<string, string>) - custom attributes (e.g., "color" -> "red")
- `images` (repeated string) - list of image URLs

### Category Message
Create a `Category` message with:
- `id` (integer) - category identifier
- `name` (string) - category name
- `parent_id` (integer) - parent category ID (0 if root)
- `product_count` (integer) - number of products in category

### ProductCatalog Message
Create a `ProductCatalog` message with:
- `products` (repeated Product) - list of all products
- `categories` (repeated Category) - list of all categories
- `metadata` (map<string, string>) - catalog metadata

### Requirements
1. Use `proto3` syntax
2. Use appropriate types for each field
3. Use repeated for lists
4. Use maps for flexible key-value data
5. Add documentation comments

## Steps

1. **Create the proto file:**
   ```bash
   touch product.proto
   ```

2. **Define your messages:**
   - Start with `syntax = "proto3";`
   - Define smaller messages first (Category)
   - Then define Product
   - Finally define ProductCatalog

3. **Compile:**
   ```bash
   python -m grpc_tools.protoc \
     --proto_path=. \
     --python_out=. \
     product.proto
   ```

4. **Test your schema:**
   ```python
   from product_pb2 import Product, Category, ProductCatalog

   # Create a product
   product = Product()
   product.id = 1
   product.name = "Gaming Laptop"
   product.description = "High-performance laptop"
   product.price = 1299.99
   product.currency = "USD"
   product.in_stock = True
   product.stock_quantity = 15

   # Add categories
   product.categories.extend(["Electronics", "Computers", "Gaming"])

   # Add tags
   product.tags.extend(["gaming", "laptop", "high-performance"])

   # Add attributes
   product.attributes["brand"] = "TechCorp"
   product.attributes["color"] = "Black"
   product.attributes["ram"] = "16GB"
   product.attributes["storage"] = "512GB SSD"

   # Add images
   product.images.extend([
       "https://example.com/image1.jpg",
       "https://example.com/image2.jpg"
   ])

   print(f"Product: {product.name}")
   print(f"Price: {product.price} {product.currency}")
   print(f"Categories: {', '.join(product.categories)}")
   print(f"Attributes: {dict(product.attributes)}")
   ```

## Tips

- Use `float` for price (or consider using an integer for cents)
- Use `repeated string` for lists of text items
- Use `map<string, string>` for flexible attributes
- Think about which fields are most frequently accessed (use low field numbers)
- Add comments to explain the purpose of each field

## Validation

Your schema should:
- ✅ Compile without errors
- ✅ Include all three messages
- ✅ Use repeated fields for lists
- ✅ Use at least one map field
- ✅ Be well-documented with comments

## Bonus Challenges

1. **Add a Review message:**
   - `id`, `product_id`, `user_id`, `rating`, `comment`, `created_at`
   - Add a `reviews` field to Product

2. **Add price history:**
   - Create a `PriceHistory` message
   - Track price changes over time

3. **Add inventory tracking:**
   - Create a `Warehouse` message
   - Use a map to track stock by warehouse

## Common Errors

**Error:** `Map key type not allowed`
- Map keys can only be scalar types (no float, double, or bytes)
- Use string or int32 as keys

**Error:** `Repeated map field`
- You cannot have `repeated map<>` fields
- Use a wrapper message instead

**Error:** `Wrong type for repeated field`
- Use `.append()` for single items
- Use `.extend()` for multiple items

## Next Steps

After completing this exercise:
1. Move on to Exercise 03 (Messaging System)
2. Try the bonus challenges
3. Experiment with different map key types

Good luck!
