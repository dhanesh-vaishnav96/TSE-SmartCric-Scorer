from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
import os
import json
from datetime import datetime
from utils.dependencies import templates
from utils import state
from models.match import Match
from utils.pdf_generator import generate_scorecard_pdf

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    saved_matches = []
    if os.path.exists("matches"):
        for filename in os.listdir("matches"):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join("matches", filename), "r") as f:
                        data = json.load(f)
                        saved_matches.append({
                            "filename": filename,
                            "team_a": data["team_a"]["name"],
                            "team_b": data["team_b"]["name"],
                            "team_a_score": f"{data['team_a']['runs']}/{data['team_a']['wickets']}",
                            "team_b_score": f"{data['team_b']['runs']}/{data['team_b']['wickets']}",
                            "status": data.get("status_message", "Finished"),
                            "date": datetime.fromtimestamp(os.path.getmtime(os.path.join("matches", filename))).strftime("%Y-%m-%d %H:%M")
                        })
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    # Sort by date descending
    saved_matches.sort(key=lambda x: x["date"], reverse=True)

    is_in_progress = state.current_match is not None and not state.current_match.is_finished
    
    return templates.TemplateResponse(
        request=request,
        name="index.html", 
        context={
            "match": state.current_match, 
            "saved_matches": saved_matches,
            "is_in_progress": is_in_progress
        }
    )

@router.get("/view-saved-match/{filename}", response_class=HTMLResponse)
async def view_saved_match(request: Request, filename: str):
    file_path = os.path.join("matches", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Match not found")
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            match_obj = Match.from_dict(data)
            return templates.TemplateResponse(
                request=request,
                name="scorecard.html", 
                context={
                    "match": match_obj, 
                    "is_saved_view": True,
                    "match_filename": filename
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading match: {str(e)}")

@router.get("/download-saved-pdf/{filename}")
async def download_saved_pdf(filename: str):
    file_path = os.path.join("matches", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Match not found")
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            match_obj = Match.from_dict(data)
            pdf_buffer = generate_scorecard_pdf(match_obj)
            return StreamingResponse(
                pdf_buffer,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=scorecard_{filename.replace('.json', '.pdf')}"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@router.post("/delete-match/{filename}")
async def delete_match(filename: str):
    file_path = os.path.join("matches", filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return RedirectResponse(url="/", status_code=303)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting match: {str(e)}")
    raise HTTPException(status_code=404, detail="Match not found")
