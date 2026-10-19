-- =============================================================
-- Kairos — test data (Lisboa and Setúbal)
-- Password for every test user: kairos123
-- =============================================================

-- Districts
INSERT INTO district (id, name) VALUES
    (1, 'Lisboa'),
    (2, 'Setúbal');

INSERT INTO district_neighbor (district_id, neighbor_id) VALUES
    (1, 2),
    (2, 1);

-- Users (bcrypt hash of "kairos123")
INSERT INTO app_user (id, name, email, password_hash, role, district_id) VALUES
    -- admin
    (1,  'Administrator',    'admin@kairos.pt',         '$2b$12$vm69WLH3KwIQCMFLENPuheYcfcFGAvcCHMxjTV738xWPclhfdlr1.', 'admin',    NULL),
    -- operators
    (2,  'Operator Lisboa',  'operator.lx@kairos.pt',   '$2b$12$vm69WLH3KwIQCMFLENPuheYcfcFGAvcCHMxjTV738xWPclhfdlr1.', 'operator', 1),
    (3,  'Operator Setúbal', 'operator.st@kairos.pt',   '$2b$12$vm69WLH3KwIQCMFLENPuheYcfcFGAvcCHMxjTV738xWPclhfdlr1.', 'operator', 2),
    -- crew (Lisboa)
    (4,  'João Silva',       'joao.silva@kairos.pt',    '$2b$12$vm69WLH3KwIQCMFLENPuheYcfcFGAvcCHMxjTV738xWPclhfdlr1.', 'crew',     1),
    (5,  'Jorge Costa',      'jorge.costa@kairos.pt',   '$2b$12$vm69WLH3KwIQCMFLENPuheYcfcFGAvcCHMxjTV738xWPclhfdlr1.', 'crew',     1),
    (6,  'Rita Ferreira',    'rita.ferreira@kairos.pt', '$2b$12$vm69WLH3KwIQCMFLENPuheYcfcFGAvcCHMxjTV738xWPclhfdlr1.', 'crew',     1),
    (7,  'Tiago Lopes',      'tiago.lopes@kairos.pt',   '$2b$12$vm69WLH3KwIQCMFLENPuheYcfcFGAvcCHMxjTV738xWPclhfdlr1.', 'crew',     1),  -- off shift
    -- crew (Setúbal)
    (8,  'Ana Santos',       'ana.santos@kairos.pt',    '$2b$12$vm69WLH3KwIQCMFLENPuheYcfcFGAvcCHMxjTV738xWPclhfdlr1.', 'crew',     2),
    (9,  'Miguel Rocha',     'miguel.rocha@kairos.pt',  '$2b$12$vm69WLH3KwIQCMFLENPuheYcfcFGAvcCHMxjTV738xWPclhfdlr1.', 'crew',     2),
    (10, 'Sofia Martins',    'sofia.martins@kairos.pt', '$2b$12$vm69WLH3KwIQCMFLENPuheYcfcFGAvcCHMxjTV738xWPclhfdlr1.', 'crew',     2);  -- off shift

-- Units (approximate positions of real bases)
-- Units with a crew member on shift are available; the others are unavailable
INSERT INTO unit (id, code, license_plate, type, support_level, status, district_id, latitude, longitude, user_id) VALUES
    -- Lisboa
    (1, 'AMB-LX-01',  'AA-01-BB', 'ambulance', 'basic',    'available',   1, 38.7487, -9.1606, 4),     -- Santa Maria
    (2, 'AMB-LX-02',  'AB-02-BC', 'ambulance', 'basic',    'available',   1, 38.6979, -9.2066, 5),     -- Belém
    (3, 'AMB-LX-03',  'BB-03-CD', 'ambulance', 'advanced', 'available',   1, 38.7181, -9.1389, 6),     -- São José
    (4, 'VMER-LX-01', 'BC-04-DE', 'vmer',      'advanced', 'unavailable', 1, 38.8309, -9.1685, NULL),  -- Loures
    -- Setúbal
    (5, 'AMB-ST-01',  'CC-01-EF', 'ambulance', 'basic',    'available',   2, 38.5260, -8.8856, 8),     -- Setúbal
    (6, 'AMB-ST-02',  'CE-02-FG', 'ambulance', 'advanced', 'available',   2, 38.6745, -9.1772, 9),     -- Almada
    (7, 'AMB-ST-03',  'EE-03-HJ', 'ambulance', 'basic',    'unavailable', 2, 38.6603, -9.0721, NULL);  -- Barreiro

-- Reset sequences after inserting explicit ids
SELECT setval('district_id_seq', (SELECT max(id) FROM district));
SELECT setval('app_user_id_seq', (SELECT max(id) FROM app_user));
SELECT setval('unit_id_seq',     (SELECT max(id) FROM unit));
