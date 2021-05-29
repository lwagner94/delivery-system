mod models;

use actix_web::middleware::Logger;
use actix_web::{get, post, web, App, HttpRequest, HttpResponse, HttpServer, Responder};
use anyhow::Result;
use dotenv::dotenv;
use models::AuthToken;
use models::Session;
use models::User;
use models::UserCredentials;
use sqlx::postgres::PgPoolOptions;

use crate::models::Claim;
use jsonwebtoken::{
    decode, encode, Algorithm, DecodingKey, EncodingKey, Header, TokenData, Validation,
};
use pwhash::bcrypt;
use sqlx::PgPool;
use uuid::Uuid;

#[post("/auth/login")]
async fn login(
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

#[post("/auth/logout")]
async fn logout(req: HttpRequest, pool: web::Data<PgPool>) -> impl Responder {
    if let Some(session) = get_session(&req, &pool).await {
        if let Ok(_) = Session::delete_by_id(session.id, &pool).await {
            return HttpResponse::Ok().finish();
        }
    }
    return HttpResponse::Unauthorized().body("Access token is missing or invalid");
}

#[actix_web::main]
async fn main() -> Result<()> {
    dotenv().ok();
    std::env::set_var("RUST_LOG", "actix_web=info");
    env_logger::init();

    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&std::env::var("DATABASE_URL")?)
        .await
        .expect("Could not connect to database");

    HttpServer::new(move || {
        App::new()
            .data(pool.clone())
            .wrap(Logger::default())
            .service(login)
            .service(logout)
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await?;
    Ok(())
}
