from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import uvicorn

# Import your route file
from routes import travel

# Create FastAPI app
app = FastAPI(title="Smart Travel Planner")

# ✅ Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Set up templates folder
templates = Jinja2Templates(directory="templates")

# ✅ Include your backend routes
app.include_router(travel.router, prefix="/api")

# ✅ Homepage route (renders index.html)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ✅ Optional health check route
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Smart Travel Planner is running"}

# ✅ Only run with uvicorn when executed directly (for local development)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)