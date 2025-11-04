#!/usr/bin/env python3
"""
Example demonstrating collections in Protocol Buffers (repeated fields and maps)

This script shows:
1. How to use repeated fields (lists)
2. How to use map fields (key-value pairs)
3. Operations on collections
"""

import subprocess
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def compile_protos():
    """Compile both proto files"""
    print("📦 Compiling proto files...\n")

    protos = ["repeated_fields.proto", "maps_example.proto"]

    for proto in protos:
        result = subprocess.run([
            "python", "-m", "grpc_tools.protoc",
            "--proto_path=.",
            "--python_out=.",
            proto
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))

        if result.returncode != 0:
            print(f"❌ Failed to compile {proto}")
            print(result.stderr)
            sys.exit(1)
        print(f"✅ Compiled {proto}")

    print()

def test_repeated_fields():
    """Test repeated fields (lists)"""
    print("=" * 60)
    print("Testing Repeated Fields (Lists)")
    print("=" * 60 + "\n")

    import repeated_fields_pb2 as rf

    # Create user with multiple emails
    user = rf.User()
    user.id = 1
    user.name = "Alice"

    # Add emails one by one
    user.emails.append("alice@example.com")
    user.emails.append("alice@work.com")
    user.emails.append("alice.personal@gmail.com")

    # Add phone numbers with extend
    user.phone_numbers.extend(["+1-555-0100", "+1-555-0101"])

    print("📧 User Emails:")
    for i, email in enumerate(user.emails, 1):
        print(f"   {i}. {email}")

    print(f"\n📱 User Phone Numbers:")
    for i, phone in enumerate(user.phone_numbers, 1):
        print(f"   {i}. {phone}")

    # Shopping cart with products
    print("\n" + "-" * 60)
    cart = rf.ShoppingCart()
    cart.user_id = 1

    # Add products
    product1 = cart.products.add()
    product1.id = 101
    product1.name = "Laptop"
    product1.price = 999.99
    product1.quantity = 1

    product2 = cart.products.add()
    product2.id = 102
    product2.name = "Mouse"
    product2.price = 25.50
    product2.quantity = 2

    # Can also add product IDs
    cart.product_ids.extend([101, 102])

    print("\n🛒 Shopping Cart:")
    for product in cart.products:
        print(f"   - {product.name}: ${product.price} x{product.quantity}")

    cart.total = sum(p.price * p.quantity for p in cart.products)
    print(f"   Total: ${cart.total:.2f}")

    # Blog post with tags and comments
    print("\n" + "-" * 60)
    post = rf.BlogPost()
    post.id = 1
    post.title = "Introduction to Protocol Buffers"
    post.content = "Protocol Buffers is a great serialization format..."
    post.author = "Alice"

    # Add tags
    post.tags.extend(["protobuf", "grpc", "tutorial", "python"])

    # Add comments
    comment1 = post.comments.add()
    comment1.id = 1
    comment1.author = "Bob"
    comment1.text = "Great article!"
    comment1.timestamp = 1699000000

    comment2 = post.comments.add()
    comment2.id = 2
    comment2.author = "Charlie"
    comment2.text = "Very helpful, thanks!"
    comment2.timestamp = 1699000100

    print(f"\n📝 Blog Post: '{post.title}'")
    print(f"   Author: {post.author}")
    print(f"   Tags: {', '.join(post.tags)}")
    print(f"   Comments: {len(post.comments)}")
    for comment in post.comments:
        print(f"      - {comment.author}: {comment.text}")

    # List operations
    print("\n" + "-" * 60)
    print("\n🔧 List Operations:")
    print(f"   Length: len(user.emails) = {len(user.emails)}")
    print(f"   Access: user.emails[0] = {user.emails[0]}")
    print(f"   Slice: user.emails[:2] = {user.emails[:2]}")
    print(f"   In check: 'alice@example.com' in user.emails = {'alice@example.com' in user.emails}")

    # Clear a list
    cart.product_ids.clear()
    print(f"   After clear: len(cart.product_ids) = {len(cart.product_ids)}")

    # Delete element
    del user.emails[0]
    print(f"   After delete: user.emails = {list(user.emails)}")

    # Serialization size
    serialized = post.SerializeToString()
    print(f"\n💾 Serialized blog post: {len(serialized)} bytes")

