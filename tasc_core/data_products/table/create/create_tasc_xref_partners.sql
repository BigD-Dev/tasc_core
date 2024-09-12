DROP TABLE IF EXISTS tasc_prod.tasc_xref_partners CASCADE;
CREATE TABLE tasc_prod.tasc_xref_partners (
    id SERIAL PRIMARY KEY,
    asof_dt DATE,
    partner_uid INT,
    partner_name VARCHAR(255),
    partner_full_name VARCHAR(255),
    partner_desc VARCHAR(255),
    partner_type VARCHAR(255),
    partner_primary_url VARCHAR(255),
    created_at_tms TIMESTAMP,
    created_by VARCHAR(255),
    last_modified_tms TIMESTAMP,
    last_modified_by VARCHAR(255),
    source_date DATE,
    source_datetime TIMESTAMP
);