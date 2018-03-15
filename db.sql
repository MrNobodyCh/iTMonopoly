CREATE TABLE IF NOT EXISTS users (user_id BIGINT, first_name VARCHAR, phone_number VARCHAR DEFAULT NULL, is_active BOOLEAN DEFAULT TRUE, is_subscribed_to_courses BOOLEAN DEFAULT FALSE, is_subscribed_to_events BOOLEAN DEFAULT FALSE, is_administrator BOOLEAN DEFAULT FALSE, email VARCHAR );

CREATE TABLE IF NOT EXISTS courses (id SERIAL, title VARCHAR, description VARCHAR, age VARCHAR, start_date VARCHAR, duration VARCHAR, cost VARCHAR, image VARCHAR, course_type VARCHAR, site_link VARCHAR);

CREATE TABLE IF NOT EXISTS courses_tmp (id SERIAL, title VARCHAR, description VARCHAR, age VARCHAR, start_date VARCHAR, duration VARCHAR, cost VARCHAR, image VARCHAR, course_type VARCHAR, site_link VARCHAR);

CREATE TABLE IF NOT EXISTS events (id SERIAL, image VARCHAR, title VARCHAR, description VARCHAR, event_date INT, age VARCHAR, conditions VARCHAR, site_link VARCHAR);

CREATE TABLE IF NOT EXISTS events_tmp (id SERIAL, image VARCHAR, title VARCHAR, description VARCHAR, event_date INT, age VARCHAR, conditions VARCHAR, site_link VARCHAR);

CREATE TABLE IF NOT EXISTS users_requests (id SERIAL, user_id INT, course_name VARCHAR, event_name VARCHAR, course_id INT, event_id INT, request_type VARCHAR);