-- Inicializar banco de dados PostgreSQL para Bot Telegram SMS

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    tg_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255),
    balance DECIMAL(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_tg_id ON users(tg_id);

-- Tabela de pedidos de créditos
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    credits DECIMAL(10, 2) NOT NULL,
    package_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    pluggy_charge_id VARCHAR(255) UNIQUE,
    pluggy_payment_id VARCHAR(255) UNIQUE,
    qr_code_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_pluggy_charge_id ON orders(pluggy_charge_id);

-- Tabela de aluguel de SMS
CREATE TABLE IF NOT EXISTS sms_rents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    activation_id VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50) NOT NULL,
    country VARCHAR(10) NOT NULL,
    service VARCHAR(100) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    sms_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_sms_rents_user_id ON sms_rents(user_id);
CREATE INDEX idx_sms_rents_status ON sms_rents(status);
CREATE INDEX idx_sms_rents_activation_id ON sms_rents(activation_id);

-- Tabela de pedidos de seguidores
CREATE TABLE IF NOT EXISTS followers_orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    profile_url VARCHAR(500) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    apex_order_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_followers_orders_user_id ON followers_orders(user_id);
CREATE INDEX idx_followers_orders_status ON followers_orders(status);

-- Tabela de logs
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    source VARCHAR(255) NOT NULL,
    payload TEXT,
    level VARCHAR(50) DEFAULT 'info',
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_source ON logs(source);
CREATE INDEX idx_logs_level ON logs(level);
CREATE INDEX idx_logs_timestamp ON logs(timestamp DESC);
