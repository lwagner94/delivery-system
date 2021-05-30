use actix_web::middleware::Logger;
use actix_web::{get, post, web, App, HttpRequest, HttpResponse, HttpServer, Responder};
use anyhow::Result;
use dotenv::dotenv;
use sqlx::postgres::PgPoolOptions;

use auth::models::{AuthToken, Claim, Session, User, UserCredentials};
use auth::routes::{login, logout, create_user, get_user, delete_user};
use jsonwebtoken::{
    decode, encode, Algorithm, DecodingKey, EncodingKey, Header, TokenData, Validation,
};
use pwhash::bcrypt;
use sqlx::PgPool;
use uuid::Uuid;
use actix_cors::Cors;

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
        let cors = Cors::permissive();
        App::new()
            .data(pool.clone())
            .wrap(Logger::default())
            .wrap(cors)
            .service(login)
            .service(logout)
            .service(create_user)
            .service(get_user)
            .service(delete_user)
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await?;
    Ok(())
}
