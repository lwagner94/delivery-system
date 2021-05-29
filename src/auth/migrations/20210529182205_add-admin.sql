-- Add migration script here
INSERT INTO "user" ("email", "password", "role")
VALUES ('admin@example.com', '$2b$10$xGFHNMXgO1D80gf8xEggAOdU9a2rld7puXKkThCL8euJNUh4QtVEW', 'admin');