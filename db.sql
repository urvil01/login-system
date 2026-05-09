CREATE TABLE users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    email TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL,

    otp TEXT,

    verified INTEGER DEFAULT 0

);