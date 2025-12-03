from fastapi import FastAPI, Request, Form
from starlette.templating import Jinja2Templates
import httpx
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse, FileResponse
import xml.etree.ElementTree as ET
import csv


load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")


@app.get("/")
async def form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/search")
async def search(request: Request, query: str = Form(...), format: str = Form(...)):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": 10,
        "start": 1
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(search_url, params=params)
        data = r.json()

    items = data.get("items", [])
    items = list(items)  # ← pokud by náhodou byl set

    # pro JSON
    if format == "json":
        filename = "results.json"
        with open(filename, "w", encoding="utf-8") as f:
            import json
            json.dump(items, f, ensure_ascii=False, indent=4)
        return FileResponse(filename, media_type="application/json", filename=filename)


    # pro XML
    elif format == "xml":
        filename = "results.xml"
        roots = ET.Element("results")
        for item in items:
            result = ET.SubElement(roots, "result")
            title = ET.SubElement(result, "title")
            title.text = item.get("title", "")
            link = ET.SubElement(result, "link")
            link.text = item.get("link", "")
            snippet = ET.SubElement(result, "snippet")
            snippet.text = item.get("snippet", "")
        tree = ET.ElementTree(roots)
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        return FileResponse(filename, media_type="application/xml", filename=filename)
    
    # pro CSV
    if format == "csv":
        filename = "results.csv"
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Link", "Snippet"])
            for item in items:
                writer.writerow([item.get("title", ""), item.get("link", ""), item.get("snippet", "")])
        return FileResponse(filename, media_type="text/csv", filename=filename)
    else:
        return JSONResponse({"error": "Neznamy format"}, status_code=400)