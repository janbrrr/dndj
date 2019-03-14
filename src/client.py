import asyncio


async def client():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)

    data = await reader.read(1000)
    print(f'{data.decode()}')
    while True:
        message = input("Enter the index: ")
        writer.write(message.encode())

        data = await reader.read(1000)
        print()
        print(f'{data.decode()}')
