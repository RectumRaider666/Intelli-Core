use crate::templates::{LandingTemplate, LogsTemplate};
use askama_axum::IntoResponse;

pub async fn landing() -> impl IntoResponse {
    LandingTemplate::new()
}

pub async fn logs_viewer() -> impl IntoResponse {
    LogsTemplate::new()
}
