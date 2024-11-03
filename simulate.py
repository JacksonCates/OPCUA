import asyncio
from asyncua import Server
from datetime import datetime
import random

class OPCUAServerSimulator:
    def __init__(self, endpoint="opc.tcp://0.0.0.0:4840/opcua/server/", name="OPCUA Server Simulator"):
        self.server = Server()
        self.server.set_endpoint(endpoint)
        self.server.set_server_name(name)
        self.objects_node = self.server.nodes.objects
        self.tags = {}

    async def _init(self, uri = "http://examples.freeopcua.github.io"):
        await self.server.init()
        self.idx = await self.server.register_namespace(uri)

    async def add_tag(self, tag_name, initial_value=0, writable=True):
        tag = await self.objects_node.add_variable(self.idx, tag_name, initial_value)
        if writable:
            await tag.set_writable()
        self.tags[tag_name] = tag
        print(f"Tag '{tag_name}' added with initial value {initial_value}")

    async def update_tag(self, tag_name, new_value):
        if tag_name in self.tags:
            await self.tags[tag_name].write_value(new_value)
            print(f"Tag {tag_name} updated to {new_value}")
        else:
            print(f"Tag {tag_name} not found")

    async def start(self):
        async with self.server:
            print(f"OPC UA Server started at {self.server.endpoint}")
            while True:
                if "Timestamp" in self.tags:
                    await self.update_tag("Timestamp", datetime.now())
                await asyncio.sleep(1)

async def main():
    plc_simulator = OPCUAServerSimulator()
    await plc_simulator._init()

    await plc_simulator.add_tag("Temperature", 25.0)
    await plc_simulator.add_tag("Pressure", 100.0)
    await plc_simulator.add_tag("Timestamp", datetime.now())

    async def simulate_tag_update():
        while True:
            await plc_simulator.update_tag("Temperature", 25 + 5*random.uniform(-1,1))
            await plc_simulator.update_tag("Pressure", 100 + 10*random.uniform(-1,1))
            await asyncio.sleep(1)

    await asyncio.gather(
        plc_simulator.start(),
        simulate_tag_update()
    )

if __name__ == "__main__":
    asyncio.run(main())
