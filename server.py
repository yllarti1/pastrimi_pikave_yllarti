from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import os, tempfile

from processor import (
    read_idx, extract_idx_points, clean_idx_points,
    read_csv, clean_csv_points, export_txt
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/process")
async def process(file: UploadFile = File(...)):
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".idx", ".csv"]:
        raise HTTPException(status_code=400, detail="Vetem .idx ose .csv")

    with tempfile.TemporaryDirectory() as td:
        in_path = os.path.join(td, "input" + ext)
        out_path = os.path.join(td, "output_clean.txt")

        content = await file.read()
        with open(in_path, "wb") as f:
            f.write(content)

        # PASTRIMI 1:1 si programi yt
        if ext == ".idx":
            lines = read_idx(in_path)
            points = extract_idx_points(lines)
            cleaned = clean_idx_points(points)
        else:
            rows = read_csv(in_path)
            cleaned = clean_csv_points(rows)

        export_txt(cleaned, out_path)

        with open(out_path, "rb") as f:
            out_bytes = f.read()

        return Response(
            content=out_bytes,
            media_type="text/plain",
            headers={"Content-Disposition": 'attachment; filename="clean.txt"'}
        )
