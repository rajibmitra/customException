"""exception.py: handles all the custom exceptions """


class ValidationException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def to_dict(self):
        """ error message in dictionary format """
        error_message = dict()
        error_message['message'] = self.message
        return error_message


class InvalidProductError(ValidationException):
    """
    Raised when a there is product information error
    """
    pass


class InvalidProductIdException(ValidationException):
    """
    Raised when a there is product information error
    """
    def to_dict(self):
        """ error message in dictionary format """
        error_message = dict()
        error_message['message'] = self.message
        return error_message


class PropertyMissingInPost(ValidationException):
    """
    Raised when a property missing in payload data
    """
    pass


class InvalidComponentId(ValidationException):
    """
    Raised when component id is invalid
    """
    pass


class NoBodyFound(ValidationException):
    """
    Raised when no body found in payload data
    """
    pass


class DuplicateComponentId(ValidationException):
    """
    Raised when there is duplicate in component id
    """
    pass


class ComponentIdNotExist(ValidationException):
    """
     Raised when there is component id doesn't exist in desired_upgrade list
    """
    pass


class BadProductVersion(ValidationException):
    """
     Raised when there is bad string in product version
    """
    pass


class ProductVersionOutOfRange(ValidationException):
    """
    Raised when product version is out of range
    """
    pass


class UpgradeVersionOutOfRange(ValidationException):
    """
    Raised when upgrade product version is out of range
    """
    pass


class BadUpgradeVersion(ValidationException):
    """
    Raised when upgrade product version is a bad string
    """
    pass


class PropertyTypeError(ValidationException):
    """
    Raised when there is a type mismatch in payload properties
    """
    pass


class EcosystemComponentNotFoundError(ValueError):
    """
    Raised when a desired upgrade component_id does not match any existing ecosystem component
    """
    pass


class InvalidProductIdError(ValueError):
    """
    Raised when encountering an invalid product_id
    """
    pass
