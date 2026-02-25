import csv

def contains_letters(value: str) -> bool:
    return any(c.isalpha() for c in value)

# ================= IDX =================

def read_idx(filepath: str):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.readlines()

def extract_idx_points(lines):
    points = []
    in_points = False

    for line in lines:
        line = line.strip()

        if line.startswith("POINTS"):
            in_points = True
            continue

        if in_points:
            if line.startswith(")"):
                break

            if "MEAS;" not in line:
                continue

            parts = [p.strip().strip('"') for p in line.split(",")]

            try:
                pid = parts[1]
                x = float(parts[2])
                y = float(parts[3])
                z = float(parts[4]) if parts[4] != "" else 0.0
            except Exception:
                continue

            points.append({
                "raw_id": pid,
                "x": x,
                "y": y,
                "z": z
            })

    return points

def detect_resection_indices(ids):
    n = len(ids)
    resection_indices = set()
    i = 0

    while i < n:
        found = False
        for L in range(2, (n - i) // 2 + 1):
            if ids[i:i + L] == ids[i + L:i + 2 * L]:
                start = i
                end = i + 2 * L

                while end + L <= n and ids[end:end + L] == ids[start:start + L]:
                    end += L

                resection_indices.update(range(start, end))
                i = end
                found = True
                break

        if not found:
            i += 1

    return resection_indices

def clean_idx_points(points):
    ids = [p["raw_id"] for p in points]
    resection_idx = detect_resection_indices(ids)

    cleaned = []
    serial = 10000

    for idx, p in enumerate(points):
        if idx in resection_idx:
            continue

        raw_id = p["raw_id"]

        if contains_letters(raw_id):
            point_number = serial
            description = raw_id
            serial += 100
        else:
            point_number = raw_id
            description = ""

        cleaned.append({
            "point_number": point_number,
            "x": p["x"],
            "y": p["y"],
            "z": p["z"],
            "description": description
        })

    return cleaned

# ================= CSV =================

def read_csv(filepath: str):
    with open(filepath, newline="", encoding="utf-8", errors="ignore") as f:
        return list(csv.reader(f))

def clean_csv_points(rows):
    cleaned = []
    serial = 10000

    for row in rows:
        if len(row) < 4:
            continue

        raw_id, x, y, z = row[:4]

        try:
            x = float(x)
            y = float(y)
            z = float(z)
        except ValueError:
            continue

        if contains_letters(raw_id):
            point_number = serial
            description = raw_id
            serial += 100
        else:
            point_number = raw_id
            description = ""

        cleaned.append({
            "point_number": point_number,
            "x": x,
            "y": y,
            "z": z,
            "description": description
        })

    return cleaned

# ================= EXPORT =================

def export_txt(points, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for p in points:
            f.write(
                f"{p['point_number']}\t{p['x']}\t{p['y']}\t{p['z']}\t{p['description']}\n"
            )
