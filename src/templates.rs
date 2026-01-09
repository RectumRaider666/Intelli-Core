use askama::Template;

#[derive(Template)]
#[template(path = "landing.html")]
pub struct LandingTemplate {
    pub server_name: String,
    pub version: String,
    pub uptime: String,
    pub connections: usize,
}

impl LandingTemplate {
    pub fn new() -> Self {
        Self {
            server_name: "".to_string(),
            version: "".to_string(),
            uptime: "".to_string(),
            connections: 0,
        }
    }
}

#[derive(Template)]
#[template(path = "logs.html")]
pub struct LogsTemplate {
    pub server_name: String,
    pub version: String,
    pub uptime: String,
    pub connections: usize,
}

impl LogsTemplate {
    pub fn new() -> Self {
        Self {
            server_name: "".to_string(),
            version: "".to_string(),
            uptime: "".to_string(),
            connections: 0,
        }
    }
}
