package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/charmbracelet/lipgloss"
	"github.com/Chiarandini/trilingual-dict/core/database"
	"github.com/Chiarandini/trilingual-dict/core/query"
	"github.com/Chiarandini/trilingual-dict/core/types"
)

var (
	// Styles
	titleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("12")).
			MarginBottom(1)

	boxStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("8")).
			Padding(1, 2).
			Width(40)

	headwordStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("14"))

	readingStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("11")).
			Italic(true)

	defStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("7")).
			MarginTop(1)

	metaStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("8")).
			Italic(true).
			MarginTop(1)

	exampleStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("6")).
			MarginTop(1)
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: dict <word>")
		fmt.Println("       dict --json <word>  (output JSON)")
		os.Exit(1)
	}

	// Check for --json flag
	jsonOutput := false
	var searchTerm string

	if os.Args[1] == "--json" {
		if len(os.Args) < 3 {
			fmt.Println("Usage: dict --json <word>")
			os.Exit(1)
		}
		jsonOutput = true
		searchTerm = os.Args[2]
	} else {
		searchTerm = os.Args[1]
	}

	// Find database
	dbPath := findDatabase()
	if dbPath == "" {
		fmt.Println("Error: dictionary.db not found")
		fmt.Println("Please run: cd data/sample && python3 generate_samples.py")
		os.Exit(1)
	}

	// Open database
	db, err := database.Open(dbPath)
	if err != nil {
		fmt.Printf("Error opening database: %v\n", err)
		os.Exit(1)
	}
	defer db.Close()

	// Query
	result, err := query.Query(db, searchTerm)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// Output
	if jsonOutput {
		outputJSON(result)
	} else {
		outputPretty(result)
	}
}

func findDatabase() string {
	// Try current directory
	if _, err := os.Stat("dictionary.db"); err == nil {
		return "dictionary.db"
	}

	// Try parent directory
	if _, err := os.Stat("../dictionary.db"); err == nil {
		return "../dictionary.db"
	}

	// Try project root (2 levels up from cmd/dict)
	if _, err := os.Stat("../../dictionary.db"); err == nil {
		return "../../dictionary.db"
	}

	// Try home directory
	home, _ := os.UserHomeDir()
	homePath := filepath.Join(home, ".tridict", "dictionary.db")
	if _, err := os.Stat(homePath); err == nil {
		return homePath
	}

	return ""
}

func outputJSON(result *types.Response) {
	encoder := json.NewEncoder(os.Stdout)
	encoder.SetIndent("", "  ")
	encoder.Encode(result)
}

func outputPretty(result *types.Response) {
	// Find Japanese and Chinese outputs
	var jaOutput, zhOutput *types.LanguageOutput
	for i := range result.Outputs {
		if result.Outputs[i].Language == "ja" {
			jaOutput = &result.Outputs[i]
		} else if result.Outputs[i].Language == "zh" {
			zhOutput = &result.Outputs[i]
		}
	}

	// Create columns
	jaBox := renderBox("Japanese", jaOutput)
	zhBox := renderBox("Chinese", zhOutput)

	// Print side by side
	fmt.Println()
	fmt.Println(lipgloss.JoinHorizontal(lipgloss.Top, jaBox, "  ", zhBox))
	fmt.Println()
}

func renderBox(title string, output *types.LanguageOutput) string {
	if output == nil {
		content := titleStyle.Render(title) + "\n\n" +
			lipgloss.NewStyle().Foreground(lipgloss.Color("8")).Render("No results found")
		return boxStyle.Render(content)
	}

	var parts []string

	// Title
	parts = append(parts, titleStyle.Render(title))

	// Headword and reading
	headwordLine := headwordStyle.Render(output.Headword)
	if output.Reading != "" {
		headwordLine += " " + readingStyle.Render("("+output.Reading+")")
	}
	parts = append(parts, headwordLine)

	// Definition
	parts = append(parts, defStyle.Render(output.Definition))

	// Metadata
	var metaParts []string

	// Type assertion for metadata
	if output.Language == "ja" {
		if meta, ok := output.Meta.(types.KanjiMeta); ok {
			if meta.JLPTLevel != "" {
				metaParts = append(metaParts, "JLPT: "+meta.JLPTLevel)
			}
			if meta.StrokeCount > 0 {
				metaParts = append(metaParts, fmt.Sprintf("%d strokes", meta.StrokeCount))
			}
		}
	} else if output.Language == "zh" {
		if meta, ok := output.Meta.(types.HanziMeta); ok {
			if meta.HSKLevel != "" {
				metaParts = append(metaParts, "HSK: "+meta.HSKLevel)
			}
			if meta.StrokeCount > 0 {
				metaParts = append(metaParts, fmt.Sprintf("%d strokes", meta.StrokeCount))
			}
		}
	}

	if len(metaParts) > 0 {
		parts = append(parts, metaStyle.Render(strings.Join(metaParts, " | ")))
	}

	// Examples (first one only)
	if len(output.Examples) > 0 {
		ex := output.Examples[0]
		exampleText := fmt.Sprintf("Ex: %s\n    %s", ex.SourceText, ex.EnglishText)
		parts = append(parts, exampleStyle.Render(exampleText))
	}

	content := strings.Join(parts, "\n")
	return boxStyle.Render(content)
}
