PGDMP                       }            news_bd    17.4    17.4 3    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false            �           1262    16853    news_bd    DATABASE     m   CREATE DATABASE news_bd WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'ru-RU';
    DROP DATABASE news_bd;
                     postgres    false            �            1259    17193    folders    TABLE     �   CREATE TABLE public.folders (
    folder_id integer NOT NULL,
    userlog character(20) NOT NULL,
    folder_name character(20) NOT NULL,
    newsid integer NOT NULL
);
    DROP TABLE public.folders;
       public         heap r       postgres    false            �            1259    17191    folders_folder_id_seq    SEQUENCE     �   CREATE SEQUENCE public.folders_folder_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public.folders_folder_id_seq;
       public               postgres    false    228            �           0    0    folders_folder_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public.folders_folder_id_seq OWNED BY public.folders.folder_id;
          public               postgres    false    226            �            1259    17192    folders_newsid_seq    SEQUENCE     �   CREATE SEQUENCE public.folders_newsid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.folders_newsid_seq;
       public               postgres    false    228            �           0    0    folders_newsid_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public.folders_newsid_seq OWNED BY public.folders.newsid;
          public               postgres    false    227            �            1259    17171    news    TABLE       CREATE TABLE public.news (
    news_id integer NOT NULL,
    type_news boolean NOT NULL,
    news_title text NOT NULL,
    news_content text NOT NULL,
    status boolean NOT NULL,
    tagid integer NOT NULL,
    sourceid integer NOT NULL,
    date timestamp without time zone
);
    DROP TABLE public.news;
       public         heap r       postgres    false            �            1259    17168    news_news_id_seq    SEQUENCE     �   CREATE SEQUENCE public.news_news_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 '   DROP SEQUENCE public.news_news_id_seq;
       public               postgres    false    225            �           0    0    news_news_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE public.news_news_id_seq OWNED BY public.news.news_id;
          public               postgres    false    222            �            1259    17170    news_sourceid_seq    SEQUENCE     �   CREATE SEQUENCE public.news_sourceid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.news_sourceid_seq;
       public               postgres    false    225            �           0    0    news_sourceid_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.news_sourceid_seq OWNED BY public.news.sourceid;
          public               postgres    false    224            �            1259    17169    news_tagid_seq    SEQUENCE     �   CREATE SEQUENCE public.news_tagid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 %   DROP SEQUENCE public.news_tagid_seq;
       public               postgres    false    225            �           0    0    news_tagid_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public.news_tagid_seq OWNED BY public.news.tagid;
          public               postgres    false    223            �            1259    17160    sources    TABLE     �   CREATE TABLE public.sources (
    source_id integer NOT NULL,
    source_name character(20) NOT NULL,
    source_link text NOT NULL
);
    DROP TABLE public.sources;
       public         heap r       postgres    false            �            1259    17159    sources_source_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sources_source_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public.sources_source_id_seq;
       public               postgres    false    221            �           0    0    sources_source_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public.sources_source_id_seq OWNED BY public.sources.source_id;
          public               postgres    false    220            �            1259    17153    tags    TABLE     _   CREATE TABLE public.tags (
    tag_id integer NOT NULL,
    tag_name character(20) NOT NULL
);
    DROP TABLE public.tags;
       public         heap r       postgres    false            �            1259    17152    tags_tag_id_seq    SEQUENCE     �   CREATE SEQUENCE public.tags_tag_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public.tags_tag_id_seq;
       public               postgres    false    219            �           0    0    tags_tag_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public.tags_tag_id_seq OWNED BY public.tags.tag_id;
          public               postgres    false    218            �            1259    17147    users    TABLE     �   CREATE TABLE public.users (
    user_login character(20) NOT NULL,
    user_password character(20) NOT NULL,
    user_role character(15) NOT NULL
);
    DROP TABLE public.users;
       public         heap r       postgres    false            <           2604    17196    folders folder_id    DEFAULT     v   ALTER TABLE ONLY public.folders ALTER COLUMN folder_id SET DEFAULT nextval('public.folders_folder_id_seq'::regclass);
 @   ALTER TABLE public.folders ALTER COLUMN folder_id DROP DEFAULT;
       public               postgres    false    226    228    228            =           2604    17197    folders newsid    DEFAULT     p   ALTER TABLE ONLY public.folders ALTER COLUMN newsid SET DEFAULT nextval('public.folders_newsid_seq'::regclass);
 =   ALTER TABLE public.folders ALTER COLUMN newsid DROP DEFAULT;
       public               postgres    false    228    227    228            9           2604    17174    news news_id    DEFAULT     l   ALTER TABLE ONLY public.news ALTER COLUMN news_id SET DEFAULT nextval('public.news_news_id_seq'::regclass);
 ;   ALTER TABLE public.news ALTER COLUMN news_id DROP DEFAULT;
       public               postgres    false    222    225    225            :           2604    17175 
   news tagid    DEFAULT     h   ALTER TABLE ONLY public.news ALTER COLUMN tagid SET DEFAULT nextval('public.news_tagid_seq'::regclass);
 9   ALTER TABLE public.news ALTER COLUMN tagid DROP DEFAULT;
       public               postgres    false    223    225    225            ;           2604    17176    news sourceid    DEFAULT     n   ALTER TABLE ONLY public.news ALTER COLUMN sourceid SET DEFAULT nextval('public.news_sourceid_seq'::regclass);
 <   ALTER TABLE public.news ALTER COLUMN sourceid DROP DEFAULT;
       public               postgres    false    224    225    225            8           2604    17163    sources source_id    DEFAULT     v   ALTER TABLE ONLY public.sources ALTER COLUMN source_id SET DEFAULT nextval('public.sources_source_id_seq'::regclass);
 @   ALTER TABLE public.sources ALTER COLUMN source_id DROP DEFAULT;
       public               postgres    false    220    221    221            7           2604    17156    tags tag_id    DEFAULT     j   ALTER TABLE ONLY public.tags ALTER COLUMN tag_id SET DEFAULT nextval('public.tags_tag_id_seq'::regclass);
 :   ALTER TABLE public.tags ALTER COLUMN tag_id DROP DEFAULT;
       public               postgres    false    218    219    219            �          0    17193    folders 
   TABLE DATA           J   COPY public.folders (folder_id, userlog, folder_name, newsid) FROM stdin;
    public               postgres    false    228   %8       �          0    17171    news 
   TABLE DATA           k   COPY public.news (news_id, type_news, news_title, news_content, status, tagid, sourceid, date) FROM stdin;
    public               postgres    false    225   B8       �          0    17160    sources 
   TABLE DATA           F   COPY public.sources (source_id, source_name, source_link) FROM stdin;
    public               postgres    false    221   _8       �          0    17153    tags 
   TABLE DATA           0   COPY public.tags (tag_id, tag_name) FROM stdin;
    public               postgres    false    219   |8       �          0    17147    users 
   TABLE DATA           E   COPY public.users (user_login, user_password, user_role) FROM stdin;
    public               postgres    false    217   �8       �           0    0    folders_folder_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.folders_folder_id_seq', 1, false);
          public               postgres    false    226            �           0    0    folders_newsid_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.folders_newsid_seq', 1, false);
          public               postgres    false    227            �           0    0    news_news_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.news_news_id_seq', 1, false);
          public               postgres    false    222            �           0    0    news_sourceid_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.news_sourceid_seq', 1, false);
          public               postgres    false    224            �           0    0    news_tagid_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.news_tagid_seq', 1, false);
          public               postgres    false    223            �           0    0    sources_source_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.sources_source_id_seq', 1, false);
          public               postgres    false    220            �           0    0    tags_tag_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('public.tags_tag_id_seq', 1, false);
          public               postgres    false    218            G           2606    17199    folders folders_pkey 
   CONSTRAINT     Y   ALTER TABLE ONLY public.folders
    ADD CONSTRAINT folders_pkey PRIMARY KEY (folder_id);
 >   ALTER TABLE ONLY public.folders DROP CONSTRAINT folders_pkey;
       public                 postgres    false    228            E           2606    17180    news news_pkey 
   CONSTRAINT     Q   ALTER TABLE ONLY public.news
    ADD CONSTRAINT news_pkey PRIMARY KEY (news_id);
 8   ALTER TABLE ONLY public.news DROP CONSTRAINT news_pkey;
       public                 postgres    false    225            C           2606    17167    sources sources_pkey 
   CONSTRAINT     Y   ALTER TABLE ONLY public.sources
    ADD CONSTRAINT sources_pkey PRIMARY KEY (source_id);
 >   ALTER TABLE ONLY public.sources DROP CONSTRAINT sources_pkey;
       public                 postgres    false    221            A           2606    17158    tags tags_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (tag_id);
 8   ALTER TABLE ONLY public.tags DROP CONSTRAINT tags_pkey;
       public                 postgres    false    219            ?           2606    17151    users users_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_login);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public                 postgres    false    217            J           2606    17205    folders folders_newsid_fkey    FK CONSTRAINT     }   ALTER TABLE ONLY public.folders
    ADD CONSTRAINT folders_newsid_fkey FOREIGN KEY (newsid) REFERENCES public.news(news_id);
 E   ALTER TABLE ONLY public.folders DROP CONSTRAINT folders_newsid_fkey;
       public               postgres    false    225    228    4677            K           2606    17200    folders folders_userlog_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.folders
    ADD CONSTRAINT folders_userlog_fkey FOREIGN KEY (userlog) REFERENCES public.users(user_login);
 F   ALTER TABLE ONLY public.folders DROP CONSTRAINT folders_userlog_fkey;
       public               postgres    false    217    4671    228            H           2606    17186    news news_sourceid_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.news
    ADD CONSTRAINT news_sourceid_fkey FOREIGN KEY (sourceid) REFERENCES public.sources(source_id);
 A   ALTER TABLE ONLY public.news DROP CONSTRAINT news_sourceid_fkey;
       public               postgres    false    221    225    4675            I           2606    17181    news news_tagid_fkey    FK CONSTRAINT     t   ALTER TABLE ONLY public.news
    ADD CONSTRAINT news_tagid_fkey FOREIGN KEY (tagid) REFERENCES public.tags(tag_id);
 >   ALTER TABLE ONLY public.news DROP CONSTRAINT news_tagid_fkey;
       public               postgres    false    4673    225    219            �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �     