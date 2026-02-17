package main

import (
	"encoding/json"
	"flag"
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
	// Define flags
	var limit int
	jsonOutput := flag.Bool("json", false, "Output JSON format")
	flag.IntVar(&limit, "limit", 5, "Maximum number of results per language (0 = unlimited)")
	flag.IntVar(&limit, "n", 5, "Shorthand for --limit")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: dict [options] <word>\n\n")
		fmt.Fprintf(os.Stderr, "Options:\n")
		flag.PrintDefaults()
		fmt.Fprintf(os.Stderr, "\nExamples:\n")
		fmt.Fprintf(os.Stderr, "  dict cat              # Show 5 results (default)\n")
		fmt.Fprintf(os.Stderr, "  dict cat -n 10        # Show 10 results\n")
		fmt.Fprintf(os.Stderr, "  dict cat --limit 1    # Show only best match (Phase 1 behavior)\n")
		fmt.Fprintf(os.Stderr, "  dict --json cat       # JSON output\n")
	}

	flag.Parse()

	// Get search term
	args := flag.Args()
	if len(args) == 0 {
		flag.Usage()
		os.Exit(1)
	}
	searchTerm := args[0]

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

	// Query with limit
	result, err := query.Query(db, searchTerm, limit)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// Output
	if *jsonOutput {
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
	// Separate outputs by language
	var jaOutputs, zhOutputs []types.LanguageOutput
	for _, output := range result.Outputs {
		if output.Language == "ja" {
			jaOutputs = append(jaOutputs, output)
		} else if output.Language == "zh" {
			zhOutputs = append(zhOutputs, output)
		}
	}

	// Create columns
	jaBox := renderBoxes("Japanese", jaOutputs)
	zhBox := renderBoxes("Chinese", zhOutputs)

	// Print side by side
	fmt.Println()
	fmt.Println(lipgloss.JoinHorizontal(lipgloss.Top, jaBox, "  ", zhBox))
	fmt.Println()
}

func renderBoxes(title string, outputs []types.LanguageOutput) string {
	if len(outputs) == 0 {
		content := titleStyle.Render(title) + "\n\n" +
			lipgloss.NewStyle().Foreground(lipgloss.Color("8")).Render("No results found")
		return boxStyle.Render(content)
	}

	// Render title with count
	titleText := fmt.Sprintf("%s (%d result", title, len(outputs))
	if len(outputs) > 1 {
		titleText += "s"
	}
	titleText += ")"

	var allParts []string
	allParts = append(allParts, titleStyle.Render(titleText))

	// Render each output
	for i, output := range outputs {
		if i > 0 {
			// Add separator between results
			allParts = append(allParts, lipgloss.NewStyle().
				Foreground(lipgloss.Color("8")).
				Render("─────────────────────────────────────"))
		}

		// Number
		numberStyle := lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("12"))
		allParts = append(allParts, numberStyle.Render(fmt.Sprintf("%d.", i+1)))

		// Headword and reading
		headwordLine := headwordStyle.Render(output.Headword)
		if output.Reading != "" {
			headwordLine += " " + readingStyle.Render("("+output.Reading+")")
		}
		allParts = append(allParts, headwordLine)

		// Definition (truncate if too long)
		def := output.Definition
		if len(def) > 100 {
			def = def[:97] + "..."
		}
		allParts = append(allParts, defStyle.Render(def))

		// Metadata
		var metaParts []string

		// Add rank indicator
		if output.Rank > 0 {
			if output.Rank <= 100 {
				metaParts = append(metaParts, "★ Common")
			} else if output.Rank <= 1000 {
				metaParts = append(metaParts, fmt.Sprintf("Rank: %d", output.Rank))
			}
		}

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
			allParts = append(allParts, metaStyle.Render(strings.Join(metaParts, " | ")))
		}
	}

	content := strings.Join(allParts, "\n")
	return boxStyle.Render(content)
}

// Legacy function for single result (kept for backward compatibility)
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
