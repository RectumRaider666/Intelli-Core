use axum::{
    extract::{Query, State},
    http::StatusCode,
    response::IntoResponse,
};
use crate::{AppState};
use std::sync::Arc;

pub async fn code_handler(
    State(_state): State<Arc<AppState>>,
    Query(_params): Query,
) -> impl IntoResponse {
    (StatusCode::OK, "Code server endpoint")
}
