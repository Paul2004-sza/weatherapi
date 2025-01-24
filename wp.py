import customtkinter as ctk
from PIL import Image
import requests
import io

class WeatherApp:
    def __init__(self, root):
        self.root = root  # Store the root window as an instance variable
        ctk.set_appearance_mode("dark")
        root.geometry("600x400")
        root.title("WEATHER DATA")

        self.title_label = ctk.CTkLabel(root, text="Weather Data", font=ctk.CTkFont(size=30, weight="bold"))
        self.title_label.pack(padx=10, pady=10)

        self.weather_frame = ctk.CTkFrame(root)
        self.weather_frame.pack(fill='x', padx=50, pady=10)

        self.entry = ctk.CTkEntry(self.weather_frame, placeholder_text="Enter the city...")
        self.entry.pack(side='left', padx=80, pady=20)

        self.command_button = ctk.CTkButton(self.weather_frame, text='Get Weather Data', command=self.get_weather)
        self.command_button.pack(side='left', padx=20, pady=20)

        self.weather_clear = ctk.CTkFrame(root)
        self.weather_clear.pack(fill='x', padx=50,pady=5)

        self.clear = ctk.CTkButton(self.weather_clear, text="Clear", command=self.clear_data)
        self.clear.pack(side='bottom', pady=(10, 10))

        self.result = ctk.CTkLabel(root, text="")
        self.result.pack()

        self.weather_icon_label = None  # Initialize the icon label

    def get_weather(self):
        city = self.entry.get().upper().strip()
        my_api = 'ef25ec4b02a9209c29f3e8a1ea079edc'
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={my_api}'
        response = requests.get(url)

        if response.status_code == 200:
            weather_data = response.json()

            temperature = weather_data['main']['temp']
            tem_c = (temperature - 273.15)
            temp_c = f"{tem_c:.2f}°C"
            tem_f = (tem_c * 9 / 5) + 32
            tem_f = f"{tem_f:.2f}°F"

            description = weather_data['weather'][0]['description'].capitalize()
            icon_code = weather_data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

            # Fetch the icon
            icon_response = requests.get(icon_url)
            if icon_response.status_code == 200:
                image_data = icon_response.content
                icon_image = Image.open(io.BytesIO(image_data))

                # Convert to CTkImage
                ctk_image = ctk.CTkImage(light_image=icon_image, dark_image=icon_image, size=(200, 200))

                # Display the icon in a label
                if self.weather_icon_label:
                    self.weather_icon_label.destroy()  # Destroy the previous icon if it exists

                self.weather_icon_label = ctk.CTkLabel(self.root, image=ctk_image)
                self.weather_icon_label.image = ctk_image  # Prevent garbage collection
                self.weather_icon_label.pack(pady=10)

            get = (f"Current weather in {city} city:\n"
                   f"Description: {description}\n"
                   f"Temperature: {temp_c} / {tem_f}")
            self.result.configure(text=get, text_color="green", font=ctk.CTkFont(size=20, weight='bold'))
        else:
            self.result.configure(text=f"Error fetching weather data for '{city}'.\n"
                                       f" Please check the city name!", text_color="orange",font=ctk.CTkFont(size=15, weight='bold'))

    def clear_data(self):
        self.entry.delete(0, ctk.END)
        self.result.configure(text="")
        if self.weather_icon_label:
            self.weather_icon_label.destroy()

if __name__ == '__main__':
    window = ctk.CTk()
    app = WeatherApp(window)
    window.mainloop()
