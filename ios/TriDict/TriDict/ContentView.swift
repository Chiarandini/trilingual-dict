import SwiftUI

struct ContentView: View {
    @EnvironmentObject var databaseManager: DatabaseManager
    @State private var searchText = ""
    @State private var searchResults: DictionaryResponse?
    @State private var isSearching = false

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Search bar
                SearchBar(text: $searchText, onSearch: performSearch)
                    .padding()

                // Results
                if isSearching {
                    ProgressView("Searching...")
                        .padding()
                } else if let results = searchResults {
                    ScrollView {
                        VStack(spacing: 16) {
                            ForEach(results.outputs, id: \.language) { output in
                                NavigationLink(destination: DetailView(output: output)) {
                                    ResultCard(output: output)
                                }
                                .buttonStyle(PlainButtonStyle())
                            }
                        }
                        .padding()
                    }
                } else {
                    VStack {
                        Spacer()
                        Image(systemName: "book.closed")
                            .font(.system(size: 64))
                            .foregroundColor(.gray)
                        Text("Search for a word in English, Japanese, or Chinese")
                            .foregroundColor(.gray)
                            .multilineTextAlignment(.center)
                            .padding()
                        Spacer()
                    }
                }
            }
            .navigationTitle("Trilingual Dictionary")
        }
    }

    private func performSearch() {
        guard !searchText.isEmpty else { return }

        isSearching = true

        // Perform search on background thread
        DispatchQueue.global(qos: .userInitiated).async {
            let results = databaseManager.search(query: searchText)

            DispatchQueue.main.async {
                isSearching = false
                searchResults = results
            }
        }
    }
}

// MARK: - Search Bar

struct SearchBar: View {
    @Binding var text: String
    var onSearch: () -> Void

    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.gray)

            TextField("Search", text: $text)
                .textFieldStyle(PlainTextFieldStyle())
                .autocapitalization(.none)
                .disableAutocorrection(true)
                .onSubmit(onSearch)

            if !text.isEmpty {
                Button(action: { text = "" }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.gray)
                }
            }
        }
        .padding(8)
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}
