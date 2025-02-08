"""Models for the results of the API requests.

The ForgeModel is designed to be a base class for all models defined in the
user's code. The Response class is used to represent the response from the
server and provides methods to convert the response to a model or get values
from the JSON content.

The Field and Condition are not generally used by the user, but are used
internally to build conditions on fields in the models.
"""

__all__ = ["ForgeModel", "Response", "Result"]

from clientforge.models.results import ForgeModel, Response, Result
