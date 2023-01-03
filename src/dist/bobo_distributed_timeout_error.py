# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.
from src.dist.bobo_distributed_error import BoboDistributedError


class BoboDistributedTimeoutError(BoboDistributedError):
    """A distributed timeout error."""
