use actix_web::body::MessageBody;
use actix_web::dev::{ServiceResponse, Service};
use actix_web::http::header::{ContentType, AUTHORIZATION};
use actix_web::http::HeaderValue;
use actix_web::middleware::Logger;
use actix_web::web::Header;
use actix_web::{http, test, web, App, HttpResponse};
use anyhow::Result;
use auth::models::{AuthToken, UserCredentials, User, NewUser};
use auth::routes::{login, logout, create_user, get_user, delete_user};
use dotenv::dotenv;
use serde_json;
use sqlx::postgres::PgPoolOptions;
use sqlx::PgPool;

macro_rules! get_app {
    // `()` indicates that the macro takes no argument.
    () => {{
        dotenv().ok();
        let pool = PgPoolOptions::new()
            .max_connections(5)
            .connect(&std::env::var("DATABASE_URL").unwrap())
            .await
            .expect("Could not connect to database");

        let app =
            test::init_service(App::new().data(pool.clone()).service(login).service(logout).service(create_user).service(get_user).service(delete_user)).await;
        (app, pool)
    }};
}

async fn cleanup_sessions(pool: &PgPool) -> Result<()> {
    let mut tx = pool.begin().await?;
    let deleted = sqlx::query!(r#"DELETE FROM "session""#)
        .execute(&mut tx)
        .await?;

    tx.commit().await?;
    Ok(())
}

async fn cleanup_users(pool: &PgPool) -> Result<()> {
    let mut tx = pool.begin().await?;
    let deleted = sqlx::query!(r#"DELETE FROM "user" WHERE "email" != 'admin@example.com'"#)
        .execute(&mut tx)
        .await?;

    tx.commit().await?;
    Ok(())
}


#[actix_rt::test]
async fn test_login_success() {
    let (mut app, pool) = get_app!();

    let req = test::TestRequest::post()
        .uri("/auth/login")
        .set_json(&UserCredentials {
            email: "admin@example.com".into(),
            password: "admin".into(),
        })
        .to_request();

    let r = test::call_service(&mut app, req).await;
    assert_eq!(http::StatusCode::OK, r.status());
    assert_eq!(r.headers().get("content-type").unwrap(), "application/json");
    let body: AuthToken = test::read_body_json(r).await;

    cleanup_sessions(&pool).await.unwrap();
}

#[actix_rt::test]
async fn test_login_no_body() {
    let (mut app, pool) = get_app!();

    let req = test::TestRequest::post()
        .uri("/auth/login")
        // .set_json(&UserCredentials {email: "admin@example.com".into(), password: "admin".into()})
        .to_request();

    let r = test::call_service(&mut app, req).await;
    assert_eq!(http::StatusCode::BAD_REQUEST, r.status());
    cleanup_sessions(&pool).await.unwrap();
}

#[actix_rt::test]
async fn test_login_invalid_body() {
    let (mut app, pool) = get_app!();

    let req = test::TestRequest::post()
        .uri("/auth/login")
        .insert_header(ContentType::json())
        .set_payload("{\"foobar\": \"test\"}".as_bytes())
        .to_request();

    let r = test::call_service(&mut app, req).await;
    assert_eq!(http::StatusCode::BAD_REQUEST, r.status());
    cleanup_sessions(&pool).await.unwrap();
}

#[actix_rt::test]
async fn test_logout_success() {
    let (mut app, pool) = get_app!();

    let req = test::TestRequest::post()
        .uri("/auth/login")
        .set_json(&UserCredentials {
            email: "admin@example.com".into(),
            password: "admin".into(),
        })
        .to_request();

    let r = test::call_service(&mut app, req).await;
    let body: AuthToken = test::read_body_json(r).await;

    let auth_header = (
        AUTHORIZATION,
        HeaderValue::from_str(&format!("Bearer {}", &body.token)).unwrap(),
    );
    let req = test::TestRequest::post()
        .uri("/auth/logout")
        .insert_header(auth_header)
        .to_request();

    let r = test::call_service(&mut app, req).await;
    assert_eq!(http::StatusCode::OK, r.status());

    cleanup_sessions(&pool).await.unwrap();
}

#[actix_rt::test]
async fn test_logout_invalid_token() {
    let (mut app, pool) = get_app!();

    let auth_header = (
        AUTHORIZATION,
        HeaderValue::from_str(&"Bearer invalid").unwrap(),
    );
    let req = test::TestRequest::post()
        .uri("/auth/logout")
        .insert_header(auth_header)
        .to_request();

    let r = test::call_service(&mut app, req).await;
    assert_eq!(http::StatusCode::UNAUTHORIZED, r.status());

    cleanup_sessions(&pool).await.unwrap();
}


#[actix_rt::test]
async fn test_create_and_get_and_delete_user() {
    let (mut app, pool) = get_app!();
    cleanup_sessions(&pool).await.unwrap();
    cleanup_users(&pool).await.unwrap();

    let req = test::TestRequest::post()
        .uri("/auth/login")
        .set_json(&UserCredentials {
            email: "admin@example.com".into(),
            password: "admin".into(),
        })
        .to_request();

    let r = test::call_service(&mut app, req).await;
    let body: AuthToken = test::read_body_json(r).await;

    let auth_header = (
        AUTHORIZATION,
        HeaderValue::from_str(&format!("Bearer {}", &body.token)).unwrap(),
    );

    let req = test::TestRequest::post()
        .uri("/auth/user")
        .insert_header(auth_header.clone())
        .set_json(&NewUser {
            email: "foobar@example.com".into(),
            password: "secret".into(),
            role: "admin".into()
        })
        .to_request();

    let r = test::call_service(&mut app, req).await;
    assert_eq!(http::StatusCode::CREATED, r.status());

    let user: User = test::read_body_json(r).await;

    assert_eq!("foobar@example.com", user.email);
    assert_eq!("admin", user.role);

    let req = test::TestRequest::get()
        .uri(&format!("/auth/user/{}", user.id.to_string()))
        .insert_header(auth_header.clone())
        .to_request();

    let r = test::call_service(&mut app, req).await;
    assert_eq!(http::StatusCode::OK, r.status());
    let got_user: User = test::read_body_json(r).await;

    assert_eq!(got_user.email, user.email);
    assert_eq!(got_user.role, user.role);
    assert_eq!(got_user.id, user.id);

    let req = test::TestRequest::delete()
        .uri(&format!("/auth/user/{}", user.id.to_string()))
        .insert_header(auth_header.clone())
        .to_request();

    let r = test::call_service(&mut app, req).await;
    assert_eq!(http::StatusCode::OK, r.status());

    let req = test::TestRequest::get()
        .uri(&format!("/auth/user/{}", user.id.to_string()))
        .insert_header(auth_header.clone())
        .to_request();

    let r = test::call_service(&mut app, req).await;
    assert_eq!(http::StatusCode::NOT_FOUND, r.status());
}
