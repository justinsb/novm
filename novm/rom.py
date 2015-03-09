# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Memory devices.
"""
import os
import tempfile

from . import device
from . import utils

# TODO: How to pick a base_address?  (I had some problems with _huge_ values here!)
# Maybe we just shouldn't auto-assign, and just start 1GB above user memory or something
auto_base_addr = 0x400000000

class RomMemory(device.Driver):

    driver = "rom"

    def create(self,
            addr=None,
            filename=None,
            **kwargs):

        if filename is None:
            raise Exception("filename is required")

        # Open the device.
        f = open(filename, 'r+b')
        fd = os.dup(f.fileno())
        utils.clear_cloexec(fd)

        # No size given? Default to file size.
        fd_stat = os.fstat(fd)
        size = fd_stat.st_size

        page_size = 4096
        if 0 != (size % page_size):
            size = size + page_size - (size % page_size)
            # Truncate the file.
            os.ftruncate(fd, size)

        # Lay out sequentially if address not provided
        if addr is None:
            global auto_base_addr
            addr = auto_base_addr
            auto_base_addr += size

        return super(RomMemory, self).create(data={
            "fd": fd,
            "filename": filename,
            "addr": addr,
            "size": size
        }, **kwargs)

    def save(self, state, pid):
        """ Open up the fd and return it back. """
        raise "Not implemented"
        return ({
            # Save the size of the memory block.
            "size": state.get("size"),
        }, {
            # Serialize the entire open fd.
            "memory": open("/proc/%d/fd/%d" % (pid, state["fd"]), "r")
        })

    def load(self, state, files):
        raise "Not implemented"
        return self.create(
            size=state.get("size"),
            fd=files["memory"].fileno())

device.Driver.register(RomMemory)
