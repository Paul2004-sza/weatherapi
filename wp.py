from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os
import plotly.graph_objects as go
from urllib.parse import quote

app = Flask(__name__)

load_dotenv()
my_api = os.getenv('WEATHER_API_KEY')
if not my_api:
    raise ValueError("API key is missing! Please set the WEATHER_API_KEY in the .env file.")

weather_images = {
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


def kelvin_to_celsius(k):
    return k - 273.15

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    temp_forecast_plot = None
    weather_forecast = []
    error_message = None

    if request.method == "POST":
        city = request.form.get("city").strip()
        city_encoded = quote(city)

        current_weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city_encoded}&appid={my_api}'
        response = requests.get(current_weather_url)

        if response.status_code == 200:
            weather_data = response.json()
            temperature = weather_data['main']['temp']
            temp_c = f"{kelvin_to_celsius(temperature):.2f}°C"
            description = weather_data['weather'][0]['description'].capitalize()
            icon_code = weather_data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@4x.png"
            background_image = weather_images.get(weather_data['weather'][0]['description'].lower(), "static/images/default.jpg")

            weather_data = {
                'city': city.upper(),
                'description': description,
                'temp_c': temp_c,
                'icon_url': icon_url,
                'background_image': background_image
            }

            forecast_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city_encoded}&appid={my_api}'
            forecast_response = requests.get(forecast_url)
            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()

                temperatures = []
                dates = []
                for entry in forecast_data['list']:
                    if entry['dt_txt'].endswith("12:00:00"):
                        date = entry['dt_txt'].split()[0]
                        temp = kelvin_to_celsius(entry['main']['temp'])  # Convert to Celsius
                        weather_forecast.append({
                            'date': date,
                            'temp': f"{temp:.1f}°C",
                            'icon': f"http://openweathermap.org/img/wn/{entry['weather'][0]['icon']}@2x.png",
                            'description': entry['weather'][0]['description'].capitalize()
                        })
                        temperatures.append(temp)
                        dates.append(date)

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

                temp_forecast_plot = fig.to_html(full_html=False, include_plotlyjs='cdn')
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
