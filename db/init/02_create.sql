DROP TABLE IF EXISTS userdata;
DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS channel;

-- テーブル:userdata
CREATE TABLE userdata(
    id SERIAL PRIMARY KEY,
    discord_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255) NOT NULL,
    discriminator VARCHAR(10) NOT NULL
);

-- テーブル: channel
CREATE TABLE channel (
    id SERIAL PRIMARY KEY,
    discord_channel_id BIGINT UNIQUE NOT NULL,
    channel_name VARCHAR(255) NOT NULL
);


-- テーブル:review
CREATE TABLE review(
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    room_id BIGINT NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration INTERVAL GENERATED ALWAYS AS (end_time - start_time) STORED,
    FOREIGN KEY (user_id) REFERENCES userdata(discord_id),
    FOREIGN KEY (room_id) REFERENCES channel(discord_channel_id)
);
