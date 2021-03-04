class Generator:
    def __init__(self, randomness_lst):
        self.val_lst = randomness_lst

    def generate_password(self):
        return f"Strong Password {len(self.val_lst)}"
