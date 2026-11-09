CREATE TABLE app_user (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(60) NOT NULL UNIQUE,
    password_hash VARCHAR(100) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE user_role (
    user_id BIGINT NOT NULL REFERENCES app_user (id),
    role VARCHAR(20) NOT NULL,
    PRIMARY KEY (user_id, role)
);

INSERT INTO app_user (username, password_hash) VALUES
    ('user',  '$2a$10$WjLsuxf9xBo/bVFWPRmK2.XQQjH7RWzCOBbolFqkF.VpPwv32AYs.'),
    ('admin', '$2a$10$uR8GTa0pm6lvm/mW0zv/yu50aRTE1SSBgMjuuY92ln65kqDM1aJsi');

INSERT INTO user_role (user_id, role)
    SELECT id, 'USER' FROM app_user;
INSERT INTO user_role (user_id, role)
    SELECT id, 'ADMIN' FROM app_user WHERE username = 'admin';
