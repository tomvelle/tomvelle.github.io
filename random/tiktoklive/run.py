from TikTokLive import TikTokLiveClient
from TikTokLive.events import (
    ConnectEvent,
    CommentEvent,
    GiftEvent,
    LikeEvent,
    FollowEvent,
    ShareEvent,
    JoinEvent
)

from openai import OpenAI
client_ai = OpenAI()  # Automatically pulls from env var

# Create the client (remove "@" from username here!)
client: TikTokLiveClient = TikTokLiveClient(unique_id="im.jvcob")

# Fired when successfully connected
@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"✅ Connected to @{event.unique_id} (Room ID: {client.room_id})")

# Fired on new comments
@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    print(f"💬 {event.user.nickname}: {event.comment}")

# Fired when someone sends a gift
@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    # event.gift describes the gift, event.gift.name is the display name
    repeat = " (repeat)" if event.repeat_end == 0 else ""
    print(f"🎁 {event.user.nickname} sent {event.gift.name}{repeat}")

# Fired when someone taps like
# @client.on(LikeEvent)
# async def on_like(event: LikeEvent):
#     print(f"❤️ {event.user.nickname} liked the stream")

# Fired when someone follows
@client.on(FollowEvent)
async def on_follow(event: FollowEvent):
    print(f"👤 {event.user.nickname} followed you!")

# Fired when someone shares the stream
@client.on(ShareEvent)
async def on_share(event: ShareEvent):
    print(f"🔗 {event.user.nickname} shared the stream!")

# Fired when someone joins
@client.on(JoinEvent)
async def on_join(event: JoinEvent):
    print(f"👋 {event.user.nickname} joined the live!")

if __name__ == "__main__":
    client.run()