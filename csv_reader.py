import csv
from Model import Node

with open("Instance.csv", newline='') as f:
    reader = csv.reader(f)
    csv_file = list(reader)

# get vehicles (k)
k = csv_file[0][1]

# get max capacity (q)
q = csv_file[1][1]

# get max duration (t)
t = csv_file[2][1]

# get depot coordinates (dx, dy)
dx = csv_file[5][1]
dy = csv_file[5][2]

# get customers (n)
n = csv_file[7][1]

# get customer data list (cd)
cd = []
for i in range(11, len(csv_file)):
  c = Node(csv_file[i][0], csv_file[i][1], csv_file[i][2], csv_file[i][3], csv_file[i][4], csv_file[i][5])
  cd.append(c)

print('Vehicles:', k)
# print('Max Capacity:', q)
# print('Max Duration:', t)
# print('Depot x coord:', dx)
# print('Depot y coord:', dy)
# print('Customers:', n)

for i in range(0, len(cd)):
  print(cd[i].id + ', ' + cd[i].demand)

def get_vehicles():
  return k

def get_capacity():
  return q

def get_duration():
  return t

def get_dx():
  return dx

def get_dy():
  return dy

def get_customers():
  return n

def get_customer_data():
  return cd
