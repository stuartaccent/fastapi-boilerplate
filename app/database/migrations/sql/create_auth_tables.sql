create table auth_scopes
(
    id   uuid default gen_random_uuid() not null primary key,
    name varchar(120)                   not null unique
);

create table auth_user_types
(
    id         uuid    default gen_random_uuid() not null primary key,
    name       varchar(120)                      not null unique,
    is_default boolean default false             not null
);

create table auth_user_type_scopes
(
    user_type_id uuid default gen_random_uuid() not null
        constraint fk_auth_user_type_scopes_user_type references auth_user_types,
    scope_id     uuid default gen_random_uuid() not null
        constraint fk_auth_user_type_scopes_scope references auth_scopes,
    primary key (user_type_id, scope_id)
);

create table auth_users
(
    id              uuid    default gen_random_uuid() not null primary key,
    email           varchar(320)                      not null unique,
    hashed_password varchar(1024)                     not null,
    first_name      varchar(120)                      not null,
    last_name       varchar(120)                      not null,
    user_type_id    uuid                              not null
        constraint fk_auth_users_user_type references auth_user_types,
    is_active       boolean default true              not null,
    is_verified     boolean default false             not null,
    created_at      timestamp with time zone,
    updated_at      timestamp with time zone
);

create table auth_access_tokens
(
    token      varchar(1024) not null primary key,
    user_id    uuid          not null
        constraint fk_auth_access_tokens_user references auth_users on delete cascade,
    created_at timestamp with time zone,
    expires_at timestamp with time zone
);

create index idx_auth_access_tokens_user_id on auth_access_tokens (user_id);

create table auth_reset_tokens
(
    token      varchar(1024) not null primary key,
    user_id    uuid          not null
        constraint fk_auth_reset_tokens_user references auth_users on delete cascade,
    created_at timestamp with time zone,
    expires_at timestamp with time zone
);

create index idx_auth_reset_tokens_user_id on auth_reset_tokens (user_id);

create table auth_verify_tokens
(
    token      varchar(1024) not null primary key,
    user_id    uuid          not null
        constraint fk_auth_verify_tokens_user references auth_users on delete cascade,
    created_at timestamp with time zone,
    expires_at timestamp with time zone
);

create index idx_auth_verify_tokens_user_id on auth_verify_tokens (user_id);
