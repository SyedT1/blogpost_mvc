import dataclasses


@dataclasses.dataclass
class Message:
    user_id: int         # Add user_id to match ForeignKey in ChatMessage
    author: str
    text: str
    timestamp: str

    def asdict(self):
        return dataclasses.asdict(self)
