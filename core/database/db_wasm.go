//go:build js && wasm

package database

import (
	_ "modernc.org/sqlite"
)

const driverName = "sqlite"
