import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Sri Hanum Sastha Enterprises Website")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

site_dir = os.path.dirname(os.path.abspath(__file__))

# Mount the static site directly at root
app.mount("/", StaticFiles(directory=site_dir, html=True), name="site")

if __name__ == "__main__":
    print(f"Starting High-Performance Server at http://127.0.0.1:8080")
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")
