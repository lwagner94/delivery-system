use anyhow::Result;
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use uuid::Uuid;

use crate::models::FormatError::InvalidUUID;
use sqlx::postgres::PgRow;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum FormatError {
    #[error("Invalid UUID")]
    InvalidUUID,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct UserCredentials {
    pub email: String,
    pub password: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct AuthToken {
    pub token: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct User {
    pub id: Uuid,
    pub email: String,
    #[serde(skip_serializing)]
    pub password: String,
    pub role: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Session {
    pub id: Uuid,
    pub user_id: Uuid,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Claim {
    pub sub: Uuid,
}

impl User {
    pub async fn find_by_email(email: String, pool: &PgPool) -> Result<User> {
        let user = sqlx::query!(
            r#"
                SELECT "id", "email", "password", "role" FROM "user"
                    WHERE "email" = $1
            "#,
            email
        )
        .fetch_one(&*pool)
        .await?;

        Ok(User {
            id: user.id,
            email: user.email,
            password: user.password,
            role: user.role,
        })
    }
}

impl Session {
    pub async fn create(user: &User, pool: &PgPool) -> Result<Session> {
        let mut tx = pool.begin().await?;
        let session = sqlx::query!(
            r#"INSERT INTO "session" (user_id) VALUES ($1) RETURNING id, user_id"#,
            user.id
        )
        .fetch_one(&mut tx)
        .await?;
        tx.commit().await?;

        Ok(Session {
            id: session.id,
            user_id: session.user_id,
        })
    }

    pub async fn find_by_id(id: Uuid, pool: &PgPool) -> Result<Session> {
        let session = sqlx::query!(
            r#"
                SELECT "id", "user_id" FROM "session"
                    WHERE "id" = $1
            "#,
            id
        )
        .fetch_one(&*pool)
        .await?;

        Ok(Session {
            id: session.id,
            user_id: session.user_id,
        })
    }

    pub async fn delete_by_id(id: Uuid, pool: &PgPool) -> Result<()> {
        let mut tx = pool.begin().await?;
        let deleted = sqlx::query!(r#"DELETE FROM "session" WHERE id = $1"#, id)
            .execute(&mut tx)
            .await?;

        tx.commit().await?;
        Ok(())
    }
}
