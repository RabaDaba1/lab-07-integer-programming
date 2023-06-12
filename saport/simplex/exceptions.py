class DuplicateVariableError(Exception):
    
    def __init__(self, name: str) -> None:
        super().__init__(f"Cannot create variable named {name}. There is already a variable with the same name.")
        self.name = name


class EmptyModelError(Exception):

    def __init__(self) -> None:
        super().__init__(f"Cannot solve model without any variables.")


class MissingObjectiveError(Exception):
    
    def __init__(self) -> None:
        super().__init__(f"Cannot solve model missing an objective.")