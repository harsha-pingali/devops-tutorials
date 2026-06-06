from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# mount static files (for minimal CSS if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=FileResponse)
def read_root():
    """Return the static templates/index.html file."""
    html_path = Path(__file__).resolve().parent / "templates" / "index.html"
    return FileResponse(html_path)
