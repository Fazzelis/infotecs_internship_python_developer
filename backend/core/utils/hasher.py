from passlib.context import CryptContext


class Hasher:
    def __init__(self):
        self.hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_hash(self, item: str) -> str:
        return self.hasher.hash(item)

    def match_hash(self, item: str, item_hash: str) -> bool:
        return self.hasher.verify(item, item_hash)


hasher = Hasher()
