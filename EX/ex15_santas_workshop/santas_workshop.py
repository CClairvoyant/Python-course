"""Merry Christmas."""

import requests
import os
import threading
import base64
import time
import re


class Child:
    """Data about a child."""

    def __init__(self, name: str, naughty: bool, country: str, wishes: list):
        """
        Initialize a Child object.

        name: name of the child as a string
        naughty: a boolean indicating whether the child is naughty
        country: country of the child as a string
        wishes: a list of Gift objects representing the child's wishes
        """
        self.name = name
        self.naughty = naughty
        self.country = country
        self.wishes = wishes


class Gift:
    """Data about a gift."""

    def __init__(self, name: str, material_cost: int, production_time: int, weight_in_grams: int):
        """
        Initialize a Gift object.

        name: name of the gift as a string
        material_cost: cost of materials required to make the gift as an integer
        production_time: time taken to produce the gift as an integer
        weight_in_grams: weight of the gift in grams as an integer
        """
        self.name = name
        self.material_cost = material_cost
        self.production_time = production_time
        self.weight_in_grams = weight_in_grams


class Factory:
    """Factory."""

    def __init__(self, filename):
        """
        Initialize a Factory object.

        filename: the name of the file containing the gifts as a string
        """
        self.filename = filename
        self.gifts = []

    def get_gifts(self):
        """Create a list of Gift objects from the data in the file passed to the Factory object's filename attribute."""
        presents = []

        with open(self.filename) as file:
            content = file.read().split("\n")

        # Find all the gifts from the wish file.
        for row in content:
            for gift in row.split(", ")[1:]:
                presents.append(gift)
        presents = list(set(presents))

        # Create a list of threads for all the gifts
        threads = [threading.Thread(target=self.__request_data, args=(gift,)) for gift in presents]

        # Start all the threads
        for thread in threads:
            thread.start()

        # Wait for all the threads to finish
        for thread in threads:
            thread.join()

    def __request_data(self, gift: str):
        """Request data using a thread from the thread pool and make Gift objects."""
        specific_url = gift.replace(" ", "%20")
        present = requests.get(f"https://cs.ttu.ee/services/xmas/gift?name={specific_url}").json()
        self.gifts.append(Gift(gift, int(present["material_cost"]), int(present["production_time"]),
                               int(present["weight_in_grams"])))


def get_list_of_children(nice_file: str, naughty_file: str, wish_file: str):
    """Make a list of children."""
    children = []
    nice_dict = {}
    naughty_dict = {}
    wish_dict = {}

    # Get info about all the gifts in the wish file.
    factory = Factory(wish_file)
    factory.get_gifts()

    # Get list of rows for each file.
    with open(nice_file) as nice:
        nice_children = nice.read().split("\n")
    with open(naughty_file) as naughty:
        naughty_children = naughty.read().split("\n")
    with open(wish_file) as wish:
        wishes = wish.read().split("\n")

    # Add children names, countries and wishes to dictionaries.
    for child in nice_children:
        nice_dict[child.split(", ")[0]] = child.split(", ")[1]
    for child in naughty_children:
        naughty_dict[child.split(", ")[0]] = child.split(", ")[1]
    for child in wishes:
        wish_dict[child.split(", ")[0]] = child.split(", ")[1:]

    # Get Gift objects from factories and match them with nice children. Then create Children objects.
    for child in nice_dict:
        wish_list = []
        if child in wish_dict:
            for w in wish_dict[child]:
                wish_list.append(list(filter(lambda x: x.name == w, factory.gifts))[0])
        children.append(Child(child, False, nice_dict[child], wish_list))

    # Naughty kids get 5kg of coal for Christmas.
    for child in naughty_dict:
        wish_list = [Gift("Coal", 1, 0, 5000)]
        children.append(Child(child, True, naughty_dict[child], wish_list))

    return children


def delivery_data(children_list: list):
    """Figure out all about delivery orders."""
    # Make list for orders and countries they need to go to.
    orders = []
    countries = list(set(map(lambda x: x.country, children_list)))

    # Make an order for every country.
    for country in countries:
        orders.append([])

        # Find children that are from the country in hand and add their gifts to the sleigh.
        for child in list(filter(lambda x: x.country == country, children_list)):
            orders[-1].append(child)

            # If the total weight of the gifts has gone over 50kg, add it to a new order instead.
            if sum(list(map(lambda x: sum(list(map(lambda y: y.weight_in_grams, x.wishes))), orders[-1]))) > 50_000:
                orders[-1].pop()
                orders.append([])
                orders[-1].append(child)

    return orders


