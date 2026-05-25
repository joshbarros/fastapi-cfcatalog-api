class ServiceError(Exception):
    pass


class NotFoundError(ServiceError):
    def __init__(self, resource: str, resource_id: object) -> None:
        super().__init__(f"{resource} with id {resource_id!s} not found")
        self.resource = resource
        self.resource_id = resource_id


class InvalidReferenceError(ServiceError):
    def __init__(self, resource: str, missing_ids: list[object]) -> None:
        formatted = ", ".join(str(i) for i in missing_ids)
        super().__init__(f"{resource} ids not found: {formatted}")
        self.resource = resource
        self.missing_ids = missing_ids
