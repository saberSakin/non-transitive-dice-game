import sys
import secrets
import hashlib
import hmac
from itertools import product

class Dice:
    def __init__(self, faces):
        self.faces = faces

    def roll(self, value):
        return self.faces[value % len(self.faces)]

class DiceParser:
    @staticmethod
    def parse(arguments):
        dice_list = []
        num_faces_set = set()
        for arg in arguments:
            try:
                faces = list(map(int, arg.split(",")))
                if len(faces) < 1:
                    raise ValueError("Dice must have at least one face.")
                num_faces_set.add(len(faces))
                dice_list.append(Dice(faces))
            except ValueError:
                raise ValueError(f"Invalid dice configuration: {arg}. Ensure it contains comma-separated integers.")
        
        if len(num_faces_set) != 1:
            raise ValueError("All dice must have the same number of sides.")
        return dice_list

class RandomGenerator:
    @staticmethod
    def generate_key():
        return secrets.token_bytes(32)

    @staticmethod
    def generate_random_number(max_value):
        return secrets.randbelow(max_value + 1)

class HMACGenerator:
    @staticmethod
    def calculate_hmac(key, message):
        return hmac.new(key, message.encode(), hashlib.sha3_256).hexdigest()

class ProbabilityCalculator:
    @staticmethod
    def calculate_probabilities(dice_list):
        size = len(dice_list)
        probabilities = [[0] * size for _ in range(size)]

        for i, dice1 in enumerate(dice_list):
            for j, dice2 in enumerate(dice_list):
                if i != j:
                    win_count = 0
                    total = len(dice1.faces) * len(dice2.faces)
                    for roll1, roll2 in product(dice1.faces, dice2.faces):
                        if roll1 > roll2:
                            win_count += 1
                    probabilities[i][j] = win_count / total
        return probabilities

    @staticmethod
    def display_table(probabilities, dice_list):
        print("\nProbability Table:")
        for i, row in enumerate(probabilities):
            print(f"Dice {i}:", end=" ")
            for prob in row:
                print(f"{prob:.2f}", end=" ")
            print()

class FairRandomProtocol:
    @staticmethod
    def fair_random_selection(max_value):
        key = RandomGenerator.generate_key()
        random_number = RandomGenerator.generate_random_number(max_value)
        hmac_value = HMACGenerator.calculate_hmac(key, str(random_number))
        print(f"I selected a random value in the range 0..{max_value} (HMAC={hmac_value}).")

        user_input = input(f"Add your number modulo {max_value + 1}: ")
        try:
            user_number = int(user_input)
            result = (user_number + random_number) % (max_value + 1)
            print(f"My number is {random_number} (KEY={key.hex()}).")
            print(f"The result is {user_number} + {random_number} = {result} (mod {max_value + 1}).")
            return result
        except ValueError:
            print("Invalid input. Please enter an integer.")
            sys.exit(1)

class DiceGame:
    def __init__(self, dice_list):
        self.dice_list = dice_list
        self.used_dice = set()

    def get_user_choice(self):
        while True:
            print("Choose your dice:")
            for i, dice in enumerate(self.dice_list):
                if i not in self.used_dice:
                    print(f"{i} - {','.join(map(str, dice.faces))}")
            print("X - exit")
            print("? - help")

            choice = input("Your selection: ").strip().lower()
            if choice == "x":
                sys.exit(0)
            elif choice == "?":
                probabilities = ProbabilityCalculator.calculate_probabilities(self.dice_list)
                ProbabilityCalculator.display_table(probabilities, self.dice_list)
            else:
                try:
                    choice = int(choice)
                    if choice in self.used_dice or choice < 0 or choice >= len(self.dice_list):
                        raise ValueError("Invalid choice.")
                    self.used_dice.add(choice)
                    return self.dice_list[choice]
                except ValueError:
                    print("Invalid input. Try again.")

    def play(self):
        print("Let's determine who makes the first move.")
        first_move = FairRandomProtocol.fair_random_selection(1)
        user_first = first_move == 0

        if user_first:
            print("You make the first move.")
        else:
            print("I make the first move.")

        if user_first:
            user_dice = self.get_user_choice()
            computer_dice = self.get_computer_choice()
        else:
            computer_dice = self.get_computer_choice()
            user_dice = self.get_user_choice()

        print("It's time for my throw.")
        computer_throw = FairRandomProtocol.fair_random_selection(len(computer_dice.faces) - 1)
        computer_value = computer_dice.roll(computer_throw)
        print(f"My throw is {computer_value}.")

        print("It's time for your throw.")
        user_throw = FairRandomProtocol.fair_random_selection(len(user_dice.faces) - 1)
        user_value = user_dice.roll(user_throw)
        print(f"Your throw is {user_value}.")

        if user_value > computer_value:
            print("You win!")
        elif user_value < computer_value:
            print("I win!")
        else:
            print("It's a tie!")

    def get_computer_choice(self):
        for i, dice in enumerate(self.dice_list):
            if i not in self.used_dice:
                self.used_dice.add(i)
                print(f"I choose the [{','.join(map(str, dice.faces))}] dice.")
                return dice

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python game.py dice1 dice2 dice3 [...]")
        print("Example: python game.py 2,2,4,4,9,9 6,8,1,1,8,6 7,5,3,7,5,3")
        sys.exit(1)

    try:
        dice_list = DiceParser.parse(sys.argv[1:])
        game = DiceGame(dice_list)
        game.play()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