def delivery_sheets(nice_file: str, naughty_file: str, wish_file: str):
    """Print order sheets."""
    orders = delivery_data(get_list_of_children(nice_file, naughty_file, wish_file))

    # Variables for text formatting.
    empty = ""
    name = "Name"
    gifts = "Gifts"

    if os.path.exists("deliveries"):
        for file in os.listdir("deliveries"):
            os.remove(f"deliveries/{file}")
        os.rmdir("deliveries")
    os.mkdir("deliveries")

    # For each order, find the length of the longest string in name and gifts category.
    for i in range(len(orders)):
        name_length = len(max(orders[i], key=lambda y: len(y.name)).name)
        name_length = name_length if name_length >= 4 else 4
        wishes = list(map(lambda z: ", ".join(list(map(lambda y: y.name, z.wishes))), orders[i]))
        gifts_length = len(max(wishes, key=len))
        gifts_length = gifts_length if gifts_length >= 5 else 5

        with open(f"deliveries/delivery_{i + 1}.txt", "w") as file:
            file.write(
                "                        DELIVERY ORDER" + "\n"
                "                                                          _v" + "\n"
                "                                                     __* (__)" + "\n"
                r"             ff     ff     ff     ff                {\/ (_(__).-." + "\n"
                r"      ff    <_\__, <_\__, <_\__, <_\__,      __,~~.(`>|-(___)/ ,_)" + "\n"
                r"    o<_\__,  (_ ff ~(_ ff ~(_ ff ~(_ ff~~~~~@ )\/_;-\"``     |" + "\n"
                r"      (___)~~//<_\__, <_\__, <_\__, <_\__,    | \__________/|" + "\n"
                r"      // >>     (___)~~(___)~~(___)~~(___)~~~~\\_/_______\_//" + "\n"
                "                // >>  // >>  // >>  // >>     `'---------'`" + "\n"
                "\n"
                "FROM: NORTH POLE CHRISTMAS CHEER INCORPORATED" + "\n"
                f"TO: {orders[i][0].country}" + "\n"
                "\n"
                fr"//{empty:=<{name_length + 2}}[]{empty:=<{gifts_length + 2}}[]{empty:=<18}\\" + "\n"
                fr"|| {name:^{name_length}} || {gifts:^{gifts_length}} || Total Weight(kg) ||" + "\n"
                fr"|]{empty:=<{name_length + 2}}[]{empty:=<{gifts_length + 2}}[]{empty:=<18}[|" + "\n"
            )

            # Calculate the total weight of each child's gifts.
            for x, child in enumerate(orders[i]):
                total_weight = str(round(sum(list(map(lambda y: y.weight_in_grams, child.wishes))) / 1000, 1))
                if total_weight[-2:] == ".0":
                    total_weight = total_weight[:-2]
                file.write(
                    fr"|| {child.name:<{name_length}} || {wishes[x]:<{gifts_length}} || {total_weight:>16} ||" + "\n"
                )

            file.write(
                fr"\\{empty:=<{name_length + 2}}[]{empty:=<{gifts_length + 2}}[]{empty:=<18}//"
            )


def decode_caesar(letter: str):
    """Decode Caesar cipher."""
    decoded_letter = ""

    for character in letter:
        if character.isalpha() and character.islower():
            new_pos = (ord(character) - ord("a") - 4) % 26
            decoded_letter += chr(new_pos + ord("a"))
        elif character.isalpha() and character.isupper():
            new_pos = (ord(character) - ord("A") - 4) % 26
            decoded_letter += chr(new_pos + ord("A"))
        else:
            decoded_letter += character

    return decoded_letter


def decode_base64(letter: str):
    """Decode base64 encoding."""
    base64_bytes = letter.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)

    return message_bytes.decode('ascii')


def get_letter(wish_file: str, letter_count: int):
    """Get letters to Santa from a website using multithreading."""
    letters = []
    threads = []
    wish_lines = []

    # Make threads, start them, and add them to the threads list.
    for x in range(letter_count):
        thread = threading.Thread(target=__make_requests, args=(letters,))
        thread.start()
        threads.append(thread)

    # Wait for the threads to finish.
    for thread in threads:
        thread.join()

    # For each letter received, check if they have wishes in them and decode if necessary.
    for letter in letters:
        if "SSB3YW50" in letter or "SSB3aXNoIGZvcg==" in letter or "d2lzaGxpc3Q6" in letter:
            normal_letter = decode_base64(letter)
        elif "m aerx" in letter or "m amwl jsv" in letter or "amwlpmwx:" in letter:
            normal_letter = decode_caesar(letter)
        else:
            normal_letter = letter

        # Find and collect wishes.
        if "I want" in normal_letter or "I wish for" in normal_letter or "wishlist:" in normal_letter:
            name = re.search(r"(?<=\n)(?<!\n\n)[A-Za-z]+(?=, )", normal_letter).group()
            name = name.capitalize()
            wishes = re.search(r"(?<=.{4}I want |I wish for |.wishlist: ).+(?=\.)", normal_letter, re.IGNORECASE).group()
            wishes = __remove_unwanted_punctuation(wishes)
            wish_lines.append(name + ", " + wishes)

    wish_lines = list(set(wish_lines))

    if not os.path.exists(wish_file):
        with open(wish_file, "w") as file:
            file.write(wish_lines[0])

    with open(wish_file, "r") as file:
        content = file.read()

    with open(wish_file, "a") as file:
        for line in wish_lines:
            if line.split(", ")[0] not in content:
                file.write("\n" + line)


def __remove_unwanted_punctuation(wishes):
    """Remove unwanted punctuation (from acrylic paint brush set)."""
    if " , " in wishes:
        wishes = wishes.replace(" , ", ", ")
    if "." in wishes:
        wishes = wishes.replace(".", ",")
    return wishes


def __make_requests(letters):
    """Make a request for a letter to Santa."""
    letters.append(requests.get("https://cs.ttu.ee/services/xmas/letter").json()["letter"])


if __name__ == '__main__':  # pragma: no cover
    start = time.time()
    delivery_sheets("nice_list.csv", "naughty_list.csv", "wish_list.csv")
    end = time.time()
    print(end - start)

    start = time.time()
    get_letter("somethingweird.csv", 100)
    end = time.time()
    print(end - start)
