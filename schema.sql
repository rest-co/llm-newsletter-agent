CREATE TABLE news_articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    link TEXT UNIQUE,
    original_link TEXT,
    content TEXT,
    pub_date TIMESTAMP,
    representative_news_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
