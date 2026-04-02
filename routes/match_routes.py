from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
import os
import json
from datetime import datetime
from utils.dependencies import templates
from utils import state
from models.match import Match
from utils.pdf_generator import generate_scorecard_pdf

router = APIRouter()

@router.post("/reset-match")
async def reset_match():
    state.current_match = None
    return RedirectResponse(url="/", status_code=303)

@router.post("/start-match")
async def start_match(
    team_a: str = Form(...),
    team_b: str = Form(...),
    overs: int = Form(...),
    match_mode: str = Form("double")
):
    state.current_match = Match(team_a, team_b, overs, match_mode)
    return RedirectResponse(url="/toss", status_code=303)

@router.get("/toss", response_class=HTMLResponse)
async def toss_page(request: Request):
    if not state.current_match:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("toss.html", {"request": request, "match": state.current_match})

@router.post("/toss-choice")
async def toss_choice(
    winner: str = Form(...),
    choice: str = Form(...)
):
    # Initialize batting/bowling team
    toss_winner_team = state.current_match.team_a if winner == "team_a" else state.current_match.team_b
    other_team = state.current_match.team_b if winner == "team_a" else state.current_match.team_a

    if choice == "bat":
        state.current_match.batting_team = toss_winner_team
        state.current_match.bowling_team = other_team
        state.current_match.toss_winner = toss_winner_team
    else:
        state.current_match.batting_team = other_team
        state.current_match.bowling_team = toss_winner_team
        state.current_match.toss_winner = toss_winner_team

    return RedirectResponse(url="/setup-players", status_code=303)

@router.get("/setup-players", response_class=HTMLResponse)
async def setup_players(request: Request):
    if not state.current_match:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("setup_players.html", {"request": request, "match": state.current_match})

@router.post("/initialize-players")
async def initialize_players(
    striker: str = Form(...),
    non_striker: str = Form(None),
    bowler: str = Form(...)
):
    state.current_match.striker = state.current_match.batting_team.get_player(striker)
    if state.current_match.match_mode == 'double' and non_striker:
        state.current_match.non_striker = state.current_match.batting_team.get_player(non_striker)
    else:
        state.current_match.non_striker = None
    
    state.current_match.current_bowler = state.current_match.bowling_team.get_player(bowler)
    return RedirectResponse(url="/match", status_code=303)

@router.get("/match", response_class=HTMLResponse)
async def match_screen(request: Request):
    if not state.current_match:
        return RedirectResponse(url="/")
    
    # Check if we need new players (after wicket or over)
    if not state.current_match.striker or (state.current_match.match_mode == 'double' and not state.current_match.non_striker):
         return RedirectResponse(url="/new-batsman", status_code=303)
    
    return templates.TemplateResponse("match.html", {"request": request, "match": state.current_match})

@router.post("/update-score")
async def update_score(action: str = Form(...), value: int = Form(0)):
    if state.current_match:
        state.current_match.update_score(action, value)
    
    if state.current_match.is_finished:
        return RedirectResponse(url="/scorecard", status_code=303)
    
    # Check if a new innings just started
    if state.current_match.current_innings == 2 and not state.current_match.striker:
         return RedirectResponse(url="/setup-players", status_code=303)

    # If over is completed, need a new bowler
    if state.current_match.batting_team.balls % 6 == 0 and action not in ["wide", "no_ball"] and state.current_match.batting_team.balls > 0:
         return RedirectResponse(url="/new-bowler", status_code=303)
    
    # If striker is out, need a new batsman
    if state.current_match.striker and state.current_match.striker.is_out:
         state.current_match.striker = None # Trigger selection
         return RedirectResponse(url="/new-batsman", status_code=303)

    return RedirectResponse(url="/match", status_code=303)

@router.get("/new-batsman", response_class=HTMLResponse)
async def new_batsman_page(request: Request):
    return templates.TemplateResponse("new_batsman.html", {"request": request, "match": state.current_match})

@router.post("/set-batsman")
async def set_batsman(name: str = Form(...)):
    state.current_match.striker = state.current_match.batting_team.get_player(name)
    return RedirectResponse(url="/match", status_code=303)

@router.get("/new-bowler", response_class=HTMLResponse)
async def new_bowler_page(request: Request):
    return templates.TemplateResponse("new_bowler.html", {"request": request, "match": state.current_match})

@router.post("/set-bowler")
async def set_bowler(name: str = Form(...)):
    state.current_match.current_bowler = state.current_match.bowling_team.get_player(name)
    return RedirectResponse(url="/match", status_code=303)

@router.get("/scorecard", response_class=HTMLResponse)
async def scorecard(request: Request):
    if not state.current_match:
         return RedirectResponse("/")
    return templates.TemplateResponse("scorecard.html", {"request": request, "match": state.current_match})

@router.get("/download-pdf")
async def download_pdf():
    if not state.current_match:
        raise HTTPException(status_code=400, detail="No match data found")
    
    pdf_buffer = generate_scorecard_pdf(state.current_match)
    filename = f"scorecard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/save-match")
async def save_match():
    if not state.current_match:
        return RedirectResponse("/")
    
    if not os.path.exists("matches"):
        os.makedirs("matches")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"matches/match_{timestamp}.json"
    data = state.current_match.to_dict()
    data["filename"] = f"match_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    
    # After saving, clear the current match so the home page shows "Start New Match"
    state.current_match = None
    return RedirectResponse("/", status_code=303)

@router.post("/discard-match")
async def discard_match():
    state.current_match = None
    return RedirectResponse("/", status_code=303)
