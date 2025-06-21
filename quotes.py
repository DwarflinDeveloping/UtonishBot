import json
import os
import traceback
from pathlib import Path
from typing import Iterator

from discord import Message

BENYI_IDS = [1324055373711147150, 1373731007064309844]


class QuoteGenerator:
    def __init__(self, save_path: os.PathLike = 'quotes.txt'):
        quotes_dir = os.getenv('QUOTES_DIR')
        if not quotes_dir:
            raise EnvironmentError('Environment variable \'QUOTES_DIR\' not specified!')
        self.quotes_dir = Path(quotes_dir)
        self.save_path = save_path

        self.quotes: list[str] = []
        self.run()

    def iter_messages(self) -> Iterator[dict]:
        for subdir in os.listdir(self.quotes_dir):
            for filename in os.listdir(self.quotes_dir / subdir):
                file_path = self.quotes_dir / subdir / filename
                if not file_path.is_file():
                    continue
                yield from json.loads(file_path.read_text())['messages']

    def check_quote(self, message: dict) -> bool:
        if int(message['author']['id']) not in BENYI_IDS:
            return False

        content = message['content']
        if len(content) < 7 or content in self.quotes:
            return False

        return True

    def run(self) -> None:
        for message in self.iter_messages():
            try:
                check = self.check_quote(message)
            except:
                traceback.print_exc()
                continue

            if check:
                self.quotes.append(message['content'])

    def save(self) -> None:
        exported_quotes = [quote.replace('\n', '\\n') + '\n' for quote in self.quotes]
        with open(self.save_path, 'w+', encoding='utf-8') as file:
            file.writelines(exported_quotes)

    @staticmethod
    def load(save_path: os.PathLike = 'quotes.txt') -> Iterator[str]:
        save_path = Path(save_path)
        if not save_path.is_file():
            return

        with open(save_path, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                yield line.replace('\\n', '\n').replace('@everyone', '\@everyone')[:-1]
