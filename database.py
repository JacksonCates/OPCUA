import os, time
from influxdb_client_3 import InfluxDBClient3, Point
from dotenv import load_dotenv

class Database:
    def __init__(self, host, org, database) -> None:
        self.database = database
        self.org = org
        self.host = host

        # Gets de token
        load_dotenv()
        token = os.environ.get("INFLUXDB_TOKEN")

        self.client = InfluxDBClient3(host=host, token=token, org=org)

    def close(self):
        self.client.close()

    def write(self, measurement, data: dict):
        for key in data:
            point = (
                Point(measurement)
                .field(key, data[key])
            )
        self.client.write(database=self.database, record=point)