def test_maps():
    """Test map fields"""
    print("\n" + "=" * 60)
    print("Testing Map Fields (Key-Value Pairs)")
    print("=" * 60 + "\n")

    import maps_example_pb2 as maps

    # User preferences
    prefs = maps.UserPreferences()
    prefs.user_id = "user123"

    # Add settings (string to string)
    prefs.settings["theme"] = "dark"
    prefs.settings["language"] = "en"
    prefs.settings["timezone"] = "UTC"

    # Add counters (string to int)
    prefs.counters["login_count"] = 42
    prefs.counters["posts_created"] = 15
    prefs.counters["comments"] = 128

    # Add feature flags (string to bool)
    prefs.features["beta_features"] = True
    prefs.features["notifications"] = True
    prefs.features["dark_mode"] = True

    print("⚙️  User Preferences:")
    print("   Settings:")
    for key, value in prefs.settings.items():
        print(f"      {key}: {value}")

    print("\n   Counters:")
    for key, value in prefs.counters.items():
        print(f"      {key}: {value}")

    print("\n   Features:")
    for key, value in prefs.features.items():
        print(f"      {key}: {value}")

    # Product with attributes
    print("\n" + "-" * 60)
    product = maps.Product()
    product.id = 1
    product.name = "Gaming Laptop"

    # Add attributes
    product.attributes["brand"] = "Dell"
    product.attributes["color"] = "Black"
    product.attributes["processor"] = "Intel i7"
    product.attributes["ram"] = "16GB"

    # Add dimensions
    product.dimensions["width"] = 35.5
    product.dimensions["height"] = 2.5
    product.dimensions["depth"] = 25.0
    product.dimensions["weight"] = 2.1

    # Add stock levels
    product.stock["warehouse_east"] = 50
    product.stock["warehouse_west"] = 35
    product.stock["warehouse_central"] = 100

    print(f"\n📦 Product: {product.name}")
    print("   Attributes:")
    for key, value in product.attributes.items():
        print(f"      {key}: {value}")

    print("\n   Dimensions (cm):")
    for key, value in product.dimensions.items():
        print(f"      {key}: {value}")

    print("\n   Stock:")
    for warehouse, count in product.stock.items():
        print(f"      {warehouse}: {count} units")

    # Translations
    print("\n" + "-" * 60)
    translation = maps.Translation()
    translation.key = "welcome_message"
    translation.translations["en"] = "Welcome!"
    translation.translations["es"] = "¡Bienvenido!"
    translation.translations["fr"] = "Bienvenue!"
    translation.translations["de"] = "Willkommen!"
    translation.translations["ja"] = "ようこそ!"

    print(f"\n🌍 Translation for '{translation.key}':")
    for lang, text in translation.translations.items():
        print(f"   {lang}: {text}")

    # Map operations
    print("\n" + "-" * 60)
    print("\n🔧 Map Operations:")
    print(f"   Length: len(prefs.settings) = {len(prefs.settings)}")
    print(f"   Access: prefs.settings['theme'] = {prefs.settings['theme']}")
    print(f"   Get with default: prefs.settings.get('missing', 'default') = {prefs.settings.get('missing', 'default')}")
    print(f"   In check: 'theme' in prefs.settings = {'theme' in prefs.settings}")
    print(f"   Keys: prefs.counters.keys() = {list(prefs.counters.keys())}")
    print(f"   Values: prefs.counters.values() = {list(prefs.counters.values())}")

    # Update
    prefs.settings.update({"theme": "light", "font_size": "14"})
    print(f"   After update: prefs.settings['theme'] = {prefs.settings['theme']}")

    # Clear
    test_map = maps.UserPreferences()
    test_map.settings["key1"] = "value1"
    test_map.settings.clear()
    print(f"   After clear: len(test_map.settings) = {len(test_map.settings)}")

    # Serialization
    serialized = product.SerializeToString()
    print(f"\n💾 Serialized product: {len(serialized)} bytes")

