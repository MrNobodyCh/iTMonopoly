--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.6
-- Dumped by pg_dump version 9.6.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: courses; Type: TABLE; Schema: public; Owner: e_chupikov
--

CREATE TABLE courses (
    id integer NOT NULL,
    title character varying,
    description character varying,
    age character varying,
    start_date character varying,
    duration character varying,
    cost character varying,
    image character varying,
    course_type character varying,
    site_link character varying
);


ALTER TABLE courses OWNER TO e_chupikov;

--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: e_chupikov
--

CREATE SEQUENCE courses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE courses_id_seq OWNER TO e_chupikov;

--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: e_chupikov
--

ALTER SEQUENCE courses_id_seq OWNED BY courses.id;


--
-- Name: courses_tmp; Type: TABLE; Schema: public; Owner: e_chupikov
--

CREATE TABLE courses_tmp (
    id integer NOT NULL,
    title character varying,
    description character varying,
    age character varying,
    start_date character varying,
    duration character varying,
    cost character varying,
    image character varying,
    course_type character varying,
    site_link character varying
);


ALTER TABLE courses_tmp OWNER TO e_chupikov;

--
-- Name: courses_tmp_id_seq; Type: SEQUENCE; Schema: public; Owner: e_chupikov
--

CREATE SEQUENCE courses_tmp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE courses_tmp_id_seq OWNER TO e_chupikov;

--
-- Name: courses_tmp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: e_chupikov
--

ALTER SEQUENCE courses_tmp_id_seq OWNED BY courses_tmp.id;


--
-- Name: events; Type: TABLE; Schema: public; Owner: e_chupikov
--

CREATE TABLE events (
    id integer NOT NULL,
    image character varying,
    title character varying,
    description character varying,
    event_date integer,
    age character varying,
    conditions character varying,
    site_link character varying
);


ALTER TABLE events OWNER TO e_chupikov;

--
-- Name: events_id_seq; Type: SEQUENCE; Schema: public; Owner: e_chupikov
--

CREATE SEQUENCE events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE events_id_seq OWNER TO e_chupikov;

--
-- Name: events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: e_chupikov
--

ALTER SEQUENCE events_id_seq OWNED BY events.id;


--
-- Name: events_tmp; Type: TABLE; Schema: public; Owner: e_chupikov
--

CREATE TABLE events_tmp (
    id integer NOT NULL,
    image character varying,
    title character varying,
    description character varying,
    event_date integer,
    age character varying,
    conditions character varying,
    site_link character varying
);


ALTER TABLE events_tmp OWNER TO e_chupikov;

--
-- Name: events_tmp_id_seq; Type: SEQUENCE; Schema: public; Owner: e_chupikov
--

CREATE SEQUENCE events_tmp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE events_tmp_id_seq OWNER TO e_chupikov;

--
-- Name: events_tmp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: e_chupikov
--

ALTER SEQUENCE events_tmp_id_seq OWNED BY events_tmp.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: e_chupikov
--

CREATE TABLE users (
    user_id bigint,
    first_name character varying,
    phone_number character varying,
    is_active boolean DEFAULT true,
    is_subscribed_to_courses boolean DEFAULT false,
    is_subscribed_to_events boolean DEFAULT false,
    is_administrator boolean DEFAULT false,
    email character varying
);


ALTER TABLE users OWNER TO e_chupikov;

--
-- Name: users_requests; Type: TABLE; Schema: public; Owner: e_chupikov
--

CREATE TABLE users_requests (
    id integer NOT NULL,
    user_id integer,
    course_name character varying,
    event_name character varying,
    course_id integer,
    event_id integer,
    request_type character varying
);


ALTER TABLE users_requests OWNER TO e_chupikov;

--
-- Name: users_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: e_chupikov
--

CREATE SEQUENCE users_requests_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE users_requests_id_seq OWNER TO e_chupikov;

--
-- Name: users_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: e_chupikov
--

ALTER SEQUENCE users_requests_id_seq OWNED BY users_requests.id;


--
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: e_chupikov
--

ALTER TABLE ONLY courses ALTER COLUMN id SET DEFAULT nextval('courses_id_seq'::regclass);


--
-- Name: courses_tmp id; Type: DEFAULT; Schema: public; Owner: e_chupikov
--

ALTER TABLE ONLY courses_tmp ALTER COLUMN id SET DEFAULT nextval('courses_tmp_id_seq'::regclass);


--
-- Name: events id; Type: DEFAULT; Schema: public; Owner: e_chupikov
--

ALTER TABLE ONLY events ALTER COLUMN id SET DEFAULT nextval('events_id_seq'::regclass);


--
-- Name: events_tmp id; Type: DEFAULT; Schema: public; Owner: e_chupikov
--

ALTER TABLE ONLY events_tmp ALTER COLUMN id SET DEFAULT nextval('events_tmp_id_seq'::regclass);


--
-- Name: users_requests id; Type: DEFAULT; Schema: public; Owner: e_chupikov
--

ALTER TABLE ONLY users_requests ALTER COLUMN id SET DEFAULT nextval('users_requests_id_seq'::regclass);


