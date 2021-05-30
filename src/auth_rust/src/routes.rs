use actix_web::middleware::Logger;
use actix_web::{get, post, delete, web, App, HttpRequest, HttpResponse, HttpServer, Responder};
use actix_web::middleware;
use anyhow::Result;
use dotenv::dotenv;
use sqlx::postgres::PgPoolOptions;

use crate::models::{AuthToken, Claim, Session, User, UserCredentials, NewUser};
use jsonwebtoken::{
    decode, encode, Algorithm, DecodingKey, EncodingKey, Header, TokenData, Validation,
};
use pwhash::bcrypt;
use sqlx::PgPool;
use uuid::Uuid;
use std::str::FromStr;

#[post("/auth/login")]
pub async fn login(
    user_credentials: web::Json<UserCredentials>,
    db_pool: web::Data<PgPool>,
) -> impl Responder {
    match User::find_by_email(user_credentials.email.clone(), db_pool.get_ref()).await {
        Ok(user) => {
            if bcrypt::verify(&user_credentials.password, &user.password) {
                match Session::create(&user, db_pool.get_ref()).await {
                    Ok(session) => HttpResponse::Ok().json(AuthToken {
                        token: encode(
                            &Header::default(),
                            &Claim { sub: session.id },
                            &EncodingKey::from_secret("secret".as_ref()),
                        )
                        .unwrap(),
                    }),
                    Err(_e) => HttpResponse::InternalServerError().finish(),
                }
            } else {
                HttpResponse::Unauthorized().body("User credentials are not valid")
            }
        }
        Err(_e) => return HttpResponse::Unauthorized().body("User credentials are not valid"),
    }
}

fn extract_bearer_token(req: &HttpRequest) -> Option<String> {
    req.headers()
        .get("Authorization")
        .and_then(|s| s.to_str().ok())
        .and_then(|slice| {
            if slice.starts_with("Bearer ") {
                let token = slice.trim_start_matches("Bearer ").trim();
                Some(String::from(token))
            } else {
                None
            }
        })
}

fn session_from_bearer_token(req: &HttpRequest) -> Option<Uuid> {
    extract_bearer_token(req)
        .and_then(|token| {
            decode(
                &token,
                &DecodingKey::from_secret("secret".as_ref()),
                &Validation {
                    validate_exp: false,
                    ..Default::default()
                },
            )
            .ok()
        })
        .and_then(|token_data: TokenData<Claim>| Some(token_data.claims.sub))
}

async fn get_session(req: &HttpRequest, pool: &web::Data<PgPool>) -> Option<Session> {
    if let Some(session_id) = session_from_bearer_token(&req) {
        return Session::find_by_id(session_id, &pool).await.ok();
    }
    None
}

async fn get_session_and_user(req: &HttpRequest, pool: &web::Data<PgPool>) -> Option<(Session, User)> {
    let session_id = session_from_bearer_token(&req)?;
    let session = Session::find_by_id(session_id, &pool).await.ok()?;
    let user = User::find_by_id(session.user_id, &pool).await.ok()?;

    Some((session, user))
}

#[post("/auth/logout")]
pub async fn logout(req: HttpRequest, pool: web::Data<PgPool>) -> impl Responder {
    if let Some(session) = get_session(&req, &pool).await {
        if let Ok(_) = Session::delete_by_id(session.id, &pool).await {
            return HttpResponse::Ok().finish();
        }
    }
    return HttpResponse::Unauthorized().body("Access token is missing or invalid");
}

#[post("/auth/user")]
pub async fn create_user(req: HttpRequest, new_user: web::Json<NewUser>, pool: web::Data<PgPool>) -> impl Responder {
    let (_, user) = match get_session_and_user(&req, &pool).await {
        Some((session, user)) => (session, user),
        None => return HttpResponse::Unauthorized().body("Access token is missing or invalid")
    };

    if user.role != "admin" {
        return HttpResponse::Forbidden().body("User is not permitted to perform this operations");
    }

    let hash = bcrypt::hash(&new_user.password).unwrap();
    if let Ok(new_user) = User::create(&new_user.email, &hash, &new_user.role, &pool).await {
        return HttpResponse::Created().json(&new_user);
    }

    return HttpResponse::Unauthorized().body("Access token is missing or invalid");
}

#[get("/auth/user/{user_id}")]
pub async fn get_user(req: HttpRequest, user_id: web::Path<String>, pool: web::Data<PgPool>) -> impl Responder {
    if let Some(session) = get_session(&req, &pool).await {
        if let Ok(user) = User::find_by_id(session.user_id, &pool).await {

            let id = match user_id.as_str() {
                "self" => Some(user.id),
                _ => Uuid::from_str(&user_id).ok()
            };

            if id.is_none() {
                return HttpResponse::NotFound().body("User with given id not found");
            }

            let uuid = id.unwrap();

            if user.role == "admin" || user.id == uuid {
                return match User::find_by_id(uuid, &pool).await {
                    Ok(user) => HttpResponse::Ok().json(user),
                    Err(_) => HttpResponse::NotFound().body("User with given id not found")
                };
            } else {
                return HttpResponse::Forbidden().body("User is not permitted to perform this operations")
            }


        }
    }
    return HttpResponse::Unauthorized().body("Access token is missing or invalid");
}

#[delete("/auth/user/{user_id}")]
pub async fn delete_user(req: HttpRequest, user_id: web::Path<String>, pool: web::Data<PgPool>) -> impl Responder {
    if let Some(session) = get_session(&req, &pool).await {
        if let Ok(user) = User::find_by_id(session.user_id, &pool).await {

            let id = match user_id.as_str() {
                "self" => Some(user.id),
                _ => Uuid::from_str(&user_id).ok()
            };

            if id.is_none() {
                return HttpResponse::NotFound().body("User with given id not found");
            }

            let uuid = id.unwrap();

            return if user.role == "admin" || user.id == uuid {
                match User::find_by_id(uuid, &pool).await {
                    Ok(user) => {
                        User::delete_by_id(uuid, &pool).await;
                        HttpResponse::Ok().finish()
                    },
                    Err(_) => HttpResponse::NotFound().body("User with given id not found")
                }
            } else {
                HttpResponse::Forbidden().body("User is not permitted to perform this operations")
            }
        }
    }
    return HttpResponse::Unauthorized().body("Access token is missing or invalid");
}
