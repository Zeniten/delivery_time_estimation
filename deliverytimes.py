from geopy.distance import geodesic
from datetime import datetime, timedelta
import time

from utilities import create_csv, routeplans, stoplocations, driverpositions

start_time = time.time()

routeplans = routeplans()
driverpositions = driverpositions()
stoplocations = stoplocations()

AVERAGE_WALKING_SPEED = 5 # km/h
R = 50 # radius of 30 meters

def driver_is_inside_location_area(driver_position, location_position):
    return geodesic(driver_position, location_position).meters <= R

def estimated_duration(timestamps_list):
    if not timestamps_list:
        return 0
    else:
        durations = [int(timedelta.total_seconds(timestamps[1] - timestamps[0])) for timestamps in timestamps_list]
        return max(durations)

def driver_is_moving_at_walking_speed(speed):
    return speed < AVERAGE_WALKING_SPEED + 2 # buffer

def enter_and_leave_timestamps(driver_positions, stoplocation_position, deliverystatustimestamp):
    enter_timestamp = 0
    leave_timestamp = 0
    # A driver might enter and leave an area multiple times. You should compute the set containing every
    # enter-and-leave-timestamps tuples, and then select the best one. If there's only one tuple, select
    # that one. If there are many, you select the best one.
    # -- What does "best one" mean?
    timestamps_list = []

    for e in driver_positions:
        if enter_timestamp == 0:
            # Optimizing enter_timestamp
            # Idea: Use speed data to shrink R, decreasing the area.
            if driver_is_inside_location_area(e["position"], stoplocation_position) and driver_is_moving_at_walking_speed(e["speed"]):
                enter_timestamp = e["logtime"]
        if enter_timestamp != 0 and leave_timestamp == 0:
            if not driver_is_inside_location_area(e["position"], stoplocation_position) and not driver_is_moving_at_walking_speed(e["speed"]):
                leave_timestamp = e["logtime"]
                timestamps_list.append((enter_timestamp, leave_timestamp))
                enter_timestamp = 0
                leave_timestamp = 0
    
    # Optimizing leave_timestamp
    # Use deliverystatustimestamp if driver registered delivery before leaving the area
    # Comment: Some drivers might register delivery before actually delivering. E.g., a driver might drive to
    # a location, then register the delivery, then go and drop off the delivery.
    if deliverystatustimestamp != 0:
        timestamps_list = [(timestamps[0], deliverystatustimestamp) if timedelta.total_seconds(timestamps[1] - deliverystatustimestamp) > 0 and timedelta.total_seconds(deliverystatustimestamp - timestamps[0]) > 0 else timestamps for timestamps in timestamps_list]

    return timestamps_list

# def fill_in_delivery_time_estimates():
#     for routeplanid, routes in routeplans.items():
#         for routeid, driver in routes.items():
#             for driverid, stoplocs in driver.items():
#                 for stoplocationid, duration in stoplocs.items():
#                     stoplocation = {}

#                     try:
#                         # some stoplocationids are not in stoplocations
#                         stoplocation = stoplocations[routeplanid][routeid][stoplocationid]
#                         driver_positions = driverpositions[routeid][driverid]
#                     except:
#                         continue

#                     deliverystatustimestamp = stoplocations[routeplanid][routeid][stoplocationid]["deliverystatustimestamp"]

#                     timestamps = enter_and_leave_timestamps(
#                         driver_positions,
#                         stoplocation["position"],
#                         deliverystatustimestamp
#                     )

#                     routeplans[routeplanid][routeid][driverid][stoplocationid]["estimated_duration"] = estimated_duration(timestamps)

estimated_durations = []

def fill_in_delivery_time_estimates():
    for item in routeplans:
        try:
            # item[0]: routeplanid
            # item[1]: routeid
            # item[2]: driverid
            # item[3]: stoplocationid
            # item[4]: duration

            # some stoplocationids are not in stoplocations
            routeplanid = int(item[0])
            routeid = int(item[1])
            driverid = int(item[2])
            stoplocationid = int(item[3])

            stoplocation = stoplocations[routeplanid][routeid][stoplocationid]
            driver_positions = driverpositions[routeid][driverid]
            stoplocation_position = stoplocation["position"]
            deliverystatustimestamp = stoplocation["deliverystatustimestamp"]

            timestamps = enter_and_leave_timestamps(
                driver_positions,
                stoplocation_position,
                deliverystatustimestamp
            )

            estimated_durations.append(item + [estimated_duration(timestamps)])
        except:
            continue

fill_in_delivery_time_estimates()

#create_csv(routeplans, stoplocations)

# for routeplanid, routes in routeplans.items():
#     for routeid, driver in routes.items():
#         for driverid, stoplocs in driver.items():
#             for stoplocationid, durations in stoplocs.items():
#                 if len(durations) > 1:
#                     print(durations)

print(estimated_durations)

print("--- %s seconds ---" % (time.time() - start_time))
