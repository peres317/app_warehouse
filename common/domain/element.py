from abc import ABC, abstractmethod


class Element(ABC):
    """Interface of a element of the domain.
    """
    
    @abstractmethod
    def to_dict(self) -> dict:
        """Creates a dictionary with the data representating the element.

        Returns:
            dict: Dictionary.
        """
        pass