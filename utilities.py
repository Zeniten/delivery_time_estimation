import pandas as pd


def create_csv(routeplans, stoplocations, driverpositions, estimated_durations):
    df = routeplans.merge(stoplocations[['stoplocationid', 'deliverystatus']], on='stoplocationid', how='left')
    df = df.merge(estimated_durations[['routeplanid', 'estimated_duration']], on='routeplanid', how='left')
    print(df)
    df.to_csv('estimated_delivery_times.csv', index = False)


def remove_tzinfo(date_string):
    return date_string.split("+")[0]


def remove_microseconds(date_string):
    return date_string.split(".")[0]


def routeplans():
    csv = "routeplans_test.csv"
    routeplans = pd.read_csv(csv, sep='\t', header=0, na_values=["(null)"])
    print('%s read shape: %s' % (csv, routeplans.shape))
    routeplans.dropna(subset=["driverid"], inplace=True)      # ignoring routes without driver
    print(routeplans.ftypes)
    return routeplans


def get_routeids(stoplocations):
    return stoplocations.groupby(['routeid', 'stoplocationid'])


def stoplocations():
    csv = "stoplocations_test.csv"
    stoplocations = pd.read_csv(csv, sep='\t', header=0, na_values=["(null)"])
    print('%s read shape: %s' % (csv, stoplocations.shape))
    stoplocations.dropna(subset=["latitude", "longitude"], inplace=True)      # ignoring locations without latitude or longitude
    stoplocations['position'] = stoplocations.apply(lambda x: (x['latitude'], x['longitude']), axis=1)
    stoplocations['deliverystatustimestamp'] = pd.to_datetime(stoplocations['deliverystatustimestamp'].apply(lambda x: remove_microseconds(remove_tzinfo(x))))
    print(stoplocations.ftypes)
    return stoplocations


def get_drivers(driverpositions):
    return driverpositions.groupby(['routeid', 'driverid'])


def driverpositions():
    csv = "driverpositions_test.csv"
    driverpositions = pd.read_csv(csv, sep='\t', header=0, na_values=["(null)"])  # use "," when using Terje's file
    print('%s read shape: %s' % (csv, driverpositions.shape))
    driverpositions.dropna(subset=["latitude", "longitude"], inplace=True)      # ignoring positions without latitude or longitude
    driverpositions['position'] = driverpositions.apply(lambda x: (x['latitude'], x['longitude']), axis=1)
    driverpositions['logtime'] = pd.to_datetime(driverpositions['logtime'].apply(lambda x: remove_microseconds(remove_tzinfo(x))))
    driverpositions['speed'] = driverpositions['speed'].fillna(value=0)
    driverpositions = driverpositions.sort_values(by=['routeid', 'driverid', 'logtime'])
    print(driverpositions.ftypes)
    return driverpositions
