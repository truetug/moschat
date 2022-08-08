import os


SERVICE_DB = {
    "help": {
        "cls": "app.services.help.HelpService",
        "description": "Доступные команды",
        "enabled": True,
        "perms": None,
    },
    "simple": {
        "cls": "app.services.simple.SimpleService",
        "description": "Стемминг аргументов",
        "enabled": True,
        "perms": None,
    },
    "auth": {
        "cls": "app.services.auth.AuthService",
        "description": (
            "Авторизация\n"
            "Например: `\\auth some1@mail.ru psswd`"
        ),
        "enabled": True,
        "perms": None,
    },
    "weather": {
        "cls": "app.services.weather.WeatherService",
        "description": (
            "Погода в определенном городе\n"
            "Например: `\\weather moscow 2022-02-24`\n"
        ),
        "enabled": True,
        "perms": "can_use_weather",
    },
    "currencies": {
        "cls": "app.services.currencies.CurrenciesService",
        "description": (
            "Курс валют на дату\n"
            "Например: `\\currencies RUB USD 2022-02-24`\n"
        ),
        "enabled": False,
        "perms": "can_use_currencies",
    },

}

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "191e1fe7dbmshf00b958ce4eddb7p18fdd8jsnbbf0f74a1c3c")
