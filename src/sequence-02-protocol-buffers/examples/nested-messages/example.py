#!/usr/bin/env python3
"""
Example demonstrating nested messages in Protocol Buffers

This script shows:
1. How to create and use nested messages
2. Composition of complex structures
3. Deep nesting patterns
4. Nested messages within repeated fields
"""

import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def compile_proto():
    """Compile the proto file"""
    print("=æ Compiling address.proto...\n")

    result = subprocess.run([
        "python", "-m", "grpc_tools.protoc",
        "--proto_path=.",
        "--python_out=.",
        "address.proto"
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__))

    if result.returncode != 0:
        print("L Compilation failed!")
        print(result.stderr)
        sys.exit(1)

    print(" Compilation successful!\n")

def test_basic_nesting():
    """Test basic nested messages"""
    print("=" * 60)
    print("Testing Basic Nested Messages")
    print("=" * 60 + "\n")

    import address_pb2

    # Create a person with nested address
    person = address_pb2.Person()
    person.id = 1
    person.name = "Alice Johnson"
    person.email = "alice@example.com"

    # Set home address (nested message)
    person.home_address.street = "123 Main St"
    person.home_address.city = "Springfield"
    person.home_address.state = "IL"
    person.home_address.zip_code = "62701"
    person.home_address.country = "USA"

    # Set work address
    person.work_address.street = "456 Business Ave"
    person.work_address.city = "Springfield"
    person.work_address.state = "IL"
    person.work_address.zip_code = "62702"
    person.work_address.country = "USA"

    print(f"=d Person: {person.name}")
    print(f"   Email: {person.email}")
    print(f"\n   <à Home Address:")
    print(f"      {person.home_address.street}")
    print(f"      {person.home_address.city}, {person.home_address.state} {person.home_address.zip_code}")
    print(f"      {person.home_address.country}")
    print(f"\n   <â Work Address:")
    print(f"      {person.work_address.street}")
    print(f"      {person.work_address.city}, {person.work_address.state} {person.work_address.zip_code}")

    # Alternative: Use CopyFrom
    print("\n" + "-" * 60)
    print("Using CopyFrom for nested messages:")

    address = address_pb2.Address()
    address.street = "789 Oak Lane"
    address.city = "Chicago"
    address.state = "IL"
    address.zip_code = "60601"
    address.country = "USA"

    person2 = address_pb2.Person()
    person2.id = 2
    person2.name = "Bob Smith"
    person2.home_address.CopyFrom(address)

    print(f"\n=d {person2.name}'s home:")
    print(f"   {person2.home_address.street}, {person2.home_address.city}")

    # Serialization
    serialized = person.SerializeToString()
    print(f"\n=¾ Serialized person with addresses: {len(serialized)} bytes")

def test_repeated_nested():
    """Test repeated nested messages"""
    print("\n" + "=" * 60)
    print("Testing Repeated Nested Messages")
    print("=" * 60 + "\n")

    import address_pb2

    # Create company with multiple offices
    company = address_pb2.Company()
    company.name = "Tech Corp"

    # Set headquarters
    company.headquarters.street = "1 Corporate Plaza"
    company.headquarters.city = "New York"
    company.headquarters.state = "NY"
    company.headquarters.zip_code = "10001"
    company.headquarters.country = "USA"

    # Add multiple offices
    office1 = company.offices.add()
    office1.street = "100 Tech Way"
    office1.city = "San Francisco"
    office1.state = "CA"
    office1.zip_code = "94105"
    office1.country = "USA"

    office2 = company.offices.add()
    office2.street = "200 Innovation Dr"
    office2.city = "Austin"
    office2.state = "TX"
    office2.zip_code = "73301"
    office2.country = "USA"

    # Add employees
    emp1 = company.employees.add()
    emp1.id = 1
    emp1.name = "Alice"
    emp1.email = "alice@techcorp.com"
    emp1.department = "Engineering"
    emp1.address.city = "San Francisco"
    emp1.address.state = "CA"

    emp2 = company.employees.add()
    emp2.id = 2
    emp2.name = "Bob"
    emp2.email = "bob@techcorp.com"
    emp2.department = "Sales"
    emp2.address.city = "Austin"
    emp2.address.state = "TX"

    print(f"<â Company: {company.name}")
    print(f"\n   HQ: {company.headquarters.city}, {company.headquarters.state}")
    print(f"\n   Offices ({len(company.offices)}):")
    for i, office in enumerate(company.offices, 1):
        print(f"      {i}. {office.city}, {office.state}")

    print(f"\n   Employees ({len(company.employees)}):")
    for emp in company.employees:
        print(f"      - {emp.name} ({emp.department}) - {emp.address.city}")

    serialized = company.SerializeToString()
    print(f"\n=¾ Serialized company: {len(serialized)} bytes")

