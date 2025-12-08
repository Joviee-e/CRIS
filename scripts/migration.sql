CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 1f2684708466

CREATE TABLE users (
    id VARCHAR(36) NOT NULL, 
    email VARCHAR(255) NOT NULL, 
    password_hash VARCHAR(255) NOT NULL, 
    role VARCHAR(30) DEFAULT 'user' NOT NULL, 
    created_at DATETIME NOT NULL, 
    updated_at DATETIME NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_users_email UNIQUE (email)
);

CREATE INDEX ix_users_email ON users (email);

CREATE INDEX ix_users_role ON users (role);

CREATE TABLE applications (
    id VARCHAR(36) NOT NULL, 
    sr_no INTEGER NOT NULL, 
    purpose VARCHAR(255) NOT NULL, 
    department VARCHAR(100) NOT NULL, 
    emp_no VARCHAR(100) NOT NULL, 
    emp_name VARCHAR(255) NOT NULL, 
    designation VARCHAR(255), 
    remarks TEXT, 
    status VARCHAR(50) DEFAULT 'pending' NOT NULL, 
    created_by VARCHAR(36) NOT NULL, 
    created_at DATETIME NOT NULL, 
    updated_at DATETIME NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(created_by) REFERENCES users (id)
);

CREATE INDEX ix_applications_sr_no ON applications (sr_no);

CREATE INDEX ix_applications_created_by ON applications (created_by);

CREATE TABLE action_logs (
    id VARCHAR(36) NOT NULL, 
    application_id VARCHAR(36) NOT NULL, 
    action VARCHAR(100) NOT NULL, 
    actor_id VARCHAR(36), 
    comment TEXT, 
    created_at DATETIME NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(application_id) REFERENCES applications (id), 
    FOREIGN KEY(actor_id) REFERENCES users (id)
);

CREATE INDEX ix_action_logs_application_id ON action_logs (application_id);

CREATE TABLE attachments (
    id VARCHAR(36) NOT NULL, 
    application_id VARCHAR(36) NOT NULL, 
    filename VARCHAR(255) NOT NULL, 
    mime_type VARCHAR(100) NOT NULL, 
    size INTEGER NOT NULL, 
    created_at DATETIME NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(application_id) REFERENCES applications (id)
);

CREATE INDEX ix_attachments_application_id ON attachments (application_id);

INSERT INTO alembic_version (version_num) VALUES ('1f2684708466') RETURNING version_num;

-- Running upgrade 1f2684708466 -> 20251206_add_role_to_users

UPDATE alembic_version SET version_num='20251206_add_role_to_users' WHERE alembic_version.version_num = '1f2684708466';

