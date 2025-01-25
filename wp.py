from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os
import plotly.graph_objects as go
from urllib.parse import quote

class WeatherApp:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('WEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("API key is missing! Please set the WEATHER_API_KEY in the .env file.")

        self.weather_images = {
            "clear sky": "static/images/sunny.jpg",
            "few clouds": "static/images/partly_cloudy.jpg",
            "scattered clouds": "static/images/cloudy.jpg",
            "broken clouds": "static/images/broken_cloudy.jpg",
            "shower rain": "static/images/rainy_shower.jpg",
            "rain": "static/images/rainy.jpg",
            "thunderstorm": "static/images/thunderstorm.jpg",
            "snow": "static/images/snowy.jpg",
            "mist": "static/images/misty.jpg",
            "overcast clouds": "static/images/overcastcloud.jpg",
        }

    @staticmethod
    def kelvin_to_celsius(k):
        return k - 273.15

    def get_current_weather(self, city):
        url = f'http://api.openweathermap.org/data/2.5/weather?q={quote(city)}&appid={self.api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                'city': city.upper(),
                'description': data['weather'][0]['description'].capitalize(),
                'temp_c': f"{self.kelvin_to_celsius(data['main']['temp']):.2f}°C",
                'icon_url': f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@4x.png",
                'background_image': self.weather_images.get(data['weather'][0]['description'].lower(), "static/images/default.jpg")
            }
        return None

    def get_weather_forecast(self, city):
        url = f'http://api.openweathermap.org/data/2.5/forecast?q={quote(city)}&appid={self.api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            forecast = []
            temperatures = []
            dates = []

            for entry in data['list']:
                if entry['dt_txt'].endswith("12:00:00"):
                    date = entry['dt_txt'].split()[0]
                    temp = self.kelvin_to_celsius(entry['main']['temp'])
                    forecast.append({
                        'date': date,
                        'temp': f"{temp:.1f}°C",
                        'icon': f"http://openweathermap.org/img/wn/{entry['weather'][0]['icon']}@2x.png",
                        'description': entry['weather'][0]['description'].capitalize()
                    })
                    temperatures.append(temp)
                    dates.append(date)

            return forecast, dates, temperatures
        return [], [], []

    def generate_forecast_plot(self, dates, temperatures):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=temperatures,
            mode='lines+markers',
            name='Temperature',
            line=dict(color='orange', width=3),
            marker=dict(size=10, color='red')
        ))
        fig.update_layout(
            title='5-Day Temperature Forecast',
            xaxis_title='Date',
            yaxis_title='Temperature (°C)',
            template='plotly_dark',
            font=dict(family="Poppins, sans-serif", size=14),
            title_font=dict(size=20),
            paper_bgcolor='#1e2130',
            plot_bgcolor='#1e2130'
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255, 255, 255, 0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255, 255, 255, 0.2)')
        return fig.to_html(full_html=False, include_plotlyjs='cdn')


app = Flask(__name__)
weather_app = WeatherApp()

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    temp_forecast_plot = None
    weather_forecast = []
    error_message = None

    if request.method == "POST":
        city = request.form.get("city").strip()
        weather_data = weather_app.get_current_weather(city)

        if weather_data:
            weather_forecast, dates, temperatures = weather_app.get_weather_forecast(city)
            if dates and temperatures:
                temp_forecast_plot = weather_app.generate_forecast_plot(dates, temperatures)
        else:
            error_message = "City not found! Please try again."

    return render_template(
        "index.html",
        weather_data=weather_data,
        temp_forecast_plot=temp_forecast_plot,
        weather_forecast=weather_forecast,
        error_message=error_message
    )

if __name__ == "__main__":
    app.run(debug=True)
