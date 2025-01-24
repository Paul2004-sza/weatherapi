from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import io
import base64
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


def kelvin_to_fahrenheit(k):
    return (kelvin_to_celsius(k) * 9 / 5) + 32


@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    prediction_plot = None
    weather_image = None
    icon_url = None

    if request.method == "POST":
        city = request.form.get("city").strip()


        city_encoded = quote(city)


        url = f'http://api.openweathermap.org/data/2.5/weather?q={city_encoded}&appid={my_api}'
        response = requests.get(url)

        if response.status_code == 200:
            weather_data = response.json()
            temperature = weather_data['main']['temp']
            tem_c = kelvin_to_celsius(temperature)  # Convert Kelvin to Celsius
            temp_c = f"{tem_c:.2f}°C"
            tem_f = kelvin_to_fahrenheit(temperature)  # Convert to Fahrenheit
            temp_f = f"{tem_f:.2f}°F"
            description = weather_data['weather'][0]['description'].capitalize()
            icon_code = weather_data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@4x.png"
            weather_image = weather_images.get(description.lower(), "static/images/default.jpg")

            weather_data = {
                'city': city.upper(),
                'description': description,
                'temp_c': temp_c,
                'temp_f': temp_f,
                'icon_url': icon_url
            }

            # Fetch 5-day forecast data
            forecast_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city_encoded}&appid={my_api}'
            forecast_response = requests.get(forecast_url)
            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                # Extract temperature data for prediction (next 5 days)
                temperatures = []
                dates = []
                for entry in forecast_data['list']:
                    # We take one data point per day (12 PM)
                    if entry['dt_txt'].endswith("12:00:00"):
                        date = entry['dt_txt'].split()[0]
                        temp = kelvin_to_celsius(entry['main']['temp'])  # Convert to Celsius
                        temperatures.append(temp)
                        dates.append(date)


                fig, ax = plt.subplots()
                ax.plot(dates, temperatures, marker='o', linestyle='-', color='#4CAF50', linewidth=2)
                ax.set(xlabel='Date', ylabel='Temperature (°C)', title=f'Temperature Predictions for {city}')
                ax.grid(True, linestyle='--', alpha=0.5)


                for i, temp in enumerate(temperatures):
                    ax.text(dates[i], temp, f"{temp:.1f}°C", fontsize=9, ha='center', va='bottom')

                plt.xticks(rotation=45)
                plt.tight_layout()


                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                plot_url = base64.b64encode(img.getvalue()).decode('utf8')
                prediction_plot = f"data:image/png;base64,{plot_url}"
        else:
            weather_data = {'error': "Error fetching weather data. Please check the city name!"}

    return render_template("index.html", weather_data=weather_data, prediction_plot=prediction_plot,
                           weather_image=weather_image, icon_url=icon_url)


if __name__ == "__main__":
    app.run(debug=True)
