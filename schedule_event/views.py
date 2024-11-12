from django.shortcuts import render
from datetime import datetime
import pytz
import json

from schedule_event.models import Interview_slot


def convert_utc_to_timezone(utc_time_str, timezone_str):
    fmt = "%Y-%m-%dT%H:%M:%S.%f"
    utc_dt = datetime.fromisoformat(utc_time_str.replace("Z", "+00:00"))
    target_tz = pytz.timezone(timezone_str)
    target_dt = utc_dt.astimezone(target_tz)
    return target_dt.strftime(fmt)


def convert_to_different_timezone(utc_time_str, given_time_zone, time_zone):
    try:
        utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except Exception as e:
        try:
            utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%f")
        except:
            utc_time_str = utc_time_str[:-1]
            utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%f")
    utc_time = pytz.utc.localize(utc_time)
    calcutta_timezone = pytz.timezone(given_time_zone)
    calcutta_time = utc_time.astimezone(calcutta_timezone)
    # Format the datetime object to a string
    calcutta_time_str = calcutta_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
    return calcutta_time_str


def convert_to_another_timnezone(time_zone, event_tz):
    utc_time = datetime.now()
    kolkata_timezone = pytz.timezone("Asia/Kolkata")
    kolkata_time = utc_time.astimezone(kolkata_timezone)
    formatted_time = kolkata_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
    return datetime.fromisoformat(formatted_time)


def cuurent_tz_format_change():
    current_time = datetime.now()
    output_datetime_format_str = "%Y-%m-%dT%H:%M:%S.%f"
    current_time = datetime.strptime(str(current_time), "%Y-%m-%d %H:%M:%S.%f")
    formatted_time = current_time.strftime(output_datetime_format_str)
    return datetime.fromisoformat(formatted_time)


def change_timezone_time(current_time_str, current_time_zone_str, change_time_zone_str):
    output_datetime_format_str = "%Y-%m-%dT%H:%M:%S.%f"
    try:
        current_time = datetime.strptime(current_time_str, "%Y-%m-%dT%H:%M:%S.%f")
    except Exception as e:
        try:
            current_time_str1 = current_time_str[:-1]
            current_time = datetime.strptime(current_time_str1, "%Y-%m-%dT%H:%M:%S.%f")
        except Exception as e:
            try:
                current_time = datetime.strptime(
                    current_time_str, "%Y-%m-%dT%H:%M:%S.%fZ"
                )
            except:
                current_time = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
    current_time_zone = pytz.timezone(current_time_zone_str)
    current_time = current_time_zone.localize(current_time)
    change_time_zone = pytz.timezone(change_time_zone_str)
    converted_time = current_time.astimezone(change_time_zone)
    output_datetime = converted_time.strftime(output_datetime_format_str)
    return datetime.fromisoformat(output_datetime)


def format_time_change(current_time_str):
    current_time_str = str(current_time_str)
    try:
        current_time = datetime.strptime(current_time_str, "%Y-%m-%dT%H:%M:%S.%f")
    except Exception as e:
        try:
            current_time_str1 = current_time_str[:-1]
            current_time = datetime.strptime(current_time_str1, "%Y-%m-%dT%H:%M:%S.%f")
        except Exception as e:
            try:
                current_time = datetime.strptime(
                    current_time_str, "%Y-%m-%dT%H:%M:%S.%fZ"
                )
            except:
                current_time = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
    output_datetime_format_str = "%Y-%m-%dT%H:%M:%S.%f"
    current_time = current_time.strftime(output_datetime_format_str)
    return datetime.fromisoformat(current_time)


def sort_by_s_time(item):
    time = item["s_time"]
    # Convert to datetime object
    date_object = time
    if isinstance(date_object, str):
        try:
            date_object = datetime.strptime(date_object, "%Y-%m-%d %H:%M:%S")
        except:
            date_object = datetime.strptime(date_object, "%Y-%m-%dT%H:%M:%S.%f0")
    return date_object.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]


def order_by_s_time(item):
    try:
        time = datetime.strptime(item["s_time"], "%Y-%m-%dT%H:%M:%S.%f")
    except:
        item["s_time"] = (item["s_time"])[:-1]
        time = datetime.strptime(item["s_time"], "%Y-%m-%dT%H:%M:%S.%f")
    return time


def slotterevents_verify(data, dateformat):
    upcomingnewdata = []
    pastnewdata = []
    for i in data:
        try:
            time_zone = Interview_slot.objects.get(id=i["id"]).event_id.times_zone
            time_zone = time_zone.split(" ")
            time_zone = time_zone[1]
            time_zone = time_zone.strip("()")
            calevents_datetime_strs = convert_utc_to_timezone(dateformat, time_zone)
            calevents_datetime_strs = datetime.strptime(
                calevents_datetime_strs, "%Y-%m-%dT%H:%M:%S.%f"
            ).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            calevents_datetime_strs = dateformat
            pass
        if Interview_slot.objects.filter(
            startevent__gte=calevents_datetime_strs, id=i["id"]
        ).exists():
            upcomingnewdata.append(i)
        elif Interview_slot.objects.filter(
            startevent__lt=calevents_datetime_strs, id=i["id"]
        ).exists():
            pastnewdata.append(i)
    sorted_past = sorted(pastnewdata, key=lambda x: x["startevent"])
    sorted_upcoming = sorted(upcomingnewdata, key=lambda y: y["endevent"])
    context = {"upcoming": sorted_upcoming, "past": sorted_past[::-1]}
    return context
