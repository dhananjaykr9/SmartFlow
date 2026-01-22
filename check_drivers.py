import pyodbc

print("--- Available ODBC Drivers ---")
drivers = pyodbc.drivers()
for driver in drivers:
    print(driver)
print("------------------------------")