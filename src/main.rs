mod handlers;
mod templates;

use axum::{routing::get, Router};
use tower_http::services::ServeDir;
use std::sync::Arc;
use tracing::{info, error};
use rusqlite::{Connection, OptionalExtension, Result as SqlResult};
use std::fs;

#[derive(Debug, Clone, PartialEq)]
pub enum NodeType {
    Parent,
    Child,
}

impl NodeType {
    fn as_str(&self) -> &str {
        match self {
            NodeType::Parent => "parent",
            NodeType::Child => "child",
        }
    }
}

#[derive(Debug)]
pub struct PackageInfo {
    name: String,
    version: String,
    uuid: String,
    server: String,
}

impl PackageInfo {
    pub fn new(name: String, version: String, uuid: String, server: String) -> Self {
        Self { name, version, uuid, server }
    }
}

fn read_package_info(cargo_toml_path: &str) -> PackageInfo {
    let cargo_content = fs::read_to_string(cargo_toml_path)
        .expect("Failed to read Cargo.toml");

    let mut name = String::new();
    let mut version = String::new();
    let mut uuid = String::new();
    let mut server = String::new();

    for line in cargo_content.lines() {
        let line = line.trim();
        if line.starts_with("name =") {
            name = line.split('"').nth(1).unwrap_or("").to_string();
        } else if line.starts_with("version =") {
            version = line.split('"').nth(1).unwrap_or("").to_string();
        } else if line.starts_with("uuid =") {
            uuid = line.split('"').nth(1).unwrap_or("").to_string();
        } else if line.starts_with("server =") {
            server = line.split('"').nth(1).unwrap_or("").to_string();
        }
    }

    PackageInfo { name, version, uuid, server }
}

fn determine_node_type(package_name: &str) -> NodeType {
    if package_name.ends_with("core") {
        NodeType::Parent
    } else if package_name.ends_with("child") {
        NodeType::Child
    } else {
        info!("Package name '{}' doesn't end in 'core' or 'child', defaulting to Parent", package_name);
        NodeType::Parent
    }
}

fn patch_uuid_to_cargo(cargo_toml_path: &str, new_uuid: &str) -> std::io::Result<()> {
    let cargo_content = fs::read_to_string(cargo_toml_path)?;
    let mut new_content = String::new();

    for line in cargo_content.lines() {
        if line.trim().starts_with("uuid =") {
            let indent = line.len() - line.trim_start().len();
            new_content.push_str(&format!("{}uuid = \"{}\"\n", " ".repeat(indent), new_uuid));
        } else {
            new_content.push_str(line);
            new_content.push('\n');
        }
    }

    fs::write(cargo_toml_path, new_content)?;
    info!("Patched UUID into Cargo.toml: {}", new_uuid);
    Ok(())
}

fn init_database_from_schema(conn: &Connection, schema_path: &str) -> SqlResult<()> {
    info!("Loading database schema from: {}", schema_path);
    let schema_sql = fs::read_to_string(schema_path)
        .expect("Failed to read schema file");
    conn.execute_batch(&schema_sql)?;
    info!("Database schema initialized successfully");
    Ok(())
}

fn manage_system_node(conn: &Connection, package_info: &PackageInfo,) -> SqlResult<i64> {
    let node_type = determine_node_type(&package_info.name);
    let existing_node: Option<(i64, String)> = conn
        .query_row(
            "SELECT id, server_name FROM system WHERE node_uuid = ?1",
            [&package_info.uuid],
            |row| Ok((row.get(0)?, row.get(1)?)),
        )
        .optional()?;

    match existing_node {
        Some((node_id, existing_name)) => {
            info!("Node already registered: {} (ID: {})", existing_name, node_id);
            info!("Using existing registration, no updates needed");
            Ok(node_id)
        }
        None => {
            let main_state = serde_json::json!({
                "version": package_info.version,
                "server": package_info.server,
                "started_at": chrono::Utc::now().to_rfc3339(),
            }).to_string();

            conn.execute(
                "INSERT INTO system (node_uuid, node, server_name, main_state)
                 VALUES (?1, ?2, ?3, ?4)",
                [
                    &package_info.uuid,
                    node_type.as_str(),
                    &package_info.name,
                    &main_state,
                ],
            )?;

            let node_id = conn.last_insert_rowid();
            info!("Registered new {} node: {} (ID: {})", node_type.as_str(), package_info.name, node_id);
            Ok(node_id)
        }
    }
}

fn set_node_status(conn: &Connection, node_uuid: &str, status: &str) -> SqlResult<()> {
    conn.execute(
        "UPDATE system SET status = ?1 WHERE node_uuid = ?2",
        [status, node_uuid],
    )?;
    info!("Node {} status set to: {}", node_uuid, status);
    Ok(())
}

fn log_important_event_to_db(
    conn: &Connection,
    server_id: i64,
    log_level: &str,
    message: &str,
    content: Option<&str>,
) -> SqlResult<()> {
    conn.execute( 66
        "INSERT INTO logs (server_id, log_level, message, content) VALUES (?1, ?2, ?3, ?4)",
        [
            &server_id.to_string(),
            log_level,
            message,
            content.unwrap_or("{}"),
        ],
    )?;
    Ok(())
}

pub struct AppState {
    pub redis_client: redis::Client,
    pub db_connection: Connection,
}

impl AppState {
    pub fn new(redis_client: redis::Client, db_connection: Connection) -> Self {
        Self { redis_client, db_connection }
    }
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_target(false)
        .compact()
        .init();

    let redis_client = redis::Client::open("redis://0.0.0.0:6379/")
        .expect("Failed to connect to Redis");

    let db = rusqlite::Connection::open("/venv/data/db/main.db")
        .expect("Failed to open database");
    init_database_from_schema(&db, "/venv/data/db/main.sql")
        .expect("Failed to initialize database schema");

    let mut package_info = read_package_info("/venv/Cargo.toml");
    if package_info.uuid.is_empty() {
        package_info.uuid = uuid::Uuid::new_v4().to_string();
        info!("No UUID found in Cargo.toml! Generating new UUID: {}", package_info.uuid);
        if let Err(e) = patch_uuid_to_cargo("/venv/Cargo.toml", &package_info.uuid) {
            error!("Failed to patch UUID into Cargo.toml: {}", e);
            error!("Please manually add: uuid = \"{}\"", package_info.uuid);
        }
    }
    info!("Package: {} v{}", package_info.name, package_info.version);
    info!("Node UUID: {}", package_info.uuid);
    let server_id = manage_system_node(&db, &package_info)
        .expect("Failed to manage system node");
    info!("Node operational with ID: {}", server_id);

    let state = Arc::new(AppState::new(redis_client, db));

    let app = Router::new()
        .route("/", get(handlers::logs::landing))
        .route("/health", get(handlers::health::health_check))
        .route("/logs", get(handlers::logs::logs_viewer))
        .route("/favicon.ico", get(handlers::static_files::favicon))
        .route("/code", get(handlers::code::code_handler))
        .nest_service("/static", ServeDir::new("static"))
        .nest_service("/data/logs", ServeDir::new("data/logs"))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080")
        .await
        .expect("Failed to bind to port 8080");

    info!("Server listening on http://0.0.0.0:8080");

    axum::serve(listener, app)
        .await
        .expect("Server failed");
}
