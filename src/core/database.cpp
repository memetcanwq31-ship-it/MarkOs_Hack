#include "core/database.hpp"
#include "core/logger.hpp"

namespace wordsploit {

void Database::initialize(const std::string& dbPath) {
    int rc = sqlite3_open(dbPath.c_str(), &db);
    if (rc) {
        Logger::getInstance().error("Cannot open database: " + dbPath);
        return;
    }
    Logger::getInstance().info("Database initialized: " + dbPath);
    
    // Create tables
    std::string schema = R"(
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY,
            name TEXT,
            ip TEXT UNIQUE,
            port INTEGER,
            service TEXT,
            status TEXT,
            created_at TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS vulnerabilities (
            id INTEGER PRIMARY KEY,
            target_id INTEGER,
            name TEXT,
            severity TEXT,
            description TEXT,
            solution TEXT,
            found_at TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            target_id INTEGER,
            payload_id INTEGER,
            status TEXT,
            created_at TIMESTAMP
        );
    )";
    
    execute(schema);
}

bool Database::execute(const std::string& query) {
    char* errMsg = nullptr;
    int rc = sqlite3_exec(db, query.c_str(), nullptr, nullptr, &errMsg);
    if (rc != SQLITE_OK) {
        Logger::getInstance().error("SQL error: " + std::string(errMsg));
        sqlite3_free(errMsg);
        return false;
    }
    return true;
}

std::vector<std::map<std::string, std::string>> Database::query(const std::string& sql) {
    std::vector<std::map<std::string, std::string>> results;
    sqlite3_stmt* stmt;
    
    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) == SQLITE_OK) {
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            std::map<std::string, std::string> row;
            int cols = sqlite3_column_count(stmt);
            for (int i = 0; i < cols; i++) {
                row[reinterpret_cast<const char*>(sqlite3_column_name(stmt, i))] =
                    reinterpret_cast<const char*>(sqlite3_column_text(stmt, i));
            }
            results.push_back(row);
        }
    }
    sqlite3_finalize(stmt);
    return results;
}

void Database::close() {
    if (db) {
        sqlite3_close(db);
    }
}

} // namespace wordsploit