def test_deep_nesting():
    """Test deeply nested structures"""
    print("\n" + "=" * 60)
    print("Testing Deep Nesting")
    print("=" * 60 + "\n")

    import address_pb2

    # Create order with nested items and shipping
    order = address_pb2.Order()
    order.id = 12345
    order.customer_name = "Charlie Brown"
    order.order_date = 1699000000
    order.total_amount = 0.0

    # Add order items
    item1 = order.items.add()
    item1.product_id = 101
    item1.product_name = "Laptop"
    item1.quantity = 1
    item1.unit_price = 999.99
    item1.total_price = 999.99

    item2 = order.items.add()
    item2.product_id = 102
    item2.product_name = "Mouse"
    item2.quantity = 2
    item2.unit_price = 25.50
    item2.total_price = 51.00

    item3 = order.items.add()
    item3.product_id = 103
    item3.product_name = "Keyboard"
    item3.quantity = 1
    item3.unit_price = 75.00
    item3.total_price = 75.00

    order.total_amount = sum(item.total_price for item in order.items)

    # Set shipping info (nested within nested)
    order.shipping.shipping_address.street = "789 Customer Ln"
    order.shipping.shipping_address.city = "Portland"
    order.shipping.shipping_address.state = "OR"
    order.shipping.shipping_address.zip_code = "97201"
    order.shipping.shipping_address.country = "USA"
    order.shipping.carrier = "UPS"
    order.shipping.tracking_number = "1Z999AA10123456784"
    order.shipping.estimated_delivery = 1699259600

    print(f"=æ Order #{order.id}")
    print(f"   Customer: {order.customer_name}")
    print(f"\n   Items:")
    for item in order.items:
        print(f"      - {item.product_name} x{item.quantity} @ ${item.unit_price} = ${item.total_price}")
    print(f"\n   Total: ${order.total_amount:.2f}")
    print(f"\n   =î Shipping to:")
    print(f"      {order.shipping.shipping_address.street}")
    print(f"      {order.shipping.shipping_address.city}, {order.shipping.shipping_address.state}")
    print(f"      Carrier: {order.shipping.carrier}")
    print(f"      Tracking: {order.shipping.tracking_number}")

    serialized = order.SerializeToString()
    print(f"\n=¾ Serialized order: {len(serialized)} bytes")

