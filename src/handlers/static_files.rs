use axum::{
    http::{header, StatusCode},
    response::IntoResponse,
};
use tokio::fs;

pub async fn favicon() -> impl IntoResponse {
    match fs::read("static/img/favicon.ico").await {
        Ok(content) => (
            StatusCode::OK,
            [(header::CONTENT_TYPE, "image/x-icon")],
            content,
        )
            .into_response(),
        Err(_) => (StatusCode::NOT_FOUND, "Favicon not found").into_response(),
    }
}
