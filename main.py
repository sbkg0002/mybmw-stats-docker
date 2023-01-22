from asyncio import run as asyncrun
from tabulate import tabulate
from geopy.geocoders import Nominatim

import os

from bimmer_connected.account import MyBMWAccount
from bimmer_connected.api.regions import Regions

bmw_username = os.environ['BMW_USERNAME']
bmw_pw = os.environ['BMW_PW']
bmw_vin = os.environ['BMW_VIN']


def _get_address_for_gps(latitude: str, longitude: str):
    geolocator = Nominatim(user_agent="mybmw")
    loc = geolocator.reverse(
        f"{latitude}, {longitude}", zoom=10)
    return loc.address


# Connect
account = MyBMWAccount(bmw_username, bmw_pw, Regions.REST_OF_WORLD)
asyncrun(account.get_vehicles())
car = account.get_vehicle(bmw_vin)
battery = car.fuel_and_battery
charge_status = battery.charging_status.value
battery_percentage = battery.remaining_battery_percent
if charge_status == 'CHARGING':
    battery_status = f"{battery_percentage}%: {battery.charging_end_time}"
else:
    battery_status = f"{battery_percentage}%"
location = car.vehicle_location.location


table = [["Car", f"{(car.brand.value).upper()} {car.name}"],
         ["Battery",
             f"{battery_percentage.numerator}% ({charge_status})"],
         ["Location", _get_address_for_gps(
             latitude=location.latitude, longitude=location.longitude)]
         ]
print(tabulate(table))

# ac = run(vehicle.remote_services.trigger_remote_air_conditioning())
# print(result.ac)
