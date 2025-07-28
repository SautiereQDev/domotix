"""
Base command module for the Command pattern.

This module contains the abstract Command class that serves as the base
for all system commands.

Classes:
    Command: Abstract base class for all commands
"""

from abc import ABC, abstractmethod


class Command(ABC):
    """
    Abstract base class for all commands.

    This class defines the common interface that all commands
    must implement to use the Command pattern.

    Abstract Methods:
        execute(): Executes the command
    """

    @abstractmethod
    def execute(self):
        """
        Executes the command.

        This method must be implemented by all subclasses.
        """
        raise NotImplementedError(
            "The execute method must be implemented by subclasses"
        )
