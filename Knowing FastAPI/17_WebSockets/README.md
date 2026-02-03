## **What is a WebSocket?**

- A **communication protocol** that enables **full-duplex (two-way) communication** between a client and a server.  
- Unlike **HTTP**, it keeps the connection **open**, allowing **real-time data exchange**.  
- Uses a **single TCP connection** for both sending and receiving messages.  
- Starts as an **HTTP handshake**, then **upgrades** to the WebSocket protocol.

---

### **In One Line**

> **WebSocket = Always-open, two-way communication channel over a single TCP connection for real-time apps.**

---

## **Explanation**

### **1. Full-Duplex Communication**
- Both **client and server** can send messages **simultaneously**.  
- No strict **request → response** pattern like HTTP.

**Why it matters:**  
Ideal for **real-time systems** such as chats, live dashboards, multiplayer games, and tracking systems.

---

### **2. Persistent Connection (Unlike HTTP)**
- **HTTP:** Connection usually **closes after a response**.  
- **WebSocket:** Connection stays **continuously open**.

**Why it matters:**  
Eliminates repeated connection overhead → **low latency** and **faster updates**.

---

### **3. Single TCP Connection**
- All communication flows through **one long-lived socket**.  
- No polling or repeated requests required.

**Why it matters:**  
More **efficient**, reduces **bandwidth usage** and **server load**.

---

### **4. HTTP Handshake → Protocol Upgrade**
- Connection begins as a normal **HTTP request**.  
- Server responds with **`101 Switching Protocols`**.  
- Communication then switches to **WebSocket frames**, not HTTP.

**Why it matters:**  
Works smoothly with existing **web infrastructure** (ports, proxies, firewalls).

---

## **How WebSockets are Useful in the Real World**

### **Real-Time Chat Applications** (WhatsApp Web, Slack, Messenger)
- Messages appear **instantly** without refreshing.  
- Supports **typing indicators**, **read receipts**, and **online status**.

---

### **Live Sports Scores / Match Updates**
- Scores and events are **pushed immediately** as they happen.

---

### **Stock Market Dashboards**
- Prices change **every second**.  
- WebSockets stream **live market ticks** efficiently.

---

### **Online Multiplayer Games**
- Player actions and movements sync **in real time** across users.

---

### **Collaborative Tools** (Google Docs, Whiteboards)
- Multiple users edit the **same document simultaneously**.

---

### **IoT Devices**
- Sensors send **continuous data streams**  
  (temperature, GPS, health metrics).

---

### **Live Notifications (E-commerce / Ticket Booking)**
- Order updates, ticket availability, and flash sales delivered **instantly**.

---

## **Summary**

**What’s happening**
"wb" → Write Binary mode

Used for non-text data (images, videos, audio)

Python writes raw bytes into the file

Why binary?
Images are not text. They are byte streams like:

￼Copy code
*WebSockets power systems where _speed_, _instant updates_, and _two-way communication_ are critical.**

---

# 1️⃣ Writing an Image File

```python
with open(f"{IMAGES_DIR}/non_blocking_img{i}.jpg", "wb") as f:
```

## What’s happening

- `"wb"` → Write Binary mode
- Used for non-text data (images, videos, audio)
- Python writes raw bytes into the file

## Why binary?

Images are not text. They are byte streams like:

```
\xff\xd8\xff\xe0\x00\x10JFIF...
```

If you use text mode → file gets corrupted.

## Typical use case

```python
f.write(image_bytes)
```

Used in:
- File uploads
- OpenCV image saving
- API image generation
- Streaming camera frames

# 2️⃣ Reading an HTML File

```python
with open("static/chat.html", "r") as f:
```

## What’s happening

- `"r"` → Read Text mode
- Used for readable text files
- Python reads it as a string

```python
html = f.read()
return HTMLResponse(html)
```

HTML is plain text:
```html
<h1>Hello</h1>
```

---

## FastAPI response handling.

FastAPI can return different response types depending on what you want the browser to do.

### 1️⃣ RedirectResponse

```python
return RedirectResponse(url="/users", status_code=303)
```

## What it does

👉 Tells the browser:

> “Go to another URL instead.”

The server does not send a page. It sends an instruction.

### Status Code 303

Means: See Other

Common after POST (form submission)

Prevents form resubmission on refresh

## Real Example

User submits a form →
Server saves data →
Redirect to /users page.

### 2️⃣ TemplateResponse

```python
return templates.TemplateResponse(
    "users.html",
    {"request": request, "users_list": users_list}
)
```

## What it does

👉 Renders an HTML template with backend data.

FastAPI:
- Loads users.html
- Injects variables
- Returns final HTML

This is Dynamic HTML

Inside template:

```jinja
{% for user in users_list %}
  <p>{{ user.name }}</p>
{% endfor %}
```

## Important

"`request`: request" is required by Jinja2 templates.

### 3️⃣ HTMLResponse

```python
return HTMLResponse(content=f.read(), status_code=200)
```

## What it does

👉 Sends raw HTML content to the browser.

No templating. No dynamic injection.

Just:

```html
<h1>Hello</h1>
```

## Used when

- Simple static HTML file
- No template engine
- Small demo apps

## Difference Summary

| Response        | Purpose                           | Dynamic? | Typical Use                 |
|------------------|----------------------------------|----------|------------------------------|
| RedirectResponse  | Send user to another URL         | ❌       | After form submission        |
| TemplateResponse  | Render HTML template             | ✅       | Pages with backend data      |
| HTMLResponse      | Send plain HTML                  | ❌       | Static/simple pages          |

## Flow Visualization

```
POST /create-user
    ↓
RedirectResponse → /users
    ↓
GET /users
    ↓
TemplateResponse → users.html with data
```

## One-line Summary

Redirect = move user, TemplateResponse = build HTML with data, HTMLResponse = send plain HTML.

---

- **Send data →** JSON  
- **Show page with data →** TemplateResponse  
- **Show simple HTML →** HTMLResponse  
- **Move user to another page →** RedirectResponse  

---