--
-- PostgreSQL database dump
--

\restrict yohlc23CfBa5XlHXe9TdIpsVbeabDnE1HKpwreC6Pxx9W7vh2bYy41f9LybXu2a

-- Dumped from database version 16.10 (Homebrew)
-- Dumped by pg_dump version 16.10 (Homebrew)

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
-- Name: application_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.application_status AS ENUM (
    'PENDING',
    'SHORTLISTED',
    'APPROVED',
    'REJECTED',
    'WITHDRAWN'
);


ALTER TYPE public.application_status OWNER TO postgres;

--
-- Name: campaign_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.campaign_status AS ENUM (
    'DRAFT',
    'ACTIVE',
    'PAUSED',
    'COMPLETED',
    'ARCHIVED'
);


ALTER TYPE public.campaign_status OWNER TO postgres;

--
-- Name: order_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.order_status AS ENUM (
    'IN_PROGRESS',
    'DELIVERED',
    'APPROVED',
    'REVISION',
    'CANCELLED'
);


ALTER TYPE public.order_status OWNER TO postgres;

--
-- Name: payment_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.payment_status AS ENUM (
    'PENDING',
    'COMPLETED',
    'FAILED',
    'REFUNDED'
);


ALTER TYPE public.payment_status OWNER TO postgres;

--
-- Name: payment_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.payment_type AS ENUM (
    'HOLD',
    'RELEASE',
    'PAYOUT'
);


ALTER TYPE public.payment_type OWNER TO postgres;

--
-- Name: report_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.report_type AS ENUM (
    'AGENT_SUMMARY',
    'FACTORY_STATUS',
    'QUALITY_REVIEW',
    'ANALYTICS'
);


ALTER TYPE public.report_type OWNER TO postgres;

--
-- Name: user_role; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.user_role AS ENUM (
    'BRAND',
    'CREATOR',
    'AGENT',
    'FACTORY',
    'ADMIN',
    'VIEWER'
);


ALTER TYPE public.user_role OWNER TO postgres;

--
-- Name: video_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.video_status AS ENUM (
    'SUBMITTED',
    'APPROVED',
    'REVISION',
    'REJECTED'
);


ALTER TYPE public.video_status OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: applications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.applications (
    id uuid NOT NULL,
    campaign_id uuid NOT NULL,
    creator_id uuid NOT NULL,
    status public.application_status NOT NULL,
    pitch text,
    proposed_budget numeric(12,2),
    message text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.applications OWNER TO postgres;

--
-- Name: campaigns; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.campaigns (
    id uuid NOT NULL,
    brand_id uuid NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    brief text,
    budget numeric(12,2) NOT NULL,
    currency character varying(8) NOT NULL,
    status public.campaign_status NOT NULL,
    start_date date,
    end_date date,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT campaign_budget_positive CHECK ((budget >= (0)::numeric))
);


ALTER TABLE public.campaigns OWNER TO postgres;

--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    id uuid NOT NULL,
    application_id uuid NOT NULL,
    campaign_id uuid NOT NULL,
    creator_id uuid NOT NULL,
    brand_id uuid NOT NULL,
    status public.order_status NOT NULL,
    agreed_budget numeric(12,2),
    deliverables text,
    delivery_due timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    id uuid NOT NULL,
    order_id uuid NOT NULL,
    payment_type public.payment_type NOT NULL,
    status public.payment_status NOT NULL,
    amount numeric(12,2) NOT NULL,
    currency character varying(8) NOT NULL,
    reference character varying(120),
    processed_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- Name: ratings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ratings (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    score numeric(3,2) NOT NULL,
    source character varying(50) NOT NULL,
    comment text,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.ratings OWNER TO postgres;

--
-- Name: reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reports (
    id uuid NOT NULL,
    author_id uuid,
    campaign_id uuid,
    order_id uuid,
    report_type public.report_type NOT NULL,
    content text NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.reports OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    email character varying(255) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    full_name character varying(255),
    role public.user_role NOT NULL,
    bio character varying(1000),
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: videos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.videos (
    id uuid NOT NULL,
    order_id uuid NOT NULL,
    storage_url character varying(500) NOT NULL,
    thumbnail_url character varying(500),
    status public.video_status NOT NULL,
    notes text,
    submitted_at timestamp without time zone DEFAULT now() NOT NULL,
    approved_at timestamp without time zone
);


ALTER TABLE public.videos OWNER TO postgres;

--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: applications applications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_pkey PRIMARY KEY (id);


--
-- Name: campaigns campaigns_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.campaigns
    ADD CONSTRAINT campaigns_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: payments payments_reference_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_reference_key UNIQUE (reference);


--
-- Name: ratings ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_pkey PRIMARY KEY (id);


--
-- Name: reports reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_pkey PRIMARY KEY (id);


--
-- Name: applications uq_application_campaign_creator; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT uq_application_campaign_creator UNIQUE (campaign_id, creator_id);


--
-- Name: orders uq_order_application; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT uq_order_application UNIQUE (application_id);


--
-- Name: ratings uq_rating_user_source; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT uq_rating_user_source UNIQUE (user_id, source);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: videos videos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos
    ADD CONSTRAINT videos_pkey PRIMARY KEY (id);


--
-- Name: ix_applications_campaign_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_applications_campaign_id ON public.applications USING btree (campaign_id);


--
-- Name: ix_applications_creator_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_applications_creator_id ON public.applications USING btree (creator_id);


--
-- Name: ix_campaigns_brand_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_campaigns_brand_id ON public.campaigns USING btree (brand_id);


--
-- Name: ix_orders_application_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_orders_application_id ON public.orders USING btree (application_id);


--
-- Name: ix_payments_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_order_id ON public.payments USING btree (order_id);


--
-- Name: ix_ratings_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ratings_user_id ON public.ratings USING btree (user_id);


--
-- Name: ix_reports_author_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reports_author_id ON public.reports USING btree (author_id);


--
-- Name: ix_reports_campaign_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reports_campaign_id ON public.reports USING btree (campaign_id);


--
-- Name: ix_reports_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reports_order_id ON public.reports USING btree (order_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_videos_order_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_videos_order_id ON public.videos USING btree (order_id);


--
-- Name: applications applications_campaign_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES public.campaigns(id) ON DELETE CASCADE;


--
-- Name: applications applications_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: campaigns campaigns_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.campaigns
    ADD CONSTRAINT campaigns_brand_id_fkey FOREIGN KEY (brand_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: orders orders_application_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_application_id_fkey FOREIGN KEY (application_id) REFERENCES public.applications(id) ON DELETE CASCADE;


--
-- Name: orders orders_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_brand_id_fkey FOREIGN KEY (brand_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: orders orders_campaign_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES public.campaigns(id) ON DELETE CASCADE;


--
-- Name: orders orders_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: payments payments_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: ratings ratings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: reports reports_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: reports reports_campaign_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES public.campaigns(id) ON DELETE CASCADE;


--
-- Name: reports reports_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: videos videos_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.videos
    ADD CONSTRAINT videos_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict yohlc23CfBa5XlHXe9TdIpsVbeabDnE1HKpwreC6Pxx9W7vh2bYy41f9LybXu2a

