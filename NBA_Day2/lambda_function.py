import os
import json
import requests
import boto3
from datetime import datetime, timedelta, timezone
import logging
# this two imports are required when running the code in aws lambda. Because I zipped the dependencies into a package folder and uploaded it to the lambda function.
# import sys
# sys.path.append('./package') 

logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
def format_game_data(game):
    game_id = game['GameID']
    home_team = game['HomeTeam']
    away_team = game['AwayTeam']
    home_score = game['HomeTeamScore']
    away_score = game['AwayTeamScore']
    game_status = game['Status']
    game_date = game['DateTime']
    channel = game['Channel']
    final_score = f"{away_score}-{home_score}"

    quarters = game["Quarters"]
    quarter_scores = ', '.join([f"Q{q['Number']}: {q.get('AwayScore', 'N/A')}-{q.get('HomeScore', 'N/A')}" for q in quarters])

    if game_status == "Final":
        return (
            f"Game Status: {game_status}\n"
            f"{away_team} vs {home_team}\n"
            f"Final Score: {final_score}\n"
            f"Start Time: {game_date}\n"
            f"Channel: {channel}\n"
            f"Quarter Scores: {quarter_scores}\n"
        )
    elif game_status == "InProgress":
        last_play = game["LastPlay"]
        return (
            f"Game Status: {game_status}\n"
            f"{away_team} vs {home_team}\n"
            f"Current Score: {final_score}\n"
            f"Last Play: {last_play}\n"
            f"Channel: {channel}\n"
        )
    elif game_status == "Scheduled":
        return (
            f"Game Status: {game_status}\n"
            f"{away_team} vs {home_team}\n"
            f"Start Time: {game_date}\n"
            f"Channel: {channel}\n"
        )
    else:
        return (
            f"Game Status: {game_status}\n"
            f"{away_team} vs {home_team}\n"
            f"Details are unavailable at the moment.\n"
        )
def lambda_handler(event, context):
    api_key = os.environ['NBA_API_KEY']
    sns_topic = os.environ['SNS_TOPIC_ARN']
    sns_client = boto3.client('sns')

    utc_now = datetime.now(timezone.utc)
    ps_time = utc_now - timedelta(hours=8)
    today = ps_time.strftime('%Y-%m-%d')

    logging.info(f"Fetching games for date: {today}")

    api_url = f"https://api.sportsdata.io/v3/nba/scores/json/GamesByDate/{today}?key={api_key}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        games = response.json()
        logging.info(f"Games fetched: {games}")
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return {
            'statusCode': 500,
            'body': json.dumps(f'Internal Server Error: {e}')
        }

    messages = [format_game_data(game) for game in games]
    final_message = "\n---\n".join(messages) if messages else "No games available for today."
    try:
        sns_client.publish(
            TopicArn=sns_topic,
            Message=final_message,
            Subject="NBA Game Updates"
        )
        print("Message published to SNS successfully.")
    except Exception as e:
        logging.error(f"Error publishing to SNS: {e}")
        return {"statusCode": 500, "body": "Error publishing to SNS"}
    
    return {"statusCode": 200, "body": "Data processed and sent to SNS"}
