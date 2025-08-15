import asyncio
from websockets.sync.client import connect 
from websockets.asyncio.client import connect as async_connect

uri = "ws://localhost:8765"

def echo() -> None:
  with connect(uri=uri) as websocket:
    name = input("What's your name?")

    websocket.send(name)
    print(f"<<< {name}")

    greeting = websocket.recv()
    print(f">>> {greeting}")


async def echo_async() -> None:
  async with async_connect(uri=uri) as websocket:
    name = input("What's your name?")

    await websocket.send(name)
    print(f"<<< {name}")

    greeting = await websocket.recv()
    print(f">>> {greeting}")


async def main():
   await asyncio.gather(echo_async())


if __name__ == "__main__":
  #  asyncio.run(echo_async())
  #  asyncio.run(main())
   echo()