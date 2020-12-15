-- PRAGMA synchronous="OFF";
-- pragma locking_mode="EXCLUSIVE";
CREATE TABLE packages
(
    pkgKey INTEGER PRIMARY KEY,
    pkgId TEXT,
    name TEXT,
    arch TEXT,
    version TEXT,
    epoch TEXT,
    release TEXT,
    summary TEXT,
    description TEXT,
    url TEXT,
    time_file INTEGER,
    time_build INTEGER,
    rpm_license TEXT,
    rpm_vendor TEXT,
    rpm_group TEXT,
    rpm_buildhost TEXT,
    rpm_sourcerpm TEXT,
    rpm_header_start INTEGER,
    rpm_header_end INTEGER,
    rpm_packager TEXT,
    size_package INTEGER,
    size_installed INTEGER,
    size_archive INTEGER,
    location_href TEXT,
    location_base TEXT,
    checksum_type TEXT
);

CREATE TABLE conflicts
(
    name TEXT,
    flags TEXT,
    epoch TEXT,
    version TEXT,
    release TEXT,
    pkgKey INTEGER
);

CREATE TABLE db_info
(
    dbversion INTEGER,
    checksum TEXT
);

CREATE TABLE files
(
    name TEXT,
    type TEXT,
    pkgKey INTEGER
);

CREATE TABLE obsoletes
(
    name TEXT,
    flags TEXT,
    epoch TEXT,
    version TEXT,
    release TEXT,
    pkgKey INTEGER
);

CREATE TABLE provides
(
    name TEXT,
    flags TEXT,
    epoch TEXT,
    version TEXT,
    release TEXT,
    pkgKey INTEGER
);

CREATE TABLE requires
(
    name TEXT,
    flags TEXT,
    epoch TEXT,
    version TEXT,
    release TEXT,
    pkgKey INTEGER ,
    pre BOOL DEFAULT FALSE
);

CREATE INDEX filenames ON files (name);
CREATE INDEX packageId ON packages (pkgId);
CREATE INDEX packagename ON packages (name);
CREATE INDEX pkgconflicts on conflicts (pkgKey);
CREATE INDEX pkgobsoletes on obsoletes (pkgKey);
CREATE INDEX pkgprovides on provides (pkgKey);
CREATE INDEX pkgrequires on requires (pkgKey);
CREATE INDEX providesname ON provides (name);
CREATE INDEX requiresname ON requires (name);