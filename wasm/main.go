//go:build js && wasm

package main

import (
	"encoding/json"
	"syscall/js"

	"github.com/trilingual-dict/core/database"
	"github.com/trilingual-dict/core/query"
)

var db *database.DB

func main() {
	// Initialize database
	var err error
	db, err = database.Open("/dictionary.db")
	if err != nil {
		println("Failed to open database:", err.Error())
		return
	}

	// Register JavaScript functions
	js.Global().Set("TriDictSearch", js.FuncOf(triDictSearch))
	js.Global().Set("TriDictReady", js.ValueOf(true))

	println("TriDict WASM module loaded successfully")

	// Keep the program running
	<-make(chan bool)
}

func triDictSearch(this js.Value, args []js.Value) interface{} {
	if len(args) < 1 {
		return map[string]interface{}{
			"error": "No search term provided",
		}
	}

	input := args[0].String()

	result, err := query.Query(db, input)
	if err != nil {
		return map[string]interface{}{
			"error": err.Error(),
		}
	}

	// Convert to JSON
	jsonBytes, err := json.Marshal(result)
	if err != nil {
		return map[string]interface{}{
			"error": "Failed to marshal JSON: " + err.Error(),
		}
	}

	return string(jsonBytes)
}