--
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: e_chupikov
--

COPY courses (id, title, description, age, start_date, duration, cost, image, course_type, site_link) FROM stdin;
35	Разработка веб-проектов (Front-end)	Открыт набор в новые группы!	15-55	31 марта 2018 г.	5 месяцев	16 900 руб. в месяц	AgADAgADmqgxG6sLuUjj6P8wUapt9TvtAw4ABPKMxv6l_YrVcdQDAAEC	adult	http://itmonopoly.com/courses/adults/razrabotka-veb-proektov-front-end/
36	Разработка веб-проектов (Back-end)	Открыт набор в новые группы!	15-55	31 марта 2018 г.	5 месяцев	17 900 руб. в месяц	AgADAgADm6gxG6sLuUhtBHSyjVX9XyOfmg4ABNPyiIS_dtIkCPEBAAEC	adult	http://itmonopoly.com/courses/adults/razrabotka-veb-proektov-back-end/
37	Разработка игр с использованием Unity 3D	Открыт набор в новые группы!	16-55	31 марта 2018 г.	12 месяцев	18 900 руб. в месяц	AgADAgADnqgxG6sLuUgezZ4Q2e5PSi4cMw4ABA130itPZWkCiZQEAAEC	adult	http://itmonopoly.com/courses/adults/razrabotka-igr-s-ispolzovaniem-unity-3d/
38	Создание игр (Scratch 2.0)	Открыт набор в новые группы!	8-15	1 марта 2018 г.	2 месяца	15 000 руб. в месяц	AgADAgADnKgxG6sLuUioaGMGYt8lNuiimg4ABIbfnaudbhZ9ZPQBAAEC	kids	http://itmonopoly.com/courses/kids/gamedev-course/
39	Создание компьютерной анимации	Открыт набор в новые группы!	8-15	1 марта 2018 г.	2 месяца	15 000 руб. в месяц	AgADAgADnagxG6sLuUjntlmSVOUCNmf3Mg4ABF8D6_-MTC5qVqEEAAEC	kids	http://itmonopoly.com/courses/kids/animation-course/
40	Робототехника	Открыт набор в новые группы!	8-15	1 марта 2018 г.	2 месяца	6 000 руб. в месяц	AgADAgADvqgxG6sLuUhZJCjUfpIZPGAHMw4ABLSL8yAvIWvnIqEEAAEC	kids	http://itmonopoly.com/courses/kids/roboto-course/
41	IT.Kids	Открыт набор в новые группы! Курс, максимально раскрывающий творческий потенциал ребёнка.	8-14	1 марта 2018 г.	8 месяцев	12 900 руб. в месяц	AgADAgADv6gxG6sLuUj5p-ZEpf2dWQQMnA4ABLEQ-BjEkU7JyPcBAAEC	kids	http://itmonopoly.com/courses/kids/it-kids/
42	Gamedev.Kids	Открыт набор в новые группы! Углубленный курс по созданию компьютерных игр для детей.	8-14	1 марта 2018 г.	8 месяцев	14 900 руб. в месяц	AgADAgADdKgxG6sLsUg7bt_Usgabe9gQMw4ABGQCaCXf-cvl75EEAAEC	kids	http://itmonopoly.com/courses/kids/gamedev-kids/
43	Python + Data Science	Открыт набор в новые группы!	15-55	31 марта 2018 г.	4 месяца	18 900 руб. в месяц	AgADAgADwKgxG6sLuUispQ8IR_UOZKIBnA4ABMX49YVw5ClNTPkBAAEC	adult	http://itmonopoly.com/courses/adults/python-data-science/
48	Design.Kids	Углубленный курс по развитию творческого потенциала ребёнка с погружением в увлекательный мир!	8-14	1 марта 2018 г.	8 месяцев	14 900 руб. в месяц	AgADAgADwqgxG6sLuUj2Rl11dK_s97QInA4ABBps3Uuu_0_CVPsBAAEC	kids	http://itmonopoly.com/courses/kids/design-kids/
51	Coder.Kids	Углубленный курс по программированию для школьников!	8-14	1 марта 2018 г.	8 месяцев	14 900 руб. в месяц	AgADAgADoagxG4FCeUjMuEVym_762wToAw4ABIzDfnK3P-Jks44DAAEC	kids	http://itmonopoly.com/courses/kids/coder-kids/
55	Kids.Start	Программа раннего развития детей дошкольного возраста	5-7 лет	31 марта 2018 г.	8 месяцев	6 900 руб. в месяц	AgADAgADpagxG4FCeUjI--WgMPU8YxUMnA4ABCxKmNcBW8E9GbABAAEC	kids	http://itmonopoly.com/courses/kids/kids-start/
56	Тестирование ПО (QA)	Открыт набор в новые группы!	15-55 лет	1 марта 2018 г.	5 месяцев	16 900 руб. в месяц	AgADAgADmagxG6sLuUi5lgZkSYMjad4LnA4ABO9ocX2Xv3EjvvEBAAEC	adult	http://itmonopoly.com/courses/adults/testirovanie-po-qa/
57	Design.project	Открыт набор в новые группы! Очное обучение в центре Москвы. Гарантированная стажировка, международный сертификат.	15-55 лет	31 марта 2018 г.	5 месяцев	16 900 руб. в месяц	AgADAgADuqgxG4FCgUgZ4hcLINTALm6cQw4ABJtFJvUTaokTGrcBAAEC	adult	http://itmonopoly.com/courses/adults/design-project/
68	Программирование на JAVA	Открыт набор в новые группы!	15-55 лет	31 марта 2018 г.	5 месяцев	16 500 руб. в месяц	AgADAgADuKgxG4FCgUgrPOWZmi-2eFcZnA4ABC_R0hErJQG8lLgBAAEC	adult	http://itmonopoly.com/courses/adults/java/
\.


