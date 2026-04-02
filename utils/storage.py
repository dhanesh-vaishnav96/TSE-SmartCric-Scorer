import os
import json
import config
from datetime import datetime
from models.match import Match

def get_all_matches():
    saved_matches = []
    if os.path.exists(config.MATCHES_DIR):
        for filename in os.listdir(config.MATCHES_DIR):
            if filename.endswith(".json"):
                try:
                    file_path = os.path.join(config.MATCHES_DIR, filename)
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        saved_matches.append({
                            "filename": filename,
                            "team_a": data["team_a"]["name"],
                            "team_b": data["team_b"]["name"],
                            "team_a_score": f"{data['team_a']['runs']}/{data['team_a']['wickets']}",
                            "team_b_score": f"{data['team_b']['runs']}/{data['team_b']['wickets']}",
                            "status": data.get("status_message", "Finished"),
                            "date": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M")
                        })
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    # Sort by date descending
    saved_matches.sort(key=lambda x: x["date"], reverse=True)
    return saved_matches

def save_match_data(match_obj):
    if not os.path.exists(config.MATCHES_DIR):
        os.makedirs(config.MATCHES_DIR)
    
    filename = f"match_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    file_path = os.path.join(config.MATCHES_DIR, filename)
    with open(file_path, "w") as f:
        json.dump(match_obj.to_dict(), f, indent=4)
    return filename

def load_match_from_file(filename):
    file_path = os.path.join(config.MATCHES_DIR, filename)
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return Match.from_dict(data)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None
