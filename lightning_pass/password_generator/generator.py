from passgen import passgen


class Generator:
    def __init__(
        self,
        randomness_lst,
        length,
        numbers,
        symbols,
        lowercase,
        uppercase,
    ):
        self.val_lst = randomness_lst
        self.length = length
        self.numbers = numbers
        self.symbols = symbols
        self.lowercase = lowercase
        self.uppercase = uppercase

    def generate_password(self):
        if self.lowercase and self.uppercase:
            case = "both"
        elif self.lowercase is False:
            case = "upper"
        elif self.uppercase is False:
            case = "lower"

        password = passgen(
            length=self.length,
            punctuation=self.symbols,
            digits=self.numbers,
            case=case,
        )
        return password
