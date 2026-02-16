import SwiftUI

@main
struct TridictApp: App {
    @StateObject private var databaseManager = DatabaseManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(databaseManager)
        }
    }
}
