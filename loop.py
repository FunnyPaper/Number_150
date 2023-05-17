import pygame
import utilities as util
from number_evolver import NumberEvolver
from enum import IntEnum


class Loop:
    """
    Abstracts game loop operations
    """
    class Alignment(IntEnum):
        """
        Label alignments
        """
        LEFT = 0
        TOP = 1
        RIGHT = 2
        BOTTOM = 3
        CENTER = 4

    def __init__(self,
                 size: tuple[int, int] = (1080, 800),
                 caption: str = "Genetic algorithm"):
        """
        Initializes Loop instance

        :param size: Window screen size
        :param caption: Window title caption
        """
        # default data
        self.__size: tuple[int, int] = size
        self.__offset: list[int, int] = [0, 0]
        self.__cursor: list[int, int] = [0, 0]
        self.__dragging: bool = False
        self.__running: bool = True
        self.__label_font_size: int = 30

        # reusable pygame resources
        pygame.init()
        pygame.display.set_caption(caption)
        self.__screen: pygame.Surface = pygame.display.set_mode(size)
        self.__label_font: pygame.font.Font = pygame.font.SysFont("monospace", self.__label_font_size)
        self.__data_font: pygame.font.Font = pygame.font.SysFont("monospace", 15)
        self.__labels: dict[str, pygame.surface] = {
            '255': self.__label_font.render('255', False, (255, 0, 255)),
            '0': self.__label_font.render('0', False, (255, 0, 255)),
            'best': self.__data_font.render('best', False, (255, 0, 255)),
            'iteration': self.__data_font.render('iteration', False, (255, 0, 255))
        }

    def __draw_label(self,
                     label: pygame.surface,
                     x: float,
                     y: float,
                     alignment: Alignment = Alignment.CENTER) -> None:
        """
        Draw label onto the screen

        :param label: Label to draw
        :param x: X offset to draw
        :param y: Y offset to draw
        :param alignment: Label alignment
        """
        # Update label offset
        offset: list[float, float] = [0, 0]
        if alignment == Loop.Alignment.LEFT:
            offset = [-label.get_width(), -label.get_height() / 2]
        elif alignment == Loop.Alignment.RIGHT:
            offset = [0, -label.get_height() / 2]
        elif alignment == Loop.Alignment.TOP:
            offset = [-label.get_width() / 2, -label.get_height()]
        elif alignment == Loop.Alignment.BOTTOM:
            offset = [-label.get_width() / 2, 0]
        elif alignment == Loop.Alignment.CENTER:
            offset = [-label.get_width() / 2, -label.get_height() / 2]

        self.__screen.blit(label, (x + self.__offset[0] + offset[0], y + self.__offset[1] + offset[1]))

    def __draw_line(self,
                    start: tuple[float, float],
                    end: tuple[float, float],
                    color: tuple[int, int, int],
                    width: int = 1) -> None:
        """
        Draw line onto the screen

        :param start: Line's start position
        :param end: Line's end position
        :param color: Line's color
        """
        pygame.draw.line(
            self.__screen,
            color,
            (start[0] + self.__offset[0], start[1] + self.__offset[1]),
            (end[0] + self.__offset[0], end[1] + self.__offset[1]),
            width
        )

    def __draw_circle(self,
                      center: tuple[float, float],
                      radius: int,
                      color: tuple[int, int, int]) -> None:
        """
        Draw circle onto the screen

        :param center: Circle's center
        :param radius: Circle's radius
        :param color: Circle's color
        """
        pygame.draw.circle(
            self.__screen,
            color,
            (center[0] + self.__offset[0], center[1] + self.__offset[1]),
            radius
        )

    def __handle_events(self) -> None:
        """
        Handles pygame events
        """
        for event in pygame.event.get():
            # Quit window
            if event.type == pygame.QUIT:
                self.__running = False
                pygame.quit()

            # Mouse button click
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                self.__dragging = not self.__dragging
                self.__cursor = event.pos

            # Mouse drag
            if event.type == pygame.MOUSEMOTION:
                if self.__dragging:
                    self.__offset[0] += event.pos[0] - self.__cursor[0]
                    self.__offset[1] += event.pos[1] - self.__cursor[1]
                    self.__cursor = event.pos

    def run(self,
            desired_number: int = 150,
            population_size: int = 8,
            cross_range: int = 1,
            sleep: float = 1) -> None:
        """
        Starts loop execution

        :param desired_number: Target of evolution (between 0 and 255)
        :param population_size: Size of population every iteration (at least 2)
        :param cross_range: Range of how many bits will become subject to crossing (less than half the population_size)
        :param sleep: Evolution's process time in seconds
        """
        desired_number = min(max(desired_number, 0), 255)
        self.__labels['desired'] = self.__label_font.render(str(desired_number), False, (255, 0, 255))

        # Start evolver
        evolver: NumberEvolver = NumberEvolver(desired_number, population_size, 255, cross_range, sleep)
        evolver.start()

        # Calculate Y level display for future use
        level_desired: float = util.calc_level(desired_number, 256, (200, 600))
        level_255: float = util.calc_level(255, 256, (200, 600))
        level_0: float = util.calc_level(0, 256, (200, 600))

        # Main loop
        while self.__running:
            # Handle event every iteration
            self.__handle_events()

            # Clear screen
            self.__screen.fill((0, 0, 0))

            # Render threshold lines
            line_len: int = len(evolver.history) * self.__label_font_size
            self.__draw_line((100, level_0), (line_len + 100, level_0), (255, 255, 0))
            self.__draw_line((100, level_255), (line_len + 100, level_255), (0, 255, 0))
            self.__draw_line((100, level_desired), (line_len + 100, level_desired), (150, 0, 0))

            # Render threshold labels
            self.__draw_label(self.__labels['255'], 100, level_255, Loop.Alignment.LEFT)
            self.__draw_label(self.__labels['0'], 100, level_0, Loop.Alignment.LEFT)
            self.__draw_label(self.__labels['desired'], 100, level_desired, Loop.Alignment.LEFT)
            self.__draw_label(self.__labels['best'], 100, 100, Loop.Alignment.LEFT)
            self.__draw_label(self.__labels['iteration'], 100, 125, Loop.Alignment.LEFT)

            # Repeat for every entry in history list
            for iteration, population, best_number in evolver.history:
                iteration_offset: int = iteration * self.__label_font_size
                # Render individuals in population
                for num in population:
                    level_num: float = util.calc_level(num, 256, (200, 600))
                    self.__draw_circle((100 + iteration_offset, level_num), 3, (255, 255, 255))

                # Render iteration number
                self.__draw_label(
                    self.__data_font.render(
                        str(iteration),
                        False,
                        (250, 250, 250)
                    ),
                    100 + iteration_offset, 125
                )

                # Render best number
                level_best: float = util.calc_level(best_number, 256, (200, 600))
                self.__draw_circle((100 + iteration_offset, level_best), 5, (255, 0, 0))
                self.__draw_label(
                    self.__data_font.render(str(best_number), False, (255, 50, 50)),
                    100 + iteration_offset, 100
                )

                # Render current population
                self.__draw_label(
                    self.__data_font.render(
                        f'iteration: {iteration}, population: {population}',
                        False,
                        (250, 250, 250)
                    ),
                    100, 600 + iteration_offset, Loop.Alignment.RIGHT
                )

            # Update display
            pygame.display.update()
