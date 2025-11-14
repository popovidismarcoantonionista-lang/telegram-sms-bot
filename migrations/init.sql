-- Telegram SMS Bot Database Schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    tg_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255),
    balance DECIMAL(10, 2) DEFAULT 0.00 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_tg_id ON users(tg_id);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    amount DECIMAL(10, 2) NOT NULL,
    plan_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    pixintegra_charge_id VARCHAR(255) UNIQUE,
    pix_qrcode TEXT,
    pix_code TEXT,
    credits_amount DECIMAL(10, 2),
    idempotency_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    paid_at TIMESTAMP
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_charge_id ON orders(pixintegra_charge_id);
CREATE INDEX idx_orders_status ON orders(status);

-- SMS Rents table
CREATE TABLE IF NOT EXISTS sms_rents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    order_id VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    service VARCHAR(50) NOT NULL,
    country VARCHAR(10) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    sms_code VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at TIMESTAMP
);

CREATE INDEX idx_sms_rents_user_id ON sms_rents(user_id);
CREATE INDEX idx_sms_rents_order_id ON sms_rents(order_id);
CREATE INDEX idx_sms_rents_status ON sms_rents(status);

-- Followers Orders table
CREATE TABLE IF NOT EXISTS followers_orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    platform VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    target_url VARCHAR(500) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    apex_order_id VARCHAR(255) UNIQUE,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at TIMESTAMP
);

CREATE INDEX idx_followers_orders_user_id ON followers_orders(user_id);
CREATE INDEX idx_followers_orders_apex_id ON followers_orders(apex_order_id);
CREATE INDEX idx_followers_orders_status ON followers_orders(status);

-- Logs table
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    payload TEXT,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_logs_source ON logs(source);
CREATE INDEX idx_logs_level ON logs(level);
CREATE INDEX idx_logs_timestamp ON logs(timestamp);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
