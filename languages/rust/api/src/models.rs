use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct User {
    #[serde(rename = "_id")]
    pub id: Option<bson::Uuid>,
    pub name: String,
    pub email: String,
    #[serde(rename = "createdAt")]
    pub created_at: String,
}

impl User {
    pub fn new(name: String, email: String) -> Self {
        Self {
            id: None,
            name,
            email,
            created_at: chrono::Utc::now().to_rfc3339(),
        }
    }

    pub fn build(self) -> User {
        User {
            id: Some(bson::Uuid::new()),
            ..self
        }
    }
}