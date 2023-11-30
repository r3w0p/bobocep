# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
A test using distributed BoboCEP with Postman and Flask that runs a pattern
across two BoboCEP instances. The pattern accepts characters "a", followed by
"b", followed by "c". It also halts on receiving character "h". This pattern
is a singleton, and so it can only have one active run at a time.

The test demonstrates how the pattern's runs can be updated, completed, and
halted when the characters are sent by either BoboCEP instance.

Note that, in Distributed :code:`BoboCEP`, only the instance that first
completes a run will be the instance that handles the action. Therefore, the
action counter will only increment on the instance that completes its run.
"""
