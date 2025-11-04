# Exercise 01: User Schema

## Objective
Create a Protocol Buffers schema for a user management system with proper data types and field organization.

## Duration
15-20 minutes

## Learning Goals
- Define messages with appropriate scalar types
- Choose correct field numbers
- Use enums for status fields
- Compile and test a .proto file

## Task Description

Create a `user.proto` file that defines a user management schema with the following requirements:

### User Message
Create a `User` message with these fields:
- `id` (integer) - unique user identifier
- `username` (string) - user's username
- `email` (string) - email address
- `full_name` (string) - user's full name
- `age` (integer) - user's age
- `is_active` (boolean) - whether the account is active
- `created_at` (integer, 64-bit) - timestamp of account creation
- `account_type` (enum) - type of account (see below)

### AccountType Enum
Create an enum with these values:
- `ACCOUNT_TYPE_UNSPECIFIED` (0)
- `ACCOUNT_TYPE_FREE` (1)
- `ACCOUNT_TYPE_PREMIUM` (2)
- `ACCOUNT_TYPE_ENTERPRISE` (3)

### Requirements
1. Use `proto3` syntax
2. Use appropriate integer types for each field
3. Order fields with frequently accessed ones first (use field numbers 1-15)
4. Add comments to document your schema

## Steps

1. **Create the proto file:**
   ```bash
   touch user.proto
   ```

2. **Define the syntax and messages:**
   - Start with `syntax = "proto3";`
   - Define the `AccountType` enum
   - Define the `User` message

3. **Compile the proto file:**
   ```bash
   python -m grpc_tools.protoc \
     --proto_path=. \
     --python_out=. \
     user.proto
   ```

4. **Test your schema (optional):**
   Create a Python script to test:
   ```python
   from user_pb2 import User, AccountType

   user = User(
       id=1,
       username="alice",
       email="alice@example.com",
       full_name="Alice Wonder",
       age=30,
       is_active=True,
       created_at=1699000000,
       account_type=AccountType.ACCOUNT_TYPE_PREMIUM
   )

   print(user)
   ```

## Tips

- Use `int32` for the id and age fields
- Use `int64` for timestamps
- Use field numbers 1-9 for the most important fields
- Remember to start your enum at 0
- Add comments to explain each field

## Validation

Your schema should:
-  Compile without errors
-  Include all required fields
-  Use appropriate data types
-  Have a 0-value enum entry
-  Use sensible field numbering

## Solution

Check the `solution/` directory for a complete implementation if you get stuck.

## Next Steps

After completing this exercise:
1. Move on to Exercise 02 (Product Catalog)
2. Try modifying the schema to add:
   - A `last_login` timestamp
   - A `roles` repeated field (list of strings)
   - A `metadata` map field

## Common Errors

**Error:** `File not found`
- Make sure you're in the right directory
- Check that the file is named `user.proto` exactly

**Error:** `Syntax error`
- Make sure you have `syntax = "proto3";` at the top
- Check for missing semicolons
- Verify field numbers are unique

**Error:** `Enum value must start at 0`
- In proto3, the first enum value must be 0
- Name it something like `*_UNSPECIFIED`

Good luck!
