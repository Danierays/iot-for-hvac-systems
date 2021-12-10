## HVAC Device -> PC -> Cloud(MyUplink)

### Device Hierarchy
```txt
|-- gateway
|   |
|   |-- OPT-251
```
The gateway retrieves telemetry from the connected modbus slave device, converts it to protobuf formatted data and sends it to the IoT hub. 
On the other hand, It receives read/write commands from the IoT Hub and serves the command accordingly.
W.r.t this data flow, we can come up with a structure for gateway.py as shown below;

#### Gateway.py Structure
##### PSEUDO - CODE
     
     Retrieve connection string from venv and initialiase global variables
    
     Function that retrieves telemetry data from modbus slave device
        def get_telemetry():
     Funtion to convert the telemetry data into protobuf format and returns serialized data(_list.timestamps.SerializeToString())
        def convert_2proto():
     Send the telemetry data to the IoT Hub
        async def send_telemetry(list.timestamps.SerializeToString()):
                msg= Message(list.timestamps.SerializeToString())
                msg.custome_properties["topic"] = "telemetry_topic"
                await device_client.send_message(msg)
     While sending the fetched telemetry every 10secs, gateway listens for any message from IoT Hub.
        device_client.on_message_received = message_recieved_handler
     Sort out the received command according to request. telemetry, device_twin, 
        async def message_received_handler(message):
              Check message custom properties for topic to be addressed
                message.custom_properties["topic"]
              Check message data
                message.data
              Check message content_type
                message.content_type   
              With the retrieved topic, data and content_type, data is processed accordingly
     Update device twin reported properties
       reported_properties = {}
       await device_client.client.patch_twin_reported_properties(reported_properties)
    
    Define main function
    async def main():
         Connect device_client to IoT_Hub
         Loop every 10secs except KeyBoardInterrupt
                get_telemetry()
                convert_2proto()
                send_telemetry()
         Call function which asynchronously listens to incoming messages 
                device_client.on_message_received
         Handles the received message is parsed to the handler function 
                message_received_handler(message)
                 Sends the reply back to the cloud and updates the device twin at the same time
                        send_message(message)
                update_twin()
