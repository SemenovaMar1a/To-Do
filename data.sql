--
-- PostgreSQL database dump
--

\restrict SgVvYBJM7aC8eG7U4hOZlMjsHHE26P87uzeHOaYOMQHTAqeQ3v3zcgsAVBgzyRp

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (username, email, role, id, hashed_password) FROM stdin;
Коля	kol@yande.ru	ADMIN	1	$2b$12$x0/CpZRV1tTvhxzSAENsLOnoEBas0svbf8Pgn6aZBoj5/1uEIbFF.
Аня	Any@email.ru	USER	2	$2b$12$UqvP4eUKdAZ00OPDVgS0uO6S8bWBqjvflNqHkdtyN6FF8k2E/llje
Ваня	van@yandex.ru	USER	3	$2b$12$G/Jtf0lWRdrK2y6x.T1cyetm4gpkiz62CsQgxfiSi4Ig2Ysc0SqG.
mysha	s.@yandex.ru	USER	4	$2b$12$feEWme/GqZeRdsrXEUeALe40/yEtSh1TdwWyBjb3681eiILX33z72
Саша	sasha@mail.ru	USER	5	$2b$12$y3Bps7dZ0Pm15GsA/ICbyOoBcPIr1Rk4oTrgSgb6U6GEor0bmMlzi
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (title, description, id, is_completed, created_at, user_id) FROM stdin;
Сделать подарок	кукла	1	t	2025-05-05 17:29:49.731292	1
Отпуск	в Анапу	3	t	2025-06-09 12:28:48.392969	2
Поиграть в игру	стрелялка	4	f	2025-06-09 20:04:02.61723	1
Купить книгу	Маленький принц	5	f	2026-01-09 00:48:44.557888	2
\.


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tasks_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

\unrestrict SgVvYBJM7aC8eG7U4hOZlMjsHHE26P87uzeHOaYOMQHTAqeQ3v3zcgsAVBgzyRp

