import json
import os
import logging
from prometheus_client import make_wsgi_app, Gauge
from flask import Flask
from waitress import serve
import paho.mqtt.subscribe as suscribe

app = Flask("MQ2-Gas-Exporter")  # Create flask app
topic=os.getenv('TOPIC',  default="casa/gases")
hostname=os.getenv('MQTTHOST', default="192.168.20.40")
auth={'username':os.getenv('MQTTUSER', default=None), 'password':os.getenv('MQTTPASS', default=None)}
# Setup logging values
format_string = 'level=%(levelname)s datetime=%(asctime)s %(message)s'
logging.basicConfig(encoding='utf-8',
                    level=logging.DEBUG,
                    format=format_string)

# Disable Waitress Logs
log = logging.getLogger('waitress')
log.disabled = True

# Create Metrics
server = Gauge('gas_sensor_server_id', 'MQ2 server ID used to measure')
co = Gauge('gas_sensor_co_ppm',
               'MQ2 current co in ppm')
lpg = Gauge('gas_sensor_lpg_ppm',
             'MQ2 current co in ppms')
ch4 = Gauge('gas_sensor_ch4_ppm',
                       'MQ2 current co in ppm')
propane = Gauge('gas_sensor_propane_ppm',
                     'MQ2 current co in ppm')
smoke = Gauge('gas_sensor_smoke_ppm', 'MQ2 current co in ppm')

def get_data():
    msg = suscribe.simple(topic,hostname=hostname,auth=auth)
    msg_dict=json.loads(msg.payload.decode())
    return "1",msg_dict["CO"],msg_dict["LPG"],msg_dict["CH4"],msg_dict["Smoke"],msg_dict["CO"]

@app.route("/metrics")
def updateResults():
    r_server, r_co, r_lpg, r_ch4, r_propane, r_smoke = get_data()
    server.set(r_server)
    co.set(r_co)
    lpg.set(r_lpg)
    ch4.set(r_ch4)
    propane.set(r_propane)
    smoke.set(r_smoke)
    logging.info("Server=" + str(r_server) + " CO=" + str(r_co) +
                    "ppm" + " LPG=" + str(r_lpg) + "ppm" + " CH4=" +
                    str(r_ch4) + "ppm" + " Propane=" +
                    str(r_propane) +"ppm" + "Smoke=" + str(r_smoke)+"ppm")
    return make_wsgi_app()


@app.route("/")
def mainPage():
    return ("<h1>Welcome to MQ2-Gas-Exporter.</h1>" +
            "Click <a href='/metrics'>here</a> to see metrics.")


if __name__ == '__main__':
    PORT = os.getenv('GAS_PORT', 9595)
    logging.info("Starting MQ2-Gas-Exporter on http://localhost:" +
                 str(PORT))
    serve(app, host='0.0.0.0', port=PORT)
