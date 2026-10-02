from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from google import genai
from google.genai import types
import uuid
import html

app = FastAPI(title="PocketSmartAI")
client = genai.Client()

users = {}
sessions = {}
history = {}


def fallback(category):
    if category == "home":
        return (
            "Fallback Home Interior Recommendation\n\n"
            "1. Wall Decor - ₹1,000 to ₹2,000\n"
            "Simple wall decor can improve the room appearance.\n\n"
            "2. Lighting - ₹1,000 to ₹2,000\n"
            "Warm LED lighting gives a comfortable look.\n\n"
            "3. Curtains - ₹1,500 to ₹2,500\n"
            "Choose curtains matching the room style.\n\n"
            "4. Storage - ₹2,000 to ₹3,000\n"
            "Use compact storage organizers.\n\n"
            "5. Budget Saving\n"
            "Prefer multipurpose furniture and simple DIY decoration."
        )
    if category == "party":
        return (
            "Fallback Party Recommendation\n\n"
            "1. Decoration - ₹2,000 to ₹3,000\n"
            "Use balloons, banners and LED lights.\n\n"
            "2. Food - ₹4,000 to ₹5,000\n"
            "Choose a simple menu according to the guest count.\n\n"
            "3. Entertainment - ₹1,000 to ₹2,000\n"
            "Use music and simple party games.\n\n"
            "4. Venue - ₹0 to ₹5,000\n"
            "A home venue can reduce expenses.\n\n"
            "5. Budget Saving\n"
            "Use reusable decorations and compare local food packages."
        )
    return (
        "Fallback Jewelry Recommendation\n\n"
        "1. Necklace - ₹4,000 to ₹5,000\n"
        "Traditional necklace suitable for wedding occasions.\n\n"
        "2. Earrings - ₹1,500 to ₹2,000\n"
        "Matching traditional earrings.\n\n"
        "3. Bangles - ₹500 to ₹1,000\n"
        "Simple matching bangles.\n\n"
        "4. Ring - ₹500 to ₹1,000\n"
        "Minimal traditional ring.\n\n"
        "5. Budget Saving\n"
        "Choose lightweight jewellery sets and matching combinations."
    )


def add_history(username, category, details, result):
    history.setdefault(username, []).append({
        "category": category,
        "details": details,
        "result": result,
    })


def current_user():
    if sessions:
        return list(sessions.values())[-1]
    if users:
        return list(users.keys())[-1]
    return "guest"


def ai_call(prompt, category, image_bytes=None, mime_type=None):
    try:
        contents = [prompt]
        if image_bytes:
            contents.append(types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type or "image/jpeg"
            ))
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contents
        )
        return response.text
    except Exception as exc:
        text = str(exc)
        if (
            "429" in text
            or "RESOURCE_EXHAUSTED" in text
            or "503" in text
            or "UNAVAILABLE" in text
        ):
            return fallback(category)
        return "AI Error: " + text


def page(title, body):
    return f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>{html.escape(title)}</title>
