from asyncua import Client
import asyncio
import matplotlib.pyplot as plt

class DataChangeHandler:
    """Handles data change notifications."""
    def datachange_notification(self, node, val, data):
        print(f"Node {node} value changed to: {val}")
        print(f"Data: {data}")

async def main():
    async with Client(url='opc.tcp://localhost:4841/freeopcua/server/') as client:
        print("Connected to the server")
    
        print("Getting tags...")
        objects_node = client.nodes.objects
        children = await objects_node.get_children()

        print("Tags available on the server:")
        node_ids = []
        for child in children:
            display_name = await child.read_display_name()
            node_id = child.nodeid
            print(f"Node: {display_name.Text} | Node ID: {node_id}")
            node_ids.append(node_id)

        node_id = node_ids[3]
        node = client.get_node(node_id)
        handler = DataChangeHandler()
        subscription = await client.create_subscription(500, handler)
        await subscription.subscribe_data_change(node)
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
