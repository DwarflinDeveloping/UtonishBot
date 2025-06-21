import asyncio
import os
from typing import NoReturn

from dotenv import load_dotenv

from bot import UtonishBot
from quotes import QuoteGenerator


def test_quotes() -> None:
    generator = QuoteGenerator()
    print(len(generator.quotes), generator.quotes)
    generator.save()

    quotes = list(QuoteGenerator.load())
    print(len(quotes), quotes)


def main() -> NoReturn:
    load_dotenv()
    # test_quotes()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        bot = UtonishBot()
        bot.setup()

        loop.create_task(bot.start())
        loop.run_forever()

    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()

