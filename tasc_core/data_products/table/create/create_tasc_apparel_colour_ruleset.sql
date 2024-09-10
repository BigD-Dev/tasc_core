DROP TABLE IF EXISTS tasc_sandbox.tasc_apparel_colour_ruleset CASCADE;
CREATE TABLE tasc_sandbox.tasc_apparel_colour_ruleset (
    asof_dt DATE,
    outerwear VARCHAR(255),
    top_1 VARCHAR(255),
    top_2 VARCHAR(255),
    bottoms VARCHAR(255),
    socks VARCHAR(255),
    footwear VARCHAR(255),
    accessory_1 VARCHAR(255),
    accessory_2 VARCHAR(255),
    jewellery VARCHAR(255),
    colour_harmony_type VARCHAR(255),
    active_flag NUMERIC,
    source VARCHAR(255),
    filename VARCHAR(255),
    last_modified_tms TIMESTAMP,
    source_date DATE,
    source_datetime TIMESTAMP);