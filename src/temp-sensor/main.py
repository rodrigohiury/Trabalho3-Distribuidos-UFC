from device_receive_multcast_udp import start_udp_listener
from device_send_state_mq import SendState
from simul import simular_temp_sensor

import threading

if __name__ == "__main__":
    # Cria threads para cada função
    SendStateInstance = SendState()
    thread_udp = threading.Thread(target=start_udp_listener, name="UDPListener", args=(SendStateInstance,))
    thread_simul = threading.Thread(target=simular_temp_sensor, name="SimulTempSensor")
    thread_send_data = threading.Thread(target=SendStateInstance.start_sending, name="SendStateMQ")

    # Inicia as threads
    thread_udp.start()
    thread_simul.start()
    thread_send_data.start()
