import asyncio
import pathlib

import httpx
from rich.console import Console

token = pathlib.Path("token.txt").read_text()

client = httpx.AsyncClient(headers={"authorization": token})

console = Console(highlight=False)

emojis = pathlib.Path("emojis")
if not emojis.exists():
    emojis.mkdir()


def cprint(color, content):
    console.print(f"[ [bold {color}]>[/] ] {content}")


def save(server_id: str, emoji_name: str, content: bytes):
    path = pathlib.Path(emojis, server_id, emoji_name)
    if path.exists():
        return

    path.touch()
    path.write_bytes(content)


async def download_guild_emojis(server_id: str):
    path = pathlib.Path(emojis, server_id)
    if not path.exists():
        path.mkdir()

    req = await client.get(f"https://discord.com/api/v9/guilds/{server_id}/emojis")
    res = req.json()

    for emoji in res:
        extension = "gif" if emoji.get("animated") else "png"
        name = f"{emoji.get('name')}.{extension}"

        req = await client.get(f"https://cdn.discordapp.com/emojis/{name}")
        res = req.content

        save(server_id, name, res)
        cprint("green", f"Successfully saved {name} from {server_id}")


async def main():
    req = await client.get("https://discord.com/api/v9/users/@me/guilds")
    res = req.json()

    guild_ids = [guild.get("id") for guild in res]
    coros = [download_guild_emojis(guild) for guild in guild_ids]

    await asyncio.gather(*coros)


asyncio.run(main())
