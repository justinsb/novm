// Copyright 2014 Google Inc. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package machine

import (
	"novmm/platform"
	"syscall"
)

// TODO: Bad name: ROM Memory = Read-only memory memory

type RomMemory struct {
	BaseDevice

	// The FD to map
	Fd int `json:"fd"`

	// The filename (used for matching)
	Filename string `json:"filename"`

	// Address at which to map
	BaseAddr platform.Paddr `json:"addr"`
	Size     uint64         `json:"size"`

	// Our map.
	mmap []byte
}

func (user *RomMemory) reload(vm *platform.Vm, model *Model) error {
	// Create a mmap'ed region.

	var err error

	offset := 0
	size := user.Size

	user.Debug(
		"rom %s => [%x,%x]",
		user.Filename,
		user.BaseAddr, size)

	user.mmap, err = syscall.Mmap(
		user.Fd,
		int64(offset),
		int(size),
		syscall.PROT_READ,
		syscall.MAP_SHARED)
	if err != nil || user.mmap == nil {
		return err
	}

	// Allocate it in the machine.
	err = model.Reserve(
		vm,
		user,
		MemoryTypeRom,
		user.BaseAddr,
		size,
		user.mmap)
	if err != nil {
		return err
	}

	return nil
}

func NewRomMemory(info *DeviceInfo) (Device, error) {

	user := new(RomMemory)

	return user, user.init(info)
}

func (user *RomMemory) Attach(vm *platform.Vm, model *Model) error {

	// Layout the existing regions.
	err := user.reload(vm, model)
	if err != nil {
		return err
	}

	return nil
}
