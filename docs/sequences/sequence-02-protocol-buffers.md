# Sequence 02: Protocol Buffers - Complete Course

## Table of Contents
1. [Introduction to Protocol Buffers](#introduction)
2. [Syntax and Data Types](#syntax-and-data-types)
3. [The protoc Compiler](#protoc-compiler)
4. [Optimizations and Best Practices](#optimizations)
5. [Hands-on Examples](#examples)
6. [Common Patterns](#common-patterns)

---

## Introduction to Protocol Buffers {#introduction}

### What are Protocol Buffers?

Protocol Buffers (protobuf) is a language-neutral, platform-neutral, extensible mechanism for serializing structured data developed by Google. It's like JSON or XML, but:
- Smaller (binary format)
- Faster (efficient serialization)
- Type-safe (with code generation)
- Versioned (backward/forward compatible)

### Why Protocol Buffers for gRPC?

gRPC uses Protocol Buffers as its Interface Definition Language (IDL) and default serialization format:

1. **Performance:** Binary serialization is 3-10x faster than JSON
2. **Bandwidth:** Messages are 20-50% smaller than JSON
3. **Type Safety:** Compile-time type checking
4. **Code Generation:** Auto-generated client/server code
5. **Versioning:** Built-in backward compatibility

### History and Evolution

- **2001:** Developed internally at Google
- **2008:** Open-sourced (proto2)
- **2016:** Proto3 released (simplified syntax)
- **Today:** Used by Google, Netflix, Square, and thousands of companies

---

## Syntax and Data Types {#syntax-and-data-types}

### Basic Structure

A `.proto` file defines messages and services:

```proto
syntax = "proto3";

package mypackage;

// A message definition
message Person {
  string name = 1;
  int32 age = 2;
  string email = 3;
}

// A service definition
service PersonService {
  rpc GetPerson(PersonRequest) returns (Person);
}
```

### Syntax Declaration

Always start with the syntax declaration:

```proto
syntax = "proto3";  // Use proto3 (recommended)
```

Proto3 is simpler and removes several rarely-used features from proto2.

### Scalar Types

Protocol Buffers supports various scalar types:

| Proto Type | Python Type | Notes | Size |
|------------|-------------|-------|------|
| `double` | float | 64-bit float | 8 bytes |
| `float` | float | 32-bit float | 4 bytes |
| `int32` | int | Signed 32-bit | Variable |
| `int64` | int | Signed 64-bit | Variable |
| `uint32` | int | Unsigned 32-bit | Variable |
| `uint64` | int | Unsigned 64-bit | Variable |
| `sint32` | int | Signed (efficient for negatives) | Variable |
| `sint64` | int | Signed (efficient for negatives) | Variable |
| `fixed32` | int | Always 4 bytes | 4 bytes |
| `fixed64` | int | Always 8 bytes | 8 bytes |
| `sfixed32` | int | Always 4 bytes | 4 bytes |
| `sfixed64` | int | Always 8 bytes | 8 bytes |
| `bool` | bool | Boolean | 1 byte |
| `string` | str | UTF-8 or 7-bit ASCII | Variable |
| `bytes` | bytes | Arbitrary byte sequence | Variable |

#### Choosing the Right Type

```proto
message Product {
  // Use int32 for most integers
  int32 id = 1;

  // Use sint32 for frequently negative numbers
  sint32 temperature = 2;

  // Use uint32 for always positive numbers
  uint32 count = 3;

  // Use fixed32 when values are often > 2^28
  fixed32 large_value = 4;

  // Use float for decimal numbers
  float price = 5;

  // Use string for text
  string name = 6;

  // Use bytes for binary data
  bytes image = 7;

  // Use bool for true/false
  bool in_stock = 8;
}
```

### Field Numbers

Each field has a unique number (tag) used in the binary encoding:

```proto
message User {
  string name = 1;    // Field number 1
  int32 age = 2;      // Field number 2
  string email = 3;   // Field number 3
}
```

**Important Rules:**
- Field numbers 1-15 take 1 byte to encode (use for frequent fields)
- Field numbers 16-2047 take 2 bytes
- Field numbers 19000-19999 are reserved by Protocol Buffers
- **NEVER change or reuse field numbers** (breaks compatibility)

```proto
message User {
  reserved 4, 5, 6;              // Reserved numbers
  reserved "old_field", "unused"; // Reserved names

  string name = 1;     // Frequently used - use low number
  string email = 2;    // Frequently used
  string phone = 16;   // Less frequently used
}
```

### Messages (Complex Types)

Messages are structured data containers:

```proto
message Address {
  string street = 1;
  string city = 2;
  string state = 3;
  string zip_code = 4;
  string country = 5;
}

message Person {
  string name = 1;
  int32 age = 2;
  Address address = 3;  // Nested message
}
```

### Enumerations

Enums define a set of named constants:

```proto
enum OrderStatus {
  ORDER_STATUS_UNSPECIFIED = 0;  // Always have a 0 value
  ORDER_STATUS_PENDING = 1;
  ORDER_STATUS_PROCESSING = 2;
  ORDER_STATUS_SHIPPED = 3;
  ORDER_STATUS_DELIVERED = 4;
  ORDER_STATUS_CANCELLED = 5;
}

message Order {
  int32 id = 1;
  OrderStatus status = 2;
  float total = 3;
}
```

**Best Practices:**
- Always define a 0 value (required in proto3)
- Use a prefix to avoid name collisions
- Name the 0 value `*_UNSPECIFIED`

### Collections: Repeated Fields

Use `repeated` for lists/arrays:

```proto
message User {
  string name = 1;
  repeated string emails = 2;      // List of strings
  repeated Address addresses = 3;  // List of messages
}
```

Python usage:
```python
user = User(name="Alice")
user.emails.append("alice@example.com")
user.emails.append("alice@work.com")
```

### Collections: Maps

Maps for key-value pairs:

```proto
message UserPreferences {
  string user_id = 1;
  map<string, string> settings = 2;
  map<string, int32> counters = 3;
}
```

**Restrictions:**
- Keys can be any scalar type except `float`, `double`, or `bytes`
- Values can be any type except maps
- Map fields cannot be `repeated`

Python usage:
```python
prefs = UserPreferences(user_id="123")
prefs.settings["theme"] = "dark"
prefs.settings["language"] = "en"
prefs.counters["login_count"] = 42
```

### Oneof

`oneof` means "only one field can be set":

```proto
message Payment {
  int32 amount = 1;

  oneof payment_method {
    string credit_card = 2;
    string paypal_email = 3;
    string bank_account = 4;
  }
}
```

Only one of `credit_card`, `paypal_email`, or `bank_account` can be set at a time.

### Default Values

In proto3, all fields are optional and have default values:

| Type | Default Value |
|------|---------------|
| string | "" (empty string) |
| bytes | b"" (empty bytes) |
| bool | false |
| numeric | 0 |
| enum | First value (must be 0) |
| message | Language-dependent (None in Python) |
| repeated | empty list |
| map | empty map |

### Comments and Documentation

```proto
// Single-line comment

/*
 * Multi-line comment
 * Use for longer descriptions
 */

/**
 * Service for managing users
 */
service UserService {
  // Get a user by ID
  rpc GetUser(UserRequest) returns (User);
}
```

---

## The protoc Compiler {#protoc-compiler}

### Installation

Install Protocol Buffers compiler:

**macOS:**
```bash
brew install protobuf
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install protobuf-compiler
```

**Python plugin:**
```bash
pip install grpcio-tools
```

### Compilation Command

Basic syntax:
```bash
protoc --proto_path=IMPORT_PATH \
       --python_out=OUT_DIR \
       --grpc_python_out=OUT_DIR \
       path/to/file.proto
```

For Python with gRPC:
```bash
python -m grpc_tools.protoc \
  --proto_path=. \
  --python_out=. \
  --grpc_python_out=. \
  user.proto
```

### Generated Files

For `user.proto`, the compiler generates:

1. **`user_pb2.py`** - Message classes
   - Message definitions
   - Serialization methods
   - Field accessors

2. **`user_pb2_grpc.py`** - Service stubs (if services defined)
   - Client stub
   - Server base class
   - Method signatures

### Compilation Options

**`--proto_path` or `-I`:** Import path
```bash
protoc -I=./protos -I=./common --python_out=. user.proto
```

**`--python_out`:** Output directory for message classes
```bash
protoc --python_out=./generated user.proto
```

**`--grpc_python_out`:** Output directory for gRPC stubs
```bash
protoc --grpc_python_out=./generated user.proto
```

### Using Generated Code

```python
# Import generated classes
from user_pb2 import User, Address

# Create a message
user = User()
user.name = "Alice"
user.age = 30

# Or use constructor
user = User(name="Alice", age=30)

# Nested messages
address = Address(
    street="123 Main St",
    city="Springfield",
    state="IL"
)
user.address.CopyFrom(address)

# Serialize to binary
binary_data = user.SerializeToString()

# Deserialize from binary
user2 = User()
user2.ParseFromString(binary_data)

# Serialize to JSON (for debugging)
from google.protobuf.json_format import MessageToJson
json_str = MessageToJson(user)
```

---

## Optimizations and Best Practices {#optimizations}

### Performance Optimizations

#### 1. Field Number Optimization

```proto
message User {
  // Most accessed fields: use 1-15 (1 byte encoding)
  int32 id = 1;
  string name = 2;
  string email = 3;

  // Less accessed fields: use 16+ (2 bytes encoding)
  string bio = 16;
  string website = 17;
  bytes profile_picture = 18;
}
```

#### 2. Use Appropriate Integer Types

```proto
message Metrics {
  // Bad: wastes space for small numbers
  int64 count = 1;

  // Good: right-sized for the data
  int32 count = 2;

  // Better: for negative numbers
  sint32 delta = 3;

  // Best: for large positive numbers
  uint32 total = 4;
}
```

#### 3. Avoid Deep Nesting

```proto
// Bad: deeply nested
message Order {
  message Customer {
    message Address {
      message Coordinates {
        float lat = 1;
        float lng = 2;
      }
    }
  }
}

// Good: flat structure
message Coordinates {
  float lat = 1;
  float lng = 2;
}

message Address {
  Coordinates coords = 1;
}

message Customer {
  Address address = 1;
}

message Order {
  Customer customer = 1;
}
```

#### 4. Message Size Limits

Keep messages under 1MB for best performance:
- Split large data into chunks
- Use streaming for large datasets
- Consider pagination for lists

### Versioning Best Practices

#### Adding New Fields (Always Safe)

```proto
// Version 1
message User {
  int32 id = 1;
  string name = 2;
}

// Version 2 - add new field
message User {
  int32 id = 1;
  string name = 2;
  string email = 3;  // New field - OK!
}
```

#### Removing Fields (Use Reserved)

```proto
// Version 1
message User {
  int32 id = 1;
  string name = 2;
  string old_field = 3;
}

// Version 2 - remove field
message User {
  reserved 3;          // Mark as reserved
  reserved "old_field"; // Reserve name too

  int32 id = 1;
  string name = 2;
}
```

#### Changing Field Types (Risky!)

Some changes are safe, most are not:

**Safe changes:**
- `int32` ” `uint32` ” `int64` ” `uint64` (with value limits)
- `sint32` ” `sint64`
- `fixed32` ” `sfixed32`
- `fixed64` ” `sfixed64`

**Unsafe changes:**
- Any change involving `string`, `bytes`, or `bool`
- Changing to/from a `message` type

### Naming Conventions

Follow the official style guide:

```proto
// File: user_service.proto
syntax = "proto3";

// Package: lowercase with dots
package mycompany.users.v1;

// Messages: PascalCase
message UserProfile {
  // Fields: snake_case
  int32 user_id = 1;
  string first_name = 2;
  string last_name = 3;

  // Enums: PascalCase with PREFIX
  enum UserStatus {
    USER_STATUS_UNSPECIFIED = 0;
    USER_STATUS_ACTIVE = 1;
    USER_STATUS_INACTIVE = 2;
  }
  UserStatus status = 4;
}

// Services: PascalCase
service UserService {
  // Methods: PascalCase
  rpc GetUserProfile(GetUserProfileRequest) returns (UserProfile);
  rpc UpdateUserProfile(UpdateUserProfileRequest) returns (UserProfile);
}
```

### Package Organization

```proto
// Good: versioned API
syntax = "proto3";
package mycompany.users.v1;

// Import from other packages
import "mycompany/common/v1/types.proto";
import "google/protobuf/timestamp.proto";

message User {
  int32 id = 1;
  google.protobuf.Timestamp created_at = 2;
  mycompany.common.v1.Address address = 3;
}
```

### Documentation

```proto
/**
 * Represents a user in the system.
 * Users can have multiple roles and permissions.
 */
message User {
  // Unique identifier for the user
  int32 id = 1;

  // User's full name (required)
  string name = 2;

  // Primary email address (must be unique)
  string email = 3;

  /**
   * User's roles in the system.
   * A user can have multiple roles.
   */
  repeated Role roles = 4;
}
```

---

## Hands-on Examples {#examples}

### Example 1: Basic User Schema

```proto
syntax = "proto3";

message User {
  int32 id = 1;
  string username = 2;
  string email = 3;
  bool is_active = 4;
}
```

Compile:
```bash
python -m grpc_tools.protoc -I. --python_out=. user.proto
```

Use in Python:
```python
from user_pb2 import User

# Create
user = User(id=1, username="alice", email="alice@example.com", is_active=True)

# Serialize
data = user.SerializeToString()
print(f"Serialized size: {len(data)} bytes")

# Deserialize
user2 = User()
user2.ParseFromString(data)
print(f"Name: {user2.username}")
```

### Example 2: Collections

```proto
syntax = "proto3";

message Product {
  int32 id = 1;
  string name = 2;
  repeated string tags = 3;
  map<string, string> attributes = 4;
}
```

Usage:
```python
from product_pb2 import Product

product = Product(id=1, name="Laptop")
product.tags.extend(["electronics", "computers"])
product.attributes["brand"] = "Dell"
product.attributes["color"] = "Silver"
```

### Example 3: Nested Messages

```proto
syntax = "proto3";

message Address {
  string street = 1;
  string city = 2;
  string country = 3;
}

message Company {
  string name = 1;
  Address headquarters = 2;
  repeated Address offices = 3;
}
```

### Example 4: Service Definition

```proto
syntax = "proto3";

message GetUserRequest {
  int32 user_id = 1;
}

message User {
  int32 id = 1;
  string name = 2;
  string email = 3;
}

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
}
```

---

## Common Patterns {#common-patterns}

### Pattern 1: Request/Response Pairs

```proto
// Always create paired request/response messages
message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message CreateUserResponse {
  User user = 1;
  string message = 2;
}

service UserService {
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
}
```

### Pattern 2: List Operations

```proto
message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
  string filter = 3;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
  int32 total_count = 3;
}
```

### Pattern 3: Timestamps

```proto
import "google/protobuf/timestamp.proto";

message Event {
  int32 id = 1;
  string name = 2;
  google.protobuf.Timestamp created_at = 3;
  google.protobuf.Timestamp updated_at = 4;
}
```

### Pattern 4: Error Handling

```proto
message Response {
  bool success = 1;
  string error_message = 2;
  int32 error_code = 3;

  // Actual data (only if success)
  User user = 4;
}
```

### Pattern 5: Soft Deletes

```proto
import "google/protobuf/timestamp.proto";

message User {
  int32 id = 1;
  string name = 2;
  bool is_deleted = 3;
  google.protobuf.Timestamp deleted_at = 4;
}
```

---

## Summary

### Key Takeaways

1. **Proto3 Syntax:** Always use `syntax = "proto3";`
2. **Field Numbers:** Use 1-15 for frequent fields, never reuse
3. **Types:** Choose appropriate scalar types
4. **Messages:** Keep them focused and composable
5. **Collections:** Use `repeated` and `map` appropriately
6. **Versioning:** Add fields freely, reserve deleted ones
7. **Naming:** Follow style guide conventions
8. **Documentation:** Comment your schemas

### Common Mistakes to Avoid

L **Don't:**
- Change or reuse field numbers
- Use field numbers 19000-19999
- Make messages deeply nested
- Forget to compile after changes
- Use `float` for money amounts
- Remove fields without reserving

 **Do:**
- Use reserved for deleted fields
- Document your messages
- Use appropriate types
- Keep messages under 1MB
- Version your APIs
- Follow naming conventions

---

## Practice Exercises

Now that you've learned the concepts, complete the exercises:

1. **Exercise 01:** User Schema - Define a complete user profile
2. **Exercise 02:** Product Catalog - Model products with categories
3. **Exercise 03:** Messaging System - Design a chat message format

Then complete the **Lab** to solidify your understanding!

---

## References

- [Protocol Buffers Documentation](https://protobuf.dev/)
- [Proto3 Language Guide](https://protobuf.dev/programming-guides/proto3/)
- [Python Generated Code Guide](https://protobuf.dev/reference/python/python-generated/)
- [Style Guide](https://protobuf.dev/programming-guides/style/)
- [Encoding Guide](https://protobuf.dev/programming-guides/encoding/)
