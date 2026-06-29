// =========================
// PERSON
// =========================
CREATE CONSTRAINT person_id IF NOT EXISTS
FOR (p:Person)
REQUIRE p.person_id IS UNIQUE;

// =========================
// INDEXES
// =========================

CREATE INDEX person_name IF NOT EXISTS
FOR (p:Person)
ON (p.name);

CREATE INDEX account_bank IF NOT EXISTS
FOR (a:Account)
ON (a.bank_name);

CREATE INDEX transaction_amount IF NOT EXISTS
FOR (t:Transaction)
ON (t.amount);

CREATE INDEX device_ip IF NOT EXISTS
FOR (d:Device)
ON (d.ip_address);

// =========================
// ACCOUNT
// =========================
CREATE CONSTRAINT account_number IF NOT EXISTS
FOR (a:Account)
REQUIRE a.account_number IS UNIQUE;

// =========================
// DEVICE
// =========================
CREATE CONSTRAINT device_id IF NOT EXISTS
FOR (d:Device)
REQUIRE d.device_id IS UNIQUE;

// =========================
// TRANSACTION
// =========================
CREATE CONSTRAINT transaction_id IF NOT EXISTS
FOR (t:Transaction)
REQUIRE t.transaction_id IS UNIQUE;