<style>
body{{font-family:Arial,sans-serif;background:linear-gradient(135deg,#fdf2f8,#eef2ff);margin:0;padding:30px}}
.box{{max-width:900px;margin:auto;background:#fff;padding:30px;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,.12)}}
h1{{text-align:center;color:#4f46e5}}h2{{color:#222}}
.nav{{display:flex;flex-wrap:wrap;justify-content:center;gap:10px;margin:25px 0}}
.nav a{{display:inline-block;padding:12px 16px;border-radius:10px;background:#4f46e5;color:#fff;text-decoration:none}}
.nav a:hover{{background:#3730a3}}
input{{width:100%;padding:12px;margin:8px 0 14px;box-sizing:border-box;border:1px solid #ddd;border-radius:8px}}
button{{padding:12px 18px;border:0;border-radius:10px;background:#16a34a;color:#fff;cursor:pointer}}
.card{{background:#f8fafc;padding:20px;border-radius:12px;margin-top:20px;white-space:pre-wrap;line-height:1.6}}
.small{{color:#666;font-size:13px}}
</style></head>
<body><div class='box'>
<h1>💰 PocketSmartAI</h1>
<p style='text-align:center;color:#666'>Smart Budget & Recommendation Assistant</p>
<div class='nav'>
<a href='/register-page'>Register</a>
<a href='/login-page'>Login</a>
<a href='/dashboard'>📊 Dashboard</a>
<a href='/history-page'>📜 History</a>
<a href='/home-page'>🏠 Home Interior</a>
<a href='/party-page'>🎉 Party Planning</a>
<a href='/jewelry-page'>💎 Jewelry Recommendation</a>
<a href='/logout-page'>Logout</a>
</div>
{body}
</div></body></html>"""


@app.get("/", response_class=HTMLResponse)
def home():
    body = "<h2>Welcome to PocketSmartAI</h2><p>Select a feature above.</p>"
    return HTMLResponse(page("PocketSmartAI", body))


@app.get("/register-page", response_class=HTMLResponse)
def register_page():
    body = """
<h2>📝 Register</h2>
<form action='/register' method='post'>
<input name='username' placeholder='Username' required>
<input name='password' type='password' placeholder='Password' required>
<button type='submit'>Create Account</button>
</form>"""
    return HTMLResponse(page("Register", body))


@app.get("/login-page", response_class=HTMLResponse)
def login_page():
    body = """
<h2>🔐 Login</h2>
<form action='/login' method='post'>
<input name='username' placeholder='Username' required>
<input name='password' type='password' placeholder='Password' required>
<button type='submit'>Login</button>
</form>"""
    return HTMLResponse(page("Login", body))


@app.get("/home-page", response_class=HTMLResponse)
def home_page():
    body = """
<h2>🏠 Home Interior Planner</h2>
<form action='/home-page' method='post'>
<input name='budget' type='number' placeholder='Budget (₹)' required>
<input name='room_type' placeholder='Room type' required>
<input name='preferences' placeholder='Preferences' required>
<button type='submit'>Get AI Recommendations</button>
</form>"""
    return HTMLResponse(page("Home Interior", body))


@app.post("/home-page", response_class=HTMLResponse)
def home_page_submit(budget: float = Form(...), room_type: str = Form(...), preferences: str = Form(...)):
    result = ai_call(
        f"You are PocketSmart AI. Budget ₹{budget}. Room type: {room_type}. Preferences: {preferences}. Give 5 practical home interior recommendations with estimated prices and budget-saving suggestions.",
        "home"
    )
    add_history(
        current_user(),
        "Home Interior",
        f"Budget ₹{budget}, Room: {room_type}, Preferences: {preferences}",
        result,
    )
    body = (
        "<h2>🏠 Home Interior Recommendations</h2>"
        f"<div class='card'>{html.escape(result)}</div>"
        "<p><a href='/home-page'>← Back</a></p>"
    )
    return HTMLResponse(page("Home Recommendations", body))


@app.get("/party-page", response_class=HTMLResponse)
def party_page():
    body = """
<h2>🎉 Party Planner</h2>
<form action='/party-page' method='post'>
<input name='budget' type='number' placeholder='Budget (₹)' required>
<input name='guest_count' type='number' placeholder='Number of guests' required>
<input name='event_type' placeholder='Event type' required>
<input name='venue' placeholder='Venue' required>
<button type='submit'>Get AI Recommendations</button>
</form>"""
    return HTMLResponse(page("Party Planning", body))


@app.post("/party-page", response_class=HTMLResponse)
def party_page_submit(budget: float = Form(...), guest_count: int = Form(...), event_type: str = Form(...), venue: str = Form(...)):
    result = ai_call(
        f"You are PocketSmart AI. Budget ₹{budget}. Guests: {guest_count}. Event: {event_type}. Venue: {venue}. Give a practical party plan with decoration, food, entertainment, estimated costs and budget-saving suggestions.",
        "party"
    )
    add_history(
        current_user(),
        "Party Planning",
        f"Budget ₹{budget}, Guests: {guest_count}, Event: {event_type}, Venue: {venue}",
        result,
    )
    body = (
        "<h2>🎉 Party Recommendations</h2>"
        f"<div class='card'>{html.escape(result)}</div>"
        "<p><a href='/party-page'>← Back</a></p>"
    )
    return HTMLResponse(page("Party Recommendations", body))


@app.get("/jewelry-page", response_class=HTMLResponse)
def jewelry_page():
    body = """
<h2>💎 Jewelry Recommendation</h2>
<form action='/jewelry-page' method='post' enctype='multipart/form-data'>
<input name='budget' type='number' placeholder='Budget (₹)' required>
<input name='jewelry_type' placeholder='Jewelry type' required>
<input name='occasion' placeholder='Occasion' required>
<input name='preferences' placeholder='Preferences' required>
<input name='outfit_image' type='file' accept='image/*'>
<p class='small'>Outfit image is optional.</p>
<button type='submit'>Get AI Recommendations</button>
</form>"""
    return HTMLResponse(page("Jewelry Recommendation", body))


@app.post("/jewelry-page", response_class=HTMLResponse)
async def jewelry_page_submit(
    budget: float = Form(...),
    jewelry_type: str = Form(...),
    occasion: str = Form(...),
    preferences: str = Form(...),
    outfit_image: UploadFile | None = File(None),
):
    image_bytes = None
    mime_type = None
    uploaded = False
    if outfit_image is not None and outfit_image.filename:
        image_bytes = await outfit_image.read()
        mime_type = outfit_image.content_type
        uploaded = True
    prompt = f"You are PocketSmart AI. Budget ₹{budget}. Jewelry type: {jewelry_type}. Occasion: {occasion}. Preferences: {preferences}. Recommend 5 suitable jewellery options with estimated prices and budget-saving suggestions."
    if image_bytes:
        prompt += " Consider the uploaded outfit image for colour and style matching."
    result = ai_call(prompt, "jewelry", image_bytes, mime_type)
    add_history(
        current_user(),
        "Jewelry Recommendation",
        f"Budget ₹{budget}, Type: {jewelry_type}, Occasion: {occasion}, Preferences: {preferences}, Image: {'Yes' if uploaded else 'No'}",
        result,
    )
    body = (
        "<h2>💎 Jewelry Recommendations</h2>"
        f"<p><b>Image uploaded:</b> {'Yes' if uploaded else 'No'}</p>"
        f"<div class='card'>{html.escape(result)}</div>"
        "<p><a href='/jewelry-page'>← Back</a></p>"
    )
    return HTMLResponse(page("Jewelry Recommendations", body))


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    body = """
<h2>📊 User Dashboard</h2>
<p><b>Username:</b> loga</p>
<p><b>Saved Recommendations:</b> Available</p>
<p>Your PocketSmartAI dashboard is ready.</p>"""
    return HTMLResponse(page("Dashboard", body))


@app.get("/history-page", response_class=HTMLResponse)
def history_page():
    username = current_user()
    records = history.get(username, [])
    if not records:
        body = (
            "<h2>📜 Recommendation History</h2>"
            f"<p><b>Username:</b> {html.escape(username)}</p>"
            "<p>No saved recommendations yet.</p>"
        )
    else:
        cards = [
            f"<div class='card'><b>{html.escape(item['category'])}</b><br>"
            f"{html.escape(item['details'])}<br><br>"
            f"{html.escape(item['result'])}</div>"
            for item in records
        ]
        body = (
            "<h2>📜 Recommendation History</h2>"
            f"<p><b>Username:</b> {html.escape(username)}</p>"
            + "".join(cards)
        )
    return HTMLResponse(page("History", body))


@app.get("/logout-page", response_class=HTMLResponse)
def logout_page():
    return HTMLResponse(page("Logout", "<h2>Logout</h2><p>You can continue browsing PocketSmartAI.</p>"))


@app.post("/generate-home")
def generate_home(budget: float, room_type: str, preferences: str):
    result = ai_call(
        f"You are PocketSmart AI. Budget ₹{budget}. Room type: {room_type}. Preferences: {preferences}. Give 5 practical home interior recommendations.",
        "home"
    )
    add_history(
        current_user(),
        "Home Interior",
        f"Budget ₹{budget}, Room: {room_type}, Preferences: {preferences}",
        result,
    )
    return {"category": "Home Interior", "recommendations": result}


@app.post("/generate-party")
def generate_party(budget: float, guest_count: int, event_type: str, venue: str):
    result = ai_call(
        f"You are PocketSmart AI. Budget ₹{budget}. Guests: {guest_count}. Event: {event_type}. Venue: {venue}. Give a practical party plan.",
        "party"
    )
    add_history(
        current_user(),
        "Party Planning",
        f"Budget ₹{budget}, Guests: {guest_count}, Event: {event_type}, Venue: {venue}",
        result,
    )
    return {"category": "Party Planning", "recommendations": result}


@app.post("/generate-jewelry")
async def generate_jewelry(
    budget: float = Form(...),
    jewelry_type: str = Form(...),
    occasion: str = Form(...),
    preferences: str = Form(...),
    outfit_image: UploadFile | None = File(None),
):
    image_bytes = None
    mime_type = None
    if outfit_image is not None and outfit_image.filename:
        image_bytes = await outfit_image.read()
        mime_type = outfit_image.content_type
    prompt = f"You are PocketSmart AI. Budget ₹{budget}. Jewelry type: {jewelry_type}. Occasion: {occasion}. Preferences: {preferences}. Recommend 5 suitable jewellery options."
    if image_bytes:
        prompt += " Consider the uploaded outfit image for colour and style matching."
    result = ai_call(prompt, "jewelry", image_bytes, mime_type)
    add_history(
        current_user(),
        "Jewelry Recommendation",
        f"Budget ₹{budget}, Type: {jewelry_type}, Occasion: {occasion}, Preferences: {preferences}, Image: {'Yes' if image_bytes is not None else 'No'}",
        result,
    )
    return {"category": "Jewelry Recommendation", "recommendations": result, "image_uploaded": image_bytes is not None}


@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    if username in users:
        return HTMLResponse(page("Register", "<h2>Registration</h2><p>Username already exists.</p><p><a href='/register-page'>← Back</a></p>"), status_code=400)
    users[username] = password
    history.setdefault(username, [])
    return HTMLResponse(page("Register", f"<h2>Registration successful</h2><p>Welcome, {html.escape(username)}.</p><p><a href='/login-page'>Go to Login</a></p>"))


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username not in users:
        return HTMLResponse(page("Login", "<h2>Login</h2><p>User not found.</p><p><a href='/login-page'>← Back</a></p>"), status_code=401)
    if users[username] != password:
        return HTMLResponse(page("Login", "<h2>Login</h2><p>Invalid password.</p><p><a href='/login-page'>← Back</a></p>"), status_code=401)
    token = str(uuid.uuid4())
    sessions[token] = username
    return HTMLResponse(page("Login", f"<h2>Login successful</h2><p>Welcome, {html.escape(username)}.</p><p><a href='/dashboard'>Open Dashboard</a></p>"))


@app.post("/logout")
def logout(token: str):
    sessions.pop(token, None)
    return {"message": "Logout successful"}


@app.get("/session-info")
def session_info(token: str):
    if token not in sessions:
        return {"logged_in": False}
    return {"logged_in": True, "username": sessions[token]}


@app.get("/session-data")
def session_data(token: str):
    if token not in sessions:
        return JSONResponse(status_code=401, content={"message": "Please login first"})
    username = sessions[token]
    return {"username": username, "history": history.get(username, [])}


@app.get("/history")
def get_history(token: str):
    if token not in sessions:
        return JSONResponse(status_code=401, content={"message": "Please login first"})
    username = sessions[token]
    return {"username": username, "history": history.get(username, [])}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
