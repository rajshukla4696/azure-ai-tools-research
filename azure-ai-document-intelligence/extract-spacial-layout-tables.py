import pandas as pd
from collections import defaultdict
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

# Azure setup
endpoint = "<your-endpoint>"
key = "<your-key>"
client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# Open document and get layout
with open("whitepaper.pdf", "rb") as f:
    poller = client.begin_analyze_document("prebuilt-layout", f)
    result = poller.result()

lines = result.pages[0].lines
tolerance = 0.01  # Group lines based on Y-axis tolerance
rows = defaultdict(list)

# Group lines by Y-coordinate
for line in lines:
    y_top = line.polygon[0].y
    y_key = round(y_top / tolerance) * tolerance
    rows[y_key].append(line)

# Sort rows and process columns using X-axis spacing
table_data = []
for y_key in sorted(rows.keys()):
    row = rows[y_key]
    words = []
    for line in row:
        words.extend(line.words)
    words.sort(key=lambda w: w.polygon[0].x)

    prev_x = None
    row_data = []
    for word in words:
        x = word.polygon[0].x
        if prev_x and (x - prev_x) > 0.05:
            row_data.append("|")  # Mark column breaks
        row_data.append(word.content)
        prev_x = x
    table_data.append(row_data)

# Convert to DataFrame
df = pd.DataFrame(table_data)
print(df)
