#!/usr/bin/env python3
"""
Example demonstrating compilation and usage of basic Protocol Buffers types

This script:
1. Compiles the user.proto file
2. Creates message instances
3. Demonstrates serialization/deserialization
4. Shows how to access fields
"""

import subprocess
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

def compile_proto():
    """Compile the proto file using protoc"""
    print("=æ Compiling user.proto...")

    result = subprocess.run([
        "python", "-m", "grpc_tools.protoc",
        "--proto_path=.",
        "--python_out=.",
        "user.proto"
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__))

    if result.returncode != 0:
        print("L Compilation failed!")
        print(result.stderr)
        sys.exit(1)

    print(" Compilation successful!\n")

def test_basic_types():
    """Test basic scalar types"""
    print("=" * 60)
    print("Testing Basic Scalar Types")
    print("=" * 60)

    # Import generated module
    try:
        import user_pb2
    except ImportError:
        print("L Failed to import user_pb2. Make sure compilation succeeded.")
        sys.exit(1)

    # Create a User instance
    user = user_pb2.User()
    user.id = 12345
    user.username = "alice_wonder"
    user.email = "alice@example.com"
    user.is_active = True
    user.is_verified = True
    user.follower_count = 1500
    user.rating = 4.7
    user.precise_value = 3.14159265359
    user.large_number = 9223372036854775807
    user.profile_picture = b"\x89PNG\r\n\x1a\n"  # PNG header

    print("\n=Ý Created User:")
    print(f"   ID: {user.id}")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Active: {user.is_active}")
    print(f"   Verified: {user.is_verified}")
    print(f"   Followers: {user.follower_count}")
    print(f"   Rating: {user.rating}")
    print(f"   Precise Value: {user.precise_value}")
    print(f"   Large Number: {user.large_number}")
    print(f"   Profile Picture: {len(user.profile_picture)} bytes")

    # Serialize
    serialized = user.SerializeToString()
    print(f"\n=¾ Serialized to {len(serialized)} bytes")

    # Deserialize
    user2 = user_pb2.User()
    user2.ParseFromString(serialized)
    print(f" Deserialized successfully")
    print(f"   Username from deserialized: {user2.username}")

    return user_pb2

def test_integer_types(user_pb2):
    """Test different integer types"""
    print("\n" + "=" * 60)
    print("Testing Different Integer Types")
    print("=" * 60)

    integers = user_pb2.IntegerTypes()
    integers.regular_int = 42
    integers.temperature = -15  # Negative value
    integers.balance = -1000    # Negative balance
    integers.age = 30           # Positive only
    integers.timestamp = 1699000000  # Unix timestamp
    integers.fixed_value = 123456
    integers.large_fixed = 9876543210
    integers.signed_fixed = -5000
    integers.large_signed_fixed = -987654321098

    print("\n=Ê Integer Types:")
    print(f"   Regular int32: {integers.regular_int}")
    print(f"   Temperature (sint32): {integers.temperature}°C")
    print(f"   Balance (sint64): ${integers.balance}")
    print(f"   Age (uint32): {integers.age}")
    print(f"   Timestamp (uint64): {integers.timestamp}")
    print(f"   Fixed32: {integers.fixed_value}")
    print(f"   Fixed64: {integers.large_fixed}")
    print(f"   Signed Fixed32: {integers.signed_fixed}")
    print(f"   Signed Fixed64: {integers.large_signed_fixed}")

    # Show serialization size
    serialized = integers.SerializeToString()
    print(f"\n=¾ Serialized to {len(serialized)} bytes")

def test_all_types(user_pb2):
    """Test all basic types together"""
    print("\n" + "=" * 60)
    print("Testing All Basic Types")
    print("=" * 60)

    all_types = user_pb2.AllBasicTypes()

    # Set all integer fields
    all_types.int32_field = 100
    all_types.int64_field = 10000000000
    all_types.uint32_field = 200
    all_types.uint64_field = 20000000000
    all_types.sint32_field = -50
    all_types.sint64_field = -5000000000
    all_types.fixed32_field = 300
    all_types.fixed64_field = 30000000000
    all_types.sfixed32_field = -150
    all_types.sfixed64_field = -15000000000

    # Set floating point
    all_types.float_field = 3.14
    all_types.double_field = 2.718281828

    # Set boolean
    all_types.bool_field = True

    # Set string
    all_types.string_field = "Hello, Protocol Buffers!"

    # Set bytes
    all_types.bytes_field = b"Binary data \x00\x01\x02"

    print("\n All fields set successfully")

    # Serialize and check size
    serialized = all_types.SerializeToString()
    print(f"=¾ Serialized all types to {len(serialized)} bytes")

    # Deserialize to verify
    all_types2 = user_pb2.AllBasicTypes()
    all_types2.ParseFromString(serialized)

    print(f" Deserialized successfully")
    print(f"   String field: '{all_types2.string_field}'")
    print(f"   Boolean field: {all_types2.bool_field}")
    print(f"   Float field: {all_types2.float_field}")
    print(f"   Double field: {all_types2.double_field}")

def test_default_values(user_pb2):
    """Demonstrate default values in proto3"""
    print("\n" + "=" * 60)
    print("Testing Default Values (proto3)")
    print("=" * 60)

    # Create empty user
    empty_user = user_pb2.User()

    print("\n=Ë Default values for unset fields:")
    print(f"   ID (int32): {empty_user.id}")
    print(f"   Username (string): '{empty_user.username}'")
    print(f"   Email (string): '{empty_user.email}'")
    print(f"   Active (bool): {empty_user.is_active}")
    print(f"   Followers (uint32): {empty_user.follower_count}")
    print(f"   Rating (float): {empty_user.rating}")
    print(f"   Profile Picture (bytes): {len(empty_user.profile_picture)} bytes")

    print("\n=¡ Note: In proto3, all fields have default values:")
    print("   - Numbers: 0")
    print("   - Strings: '' (empty)")
    print("   - Booleans: false")
    print("   - Bytes: b'' (empty)")

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("Protocol Buffers - Basic Types Example")
    print("=" * 60 + "\n")

    # Compile the proto file
    compile_proto()

    # Run tests
    user_pb2 = test_basic_types()
    test_integer_types(user_pb2)
    test_all_types(user_pb2)
    test_default_values(user_pb2)

    print("\n" + "=" * 60)
    print(" All tests completed successfully!")
    print("=" * 60 + "\n")

    print("=¡ Key Takeaways:")
    print("   1. Proto3 uses simple, clean syntax")
    print("   2. All fields have default values")
    print("   3. Binary serialization is very compact")
    print("   4. Choose the right integer type for your data")
    print("   5. Use sint* for frequently negative numbers")
    print("   6. Use uint* for always positive numbers")
    print("   7. Use fixed* when values are often large\n")

if __name__ == "__main__":
    main()
