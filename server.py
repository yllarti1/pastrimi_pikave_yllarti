from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile

# Importo funksionet nga processor.py (duhet të jetë në të njëjtin repo)
from processor import (
    read_idx,
    extract_idx_points,
    clean_idx_points,
    read_csv,
    clean_csv_points,
    export_txt,
)

app = FastAPI(title="Pastrimi i Pikave (IDX/CSV)")

# CORS: për momentin lejoje për të gjithë; më vonë e bëjmë vetëm për domain-in e web app-it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/process")
async def process(file: UploadFile = File(...)):
    filename = (file.filename or "").strip()
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".idx", ".csv"]:
        raise HTTPException(status_code=400, detail="Lejohen vetem .idx ose .csv")

    # Emri i file-it që do kthehet: <orig>_clean.txt
    base_name = os.path.splitext(os.path.basename(filename))[0] or "file"
    clean_name = f"{base_name}_clean.txt"

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Skedari eshte bosh")

    with tempfile.TemporaryDirectory() as td:
        in_path = os.path.join(td, "input" + ext)
        out_path = os.path.join(td, clean_name)

        # ruaj input-in
        with open(in_path, "wb") as f:
            f.write(content)

        # perpunimi 1:1 si programi yt
        try:
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

        except Exception as e:
            # Kjo del në Render logs dhe të ndihmon për debug
            raise HTTPException(status_code=500, detail=f"Gabim gjate perpunimit: {str(e)}")

    return Response(
        content=out_bytes,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{clean_name}"'
        },
    )
