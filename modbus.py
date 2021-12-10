from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from scr.util import add_offset_and_decimal, remove_offset_and_decimal
from argparse import ArgumentParser
from time import sleep
import logging
import yaml
from protobuf import jpidata_pb2
import json
import time


# Define hyper/global variables
gateway_config = None
cli_args = None
modbus_client = None
id_regs = {"holding_registers": {"block-1": [], "block-2": []}, "input_registers": {"block-1": [], "block-2": []}}
corr_telemetry = {"holding_registers": {"block-1": [], "block-2": []}, "input_registers": {"block-1": [], "block-2": []}}
units = {"holding_registers": {"block-1": [], "block-2": []}, "input_registers": {"block-1": [], "block-2": []}}
register_names = {"holding_registers": {"block-1": [], "block-2": []}, "input_registers": {"block-1": [], "block-2": []}}
telemetry = {"holding_registers": [], "input_registers": []}
count = []
register_address = []
registers = ["holding_registers", "input_registers"]
blocks = ["block-1", "block-2"]
increment = 0


def convert_2proto():
    global registers, blocks, increment
    increment += 1
    _list = jpidata_pb2.JPIDataDelivery()
    _data = jpidata_pb2.JPIDataPair()
    _time = jpidata_pb2.JPIDataTimestamp()
    epoch_time = int(time.time())
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
    telemetry_out = _list
    print(f"{telemetry_out}")

    telemetry_output = telemetry_out.SerializeToString()
    print(telemetry_output)


def main():
    global gateway_config, modbus_client, telemetry, cli_args, count, register_address, corr_telemetry, units, register_names, registers, blocks

    # Load gateway configurations
    gateway_config = yaml.load(open(cli_args.gateway_config_file, "r", encoding='utf-8'), Loader=yaml.FullLoader)
    # print(json.dumps(gateway_config, indent=3))

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

    # Import slave device logging info display
    _format = ('%(asctime)-15s %(threadName)-15s'
               '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
    logging.basicConfig(format=_format)
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

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

    # Add offset and decimal to the fetched telemetry data

    for n in register_types:
        if n == holding_reg.items():
            register_accessed = registers[0]
            print(f"registers: {n}")
        else:
            register_accessed = registers[1]

        registers_data = telemetry.get(register_accessed)
        # print(f"register data set: {registers_data}")
        for k, v in n:
            for m in blocks:
                if k == m:
                    regs = list(v.keys())
                    if k == "block-1":
                        data = registers_data[0]
                    elif k == "block-2":
                        data = registers_data[1]
                    print(data)
                    register_names.get(register_accessed).update({m: regs})
                    i += 1
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

    for i in registers:
        for m in blocks:
            reg_name = register_names.get(i).get(m)
            reg_value = corr_telemetry.get(i).get(m)
            reg_unit = units.get(i).get(m)
            for itr in range(len(reg_name)):
                print(f"\t\t{reg_name[itr]} : {reg_value[itr]}{reg_unit[itr]}")

    print(f"Telemetry: {telemetry}")

    convert_2proto()


if __name__ == "__main__":
    # Handle command line parameters.
    parser = ArgumentParser()
    parser.add_argument(
        "gateway_config_file", type=str, help="The path to a gateway config."
    )
    cli_args = parser.parse_args()

    # Start the main function.
    main()
