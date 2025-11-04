# Exercise 03: Messaging System

## Objective
Design a Protocol Buffers schema for a messaging/chat application using nested messages, enums, and oneof fields.

## Duration
25-30 minutes

## Learning Goals
- Work with nested messages
- Use oneof for polymorphic data
- Model complex real-world systems
- Apply best practices for message design

## Task Description

Create a `messaging.proto` file that models a chat/messaging system with the following requirements:

### Message Types Enum
Create a `MessageType` enum:
- `MESSAGE_TYPE_UNSPECIFIED` (0)
- `MESSAGE_TYPE_TEXT` (1)
- `MESSAGE_TYPE_IMAGE` (2)
- `MESSAGE_TYPE_FILE` (3)
- `MESSAGE_TYPE_LOCATION` (4)

### TextContent Message
For text messages:
- `text` (string) - message text
- `mentions` (repeated string) - list of mentioned usernames
- `links` (repeated string) - list of URLs in message

### ImageContent Message
For image messages:
- `url` (string) - image URL
- `thumbnail_url` (string) - thumbnail URL
- `width` (integer) - image width
- `height` (integer) - image height
- `size_bytes` (integer) - file size

### FileContent Message
For file attachments:
- `filename` (string) - original filename
- `url` (string) - download URL
- `mime_type` (string) - file MIME type
- `size_bytes` (integer, 64-bit) - file size

### LocationContent Message
For location sharing:
- `latitude` (double) - latitude coordinate
- `longitude` (double) - longitude coordinate
- `address` (string) - human-readable address
- `place_name` (string) - place name (if any)

### Message Message
Create a main `Message` message with:
- `id` (string) - unique message ID
- `conversation_id` (string) - conversation/channel ID
- `sender_id` (string) - user ID of sender
- `sender_name` (string) - display name of sender
- `timestamp` (integer, 64-bit) - message timestamp
- `type` (MessageType) - message type
- `content` (oneof) - message content:
  - `text_content` (TextContent)
  - `image_content` (ImageContent)
  - `file_content` (FileContent)
  - `location_content` (LocationContent)
- `is_edited` (boolean) - whether message was edited
- `is_deleted` (boolean) - whether message was deleted
- `reply_to_message_id` (string) - ID of message being replied to (if any)
- `reactions` (map<string, int32>) - emoji reactions and counts

### Conversation Message
Create a `Conversation` message:
- `id` (string) - conversation ID
- `name` (string) - conversation name
- `participant_ids` (repeated string) - list of user IDs
- `messages` (repeated Message) - list of messages
- `created_at` (integer, 64-bit) - creation timestamp
- `last_message_at` (integer, 64-bit) - last message timestamp

## Requirements
1. Use `proto3` syntax
2. Use `oneof` for the polymorphic content field
3. Use appropriate types (consider 64-bit integers for IDs and sizes)
4. Use nested messages for content types
5. Add comprehensive documentation

## Steps

1. **Create the proto file:**
   ```bash
   touch messaging.proto
   ```

2. **Define messages in order:**
   - Start with the enum
   - Define content messages (Text, Image, File, Location)
   - Define the main Message message with oneof
   - Define the Conversation message

3. **Compile:**
   ```bash
   python -m grpc_tools.protoc \
     --proto_path=. \
     --python_out=. \
     messaging.proto
   ```

4. **Test your schema:**
   ```python
   from messaging_pb2 import (
       Message, TextContent, ImageContent,
       Conversation, MessageType
   )
   import time

   # Create a text message
   msg1 = Message()
   msg1.id = "msg_001"
   msg1.conversation_id = "conv_123"
   msg1.sender_id = "user_alice"
   msg1.sender_name = "Alice"
   msg1.timestamp = int(time.time())
   msg1.type = MessageType.MESSAGE_TYPE_TEXT
   msg1.text_content.text = "Hello, @bob! Check out https://example.com"
   msg1.text_content.mentions.append("bob")
   msg1.text_content.links.append("https://example.com")

   # Create an image message
   msg2 = Message()
   msg2.id = "msg_002"
   msg2.conversation_id = "conv_123"
   msg2.sender_id = "user_bob"
   msg2.sender_name = "Bob"
   msg2.timestamp = int(time.time())
   msg2.type = MessageType.MESSAGE_TYPE_IMAGE
   msg2.image_content.url = "https://example.com/image.jpg"
   msg2.image_content.thumbnail_url = "https://example.com/thumb.jpg"
   msg2.image_content.width = 1920
   msg2.image_content.height = 1080
   msg2.image_content.size_bytes = 524288

   # Add reactions
   msg1.reactions["👍"] = 5
   msg1.reactions["❤️"] = 3

   # Check which content is set
   print(f"Message 1 content type: {msg1.WhichOneof('content')}")
   print(f"Message 2 content type: {msg2.WhichOneof('content')}")

   # Create conversation
   conversation = Conversation()
   conversation.id = "conv_123"
   conversation.name = "General"
   conversation.participant_ids.extend(["user_alice", "user_bob"])
   conversation.messages.extend([msg1, msg2])
   conversation.created_at = int(time.time()) - 86400
   conversation.last_message_at = int(time.time())

   print(f"\nConversation: {conversation.name}")
   print(f"Participants: {len(conversation.participant_ids)}")
   print(f"Messages: {len(conversation.messages)}")
   ```

## Tips

- Use `oneof` to ensure only one content type is set per message
- Use `string` for IDs (more flexible than integers)
- Use `int64` for timestamps (Unix timestamps in milliseconds)
- Use `map<string, int32>` for reaction counts
- Consider using `repeated string` for lists of IDs
- Use `WhichOneof()` to check which content type is set
- Use `HasField()` to check if optional fields are set

## Validation

Your schema should:
- ✅ Compile without errors
- ✅ Use oneof for message content
- ✅ Include all message types
- ✅ Use appropriate data types
- ✅ Be well-structured and documented

## Bonus Challenges

1. **Add message status:**
   - Create a `MessageStatus` enum (SENT, DELIVERED, READ)
   - Add `status` field to Message
   - Add `read_by` map to track who read the message

2. **Add typing indicators:**
   - Create a `TypingIndicator` message
   - Include user_id, conversation_id, is_typing

3. **Add message threading:**
   - Add `thread_id` field to Message
   - Add `thread_reply_count` field

4. **Add user presence:**
   - Create a `UserPresence` message
   - Track online/offline status
   - Track last seen timestamp

## Common Errors

**Error:** `Only one field in oneof can be set`
- This is expected behavior!
- Setting one field clears others in the oneof

**Error:** `Cannot use repeated in oneof`
- Oneof fields cannot be repeated
- Use a wrapper message if needed

**Error:** `Field numbers must be unique`
- Remember that oneof fields share the same number space
- Each field needs a unique number

## Architecture Tips

For a real messaging system, consider:
- Separate messages for reads vs. writes
- Pagination for message lists
- Indexes for searching
- Separate schemas for different features
- API versioning (v1, v2, etc.)

## Next Steps

After completing this exercise:
1. Complete the main lab
2. Try the bonus challenges
3. Think about how you'd extend this for:
   - Video calls
   - Voice messages
   - Message forwarding
   - Message search

Good luck!
