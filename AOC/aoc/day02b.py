"""Day 2 part 2."""


def part_2(file_name: str):
    """Part 2."""
    with open(file_name, "r") as data:
        content = data.read()
    my_points = content.count("Y") * 3 + content.count("Z") * 6
    matches = content.split("\n")
    for match in matches:
        if match in ["A Y", "B X", "C Z"]:
            my_points += 1
        elif match in ["B Y", "C X", "A Z"]:
            my_points += 2
        else:
            my_points += 3
    return my_points
