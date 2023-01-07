--
-- PostgreSQL database dump
--

-- Dumped from database version 15.1 (Debian 15.1-1.pgdg110+1)
-- Dumped by pg_dump version 15.1 (Debian 15.1-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: antrag; Type: TABLE; Schema: public; Owner: abv
--

CREATE TABLE public.antrag (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    sitzung uuid NOT NULL,
    typ uuid NOT NULL,
    beschluss text
);


ALTER TABLE public.antrag OWNER TO abv;

--
-- Name: antragstyp; Type: TABLE; Schema: public; Owner: abv
--

CREATE TABLE public.antragstyp (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(200) NOT NULL,
    form json NOT NULL
);


ALTER TABLE public.antragstyp OWNER TO abv;

--
-- Name: referat; Type: TABLE; Schema: public; Owner: abv
--

CREATE TABLE public.referat (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(200) NOT NULL,
    zyklus interval
);


ALTER TABLE public.referat OWNER TO abv;

--
-- Name: sitzung; Type: TABLE; Schema: public; Owner: abv
--

CREATE TABLE public.sitzung (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    date date DEFAULT now() NOT NULL,
    referat uuid NOT NULL
);


ALTER TABLE public.sitzung OWNER TO abv;

--
-- Data for Name: antrag; Type: TABLE DATA; Schema: public; Owner: abv
--

COPY public.antrag (id, sitzung, typ, beschluss) FROM stdin;
\.


--
-- Data for Name: antragstyp; Type: TABLE DATA; Schema: public; Owner: abv
--

COPY public.antragstyp (id, name, form) FROM stdin;
\.


--
-- Data for Name: referat; Type: TABLE DATA; Schema: public; Owner: abv
--

COPY public.referat (id, name, zyklus) FROM stdin;
\.


--
-- Data for Name: sitzung; Type: TABLE DATA; Schema: public; Owner: abv
--

COPY public.sitzung (id, date, referat) FROM stdin;
\.


--
-- Name: antrag antrag_pk; Type: CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.antrag
    ADD CONSTRAINT antrag_pk PRIMARY KEY (id);


--
-- Name: antragstyp antragstyp_pk; Type: CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.antragstyp
    ADD CONSTRAINT antragstyp_pk PRIMARY KEY (id);


--
-- Name: referat referat_pk; Type: CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.referat
    ADD CONSTRAINT referat_pk PRIMARY KEY (id);


--
-- Name: sitzung sitzung_pk; Type: CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.sitzung
    ADD CONSTRAINT sitzung_pk PRIMARY KEY (id);


--
-- Name: antragstyp_name_index; Type: INDEX; Schema: public; Owner: abv
--

CREATE INDEX antragstyp_name_index ON public.antragstyp USING btree (name);


--
-- Name: referat_name_index; Type: INDEX; Schema: public; Owner: abv
--

CREATE INDEX referat_name_index ON public.referat USING btree (name);


--
-- Name: antrag antrag_antragstyp_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.antrag
    ADD CONSTRAINT antrag_antragstyp_id_fk FOREIGN KEY (typ) REFERENCES public.antragstyp(id);


--
-- Name: antrag antrag_sitzung_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.antrag
    ADD CONSTRAINT antrag_sitzung_id_fk FOREIGN KEY (sitzung) REFERENCES public.sitzung(id);


--
-- Name: sitzung sitzung_referat_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.sitzung
    ADD CONSTRAINT sitzung_referat_id_fk FOREIGN KEY (referat) REFERENCES public.referat(id);


--
-- PostgreSQL database dump complete
--

