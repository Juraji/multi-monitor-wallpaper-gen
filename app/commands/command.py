from abc import ABC, abstractmethod
# noinspection PyProtectedMember
from argparse import Namespace, _SubParsersAction, ArgumentParser

type SubParsersAction = _SubParsersAction[ArgumentParser]

class Command(ABC):

    def __init__(self, sub_parsers: SubParsersAction, command: str, description: str):
        self.command = command
        self.description = description

        parser = sub_parsers.add_parser(name=command, description=description)
        self.register_arguments(parser)

    @abstractmethod
    def register_arguments(self, parser: ArgumentParser):
        pass

    @abstractmethod
    def execute(self, args: Namespace) -> int:
        pass
