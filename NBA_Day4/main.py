from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
import os

class SerpAPIClient:

    """
    Client class to interact with the SerpAPI.
    """

    BASE_URL = "https://serpapi.com/search.json"

    def __init__(self, api_key:str):
        if not api_key:
            raise ValueError("API Key is required")
        self.api_key = api_key
    
    def fetch_nfl_schedule(self):
        """
        Fetches the NFL schedule from SerpAPI.
        """
        params = {
            "engine": "google",
            "q": "nfl schedule",
            "api_key": self.api_key
        }
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
class NFLScheduleService:
    """
    Service class to process NFL schedule data.
    """
    @staticmethod
    def format_games(data):
        """
        Formats the NFL schedule data into a list of games.
        """
        games = data.get("sports_results", {}).get("games", [])
        formatted_games = []

        for game in games:
            teams = game.get("teams", [])
            if len(teams) == 2:
                away_team = teams[0].get("name", "Unknown")
                home_team = teams[1].get("name", "Unknown")
            else:
                away_team, home_team = "Unknown", "Unknown"

            game_info = {
                "away_team": away_team,
                "home_team": home_team,
                "venue": game.get("venue", "Unknown"),
                "date": game.get("date", "Unknown"),
                "time": f"{game.get('time', 'Unknown')} ET" if game.get("time", "Unknown") != "Unknown" else "Unknown"
            }
            formatted_games.append(game_info)

        return formatted_games

app = FastAPI()

# Load API key from environment variables
SERP_API_KEY = os.getenv("SPORTS_API_KEY")
# Instantiate SerpAPIClient
serp_api_client = SerpAPIClient(api_key=SERP_API_KEY)

@app.get("/sports")
async def get_nfl_schedule():
    """
    Endpoint to fetch and return the NFL schedule.
    """
    try:
        data = serp_api_client.fetch_nfl_schedule()
        formatted_games = NFLScheduleService.format_games(data)

        if not formatted_games:
            return JSONResponse(content={"message": "No NFL schedule available.", "games": []}, status_code=200)

        return JSONResponse(content={"message": "NFL schedule fetched successfully.", "games": formatted_games}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "An error occurred.", "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)