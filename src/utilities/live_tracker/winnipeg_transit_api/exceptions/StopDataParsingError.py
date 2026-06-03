class StopDataParsingError(Exception):
    """
    Exception raised when an error occurs while parsing stop data from the
    Winnipeg Transit API.
    """
    def __init__(self, missing_attribute_name: str) -> None:
        super().__init__(f"Missing attribute: {missing_attribute_name}")