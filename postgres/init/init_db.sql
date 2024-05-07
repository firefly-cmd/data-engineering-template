DROP TABLE IF EXISTS application_metrics;

CREATE TABLE application_metrics (
    application_id TEXT,
    startdate TIMESTAMP,
    enddate TIMESTAMP,
    error_rate DECIMAL(5, 2),
    average_latency DECIMAL(10, 2),
    get_requests INTEGER,
    post_requests INTEGER,
    put_requests INTEGER,
    delete_requests INTEGER
);