--
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: e_chupikov
--

SELECT pg_catalog.setval('courses_id_seq', 68, true);


--
-- Data for Name: courses_tmp; Type: TABLE DATA; Schema: public; Owner: e_chupikov
--

COPY courses_tmp (id, title, description, age, start_date, duration, cost, image, course_type, site_link) FROM stdin;
\.


--
-- Name: courses_tmp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: e_chupikov
--

SELECT pg_catalog.setval('courses_tmp_id_seq', 16, true);


--
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: e_chupikov
--

COPY events (id, image, title, description, event_date, age, conditions, site_link) FROM stdin;
20	AgADAgAD6KgxGwPH0UjeuiYSiuIomXWamg4ABLvoUTttW6mspw8CAAEC	Чувство композиции	Как придумывать иллюстрации, эскизы, изображения, опираясь только на чувство композиции	1521216000	15-55	Участие бесплатное.Количество мест ограничено.	http://itmonopoly.com/events/chuvstvo-kompozitsii/
9	AgADAgADwKgxG6sLuUispQ8IR_UOZKIBnA4ABMX49YVw5ClNTPkBAAEC	День открытых дверей «Как стать программистом?»	Какие специальности самые востребованные. Сфера IT: смогу ли я? Какие знания нужны работодателям, и каким специалистам они готовы платить 1500$/месяц. Чему учат в Центре Цифрового Развития ITmonopoly.	1521216000	15-55 лет	Участие бесплатное. Количество мест ограничено	http://itmonopoly.com/events/den-otkryityih-dverey-v/
11	AgADAgADdKgxG6sLsUg7bt_Usgabe9gQMw4ABGQCaCXf-cvl75EEAAEC	Создание компьютерной анимации	Анимация персонажа путём расстановки ключей анимации	1521273600	8-15 лет	Участие бесплатное. Количество мест ограничено	http://itmonopoly.com/events/animation-event/
12	AgADAgADpagxGxBVyUgiID3vpr0XL2u1mg4ABFzeqhkwue6kS_sBAAEC	День Открытых Дверей для детей	Битвы роботов, знакомство с компьютерной анимацией, создание игр	1520074800	8-14 лет	Участие бесплатное. Количество мест ограничено	http://itmonopoly.com/events/den-otkryityih-dverey-dlya-detey/
13	AgADAgADwqgxG6sLuUj2Rl11dK_s97QInA4ABBps3Uuu_0_CVPsBAAEC	Робототехника	Что такое робототехника?	1520956800	8-15 лет	Участие бесплатное. Количество мест ограничено	http://itmonopoly.com/events/roboto-event/
23	AgADAgADoagxG4FCeUjMuEVym_762wToAw4ABIzDfnK3P-Jks44DAAEC	Создание компьютерных игр	Создание игрового уровня, с помощью преподавателя на мастер-классе	1521878400	8-15 лет	Участие бесплатное. Количество мест ограничено	http://itmonopoly.com/events/gamedev-event/
\.


--
-- Name: events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: e_chupikov
--

SELECT pg_catalog.setval('events_id_seq', 23, true);


--
-- Data for Name: events_tmp; Type: TABLE DATA; Schema: public; Owner: e_chupikov
--

COPY events_tmp (id, image, title, description, event_date, age, conditions, site_link) FROM stdin;
\.


--
-- Name: events_tmp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: e_chupikov
--

SELECT pg_catalog.setval('events_tmp_id_seq', 21, true);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: e_chupikov
--

COPY users (user_id, first_name, phone_number, is_active, is_subscribed_to_courses, is_subscribed_to_events, is_administrator, email) FROM stdin;
418335099	Egor	\N	t	f	f	f	\N
\.


--
-- Data for Name: users_requests; Type: TABLE DATA; Schema: public; Owner: e_chupikov
--

COPY users_requests (id, user_id, course_name, event_name, course_id, event_id, request_type) FROM stdin;
46	418335099	Программирование на JAVA	\N	63	\N	regfree
50	418335099	Python + Data Science	\N	43	\N	reg
53	418335099	\N	Создание компьютерных игр	\N	22	\N
54	381524416	\N	Создание компьютерных игр	\N	22	\N
\.


--
-- Name: users_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: e_chupikov
--

SELECT pg_catalog.setval('users_requests_id_seq', 57, true);


--
-- PostgreSQL database dump complete
--

