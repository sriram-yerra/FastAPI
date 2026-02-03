## **How Frontend and Backend “Meet” on the Same WebSocket?**

This is about **URL routing + protocol rules**, not magic.

---

## **1️⃣ Both Sides Agree on the Same Address**

### Frontend
```javascript
const ws = new WebSocket(`ws://${location.host}/ws`);
```
### Backend
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
```
👉 The key is /ws.

The browser says:

> “Connect me to WebSocket at /ws on this server.”

FastAPI says:

> “If a WebSocket comes to /ws, handle it here.”

Same path = same connection point.

## **2️⃣ What Happens Under the Hood**

When page loads:
```sql
Browser
   ↓  (WebSocket handshake request)
GET /ws  Upgrade: websocket
   ↓
FastAPI sees @app.websocket("/ws")
   ↓
Connection accepted
   ↓
Persistent tunnel opens
```
Now they are connected through one TCP socket.

## **3️⃣ Why location.host Works**

```javascript
ws://${location.host}/ws
```
location.host = current server + port

If page opened from:
```arduino
http://localhost:8000
```
Then:
```bash
ws://localhost:8000/ws
```
So frontend automatically connects to the same backend server serving the page.

## **4️⃣ They Are Not “Finding Each Other”**

They don't search.

They both follow a fixed rule:

| Side    | Rule                |
|---------|---------------------|
| Browser | Connect to /ws      |
| FastAPI | Listen at /ws       |

That’s like both agreeing to meet at Room 101.

## **5️⃣ What Identifies a Single Client**

Each user gets their own WebSocket connection:
```css
User A → /ws → Connection A
User B → /ws → Connection B
```
FastAPI function runs separately per connection.

## **6️⃣ Summary Analogy**

/ws = meeting room

WebSocket handshake = door opening

TCP connection = private tunnel

Messages = things passed through tunnel

## **One-line Answer**

Frontend and backend connect because both are configured to use the same WebSocket URL path (/ws) on the same server.