import json
import asyncio
from websockets.asyncio.server import serve, ServerConnection
import secrets
from typing import Literal

from connect4 import PLAYER1, PLAYER2, Connect4


JOIN = {}
WATCH = {}


async def start(websocket: ServerConnection) -> None:
    # Creates game instace
    game = Connect4()
    # Set with the different connections to server
    connected = {websocket}

    # Join key for game
    # Maps both the game instance and connection
    join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = game, connected

    try:
       # Signal that game is starting, send join key to
        event = {
            "type": "init",
            "join": join_key
        }

        await websocket.send(json.dumps(event))

        print("Player started game", id(websocket))
        await play(websocket, game, PLAYER1, connected)
    finally:
        del JOIN[join_key]


async def join(websocket: ServerConnection, join_key: str) -> None:
    try:
        game, connected = JOIN[join_key]
        game: Connect4
        connected: set[ServerConnection]
    except KeyError:
        await error(websocket, "Game not found")
        return

    connected.add(websocket)

    try:
        print("Player joined", id(websocket))
        await play(websocket, game, PLAYER2, connected)
    finally:
        connected.remove(websocket)


async def error(
    websocket: ServerConnection,
    message: str
) -> None:
    event = {
        "type": "error",
        "message": str(message)
    }
    await websocket.send(json.dumps(event))


async def play(
    websocket: ServerConnection,
    game: Connect4,
    player: Literal['red'] | Literal['yellow'],
    connected: set[ServerConnection]
) -> None:

    async for message in websocket:
        play = json.loads(message)
        try:
            row = game.play(player, play["column"])
            play_event = {
                "type": "play",
                "player": player,
                "column": play["column"],
                "row": row
            }
            print(play_event)
            for connection in connected:
                print("WEBSOCKET -", id(connection))
                await connection.send(json.dumps(play_event))
        except ValueError as ve:
            # If player clicks on board when its not their turn
            # or if they click on a column thats full,
            # show message to only that player without
            # killing their connection
            await error(websocket, str(ve))
            continue
        except Exception as e:
            await error(websocket, str(e))
            return

        else:
            if game.last_player_won:
                win_event = {
                    "type": "win",
                    "player": game.winner,
                }
                for connections in connected:
                    await connections.send(json.dumps(win_event))


async def handler(websocket: ServerConnection) -> None:
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if "join" in event:
        await join(websocket, event["join"])
    else:
        await start(websocket)


async def main() -> None:
    async with serve(handler, "", 8001) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
