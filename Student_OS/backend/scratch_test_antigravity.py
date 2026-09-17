import urllib.request
import json

base = "http://127.0.0.1:8000"

# 1. Test get chats
res = urllib.request.urlopen(f"{base}/api/antigravity/chats")
chats = json.loads(res.read().decode())
print(f"Total Antigravity Chats found: {len(chats)}")
for c in chats[:5]:
    print(f" - [{c['id'][:8]}] {c['title']} ({c['message_count']} msgs)")

# 2. Test get messages for current active chat
active_id = chats[0]['id']
res_m = urllib.request.urlopen(f"{base}/api/antigravity/chats/{active_id}/messages?limit=3")
msgs = json.loads(res_m.read().decode())
print(f"\nLast {len(msgs)} messages from active chat ({active_id[:8]}):")
for m in msgs:
    print(f" [{m['sender']}] {m['text'][:60]}...")

# 3. Test send prompt
post_data = json.dumps({"prompt": "Test connection from mobile device"}).encode('utf-8')
req = urllib.request.Request(
    f"{base}/api/antigravity/chats/{active_id}/prompt",
    data=post_data,
    headers={"Content-Type": "application/json"}
)
res_p = urllib.request.urlopen(req)
prompt_res = json.loads(res_p.read().decode())
print(f"\nPrompt execution response:")
print(f" Success: {prompt_res.get('success')}")
print(f" Reply preview: {prompt_res.get('reply')[:100]}...")
print(f" Directive file: {prompt_res.get('directive_file')}")
