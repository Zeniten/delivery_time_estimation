import csv
from datetime import datetime

def create_csv(routeplans_dict, stoplocations_dict):
    with open('estimated_delivery_times.csv', 'w', newline='') as csvfile:
        fieldnames = ['routeplanid', 'routeid', 'driverid', 'stoplocationid', 'deliverystatus', 'duration', 'estimated_duration']
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames)

        writer.writeheader()

        for routeplanid, routes in routeplans_dict.items():
            for routeid, drivers in routes.items():
                for driverid, stoplocs in drivers.items():
                    for stoplocationid, durations in stoplocs.items():
                        deliverystatus = '(null)'
                        if stoplocationid in stoplocations_dict[routeplanid][routeid]:
                            deliverystatus = stoplocations_dict[routeplanid][routeid][stoplocationid]["deliverystatus"]
                        writer.writerow({
                            'routeplanid': routeplanid,
                            'routeid': routeid,
                            'driverid': driverid,
                            'stoplocationid': stoplocationid,
                            'deliverystatus': deliverystatus,
                            'duration': durations["duration"],
                            'estimated_duration': durations["estimated_duration"] if "estimated_duration" in durations else 0
                        })

def remove_tzinfo(date_string):
    return date_string.split("+")[0]

def remove_microseconds(date_string):
    return date_string.split(".")[0]

# def routeplans():
#     routeplans = {}

#     with open("routeplans.csv", "r") as f:
#         reader = csv.reader(f, delimiter="\t")
#         for i, line in enumerate(reader):
#             if i == 0:  # skip headers
#                 continue
#             if line[2] == '(null)':     # no driver
#                 continue
#             routeplanid = int(line[0])
#             routeid = int(line[1])
#             driverid = int(line[2])
#             stoplocationid = int(line[3])
#             duration = int(line[4]) if line[4] != '(null)' else 0

#             if routeplanid in routeplans:
#                 routes = routeplans[routeplanid]

#                 if routeid in routes:
#                     drivers = routes[routeid]

#                     if driverid in drivers:
#                         stoplocations = drivers[driverid]

#                         stoplocations[stoplocationid] = {"duration": duration}
#                     else:
#                         drivers[driverid] = {stoplocationid: {"duration": duration}}
#                 else:
#                     routes[routeid] = {
#                         driverid: {
#                             stoplocationid: {
#                                 "duration": duration
#                             }
#                         }
#                     }
#             else:
#                 routeplans[routeplanid] = {
#                     routeid: {
#                         driverid: {
#                             stoplocationid: {
#                                 "duration": duration
#                             }
#                         }
#                     }
#                 }

#     return routeplans

def routeplans():
    routeplans = []

    with open("routeplans_test.csv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for i, line in enumerate(reader):
            if i == 0:  # skip headers
                continue
            if line[2] == '(null)':     # no driver
                continue

            routeplans.append(line)

    return routeplans

def stoplocations():
    stoplocations = {}

    with open("stoplocations_test.csv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for i, line in enumerate(reader):
            if i == 0:
                continue
            if line[3] == '(null)' or line[4] == '(null)':
                continue
            routeplanid = int(line[0])
            routeid = int(line[1])
            stoplocationid = int(line[2])
            data = {
                "position": (float(line[3]), float(line[4])),
                "deliverystatus": int(line[5]),
                "deliverystatustimestamp": datetime.fromisoformat(line[6] if line[6] != '(null)' else 0)
            }

            if routeplanid in stoplocations:
                routes = stoplocations[routeplanid]

                if routeid in routes:
                    stoplocs = routes[routeid]
                    stoplocs[stoplocationid] = data # Assumption: only unique stoplocationids
                else:
                    routes[routeid] = {stoplocationid: data}
            else:
                stoplocations[routeplanid] = {routeid: {stoplocationid: data}}
    
    return stoplocations

def driverpositions():
    driverpositions = {}

    with open("driverpositions_test.csv", "r") as f:
        reader = csv.reader(f, delimiter="\t") # use "," when using Terje's file
        for i, line in enumerate(reader):
            if i == 0:  # skip headers
                continue
            routeid = int(line[0])
            driverid = int(line[1])
            data = {
                "position": (float(line[2]), float(line[3])),
                "logtime": datetime.fromisoformat(remove_microseconds(remove_tzinfo(line[4]))),
                "speed": float(line[6]) if line[6] else 0.0
            }

            if routeid in driverpositions:
                drivers = driverpositions[routeid]

                if driverid in drivers:
                    drivers[driverid].append(data)
                else:
                    drivers[driverid] = [data]
            else:
                driverpositions[routeid] = {driverid: [data]}

    # sort
    for routeid, driver in driverpositions.items():
        for driverid, position_data in driver.items():
            driverpositions[routeid][driverid] = sorted(position_data, key=lambda position_datum: position_datum["logtime"])

    return driverpositions
