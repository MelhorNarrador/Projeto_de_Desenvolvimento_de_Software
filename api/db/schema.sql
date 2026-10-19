-- =============================================================
-- Kairos — database schema
-- Runs automatically the first time PostgreSQL starts
-- (docker-entrypoint-initdb.d).
-- =============================================================

-- -------------------------------------------------------------
-- Enums
-- -------------------------------------------------------------
CREATE TYPE user_role       AS ENUM ('operator', 'crew', 'admin');
CREATE TYPE support_level   AS ENUM ('basic', 'advanced');
CREATE TYPE unit_status     AS ENUM ('available', 'assigned', 'en_route', 'on_scene', 'unavailable');
CREATE TYPE incident_status AS ENUM ('pending', 'assigned', 'in_progress', 'closed');

-- -------------------------------------------------------------
-- Districts (or counties, in other countries)
-- -------------------------------------------------------------
CREATE TABLE district (
    id    SERIAL PRIMARY KEY,
    name  TEXT NOT NULL UNIQUE
);

-- Neighbouring districts (stored in both directions)
CREATE TABLE district_neighbor (
    district_id  INT NOT NULL REFERENCES district(id) ON DELETE CASCADE,
    neighbor_id  INT NOT NULL REFERENCES district(id) ON DELETE CASCADE,
    PRIMARY KEY (district_id, neighbor_id),
    CHECK (district_id <> neighbor_id)
);

-- -------------------------------------------------------------
-- Users
-- -------------------------------------------------------------
CREATE TABLE app_user (
    id             SERIAL PRIMARY KEY,
    name           TEXT NOT NULL,
    email          TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,                            -- bcrypt
    role           user_role NOT NULL,
    district_id    INT REFERENCES district(id),              -- NULL for admins
    active         BOOLEAN NOT NULL DEFAULT TRUE,            -- FALSE = account disabled (To keep Audit Logs)
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (role = 'admin' OR district_id IS NOT NULL)
);

-- -------------------------------------------------------------
-- Incidents
-- -------------------------------------------------------------
CREATE TABLE incident (
    id           SERIAL PRIMARY KEY,
    district_id  INT NOT NULL REFERENCES district(id),
    created_by   INT NOT NULL REFERENCES app_user(id),
    latitude     DOUBLE PRECISION NOT NULL,
    longitude    DOUBLE PRECISION NOT NULL,
    address      TEXT,                                       -- address picked in the search box
    victim_name  TEXT,                                       -- to be encrypted (delivery 3)
    description  TEXT,                                       -- to be encrypted (delivery 3)
    severity     SMALLINT NOT NULL CHECK (severity BETWEEN 1 AND 5),  -- 1 = red ... 5 = blue
    status       incident_status NOT NULL DEFAULT 'pending',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_incident_district_status ON incident (district_id, status);

-- -------------------------------------------------------------
-- Emergency units (ambulances, etc.)
-- -------------------------------------------------------------
CREATE TABLE unit (
    id             SERIAL PRIMARY KEY,
    code           TEXT NOT NULL UNIQUE,                     -- call sign, e.g. AMB-LX-01
    license_plate  TEXT NOT NULL UNIQUE,                     -- e.g. AA-00-BB
    type           TEXT NOT NULL,                            -- e.g. ambulance, vmer
    support_level  support_level NOT NULL,
    status         unit_status NOT NULL DEFAULT 'unavailable',
    district_id    INT NOT NULL REFERENCES district(id),
    latitude       DOUBLE PRECISION NOT NULL,
    longitude      DOUBLE PRECISION NOT NULL,
    incident_id    INT REFERENCES incident(id),             -- current mission (NULL if free)
    user_id        INT UNIQUE REFERENCES app_user(id),      -- crew member on shift (NULL = nobody)
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (status = 'unavailable' OR user_id IS NOT NULL),
    CHECK (
        (status IN ('available', 'unavailable') AND incident_id IS NULL) OR
        (status IN ('assigned', 'en_route', 'on_scene') AND incident_id IS NOT NULL)
    )
);

CREATE INDEX idx_unit_district_status ON unit (district_id, status);

-- -------------------------------------------------------------
-- Assignments (history of which unit went to which incident)
-- -------------------------------------------------------------
CREATE TABLE assignment (
    id           SERIAL PRIMARY KEY,
    incident_id  INT NOT NULL REFERENCES incident(id),
    unit_id      INT NOT NULL REFERENCES unit(id),
    eta_seconds  INT,                                        -- arrival time computed by A*
    active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX uq_assignment_unit_active ON assignment (unit_id) WHERE active;

-- -------------------------------------------------------------
-- Audit log
-- -------------------------------------------------------------
CREATE TABLE audit_log (
    id          BIGSERIAL PRIMARY KEY,
    user_id     INT REFERENCES app_user(id),                -- NULL when done by the system
    action      TEXT NOT NULL,                               -- e.g. assign, change_status
    entity      TEXT NOT NULL,                               -- e.g. unit, incident
    entity_id   INT,
    details     JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
