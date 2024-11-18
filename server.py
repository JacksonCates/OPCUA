from asyncua import Client
import asyncio

class DataChangeHandler:
    def __init__(self, server_url) -> None:
        self.server_url = server_url

    """Handles data change notifications."""
    def datachange_notification(self, node, val, data):
        print(f"Node {node} at {self.server_url.netloc} value changed to: {val}")
        #print(f"Data: {data}")

class OPCUADataCollector:
    def __init__(self) -> None:
        self.server_urls = [
            "opc.tcp://localhost:4840/freeopcua/server/",
            "opc.tcp://localhost:4841/freeopcua/server/",
            "opc.tcp://localhost:4842/freeopcua/server/"
            ] # TODO : Config
        self.tags = ["Pressure", "Temperature"] # TODO : Config
        self.clients = []

    async def connect_to_servers(self):
        """Connect to all OPC UA servers."""
        for url in self.server_urls:
            client = Client(url)
            await client.connect()
            self.clients.append(client)
            print(f"Connected to {url}")

    async def _find_node_ids(self, client: Client, tags: list[str]) -> list:
        objects_node = client.nodes.objects
        children = await objects_node.get_children()
        node_ids = []
        for child in children:
            display_name = await child.read_display_name()
            if display_name.Text in tags:
                node_ids.append(child.nodeid)
        return node_ids

    async def create_subscription(self, client: Client):
        """Create subscriptions to monitor tags"""
        node_ids = await self._find_node_ids(client, self.tags)
        for node_id in node_ids:
            node = client.get_node(node_id)
            
            handler = DataChangeHandler(client.server_url)
            subscription = await client.create_subscription(500, handler)
            await subscription.subscribe_data_change(node)

    async def collect(self):
        """Create subscriptions from all connected servers."""
        tasks = []
        for client in self.clients:
            tasks.append(self.create_subscription(client))
        await asyncio.gather(*tasks)

    async def start(self):
        """Main method to start the server"""
        await self.collect()
        await asyncio.Event().wait() # Wait forever

    async def disconnect(self):
        """Disconnect all OPC UA clients."""
        for client in self.clients:
            await client.disconnect()

async def main():
    collector = OPCUADataCollector()
    await collector.connect_to_servers()
    await collector.start()

if __name__ == "__main__":
    asyncio.run(main())
