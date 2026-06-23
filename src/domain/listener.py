class Listener:
    """
    Interface for any class that listens for changes in the domain model. The
    notify() method should implement a response to any changes in state.
    """
    def notify(self) -> None:
        pass
