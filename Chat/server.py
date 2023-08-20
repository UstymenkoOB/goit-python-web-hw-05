import asyncio
import logging
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from exchange import *

logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if "exchange" in message.lower():
                text = await exchange(message.split())
                await self.send_to_clients(f"{ws.name} requests an exchange rates: ")
                for entry in text:
                    date = list(entry.keys())[0]
                    await self.send_to_clients(f'{date}')
                    currencies = entry[date]
                    for currency, rates in currencies.items():
                        sale_rate = rates['sale']
                        purchase_rate = rates['purchase']
                        await self.send_to_clients(f"  {currency}: sale: {sale_rate}, purchase: {purchase_rate}")
            else:
                await self.send_to_clients(f"{ws.name}: {message}")
        

async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
