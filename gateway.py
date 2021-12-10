import asyncio
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import MethodResponse, Message
from scr.util import remove_offset_and_decimal, add_offset_and_decimal
from protobuf import jpidata_pb2
from dotenv import load_dotenv
from os import getenv
import time
from time import sleep
import logging
import json
import yaml

# Define global parameters
gateway_config = None
cli_args = None
reg_address, decimal, offset, id_, settings = None, None, None, None, None
registers_types = ["holding_registers"]
blocks = ["block-1", "block-2"]
modbus_client = None
id_regs = {"holding_registers": {"block-1": [], "block-2": []}, "input_registers": {"block-1": [], "block-2": []}}
corr_telemetry = {"holding_registers": {"block-1": [], "block-2": []}, "input_registers": {"block-1": [], "block-2": []}}
units = {"holding_registers": {"block-1": [], "block-2": []}, "input_registers": {"block-1": [], "block-2": []}}
register_names = {"holding_registers": {"block-1": [], "block-2": []}, "input_registers": {"block-1": [], "block-2": []}}
telemetry = {"holding_registers": [], "input_registers": []}
count = []
register_address = []
registers = ["holding_registers", "input_registers"]


# Protobuf variables
_list = jpidata_pb2.JPIDataDelivery()
_time = jpidata_pb2.JPIDataTimestamp()
_data = jpidata_pb2.JPIDataPair()
epoch_time = int(time.time())
_single_data = jpidata_pb2.JPIDataPair()
_single_time = jpidata_pb2.JPIDataTimestamp()
_single_list = jpidata_pb2.JPIDataDelivery()

# Retrieve connection string
load_dotenv()
connection_string = getenv("CONNECTION_STRING")

