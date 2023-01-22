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
    antrag_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    sitz_id uuid NOT NULL,
    typ_id uuid NOT NULL,
    antrag_text text NOT NULL,
    asteller_id uuid NOT NULL,
    antrag_summe money
);


ALTER TABLE public.antrag OWNER TO abv;

--
-- Name: antragssteller; Type: TABLE; Schema: public; Owner: abv
--

CREATE TABLE public.antragssteller (
    asteller_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    asteller_name character varying(50) NOT NULL,
    asteller_vorname character varying(50) NOT NULL
);


ALTER TABLE public.antragssteller OWNER TO abv;

--
-- Name: antragstyp; Type: TABLE; Schema: public; Owner: abv
--

CREATE TABLE public.antragstyp (
    typ_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    typ_name character varying(200) NOT NULL,
    form json NOT NULL
);


ALTER TABLE public.antragstyp OWNER TO abv;

--
-- Name: beschluesse; Type: TABLE; Schema: public; Owner: abv
--

CREATE TABLE public.beschluesse (
    antrag_id uuid NOT NULL,
    sitz_id uuid NOT NULL,
    sitz_berechtigung integer,
    beschluss text
);


ALTER TABLE public.beschluesse OWNER TO abv;

--
-- Name: referat; Type: TABLE; Schema: public; Owner: abv
--

CREATE TABLE public.referat (
    ref_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    ref_name character varying(200) NOT NULL,
    zyklus integer
);


ALTER TABLE public.referat OWNER TO abv;

--
-- Name: sitzung; Type: TABLE; Schema: public; Owner: abv
--

CREATE TABLE public.sitzung (
    sitz_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    sitz_date date DEFAULT now() NOT NULL,
    ref_id uuid NOT NULL
);


ALTER TABLE public.sitzung OWNER TO abv;

--
-- Data for Name: antrag; Type: TABLE DATA; Schema: public; Owner: abv
--


ALTER TABLE ONLY public.antrag
    ADD CONSTRAINT antrag_pk PRIMARY KEY (antrag_id);


--
-- Name: antragssteller antragssteller_pk; Type: CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.antragssteller
    ADD CONSTRAINT antragssteller_pk PRIMARY KEY (asteller_id);


--
-- Name: antragstyp antragstyp_pk; Type: CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.antragstyp
    ADD CONSTRAINT antragstyp_pk PRIMARY KEY (typ_id);


--
-- Name: beschluesse beschluesse_pk; Type: CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.beschluesse
    ADD CONSTRAINT beschluesse_pk PRIMARY KEY (antrag_id, sitz_id);


--
-- Name: referat referat_pk; Type: CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.referat
    ADD CONSTRAINT referat_pk PRIMARY KEY (ref_id);


--
-- Name: sitzung sitzung_pk; Type: CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.sitzung
    ADD CONSTRAINT sitzung_pk PRIMARY KEY (sitz_id);


--
-- Name: antragstyp_name_index; Type: INDEX; Schema: public; Owner: abv
--

CREATE INDEX antragstyp_name_index ON public.antragstyp USING btree (typ_name);


--
-- Name: referat_name_index; Type: INDEX; Schema: public; Owner: abv
--

CREATE INDEX referat_name_index ON public.referat USING btree (ref_name);


--
-- Name: antrag antrag_antragstyp_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.antrag
    ADD CONSTRAINT antrag_antragstyp_id_fk FOREIGN KEY (typ_id) REFERENCES public.antragstyp(typ_id);


--
-- Name: antrag antrag_asteller; Type: FK CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.antrag
    ADD CONSTRAINT antrag_asteller FOREIGN KEY (asteller_id) REFERENCES public.antragssteller(asteller_id);


--
-- Name: beschluesse antrag_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.beschluesse
    ADD CONSTRAINT antrag_id_fk FOREIGN KEY (antrag_id) REFERENCES public.antrag(antrag_id);


--
-- Name: antrag antrag_sitzung_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.antrag
    ADD CONSTRAINT antrag_sitzung_id_fk FOREIGN KEY (sitz_id) REFERENCES public.sitzung(sitz_id);


--
-- Name: beschluesse sitzung_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.beschluesse
    ADD CONSTRAINT sitzung_id_fk FOREIGN KEY (sitz_id) REFERENCES public.sitzung(sitz_id);


--
-- Name: sitzung sitzung_referat_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: abv
--

ALTER TABLE ONLY public.sitzung
    ADD CONSTRAINT sitzung_referat_id_fk FOREIGN KEY (ref_id) REFERENCES public.referat(ref_id);


--
-- PostgreSQL database dump complete
--

