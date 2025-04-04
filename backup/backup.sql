--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: folder_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.folder_users (
    folderid integer NOT NULL,
    userid integer NOT NULL
);


ALTER TABLE public.folder_users OWNER TO postgres;

--
-- Name: folder_users_folderid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.folder_users_folderid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.folder_users_folderid_seq OWNER TO postgres;

--
-- Name: folder_users_folderid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.folder_users_folderid_seq OWNED BY public.folder_users.folderid;


--
-- Name: folder_users_userid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.folder_users_userid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.folder_users_userid_seq OWNER TO postgres;

--
-- Name: folder_users_userid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.folder_users_userid_seq OWNED BY public.folder_users.userid;


--
-- Name: folders_contents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.folders_contents (
    folderid integer NOT NULL,
    newsid integer NOT NULL
);


ALTER TABLE public.folders_contents OWNER TO postgres;

--
-- Name: folders_contents_folderid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.folders_contents_folderid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.folders_contents_folderid_seq OWNER TO postgres;

--
-- Name: folders_contents_folderid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.folders_contents_folderid_seq OWNED BY public.folders_contents.folderid;


--
-- Name: folders_contents_newsid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.folders_contents_newsid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.folders_contents_newsid_seq OWNER TO postgres;

--
-- Name: folders_contents_newsid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.folders_contents_newsid_seq OWNED BY public.folders_contents.newsid;


--
-- Name: folders_names; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.folders_names (
    folder_id integer NOT NULL,
    folder_name character(20) NOT NULL
);


ALTER TABLE public.folders_names OWNER TO postgres;

--
-- Name: folders_names_folder_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.folders_names_folder_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.folders_names_folder_id_seq OWNER TO postgres;

--
-- Name: folders_names_folder_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.folders_names_folder_id_seq OWNED BY public.folders_names.folder_id;


--
-- Name: news; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.news (
    news_id integer NOT NULL,
    type_news character(4) NOT NULL,
    author character(100) NOT NULL,
    date timestamp without time zone NOT NULL,
    link text NOT NULL,
    source text NOT NULL
);


ALTER TABLE public.news OWNER TO postgres;

--
-- Name: news_news_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.news_news_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.news_news_id_seq OWNER TO postgres;

--
-- Name: news_news_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.news_news_id_seq OWNED BY public.news.news_id;


--
-- Name: suggested; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.suggested (
    userid integer NOT NULL,
    source text NOT NULL,
    aproved boolean NOT NULL
);


ALTER TABLE public.suggested OWNER TO postgres;

--
-- Name: suggested_userid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.suggested_userid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.suggested_userid_seq OWNER TO postgres;

--
-- Name: suggested_userid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.suggested_userid_seq OWNED BY public.suggested.userid;


--
-- Name: tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tags (
    tag_name character(100) NOT NULL,
    newsid integer NOT NULL
);


ALTER TABLE public.tags OWNER TO postgres;

--
-- Name: tags_newsid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tags_newsid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tags_newsid_seq OWNER TO postgres;

--
-- Name: tags_newsid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tags_newsid_seq OWNED BY public.tags.newsid;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    login character(15) NOT NULL,
    password character(20) NOT NULL,
    role character(10) NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: folder_users folderid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folder_users ALTER COLUMN folderid SET DEFAULT nextval('public.folder_users_folderid_seq'::regclass);


--
-- Name: folder_users userid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folder_users ALTER COLUMN userid SET DEFAULT nextval('public.folder_users_userid_seq'::regclass);


--
-- Name: folders_contents folderid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folders_contents ALTER COLUMN folderid SET DEFAULT nextval('public.folders_contents_folderid_seq'::regclass);


--
-- Name: folders_contents newsid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folders_contents ALTER COLUMN newsid SET DEFAULT nextval('public.folders_contents_newsid_seq'::regclass);


--
-- Name: folders_names folder_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folders_names ALTER COLUMN folder_id SET DEFAULT nextval('public.folders_names_folder_id_seq'::regclass);


--
-- Name: news news_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.news ALTER COLUMN news_id SET DEFAULT nextval('public.news_news_id_seq'::regclass);


--
-- Name: suggested userid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggested ALTER COLUMN userid SET DEFAULT nextval('public.suggested_userid_seq'::regclass);


--
-- Name: tags newsid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tags ALTER COLUMN newsid SET DEFAULT nextval('public.tags_newsid_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: folder_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.folder_users (folderid, userid) FROM stdin;
\.


--
-- Data for Name: folders_contents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.folders_contents (folderid, newsid) FROM stdin;
\.


--
-- Data for Name: folders_names; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.folders_names (folder_id, folder_name) FROM stdin;
\.


--
-- Data for Name: news; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.news (news_id, type_news, author, date, link, source) FROM stdin;
\.


--
-- Data for Name: suggested; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.suggested (userid, source, aproved) FROM stdin;
\.


--
-- Data for Name: tags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tags (tag_name, newsid) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (user_id, login, password, role) FROM stdin;
\.


--
-- Name: folder_users_folderid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.folder_users_folderid_seq', 1, false);


--
-- Name: folder_users_userid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.folder_users_userid_seq', 1, false);


--
-- Name: folders_contents_folderid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.folders_contents_folderid_seq', 1, false);


--
-- Name: folders_contents_newsid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.folders_contents_newsid_seq', 1, false);


--
-- Name: folders_names_folder_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.folders_names_folder_id_seq', 1, false);


--
-- Name: news_news_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.news_news_id_seq', 1, false);


--
-- Name: suggested_userid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.suggested_userid_seq', 1, false);


--
-- Name: tags_newsid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tags_newsid_seq', 1, false);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_user_id_seq', 1, false);


--
-- Name: folders_names folders_names_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folders_names
    ADD CONSTRAINT folders_names_pkey PRIMARY KEY (folder_id);


--
-- Name: news news_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.news
    ADD CONSTRAINT news_pkey PRIMARY KEY (news_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: folder_users folder_users_folderid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folder_users
    ADD CONSTRAINT folder_users_folderid_fkey FOREIGN KEY (folderid) REFERENCES public.folders_names(folder_id);


--
-- Name: folder_users folder_users_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folder_users
    ADD CONSTRAINT folder_users_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(user_id);


--
-- Name: folders_contents folders_contents_folderid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folders_contents
    ADD CONSTRAINT folders_contents_folderid_fkey FOREIGN KEY (folderid) REFERENCES public.folders_names(folder_id);


--
-- Name: folders_contents folders_contents_newsid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.folders_contents
    ADD CONSTRAINT folders_contents_newsid_fkey FOREIGN KEY (newsid) REFERENCES public.news(news_id);


--
-- Name: suggested suggested_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggested
    ADD CONSTRAINT suggested_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(user_id);


--
-- Name: tags tags_newsid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_newsid_fkey FOREIGN KEY (newsid) REFERENCES public.news(news_id);


--
-- PostgreSQL database dump complete
--

