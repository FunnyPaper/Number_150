import random
import math
import utilities as util
import threading
import time
from dataclasses import dataclass, astuple


@dataclass(frozen=True)
class EvolutionIteration:
    """
    Combines set of data into one object
    """
    iteration: int
    population: list[int, ...]
    best_number: int

    def __iter__(self):
        return iter(astuple(self))

    def __getitem__(self, item):
        return iter(getattr(self, i) for i in item)


class NumberEvolver:
    @property
    def desired_number(self) -> int:
        """
        Number desired in evolution

        :return: Desired number
        """
        return self.__desired_number

    @property
    def history(self) -> list[EvolutionIteration, ...]:
        """
        Recorder history of ongoing populations

        :return: Population history
        """
        return self.__history

    def __init__(self,
                 desired_number: int,
                 population_size: int = 8,
                 max_number: int = 255,
                 cross_range: int = 1,
                 sleep: float = 1):
        """
        Initializes NumberEvolver instance

        :param desired_number: Target of evolution (between 0 and max_number)
        :param population_size: Size of population every iteration (at least 2)
        :param max_number: Maximum possible value inside population
        :param cross_range: Range of how many bits will become subject to crossing (less than half the population_size)
        :param sleep: Evolution's process time in seconds
        """
        # default data
        self.__desired_number: int = min(max(0, desired_number), max_number)
        self.__population_size: int = max(population_size, 2)
        self.__max_bits: int = math.floor(math.log(max_number, 2)) + 1
        self.__cross_range: int = min(self.__max_bits // 2, cross_range)
        self.__best: float = math.inf
        self.__iteration: int = 0
        self.__new_pop: list[int, ...] = []
        self.__history: list[EvolutionIteration, ...] = []
        self.__sleep: float = sleep

        # Create starting population
        self.__population: list[int, ...] = [random.randint(0, max_number) for _ in range(self.__population_size)]
        print('population', self.__population)

        # Threading context (moves sleep blocking logic to second thread)
        self.__thread: threading.Thread = threading.Thread(target=self.__evolve, daemon=True)

    def start(self) -> None:
        """
        Starts evolution process
        """
        self.__thread.start()

    def __evolve(self) -> None:
        """
        Evolves current population
        """
        # Keep evolving until desired number has not been reached
        while self.__best != self.__desired_number:
            self.__iteration += 1

            # Sort data for easier manipulation later (numbers that are closest to best will take earlier slots)
            self.__population = sorted(self.__population, key=lambda x: abs(x - self.__best))

            # Create new population based on previous one (25% or at least 2)
            self.__population = self.__population[:max(self.__population_size // 4, 2)]
            print('best', self.__best, 'size new', len(self.__population), self.__population)

            # Recreate population
            for _ in range(self.__population_size):
                # Draw two individuals
                random.shuffle(self.__population)
                male: list[int, ...] = util.dec_to_bin(self.__population[0], places=self.__max_bits)
                female: list[int, ...] = util.dec_to_bin(self.__population[1], places=self.__max_bits)

                # Cross individuals
                cross: int = random.randint(0, self.__max_bits // 2 - 1)
                for j in range(self.__cross_range):
                    male[cross + j], female[cross + j] = female[cross + j], male[cross + j]

                # Mutate
                mutation_id: int = random.randint(0, self.__max_bits - 1)
                male[mutation_id] = 1 - male[mutation_id]
                female[mutation_id] = 1 - female[mutation_id]

                # Add to new population
                children: list[int, int] = sorted(
                    [util.bin_to_dec(male), util.bin_to_dec(female)],
                    key=lambda x: abs(x - self.__best)
                )
                self.__new_pop.append(children[0])
            else:
                self.__population = self.__new_pop
                self.__new_pop = []
                print('iteration', self.__iteration, 'population', self.__population)

            # Search for best match
            for num in self.__population:
                num_diff: int = abs(self.__desired_number - num)
                best_diff: int = abs(self.__desired_number - self.__best)
                self.__best = self.__best if best_diff <= num_diff else num

            # Update history
            self.__history.append(EvolutionIteration(self.__iteration, self.__population, self.__best))

            # Wait for fixed time step (simulate extensive calculations)
            time.sleep(self.__sleep)
