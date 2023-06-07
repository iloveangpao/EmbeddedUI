import tornado.websocket
import tornado.web
import tornado.ioloop
import json
import random
import time
import websocket
from sensor.pseudosensor import PseudoSensor
from collections import deque





class SensorWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        # Allow requests from any origin
        return True

    def open(self):
        print("WebSocket connection established")

    def on_message(self, message):
        print("Received message:", message)
        if message == "single":
            self.send_sensor_data()
        if message == "stats":
            self.send_stats()
        elif message == "switch_off_server":
            self.switch_off_server()

    def on_close(self):
        print("WebSocket connection closed")

    def send_stats(self):
        data = self.application.sensor_stats
        if not data:
            print('no readings yet')
            self.write_message('no readings yet')
        else:
            self.write_message(json.dumps(data))

    def send_sensor_data(self):
        data = self.get_values()
        self.write_message(json.dumps(data))
        self.application.sensor_readings.append(data)
        print("Sent sensor data:", data)
        self.update_stats()

    def get_values(self):
        hum_val, temp_val = sensor.generate_values()
        data = {"humidity": hum_val, "temperature": temp_val}
        return data
    
    def update_stats(self):
        min_humidity, max_humidity, avg_humidity = self.calculate_stats(self.application.sensor_readings)
        self.application.sensor_stats = {
            "min_humidity": min_humidity,
            "max_humidity": max_humidity,
            "avg_humidity": avg_humidity
        }
        print("Stored sensor statistics:", self.application.sensor_stats)

    def calculate_stats(self, readings):
        if not readings:
            return None, None, None

        min_value = min(readings, key=lambda x: x["humidity"])["humidity"]
        max_value = max(readings, key=lambda x: x["humidity"])["humidity"]
        avg_value = sum(reading["humidity"] for reading in readings) / len(readings)
        return min_value, max_value, avg_value
    
    def switch_off_server(self):
        print("Switching off server...")
        self.close()  # Close the WebSocket connection

        # Shut down the Tornado server gracefully
        tornado.ioloop.IOLoop.current().stop()

# class SensorHandler(tornado.web.RequestHandler):
#     def check_origin(self, origin):
#         # Allow requests from any origin
#         return True

#     def get(self):
#         print("Received GET request for sensor readings")
#         data = sensor_readings.get_last_readings()
#         self.set_header("Content-Type", "application/json")
#         self.write(json.dumps(data))
#         print("Sent sensor readings:", data)

#         min_humidity, max_humidity, avg_humidity = calculate_stats(sensor_readings)
#         self.application.sensor_stats = {
#             "min_humidity": min_humidity,
#             "max_humidity": max_humidity,
#             "avg_humidity": avg_humidity
#         }
#         print("Stored sensor statistics:", self.application.sensor_stats)

sensor = PseudoSensor()

app = tornado.web.Application([
    (r"/ws", SensorWebSocket)
])
app.sensor_stats = {}
app.sensor_readings = deque(maxlen=10)

if __name__ == "__main__":
    app.listen(8888)
    print("Server started and listening on port 8888")
    tornado.ioloop.IOLoop.current().start()