def test_very_deep_nesting():
    """Test very deeply nested structures"""
    print("\n" + "=" * 60)
    print("Testing Very Deep Nesting (UserProfile)")
    print("=" * 60 + "\n")

    import address_pb2

    # Create user profile with multiple levels of nesting
    profile = address_pb2.UserProfile()
    profile.user_id = 42
    profile.username = "poweruser"

    # Personal info
    profile.personal_info.first_name = "David"
    profile.personal_info.last_name = "Miller"
    profile.personal_info.email = "david@example.com"
    profile.personal_info.phone = "+1-555-0123"
    profile.personal_info.address.street = "321 User St"
    profile.personal_info.address.city = "Seattle"
    profile.personal_info.address.state = "WA"
    profile.personal_info.address.zip_code = "98101"

    # Preferences (nested within profile)
    profile.preferences.theme = "dark"
    profile.preferences.language = "en"
    profile.preferences.notifications_enabled = True

    # Notification settings (nested within preferences)
    profile.preferences.notifications.email = True
    profile.preferences.notifications.sms = False
    profile.preferences.notifications.push = True

    # Stats
    profile.stats.posts_count = 156
    profile.stats.followers_count = 1234
    profile.stats.following_count = 567
    profile.stats.joined_date = 1640000000

    print(f"=d User Profile: {profile.username} (ID: {profile.user_id})")
    print(f"\n   Personal Info:")
    print(f"      Name: {profile.personal_info.first_name} {profile.personal_info.last_name}")
    print(f"      Email: {profile.personal_info.email}")
    print(f"      Phone: {profile.personal_info.phone}")
    print(f"      Location: {profile.personal_info.address.city}, {profile.personal_info.address.state}")

    print(f"\n   Preferences:")
    print(f"      Theme: {profile.preferences.theme}")
    print(f"      Language: {profile.preferences.language}")
    print(f"      Notifications: {profile.preferences.notifications_enabled}")

    print(f"\n   Notification Settings:")
    print(f"      Email: {profile.preferences.notifications.email}")
    print(f"      SMS: {profile.preferences.notifications.sms}")
    print(f"      Push: {profile.preferences.notifications.push}")

    print(f"\n   Stats:")
    print(f"      Posts: {profile.stats.posts_count}")
    print(f"      Followers: {profile.stats.followers_count}")
    print(f"      Following: {profile.stats.following_count}")

    serialized = profile.SerializeToString()
    print(f"\n=¾ Serialized profile: {len(serialized)} bytes")

def test_oneof_with_nested():
    """Test oneof with nested messages"""
    print("\n" + "=" * 60)
    print("Testing Oneof with Nested Messages")
    print("=" * 60 + "\n")

    import address_pb2

    # Contact with email
    contact1 = address_pb2.ContactInfo()
    contact1.id = 1
    contact1.name = "Alice"
    contact1.email_info.email = "alice@example.com"
    contact1.email_info.verified = True

    print(f"=Ç Contact 1: {contact1.name}")
    if contact1.HasField("email_info"):
        print(f"   Email: {contact1.email_info.email} (verified: {contact1.email_info.verified})")

    # Contact with phone
    contact2 = address_pb2.ContactInfo()
    contact2.id = 2
    contact2.name = "Bob"
    contact2.phone_info.country_code = "+1"
    contact2.phone_info.number = "555-0100"
    contact2.phone_info.verified = False

    print(f"\n=Ç Contact 2: {contact2.name}")
    if contact2.HasField("phone_info"):
        print(f"   Phone: {contact2.phone_info.country_code} {contact2.phone_info.number}")
        print(f"   Verified: {contact2.phone_info.verified}")

    # Contact with social
    contact3 = address_pb2.ContactInfo()
    contact3.id = 3
    contact3.name = "Charlie"
    contact3.social_info.platform = "Twitter"
    contact3.social_info.handle = "@charlie"

    print(f"\n=Ç Contact 3: {contact3.name}")
    if contact3.HasField("social_info"):
        print(f"   Social: {contact3.social_info.platform} - {contact3.social_info.handle}")

    # Check which field is set
    print(f"\n=¡ Oneof field set:")
    print(f"   Contact 1: {contact1.WhichOneof('contact_method')}")
    print(f"   Contact 2: {contact2.WhichOneof('contact_method')}")
    print(f"   Contact 3: {contact3.WhichOneof('contact_method')}")

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("Protocol Buffers - Nested Messages Example")
    print("=" * 60 + "\n")

    # Compile
    compile_proto()

    # Run tests
    test_basic_nesting()
    test_repeated_nested()
    test_deep_nesting()
    test_very_deep_nesting()
    test_oneof_with_nested()

    print("\n" + "=" * 60)
    print(" All tests completed successfully!")
    print("=" * 60 + "\n")

    print("=¡ Key Takeaways:")
    print("   1. Nested messages allow composition of complex structures")
    print("   2. Access nested fields with dot notation (person.address.city)")
    print("   3. Use .add() for repeated nested messages")
    print("   4. Use .CopyFrom() to copy entire nested messages")
    print("   5. Nested messages can be defined inside or outside parent")
    print("   6. Keep nesting reasonable (2-3 levels max for readability)")
    print("   7. Use HasField() to check if a nested message is set")
    print("   8. Oneof works with nested messages too\n")

if __name__ == "__main__":
    main()
