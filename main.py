# pylint: disable=C0103,C0114

import argparse
import os
from asyncio import run as asyncrun
from datetime import datetime

from bimmer_connected.account import MyBMWAccount
from bimmer_connected.api.regions import Regions
from geopy.geocoders import Nominatim
from pytz import timezone
from tabulate import tabulate

bmw_username = os.environ['BMW_USERNAME']
bmw_pw = os.environ['BMW_PW']
bmw_vin = os.environ['BMW_VIN']

parser = argparse.ArgumentParser()
parser.add_argument("-ac", help="Turn AC or heating on/off.",
                    choices=['on', 'off'])
args = parser.parse_args()


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

# Extra information if charging
if charge_status == 'CHARGING':
    offset = timezone('Europe/Amsterdam')
    remaining_time = battery.charging_end_time - datetime.now(offset)
    battery_status = f"{battery_percentage}%: {battery.charging_end_time}"
else:
    battery_status = f"{battery_percentage}%"

locked_state = 'Unlocked'
if car.doors_and_windows.door_lock_state == 'SECURED':
    locked_state = 'Locked'

location = car.vehicle_location.location

table = [["Car", f"{(car.brand.value).upper()} {car.name} ({locked_state})"],
         ["Battery",
             f"{battery_percentage.numerator}% ({charge_status})"],
         ["Location", _get_address_for_gps(
             latitude=location.latitude, longitude=location.longitude)]
         ]
print(tabulate(table))

# AC
if args.ac == 'on':
    ac_start = asyncrun(car.remote_services.trigger_remote_air_conditioning())
    print(f"Returned state: {ac_start}")

elif args.ac == 'off':
    ac_stop = asyncrun(
        car.remote_services.trigger_remote_air_conditioning_stop())
    print(f"Returned state: {ac_stop}")
