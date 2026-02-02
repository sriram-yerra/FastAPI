 # BIG PICTURE
You built a Server-Side Rendered Web App using:
- FastAPI → backend web framework
- Jinja2 → HTML rendering  
- SQLModel → database ORM

User fills HTML form → data goes to FastAPI → stored in DB → redirected → users list shown.

---

## 🧱 IMPORTS (TOOLS YOU BROUGHT)

| Import | Why |
|--------|-----|
| FastAPI | Main app framework (not used here directly, router is) |
| APIRouter | Allows splitting routes into files |
| Depends | Injects dependencies (DB session here) |
| Session | DB connection |
| select | SQL query builder |
| Form | Reads HTML form inputs |
| Request | Needed for templates |
| Jinja2Templates | HTML rendering |
| HTMLResponse | Tells FastAPI to return HTML |
| RedirectResponse | Redirects browser to another URL |

---

## ROUTER SETUP
```
router = APIRouter()
```
 
This file is a mini app. Later in main.py you do:
```
app.include_router(router)
```
 
So these routes become part of your main app.

---

### DATABASE **SESSION INJECTION**
```
SessionDep = Annotated[Session, Depends(get_session)]
```
 

**What this means:**
Every route using:
```
session: SessionDep
```
 

FastAPI will:
1. Call `get_session()`
2. Create DB session  
3. Give it to function
4. Close after request

**This is called Dependency Injection.**

---

## **TEMPLATES ENGINE**
```
templates = Jinja2Templates(directory="app/templates")
```
 
This tells FastAPI: "My HTML files are inside app/templates"

## ROUTE 1 → SHOW REGISTER PAGE
```
@router.get("/", response_class=HTMLResponse)
```
 

**Meaning:**
| Part | Meaning |
|------|---------|
| `@router.get("/")` | When user visits homepage |
| `response_class=HTMLResponse` | This returns HTML, not JSON |

**Function:**
```
def register_form(request: Request):
```
 
**Parameter:** `request` - Required by Jinja templates

**Output:**
```
return templates.TemplateResponse("register.html", {"request": request})
```
 
Loads register.html and sends to browser.

**🧭 Flow:**
Browser → GET / → FastAPI → renders HTML → shows form

---

## 📝 ROUTE 2 → HANDLE FORM SUBMISSION
```
@router.post("/register")
```
 
Triggered when form submits.

**These inputs come from HTML form:**
```
name: str = Form(...)
email: str = Form(...)
phone: str = Form(...)
```
 

**Form(...) tells FastAPI:** "These values come from `<form>` input fields"

**Step 1** — Create user object
```
user = User(name=name, email=email, phone=phone)
```
 
Just creates a Python object.

**Step 2** — Check duplicate email
```
existing_user = session.exec(
select(User).where(User.email == user.email)
).first()
```
 
DB query: "Give me user where email matches"
If found → error

**Step 3** — Save to database
```
session.add(user)
session.commit()
```
 

| Step | What happens |
|------|--------------|
| `add()` | Adds to DB queue |
| `commit()` | Actually writes to DB |

**Step 4** — Redirect
```
return RedirectResponse(url="/users", status_code=303)
```
 
After success: Browser automatically goes to /users

---

## 👥 ROUTE 3 → SHOW USERS LIST
```
@router.get("/users", response_class=HTMLResponse)
```
 
When browser goes to /users.

**DB Fetch:**
```
users = session.exec(select(User)).all()
```
 
Gets all users.

**Render HTML:**
```
return templates.TemplateResponse(
"users.html",
{"request": request, "users": users}
)
```
 
Sends users list into template.

**Inside HTML:**
```
{% for user in users %}
```
 
Jinja loops through DB data.

## 🔁 COMPLETE WORKFLOW

1️⃣ Browser → GET /  
   ↓
2️⃣ FastAPI returns register.html form  
   ↓
3️⃣ User fills form + submits  
   ↓
4️⃣ POST /register  
   ↓
5️⃣ FastAPI reads Form data  
   ↓
6️⃣ Checks duplicate email  
   ↓
7️⃣ Saves user in DB  
   ↓
8️⃣ Redirects → /users  
   ↓
9️⃣ GET /users  
   ↓
🔟 FastAPI fetches users  
   ↓
11️⃣ users.html shows table

---

## 🧠 KEY CONCEPTS LEARNED

| Concept | You just used |
|---------|---------------|
| Server Side Rendering | Jinja2 |
| Dependency Injection | Depends |
| Form handling | Form() |
| ORM queries | select() |
| Redirect after POST | RedirectResponse |
| Templates | TemplateResponse |

---

## 🔥 OUTPUT TYPE OF EACH ROUTE

| Route | Input | Output |
|-------|-------|--------|
| `/` | None | HTML form |
| `/register` | Form data | Redirect |
| `/users` | None | HTML table |

**If you want, next I can show:**
How to add flash messages (success/error) like real websites