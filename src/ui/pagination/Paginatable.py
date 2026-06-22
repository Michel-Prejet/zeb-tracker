from abc import ABC, abstractmethod


class Paginatable(ABC):
    """
    Base class for frames that include a pagination frame. Defines event
    handlers for each pagination button, and a current page attribute.
    All Paginatable classes should be Custom Tkinter frames.
    """
    curr_page: int

    @abstractmethod
    def next_page(self) -> None:
        pass

    @abstractmethod
    def prev_page(self) -> None:
        pass

    @abstractmethod
    def first_page(self) -> None:
        pass

    @abstractmethod
    def last_page(self) -> None:
        pass