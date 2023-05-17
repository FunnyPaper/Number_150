from functools import reduce


def bin_to_dec(n: list[int]) -> int:
    """
    Converts binary number to decimal

    :param n: Binary number to convert
    :return: Decimal counterpart
    """

    # Reduce by shifting numbers to the left (raising to the power of 2)
    return reduce(lambda prev, curr: (prev[0] + 1, prev[1] + (curr << prev[0])), n, (0, 0))[1]


def dec_to_bin(n: int, places: int = 8) -> list[int]:
    """
    Converts decimal number to binary

    :param n: Decimal number to convert
    :param places: Minimal representation length
    :return: Binary counterpart
    """

    # Create by string manipulation
    return [int(n) for n in bin(n).replace('0b', '').ljust(places, '0')]


def calc_level(n: int, max_num: int, draw_range: tuple[int, int]) -> float:
    """
    Calculates Y level to be used in displaying information

    :param n: Number to rescale
    :param max_num: Maximum scale
    :param draw_range: Lower and upper bound of drawing
    :return: Proportional Y level value
    """
    valid_range: int = draw_range[1] - draw_range[0]
    return ((max_num - n) / max_num) * valid_range + draw_range[0]
