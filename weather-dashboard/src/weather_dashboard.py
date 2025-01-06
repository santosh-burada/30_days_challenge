import os
import dotenv
import boto3
import logging
import requests
import json
from datetime import datetime

class weatherDashboard:
    def __init__(self):
        dotenv.load_dotenv()
        
        self.api_key = os.getenv('WEATHER_APIKEY')
        self.bucket_name = os.getenv('WEATHER_BUCKET_NAME')
        self.s3 = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
        print(f'API Key: {self.api_key}')
     
    def create_bucket_if_not_exists(self):
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
            print(f'Bucket {self.bucket_name} already exists')
        except Exception as e:
            print(f"Creating bucket {self.bucket_name}")
        try:
            self.s3.create_bucket(Bucket=self.bucket_name)
            print(f'Bucket {self.bucket_name} created')
        except Exception as e:
            print(f"Error creating bucket {self.bucket_name}")
            print(e)
    def fetch_weather_data(self, city):
        base_url = 'http://api.openweathermap.org/data/2.5/weather'
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            return None
    def save_to_s3(self, weather_data, city):
        """Save weather data to S3 bucket"""
        if not weather_data:
            return False
            
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        file_name = f"weather-data/{city}-{timestamp}.json"
        
        try:
            weather_data['timestamp'] = timestamp
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=json.dumps(weather_data),
                ContentType='application/json'
            )
            print(f"Successfully saved data for {city} to S3")
            return True
        except Exception as e:
            print(f"Error saving to S3: {e}")
            return False
    def save_local(self, weather_data, city):
        """Save weather data to local file"""
        if not weather_data:
            return False
            
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        directory = "data"
        file_name = f"{directory}/{city}-{timestamp}.json"
        
        try:
            weather_data['timestamp'] = timestamp
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(file_name, 'w') as f:
                json.dump(weather_data, f)
            print(f"Successfully saved data for {city} to {file_name}")
            return True
        except Exception as e:
            print(f"Error saving to {file_name}: {e}")
            return False
        

def main():
    dashboard = weatherDashboard()
    
    # Create bucket if needed
    dashboard.create_bucket_if_not_exists()
    
    cities = ["Fullerton", "Los Angeles", "New York"]
    
    for city in cities:
        print(f"\nFetching weather for {city}...")
        weather_data = dashboard.fetch_weather_data(city)
        if weather_data:
            temp = weather_data['main']['temp']
            feels_like = weather_data['main']['feels_like']
            humidity = weather_data['main']['humidity']
            description = weather_data['weather'][0]['description']
            
            print(f"Temperature: {temp}°F")
            print(f"Feels like: {feels_like}°F")
            print(f"Humidity: {humidity}%")
            print(f"Conditions: {description}")
            
            # Save to S3
            success = dashboard.save_to_s3(weather_data, city)
            if success:
                print(f"Weather data for {city} saved to S3!")

            # Save to local file
            success = dashboard.save_local(weather_data, city)
            if success:
                print(f"Weather data for {city} saved to local file!")
        else:
            print(f"Failed to fetch weather data for {city}")

if __name__ == '__main__':
    main()
