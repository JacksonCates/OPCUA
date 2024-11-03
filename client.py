from asyncua import Client
import asyncio
import matplotlib.pyplot as plt

async def main():

    n = 300
    data = {}

    async with Client(url='opc.tcp://localhost:4840/freeopcua/server/') as client:
        print("Connected to the server")
    
        print("Getting tags...")
        objects_node = client.nodes.objects
        children = await objects_node.get_children()

        print("Tags available on the server:")
        for child in children:
            display_name = await child.read_display_name()
            node_id = child.nodeid
            print(f"Node: {display_name.Text} | Node ID: {node_id}")
            data[display_name.Text] = []

        print(f"Reading tags for {n} steps...")
        for i in range(n):
            for child in children:
                display_name = await child.read_display_name()
                try:
                    value = await child.get_value()
                    print(f"Node: {display_name.Text} | Value: {value}")
                    data[display_name.Text].append(value)
                except Exception as e:
                    print(f"Failed to read value for node '{display_name.Text}': {e}")
            await asyncio.sleep(1)

    print("Tag data:", data)
    plt.figure(figsize=(10, 5))
    plt.plot(data['Timestamp'], data['Temperature'], label='Temperature')
    plt.plot(data['Timestamp'], data['Pressure'], label='Pressure')
    plt.xlabel('Timestamp')
    plt.ylabel('Values')
    plt.legend()
    plt.tight_layout()
    plt.savefig("plc_readings.png")

if __name__ == "__main__":
    asyncio.run(main())