var socket = new WebSocket("ws://localhost:8888/ws");
var humidityThreshold = null;
var temperatureThreshold = null;
var consecText = "";
var consecToggle = false
socket.onopen = function () {
    console.log("WebSocket connection established");
};
socket.onmessage = function (event) {
    var message = JSON.parse(event.data);
    if (message.hasOwnProperty("humidity")) {
        // Handle sensor data message
        var humidityThresholdElement = document.getElementById("humidity_threshold");
        var temperatureThresholdElement = document.getElementById("temperature_threshold");
        humidityThreshold = humidityThresholdElement.textContent;
        temperatureThreshold = humidityThresholdElement.textContent;
        var humidity = message.humidity;
        var temperature = message.temperature;
        if(consecToggle) {
            console.log(consecToggle)
            consecText += "Humidity: " + humidity + " " +
                                    "Temperature: " + temperature + "<br>"
            var consecElement = document.getElementById("consecutive_readings");
            consecElement.innerHTML = consecText;
            consecToggle = false;
            
        }else {
            console.log(consecToggle)
            var dataElement = document.getElementById("data");
            dataElement.innerHTML = "Humidity: " + humidity + " " +
                                    "Temperature: " + temperature;
            consecToggle = true;
        }
        if (
            ( humidityThreshold !== "" ||
            temperatureThreshold !== "" ) && (
            humidity > humidityThreshold ||
            temperature > temperatureThreshold )
        ) {
            var alarmElement = document.getElementById("alarm");
            alarmElement.innerHTML = "ALARM! One or more thresholds exceeded";
            alarmElement.className = "alarm";
        } else {
            var alarmElement = document.getElementById("alarm");
            alarmElement.innerHTML = "";
            alarmElement.className = "";
        }
    } else if (message.hasOwnProperty("min_humidity")) {
        // Handle statistics message
        var minHumidity = message.min_humidity;
        var maxHumidity = message.max_humidity;
        var avgHumidity = message.avg_humidity;
        var statsElement = document.getElementById("stats");
        statsElement.innerHTML = "Min Humidity: " + minHumidity + "<br>" +
                                 "Max Humidity: " + maxHumidity + "<br>" +
                                 "Average Humidity: " + avgHumidity;
        humidityThreshold = parseFloat(document.getElementById("humidity_threshold").value);
        temperatureThreshold = parseFloat(document.getElementById("temperature_threshold").value);
    }
};
function getSingleReading() {
    consecToggle = false
    getSensorData()
}
function getSensorData() {
    socket.send("single");
}
function getSensorStats() {
    socket.send("stats");
}
function startSensorDataInterval() {
    // consecToggle = true;
    consecText = "10 Sensor Readings: <br>";
    pollFunc(getOneInterval, 10000, 1000);
    // consecToggle = false;
}
function getOneInterval(){
    consecToggle = true
    getSensorData()
}
function pollFunc(fn, timeout, interval) {
    var startTime = (new Date()).getTime();
    interval = interval || 1000;
    (function p() {
        fn();
        if (((new Date).getTime() - startTime ) <= timeout)  {
            setTimeout(p, interval);
        }
    })();
}
function switchOffServerAndClose() {
    // Send the "Switch Off Server" message
    socket.send("switch_off_server");
    // Close the web page
    window.close();
}