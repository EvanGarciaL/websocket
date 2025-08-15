import json
import asyncio
from websockets.asyncio.server import serve
import logging  

from connect4 import PLAYER1, Connect4

# logging.basicConfig(
#   format="%(asctime)s %(message)s",
#   level=logging.DEBUG,
# )

async def handler(websocket) -> None:
  game = Connect4()
  current_player = PLAYER1

  async for message in websocket:
    message = json.loads(message)

    next_player = game.last_player
    row = game.play(player=current_player,column=message["column"])

    try:
        play_event = {
          "type": "play",
          "player": current_player,
          "column": message["column"],
          "row": row,
        }
        await websocket.send(json.dumps(obj=play_event))

    except Exception as e:
      error_event = {
        "type" : "error",
        "message" :  str(object=e),
      }
      await websocket.send(json.dumps(obj=error_event))
      continue

    else:
      if game.last_player_won:
        win_event = {
          "type" : "win",
          "player" : game.winner,
        }
        await websocket.send(json.dumps(obj=win_event))

      current_player = next_player


async def main() -> None:
  async with serve(handler, "", 8001) as server:
      await server.serve_forever()

if __name__ == "__main__":
  asyncio.run(main())