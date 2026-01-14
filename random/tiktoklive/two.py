from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent
from openai import OpenAI
import os
import json
import random

LYRICS_FILE = "lyrics.json"

# Ensure the JSON file exists and is initialized
if not os.path.exists(LYRICS_FILE):
    with open(LYRICS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# Init TikTok client (no @ in username)
client = TikTokLiveClient(unique_id="im.jvcob")

# Init OpenAI client (auto-reads from env var OPENAI_API_KEY)
client_ai = OpenAI()


# ---------- Helpers ----------

def load_lyrics():
    """Load JSON safely."""
    try:
        with open(LYRICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_lyrics(data):
    """Write JSON safely."""
    with open(LYRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def append_stanza(stanza: str, user: str = None, comment: str = None, stanza_type: str = "comment"):
    """Append a stanza to lyrics.json"""
    data = load_lyrics()
    data.append({
        "text": stanza,
        "sung": False,
        "user": user,
        "comment": comment,
        "type": stanza_type  # "comment" or "filler"
    })
    save_lyrics(data)


# ---------- Lyric Generators ----------

def make_lyric_stanza(user: str, comment: str) -> str:
    """Turn a chat comment into a 4-chord lyric stanza."""
    prompt = f"""
    You are writing lyrics for a live improv 4-chord pop-punk performance. 
    The song loops I–V–vi–IV endlessly. 

    Rules:
    - Output EXACTLY 4 short lines.
    - Keep each line under 8 words.
    - Mention the user "{user}" by name once.
    - Include their comment: "{comment}" in a natural way.
    - Make it energetic, singable, and fun.
    - No explanations, no extra text, just the lyrics.
    """

    try:
        response = client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ GPT error ({e}) — falling back")
        return f"{user} said: {comment}\nSinging it out loud\nFour chords keep it rolling\nLet’s pump up the crowd!"


def make_filler_stanza(vibe: str = "fun") -> str:
    """Generate a filler stanza not tied to any comment."""
    prompt = f"""
    Write a short 4-line pop-punk filler stanza
    for a live jam over I–V–vi–IV.
    Vibe: {vibe}.
    Rules:
    - Each line under 8 words.
    - Fun, singable, easy to chant.
    - No usernames, no audience comments.
    - Output ONLY the 4 lines.
    """
    try:
        response = client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception:
        # Fallback hardcoded filler
        fillers = [
            "Whoa-oh, keep the night alive\nFour chords drive the vibe\nHands up, shout it loud\nWe’re singing with the crowd",
            "Na-na-na, don’t slow down\nFour chords shake the town\nJump high, feel the beat\nSing it loud, repeat repeat"
        ]
        return random.choice(fillers)


def ensure_fillers(min_count: int = 4):
    """Make sure there are always at least `min_count` unsung fillers in the JSON."""
    data = load_lyrics()
    current_fillers = [s for s in data if s["type"] == "filler" and not s["sung"]]
    needed = max(0, min_count - len(current_fillers))
    if needed > 0:
        for _ in range(needed):
            stanza = make_filler_stanza()
            data.append({"text": stanza, "sung": False, "user": None, "comment": None, "type": "filler"})
        save_lyrics(data)


# ---------- TikTok Events ----------

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"✅ Connected to @{event.unique_id} (Room ID: {client.room_id})")
    ensure_fillers()  # Make sure we start with fillers


@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    stanza = make_lyric_stanza(event.user.nickname, event.comment)
    print(f"\n🎤 New Stanza from {event.user.nickname}:\n{stanza}\n")

    # Save latest stanza for OBS overlay
    with open("current_lyric.txt", "w", encoding="utf-8") as f:
        f.write(stanza)

    # Append stanza to JSON
    append_stanza(stanza, user=event.user.nickname, comment=event.comment, stanza_type="comment")

    # Top up fillers if needed
    ensure_fillers()


# ---------- Main ----------

if __name__ == "__main__":
    client.run()
