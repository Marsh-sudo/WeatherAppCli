import argparse
import json
import sys # helps us exit the program without having a traceback error
from configparser import ConfigParser
from urllib import parse,request, response # used to help sanitize user input for Api to consume it safely
from urllib import error,parse,request
from pprint import pp

import style

BASE_WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

THUNDERSTORM = range(200, 300)
DRIZZLE = range(300, 400)
RAIN = range(500, 600)
SNOW = range(600, 700)
ATMOSPHERE = range(700, 800)
CLEAR = range(800, 801)
CLOUDY = range(801, 900)


def get_api_key():
    """
    Function to fetch the api key
    """
    config = ConfigParser()
    config.read("secrets.ini")
    return config["openweather"]["api_key"]

def read_user_cli_args():
    """Handles the user cli interactions
    """
    parser = argparse.ArgumentParser(
        description="get weather and temperature info for a city"
    )
    parser.add_argument(
        "city",nargs="+",type=str,help="enter your city name" # by setting no.of arguments to "+" you allow to pass city name with two name "San Francissco"
    )
    parser.add_argument(
        "-i",
        "--imperial",
        action="store_true",
        help="display the temperature in imperial units"
    )
    return parser.parse_args() # return result which will be user-input values


if __name__ == "__main__":  #allows you to define code that should run when you’re executing weather.py as script
    user_args=read_user_cli_args()
    print(user_args.city,user_args.imperial)


def weather_query(city_input,imperial=False):
    """Builds the Url for an API request to OpenWeather weather API
    Args:
        city_input (List[str]): Name of a city as collected by argparse
        imperial (bool): Whether or not to use imperial units for temperature
     Returns:
        str: URL formatted for a call to OpenWeather's city name endpoint
    """ 
    api_key = get_api_key()
    city_name = " ".join(city_input)
    url_encoded_city_name = parse.quote_plus(city_name)
    units = "imperial" if imperial else "metric"
    url = (
        f"{BASE_WEATHER_API_URL}?q={url_encoded_city_name}"
        f"&units={units}&appid={api_key}"
    )
    return url

if __name__ == "__main__":  #allows you to define code that should run when you’re executing weather.py as script
    user_args=read_user_cli_args()
    query_url=weather_query(user_args.city,user_args.imperial)
    print(query_url)


def get_weather_data(query_url):
    """Makes an Api request to a URL and returns the data
    ARGS:
       query_url(str):URL formatted for OpenWeather's city name endpoints
    """
    try:
        response=request.urlopen(query_url)#make an HTTP GET request to the query_url parameter and saves the result as response
    except error.HTTPError as http_error:
        if http_error.code == 401: # unauthorized
            sys.exit("Access denied.Check your Api Key")
        elif http_error.code == 404: # Not found
            sys.exit("Cant find weather data for this country")
        else:
            sys.exit(f"Something went wrong...({http_error.code})")
    data = response.read() # extracts the data from the response

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response")

    return json.loads(data) #The function returns a Python object holding the JSON information fetched from query_url.


if __name__ == "__main__":
    user_args = read_user_cli_args()
    query_url = weather_query(user_args.city,user_args.imperial)
    weather_data = get_weather_data(query_url)
    # print(
    #     f"{weather_data['name']}:"
    #     f"{weather_data['weather'] [0] ['description']}"
    #     f"({weather_data['main'] ['temp']})"
    # )


def display_weather_info(weather_data,imperial=False):
    """Prints the formatted weather info for a city
    Args:
       weather_data (dict):API esponse from OpenWeather by city name
        imperial (bool): Whether or not to use imperial units for temperature
    """

    city = weather_data["name"]
    weather_id = weather_data["weather"][0]["id"]
    weather_description = weather_data["weather"] [0] ["description"]
    temperature = weather_data["main"] ["temp"]
     
    style.change_color(style.REVERSE)
    print(f"{city:^{style.PADDING}}",end="")
    style.change_color(style.RESET)
    
    weather_symbol,color = _select_weather_display_params(weather_id)

    style.change_color(color)
    print(f"\t{weather_symbol}",end=" ")
    print(f"\t{weather_description.capitalize():{style.PADDING}}",end=" ")

    style.change_color(style.RESET)
   
    print(f"({temperature}°{'F' if imperial else 'C'})")
    
def _select_weather_display_params(weather_id):

    if weather_id in THUNDERSTORM:
        display_params = ("💥", style.RED)
    elif weather_id in DRIZZLE:
        display_params = ("💧", style.CYAN)
    elif weather_id in RAIN:
        display_params = ("💦", style.BLUE)
    elif weather_id in SNOW:
        display_params = ("⛄️", style.WHITE)
    elif weather_id in ATMOSPHERE:
        display_params = ("🌀", style.MAGENTA)
    elif weather_id in CLEAR:
        display_params = ("🔆", style.YELLOW)
    elif weather_id in CLOUDY:
        display_params = ("💨", style.BRIGHTCYAN)
    else:  # In case the API adds new weather codes
        display_params = ("🌈", style.RESET)
    return display_params


if __name__ == "__main__":

    display_weather_info(weather_data,user_args.imperial)