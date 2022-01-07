import csv

with open("Instance.csv", newline='') as f:
    reader = csv.reader(f)
    csv_file = list(reader)


def get_vehicles():
    """Return available vehicles"""
    return csv_file[0][1]


def get_capacity():
    """Return max vehicle capacity"""
    return csv_file[1][1]


def get_duration():
    """Return max service time"""
    return csv_file[2][1]


def get_depot_coords():
    """Return depot coordinates as a tuple"""
    return csv_file[5][1], csv_file[5][2]


def get_customer_data():
    """Return customer attributes

    Returns:
        A list containing dictionaries of customer attributes.
        All keys correspond to Node Object fields. See Node in Model
    """
    cd = []
    for i in range(11, len(csv_file)):
        c = {'id': csv_file[i][0], 'x': csv_file[i][1], 'y': csv_file[i][2], 'demand': csv_file[i][3],
             'service_time': csv_file[i][4], 'profit': csv_file[i][5]}
        cd.append(c)
    return cd