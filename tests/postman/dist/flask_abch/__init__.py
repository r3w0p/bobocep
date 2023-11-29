# Copyright (c) 2019-2023 r3w0p
# The following code can be redistributed and/or
# modified under the terms of the MIT License.

"""
A test using distributed BoboCEP with Postman and Flask that runs a pattern
across two BoboCEP instances. The pattern accepts characters "a", followed by
"b", followed by "c". It also halts on receiving character "h".

The test demonstrates how the pattern's runs can be updated, completed, and
halted when the characters are sent by either BoboCEP instance.
"""