# Import slave device logging info display
_format = ('%(asctime)-15s %(threadName)-15s'
           '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=_format)
log = logging.getLogger()
log.setLevel(logging.DEBUG)


# Function that exits CLI
def stdin_listener():
    """
    Listener for quitting the sample
    """
    while True:
        selection = input("Press Q to quit\n")
        if selection == "Q" or selection == "q":
            print("Quitting...")
            break


# Function that converts fetched telemetry to protobuf format
def convert_2proto():
    global registers, blocks, corr_telemetry, id_regs, _list, _data, _time, epoch_time
    _list.Clear()
    _time.Clear()
    for i in registers:
        for m in blocks:
            reg_value = corr_telemetry.get(i).get(m)
            id_reg = id_regs.get(i).get(m)

            for cnt in id_reg:
                if cnt is None:
                    continue
                else:
                    # JPIDataPair
                    _data.id = cnt
                    _data.intval = reg_value[id_reg.index(cnt)]
                    # JPIDataTimestamp
                    _time.data.append(_data)
                    _time.timestamp = epoch_time

    # JPIDataDelivery
    _list.timestamps.append(_time)
    telemetry_output = _list.SerializeToString()
    return telemetry_output


# Function to get telemetry data from Optima
def get_telemetry():
    global gateway_config, modbus_client, telemetry, cli_args, count, register_address, corr_telemetry, units, register_names, registers, blocks, data

    # Retrieve gateway configuration parameters
    fieldbus = gateway_config.get("fieldbus")
    slaves = gateway_config.get("slaves")
    slave = slaves.get("optima")
    slave_id = slave.get("sid")
    modbus = fieldbus.get("modbus")
    holding_reg = slave.get("holding_registers")
    input_reg = slave.get("input_registers")
    slave_address = 0x01

    # Configure modbus client
    modbus_client = ModbusClient(
        method=modbus.get("method"),
        port=modbus.get("port"),
        parity=modbus.get("parity"),
        baudrate=modbus.get("baudrate"),
        bytesize=modbus.get("bytesize"),
        stopbits=modbus.get("stopbits"),
        timeout=modbus.get("timeout")
    )

    # Get input and holding register counts, start_address
    register_types = [holding_reg.items(), input_reg.items()]
    for i in register_types:
        for k, v in i:
            if k == "block-1":
                count.append(len(v.keys()))
                addr = str(list(v.keys())[0])
                start_addr = v.get(addr).get("address")
                register_address.append(int(start_addr))
            if k == "block-2":
                count.append(len(v.keys()))
                addr = str(list(v.keys())[0])
                start_addr = v.get(addr).get("address")
                register_address.append(int(start_addr))

    # Read telemetry data from modbus client
    retries = max(4, 0)
    cnt = [0, 1, 2, 3]

    # Connect to modbus client (OPT-251)
    try:
        modbus_client.connect()
        print(f"Connected to {slave_id}")
    except:
        print(f"Remote Slave Device:{slave_id} not Physically connected to gateway")

    # Reset registers
    for i in registers:
        telemetry.get(i).clear()

    # Read holding_registers
    for i in cnt[0:2:1]:
        rr_holding = modbus_client.read_holding_registers(address=register_address[i],
                                                          count=count[i], unit=slave_address)
        sleep(0.5)
        while rr_holding.isError():
            if retries == 0:
                return
            retries -= 1
            rr_holding = modbus_client.read_holding_registers(address=register_address[i],
                                                              count=count[i], unit=slave_address)
            sleep(0.5)
        telemetry["holding_registers"].append(rr_holding.registers)
    sleep(0.5)

    # Read input_registers
    for i in cnt[2:4:1]:
        rr_input = modbus_client.read_input_registers(address=register_address[i],
                                                      count=count[i], unit=slave_address)
        sleep(0.5)
        while rr_input.isError():
            if retries == 0:
                return
            retries -= 1
            rr_input = modbus_client.read_input_registers(address=register_address[i],
                                                          count=count[i], unit=slave_address)
            sleep(0.5)
        telemetry["input_registers"].append(rr_input.registers)

    # Reset corr_telemetry_list and id_regs list
    for i in registers:
        for m in blocks:
            corr_telemetry.get(i).get(m).clear()
            id_regs.get(i).get(m).clear()

    # Add offset and decimal to the fetched telemetry data
    for n in register_types:
        if n == holding_reg.items():
            register_accessed = registers[0]
            cnt = count[0:2:1]
        else:
            register_accessed = registers[1]
            cnt = count[2:4:1]
        registers_data = telemetry.get(register_accessed)
        for k, v in n:
            for m in blocks:
                if k == m:
                    regs = list(v.keys())
                    if k == "block-1":
                        data = registers_data[0]
                    elif k == "block-2":
                        data = registers_data[1]
                    register_names.get(register_accessed).update({m: regs})
                    for reg in range(len(regs)):
                        register = regs[reg]
                        offset = v.get(register).get("offset") or 0
                        decimal = v.get(register).get("decimal") or 0
                        unit = v.get(register).get("unit") or ' '
                        _id = v.get(register).get("id") or None
                        raw_data = data[reg]
                        real_value = add_offset_and_decimal(raw_data, offset, decimal)
                        corr_telemetry.get(register_accessed)[m].append(real_value)
                        units.get(register_accessed)[m].append(unit)
                        id_regs.get(register_accessed)[m].append(_id)

    # Print telemetry data
    for i in registers:
        for m in blocks:
            reg_name = register_names.get(i).get(m)
            reg_value = corr_telemetry.get(i).get(m)
            reg_unit = units.get(i).get(m)
            for itr in range(len(reg_name)):
                print(f"\t\t{reg_name[itr]} : {reg_value[itr]}{reg_unit[itr]}")


# Function that executes write commands to Optima
def modbus_write(value, id_):
    global reg_address, offset, decimal, gateway_config
    modbus = gateway_config.get("fieldbus").get("modbus")
    holding_reg = gateway_config.get("slaves").get("optima").get("holding_registers")
    slave_address = 0x01
    # Configure modbus client
    _client = ModbusClient(
        method=modbus.get("method"),
        port=modbus.get("port"),
        parity=modbus.get("parity"),
        baudrate=modbus.get("baudrate"),
        bytesize=modbus.get("bytesize"),
        stopbits=modbus.get("stopbits"),
        timeout=modbus.get("timeout")
    )
    for m in blocks:
        for u in holding_reg.get(m).keys():
            if holding_reg.get(m).get(u).get("id") == id_:
                reg_address = holding_reg.get(m).get(u).get("address")
                print(f"Reg_address :{reg_address}")
                offset = holding_reg.get(m).get(u).get("offset") or 0
                print(f"Offset is: {offset}")
                decimal = holding_reg.get(m).get(u).get("decimal") or 0
                print(f"Decimal is:{decimal}")

    # Write data to modbus_client
    retries = max(4, 0)
    raw_value = remove_offset_and_decimal(value, offset, decimal)
    print(f"Raw value is: {raw_value}")
    rw = _client.write_register(address=reg_address, value=raw_value, unit=slave_address)
    sleep(0.5)
    while rw.isError():
        if retries == 0:
            return
        retries -= 1
        rw = _client.write_register(address=reg_address, value=raw_value, unit=slave_address)
        sleep(0.5)
    sleep(1)


# Asynchronous Main Function
async def main():
    global registers, blocks, reg_address, gateway_config
    # Connect to JPI cloud
    device_client = IoTHubDeviceClient.create_from_connection_string(connection_string)

    # Load config file
    gateway_config = yaml.load(open("C:/../gateway-1.yaml", "r", encoding='utf-8'), Loader=yaml.FullLoader)

    # Keep Connection alive.
    await device_client.connect()

    # Send the telemetry data to IoT HuB
    async def send_telemetry():
        print("Sending telemetry")
        while True:
            get_telemetry()
            payload = convert_2proto()
            # print(f"Payload to be sent is: {payload}")
            msg = Message(payload, content_type="telemetry/pb")
            await device_client.send_message(msg)
            await asyncio.sleep(30)

    async def message_received_handler(message):
        # Print Received payload
        global reg_address, offset, decimal, gateway_config, _id, _value, id_, settings, id_reg, value_reg,_single_data,_single_list,_single_time
        print(f"Message_id is: {message.request_id}")
        method_name = message.name
        print(f"Method name: {method_name}")
        _single_list.Clear()
        _single_time.Clear()

        # Method to handle settings
        if method_name == "settings":
            method_payload = message.payload
            print(f"Method Payload {method_payload}")
            settings = method_payload["settings"]
            id_reg = int(list(settings.keys())[0])
            value_reg = int(list(settings.values())[0])
            print(f"id_reg: {id_reg,type(id_reg)}")
            print(f"Value_reg :{value_reg, type(value_reg)}")
            print(f"Settings: {settings}")
            for k, v in settings.items():
                _id = k
            print(type(_id))

            # Write to the modbus slave device and send response to cloud
            modbus_write(value=value_reg, id_=id_reg)
            _single_data.id = id_reg
            _single_data.intval = value_reg
            _single_time.data.append(_single_data)
            _single_time.timestamp = epoch_time
            _single_list.timestamps.append(_single_time)
            print(f"_single_list is :{_single_list}")
            _output = _single_list.SerializeToString()
            msg = Message(_output, content_type="telemetry/pb")
            await device_client.send_message(msg)

            # Send method response to cloud
            method_response = MethodResponse(message.request_id, status=200, payload=json.dumps({"'"+_id+"'": 'modified'}))
            await device_client.send_method_response(method_response)

        # Method to handle forcesync
        if method_name == "forcesync":
            method_response = MethodResponse(message.request_id, status=200, payload=json.dumps({'state': 'ok'}))
            await device_client.send_method_response(method_response)

    device_client.on_method_request_received = message_received_handler

    # Run the telemetry_loop in an event loop.
    send_telemetry_task = asyncio.create_task(send_telemetry())

    loop = asyncio.get_running_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)

    # Wait for user to indicate they are done listening for messages
    await user_finished

    if user_finished:
        send_telemetry_task.cancel()
        await device_client.shutdown()


if __name__ == "__main__":

    # Start the main function.
    asyncio.run(main())
