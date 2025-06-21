import os

from dotenv import load_dotenv

load_dotenv()


def admin_guilds() -> list[int]:
    gids = os.getenv('ADMIN_GUILDS')
    print(gids)
    print([int(gid) for gid in gids.split(',')] if gids else [])
    return [int(gid) for gid in gids.split(',')] if gids else []
