import json
import pandas as pd
from collections import defaultdict

# Load layout model JSON result from Azure Document Intelligence
with open("layout_result.json", "r", encoding="utf-8") as f:
    result = json.load(f)

# Select first page (you can loop over pages if needed)
page = result["pages"][0]

# Parameters
Y_TOLERANCE = 0.01  # Y-axis grouping tolerance for row alignment
X_GAP_THRESHOLD = 0.05  # X-axis spacing threshold to detect column split

# Step 1: Group lines by Y-position (to form rows)
rows = defaultdict(list)
for line in page.get("lines", []):
    y_top = line["polygon"][0]["y"]
    y_key = round(y_top / Y_TOLERANCE) * Y_TOLERANCE
    rows[y_key].append(line)

# Step 2: Process each row and group words by X-spacing
table_data = []

for y_key in sorted(rows.keys()):
    row_lines = rows[y_key]
    word_objs = []

    # Collect all words in this row
    for line in row_lines:
        word_objs.extend(line.get("words", []))

    # Sort words left to right
    word_objs.sort(key=lambda w: w["polygon"][0]["x"])

    # Build row with column breaks based on X-spacing
    prev_x = None
    row_data = []
    for word in word_objs:
        x = word["polygon"][0]["x"]
        if prev_x is not None and (x - prev_x) > X_GAP_THRESHOLD:
            row_data.append("")  # Add a new column
        row_data.append(word["content"])
        prev_x = x

    table_data.append(row_data)

# Step 3: Convert to DataFrame
df = pd.DataFrame(table_data)
print(df)
