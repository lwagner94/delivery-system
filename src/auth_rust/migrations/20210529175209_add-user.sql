-- Add migration script here
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS "user" (
    "id" uuid DEFAULT uuid_generate_v4 (),
    "email" VARCHAR NOT NULL,
    "password" VARCHAR NOT NULL,
    "role" VARCHAR NOT NULL CHECK ("role" = 'admin' OR "role" = 'provider' OR "role" = 'agent'),
    PRIMARY KEY("id"),
    UNIQUE ("email")
);