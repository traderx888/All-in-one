"""Account and Sector data models."""

from dataclasses import dataclass, field


@dataclass
class Account:
    """A Twitter/X account to monitor."""

    username: str
    note: str = ""
    priority: str = "medium"  # high | medium | low
    sectors: list[str] = field(default_factory=list)

    @property
    def profile_url(self) -> str:
        return f"https://x.com/{self.username}"

    def __hash__(self):
        return hash(self.username.lower())

    def __eq__(self, other):
        if isinstance(other, Account):
            return self.username.lower() == other.username.lower()
        return False


@dataclass
class Sector:
    """An asset sector with associated accounts."""

    name: str
    description: str = ""
    accounts: list[Account] = field(default_factory=list)

    @property
    def account_usernames(self) -> list[str]:
        return [a.username for a in self.accounts]
