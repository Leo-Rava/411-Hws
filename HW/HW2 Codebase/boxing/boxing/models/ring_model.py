import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """
    A class to manage a ring of boxers.

    Attributes:
        ring (List[Boxer]): The lust of boxers (2) in the ring

    """

    def __init__(self):
        """Initializes the RingModel with an empty ring.

        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """Simulates fight between boxers added to ring
        
        Args: None

        Raises: 
            ValueError: If there are less than two boxers in the ring
        
        """
        logger.info("Recieved request to fight two boxers")

        if len(self.ring) < 2:
            logger.error("Invalid value: Not enough boxers in the ring.")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)
        logger.info("Successfully recieved skills from boxers")

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()

        return winner.name

    def clear_ring(self):
        """Clears all songs from the playlist.

        Clears all boxers from the ring. If the ring is already empty, logs a warning.

        """
        logger.info("Recieved request to clear the ring")

        if not self.ring:
            logger.error("Clearing an empty ring")
            return
        self.ring.clear()
        logger.info("Successfully cleared the ring")

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to add to the ring.

        Raises:
            TypeError: If the song is not a valid Boxer instance.
            ValueError: If a boxer with the same 'name' already exists.

        """
        if not isinstance(boxer, Boxer):
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        if not self.ring:
            pass
        else:
            pass

        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill
