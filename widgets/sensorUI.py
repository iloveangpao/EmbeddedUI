import sys
import time
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QLineEdit
from collections import deque
from sensor.pseudosensor import PseudoSensor

class SensorDataCollector:
    def __init__(self, threshold_alarm):
        self.sensor = PseudoSensor()
        self.humidity_values = deque(maxlen=10)
        self.temperature_values = deque(maxlen=10)
        self.humidity_threshold = None
        self.temperature_threshold = None
        self.threshold_alarm = threshold_alarm

    def read_sensor(self):
        humidity, temperature = self.sensor.generate_values()
        self.humidity_values.append(humidity)
        self.temperature_values.append(temperature)

        if self.humidity_threshold and humidity > self.humidity_threshold:
            self.threshold_alarm.emit("Humidity threshold crossed!")

        if self.temperature_threshold and temperature > self.temperature_threshold:
            self.threshold_alarm.emit("Temperature threshold crossed!")

    def get_humidity_stats(self):
        if not self.humidity_values:
            return None, None, None
        humidity_min = min(self.humidity_values)
        humidity_max = max(self.humidity_values)
        humidity_avg = sum(self.humidity_values) / len(self.humidity_values)
        return humidity_min, humidity_max, humidity_avg

    def get_temperature_stats(self):
        if not self.temperature_values:
            return None, None, None
        temperature_min = min(self.temperature_values)
        temperature_max = max(self.temperature_values)
        temperature_avg = sum(self.temperature_values) / len(self.temperature_values)
        return temperature_min, temperature_max, temperature_avg

class SensorUI(QWidget):
    threshold_alarm = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.sensor_data_collector = SensorDataCollector(threshold_alarm=self.threshold_alarm)
        

        self.humidity_label = QLabel("Humidity: -")
        self.temperature_label = QLabel("Temperature: -")

        self.humidity_threshold_label = QLabel("Humidity Threshold (%):")
        self.humidity_threshold_edit = QLineEdit()

        self.temperature_threshold_label = QLabel("Temperature Threshold (°F):")
        self.temperature_threshold_edit = QLineEdit()

        self.read_button = QPushButton("Read Sensor")
        self.read_button.clicked.connect(self.read_sensor)

        self.collect_button = QPushButton("Collect Data")
        self.collect_button.clicked.connect(self.collect_data)

        self.stats_button = QPushButton("Show Stats")
        self.stats_button.clicked.connect(self.show_stats)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.quit_app)

        self.threshold_alarm.connect(self.show_alarm)

        layout = QVBoxLayout()
        layout.addWidget(self.humidity_label)
        layout.addWidget(self.temperature_label)
        layout.addWidget(self.humidity_threshold_label)
        layout.addWidget(self.humidity_threshold_edit)
        layout.addWidget(self.temperature_threshold_label)
        layout.addWidget(self.temperature_threshold_edit)
        layout.addWidget(self.read_button)
        layout.addWidget(self.collect_button)
        layout.addWidget(self.stats_button)

        self.setLayout(layout)
        self.setWindowTitle("Sensor UI")

        self.data_window = None

    def read_sensor(self):
        self.sensor_data_collector.humidity_threshold = int(self.humidity_threshold_edit.text())
        self.sensor_data_collector.temperature_threshold = int(self.temperature_threshold_edit.text())
        self.sensor_data_collector.read_sensor()
        humidity, temperature = self.sensor_data_collector.humidity_values[-1], self.sensor_data_collector.temperature_values[-1]
        self.humidity_label.setText(f"Humidity: {humidity}%")
        self.temperature_label.setText(f"Temperature: {temperature}°F")

    def collect_data(self):
        self.collect_button.setEnabled(False)
        self.data_window = DataWindow()
        self.data_window.show()

        QTimer.singleShot(1000, self.collect_reading)

    def collect_reading(self):
        self.sensor_data_collector.humidity_threshold = int(self.humidity_threshold_edit.text())
        self.sensor_data_collector.temperature_threshold = int(self.temperature_threshold_edit.text())
        self.sensor_data_collector.read_sensor()
        humidity, temperature = self.sensor_data_collector.humidity_values[-1], self.sensor_data_collector.temperature_values[-1]
        self.data_window.add_reading(humidity, temperature)

        if len(self.sensor_data_collector.humidity_values) <= 10:
            QTimer.singleShot(1000, self.collect_reading)
        else:
            self.collect_button.setEnabled(True)

    def show_stats(self):
        humidity_min, humidity_max, humidity_avg = self.sensor_data_collector.get_humidity_stats()
        temperature_min, temperature_max, temperature_avg = self.sensor_data_collector.get_temperature_stats()

        message = f"Humidity Stats:\n"
        message += f"Minimum: {humidity_min}%\n"
        message += f"Maximum: {humidity_max}%\n"
        message += f"Average: {humidity_avg:.2f}%\n\n"
        message += f"Temperature Stats:\n"
        message += f"Minimum: {temperature_min}°F\n"
        message += f"Maximum: {temperature_max}°F\n"
        message += f"Average: {temperature_avg:.2f}°F"

        QMessageBox.information(self, "Statistics", message)

    def show_alarm(self, message):
        QMessageBox.warning(self, "Alarm", message)

    def quit_app(self):
        QApplication.quit()

class DataWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.humidity_label = QLabel("Humidity Data:")
        self.temperature_label = QLabel("Temperature Data:")
        self.humidity_values = QLabel("")
        self.temperature_values = QLabel("")

        layout = QVBoxLayout()
        layout.addWidget(self.humidity_label)
        layout.addWidget(self.humidity_values)
        layout.addWidget(self.temperature_label)
        layout.addWidget(self.temperature_values)

        self.setLayout(layout)
        self.setWindowTitle("Data Window")

    def add_reading(self, humidity, temperature):
        humidity_text = self.humidity_values.text()
        temperature_text = self.temperature_values.text()

        humidity_text += f"{humidity}%\n"
        temperature_text += f"{temperature}°F\n"

        self.humidity_values.setText(humidity_text)
        self.temperature_values.setText(temperature_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SensorUI()
    ui.show()
    sys.exit(app.exec())