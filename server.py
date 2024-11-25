from asyncua import Client
import asyncio
from database import Database
from urllib.parse import ParseResult, urlunparse
import json

CONFIG_PATH = "tag_config.json"

class DataChangeHandler:
    def __init__(self, host, tag, database) -> None:
        print(host)
        self.server_url = host['host']
        self.database = database
        self.tag = tag
        print(f"Created data handler for server {self.server_url} and tag {self.tag}")

    """Handles data change notifications."""
    def datachange_notification(self, node, val, data):
        payload = {self.tag: val}
        print(f"Payload: {payload}")
        self.database.write(self.server_url, payload)

class OPCUADataCollector:
    def __init__(self, config) -> None:
        self.config = config
        self.hosts = config["plc_hosts"]
        self.clients = []
        self.database = Database(config["database_host"], config["influx_org"], config["influx_database"])

    async def connect_to_servers(self):
        """Connect to all OPC UA servers."""
        for host in self.hosts:
            url = self.hosts[host]['host']
            client = Client(url)
            await client.connect()
            self.clients.append((client, self.hosts[host]))
            print(f"Connected to {url}")

    async def _find_node_ids(self, client: Client, tags: list[str]) -> list:
        objects_node = client.nodes.objects
        children = await objects_node.get_children()
        node_ids = []
        for child in children:
            display_name = await child.read_display_name()
            if display_name.Text in tags:
                node_ids.append((child.nodeid, display_name.Text))
        return node_ids

    async def create_subscription(self, client: Client, host: dict):
        """Create subscriptions to monitor tags"""
        tags = [tag for tag in host["tags"]]
        nodes = await self._find_node_ids(client, tags)
        for node_id, tag in nodes:
            node = client.get_node(node_id)

            handler = DataChangeHandler(host, tag, self.database)
            subscription = await client.create_subscription(host['tags'][tag]['period'], handler)
            await subscription.subscribe_data_change(node)

    async def collect(self):
        """Create subscriptions from all connected servers."""
        tasks = []
        for client, host in self.clients:
            tasks.append(self.create_subscription(client, host))
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

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    collector = OPCUADataCollector(config)
    await collector.connect_to_servers()
    await collector.start()

if __name__ == "__main__":
    asyncio.run(main())
