-- Add migration script here
CREATE TABLE IF NOT EXISTS "session" (
    "id" uuid DEFAULT uuid_generate_v4 (),
    "user_id" uuid NOT NULL,
    PRIMARY KEY("id"),
    CONSTRAINT fk_user_id
        FOREIGN KEY("user_id")
            REFERENCES "user"("id")
            ON DELETE CASCADE
);