def test_map_key_types():
    """Test different map key types"""
    print("\n" + "=" * 60)
    print("Testing Different Map Key Types")
    print("=" * 60 + "\n")

    import maps_example_pb2 as maps

    key_types = maps.MapKeyTypes()

    # Integer keys
    key_types.int_to_string[1] = "one"
    key_types.int_to_string[2] = "two"
    key_types.int_to_string[-1] = "negative one"

    # Long keys
    key_types.long_to_string[1000000000] = "billion"

    # Unsigned int keys
    key_types.uint_to_string[100] = "hundred"
    key_types.uint_to_string[200] = "two hundred"

    # Boolean keys
    key_types.bool_to_string[True] = "yes"
    key_types.bool_to_string[False] = "no"

    # String keys
    key_types.string_to_string["key1"] = "value1"
    key_types.string_to_string["key2"] = "value2"

    print("🔑 Different Key Types:")
    print(f"   Int keys: {dict(key_types.int_to_string)}")
    print(f"   Long keys: {dict(key_types.long_to_string)}")
    print(f"   Uint keys: {dict(key_types.uint_to_string)}")
    print(f"   Bool keys: {dict(key_types.bool_to_string)}")
    print(f"   String keys: {dict(key_types.string_to_string)}")

def test_combined():
    """Test combining repeated and map fields"""
    print("\n" + "=" * 60)
    print("Testing Combined Collections")
    print("=" * 60 + "\n")

    import maps_example_pb2 as maps

    # Create user profile with nested structure
    profile = maps.UserProfileCorrect()
    profile.user_id = "user456"
    profile.name = "Bob"

    # Add metadata (map)
    profile.metadata["joined_date"] = "2023-01-15"
    profile.metadata["location"] = "New York"
    profile.metadata["role"] = "developer"

    # Add tags (repeated)
    profile.tags.extend(["python", "grpc", "backend"])

    # Add lists in maps (using message wrapper)
    favorites = profile.lists["favorites"]
    favorites.values.extend(["pizza", "pasta", "sushi"])

    todos = profile.lists["todos"]
    todos.values.extend(["learn protobuf", "build app", "deploy"])

    print(f"👤 User Profile: {profile.name} ({profile.user_id})")
    print("\n   Metadata:")
    for key, value in profile.metadata.items():
        print(f"      {key}: {value}")

    print(f"\n   Tags: {', '.join(profile.tags)}")

    print("\n   Lists:")
    for list_name, string_list in profile.lists.items():
        print(f"      {list_name}: {', '.join(string_list.values)}")

    # Serialization
    serialized = profile.SerializeToString()
    print(f"\n💾 Serialized profile: {len(serialized)} bytes")

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("Protocol Buffers - Collections Example")
    print("=" * 60 + "\n")

    # Compile
    compile_protos()

    # Run tests
    test_repeated_fields()
    test_maps()
    test_map_key_types()
    test_combined()

    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60 + "\n")

    print("💡 Key Takeaways:")
    print("   1. Repeated fields work like Python lists")
    print("   2. Maps work like Python dictionaries")
    print("   3. Use .add() for repeated message fields")
    print("   4. Use .append() or .extend() for repeated scalar fields")
    print("   5. Maps support dict-like operations (get, keys, values, items)")
    print("   6. Map keys can be most scalar types (not float, double, bytes)")
    print("   7. Map values can be any type except repeated")
    print("   8. Use message wrappers for complex nested structures\n")

if __name__ == "__main__":
    main()
