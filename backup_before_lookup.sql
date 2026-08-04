--
-- PostgreSQL database dump
--

\restrict VGwmUzqnK7DDwFhqZDkvGMPd6AaafJchsR8qufe0DMurQJm14wBtXZVeon2FD0V

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

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
-- Name: allocationmethod; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.allocationmethod AS ENUM (
    'direct',
    'machine_hour',
    'labor_hour',
    'production_qty',
    'area',
    'manual'
);


ALTER TYPE public.allocationmethod OWNER TO postgres;

--
-- Name: costbehavior; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.costbehavior AS ENUM (
    'fixed',
    'variable',
    'semi_variable',
    'step'
);


ALTER TYPE public.costbehavior OWNER TO postgres;

--
-- Name: costcategory; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.costcategory AS ENUM (
    'direct',
    'indirect',
    'fixed',
    'variable'
);


ALTER TYPE public.costcategory OWNER TO postgres;

--
-- Name: coststatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.coststatus AS ENUM (
    'active',
    'inactive',
    'archived'
);


ALTER TYPE public.coststatus OWNER TO postgres;

--
-- Name: costunit; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.costunit AS ENUM (
    'rial',
    'dollar',
    'euro',
    'percent',
    'hour',
    'unit'
);


ALTER TYPE public.costunit OWNER TO postgres;

--
-- Name: customer_status_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.customer_status_enum AS ENUM (
    'ACTIVE',
    'INACTIVE'
);


ALTER TYPE public.customer_status_enum OWNER TO postgres;

--
-- Name: customer_type_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.customer_type_enum AS ENUM (
    'REAL',
    'LEGAL'
);


ALTER TYPE public.customer_type_enum OWNER TO postgres;

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
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    user_id integer,
    username character varying(50),
    action character varying(50) NOT NULL,
    entity_type character varying(50),
    entity_id integer,
    details text,
    ip_address character varying(45),
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: cost_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cost_types (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(100) NOT NULL,
    category public.costcategory NOT NULL,
    cost_behavior public.costbehavior NOT NULL,
    unit public.costunit NOT NULL,
    default_amount numeric(18,2),
    allocation_method public.allocationmethod NOT NULL,
    account_code character varying(30),
    taxable boolean DEFAULT false NOT NULL,
    parent_id integer,
    description text,
    status public.coststatus DEFAULT 'active'::public.coststatus NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.cost_types OWNER TO postgres;

--
-- Name: cost_types_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cost_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cost_types_id_seq OWNER TO postgres;

--
-- Name: cost_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cost_types_id_seq OWNED BY public.cost_types.id;


--
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
    name character varying(100) NOT NULL,
    trade_name character varying(100),
    customer_type public.customer_type_enum NOT NULL,
    status public.customer_status_enum NOT NULL,
    contact_name character varying(100),
    contact_title character varying(50),
    contact_mobile character varying(20),
    phone character varying(20),
    mobile character varying(20),
    email character varying(100),
    address text,
    postal_code character varying(20),
    national_id character varying(20),
    notes text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.customers OWNER TO postgres;

--
-- Name: COLUMN customers.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.name IS 'نام شرکت';


--
-- Name: COLUMN customers.trade_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.trade_name IS 'نام تجاری';


--
-- Name: COLUMN customers.customer_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.customer_type IS 'نوع مشتری';


--
-- Name: COLUMN customers.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.status IS 'وضعیت';


--
-- Name: COLUMN customers.contact_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.contact_name IS 'نام شخص رابط';


--
-- Name: COLUMN customers.contact_title; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.contact_title IS 'سمت رابط';


--
-- Name: COLUMN customers.contact_mobile; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.contact_mobile IS 'موبایل رابط';


--
-- Name: COLUMN customers.phone; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.phone IS 'تلفن ثابت';


--
-- Name: COLUMN customers.mobile; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.mobile IS 'موبایل';


--
-- Name: COLUMN customers.email; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.email IS 'ایمیل';


--
-- Name: COLUMN customers.address; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.address IS 'آدرس کامل';


--
-- Name: COLUMN customers.postal_code; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.postal_code IS 'کدپستی';


--
-- Name: COLUMN customers.national_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.national_id IS 'شناسه ملی';


--
-- Name: COLUMN customers.notes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.notes IS 'توضیحات';


--
-- Name: customers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customers_id_seq OWNER TO postgres;

--
-- Name: customers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customers_id_seq OWNED BY public.customers.id;


--
-- Name: suppliers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.suppliers (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(200) NOT NULL,
    trade_name character varying(200),
    supplier_types json NOT NULL,
    subcategories json NOT NULL,
    specialty_description text,
    tier character varying(2) NOT NULL,
    status character varying(20) NOT NULL,
    cooperation_start date,
    contact_name character varying(150),
    contact_position character varying(100),
    mobile character varying(20),
    phone character varying(20),
    email character varying(150),
    website character varying(200),
    province character varying(50),
    city character varying(50),
    office_address text,
    factory_address text,
    national_id character varying(20),
    account_number character varying(50),
    bank_name character varying(100),
    payment_terms character varying(20),
    credit_days integer,
    credit_limit numeric(18,2),
    currency character varying(3) NOT NULL,
    has_active_contract boolean NOT NULL,
    contract_start date,
    contract_end date,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.suppliers OWNER TO postgres;

--
-- Name: suppliers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.suppliers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.suppliers_id_seq OWNER TO postgres;

--
-- Name: suppliers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.suppliers_id_seq OWNED BY public.suppliers.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    username character varying(50) NOT NULL,
    full_name character varying(100) NOT NULL,
    email character varying(100),
    password_hash character varying(255) NOT NULL,
    role character varying(20) NOT NULL,
    is_active boolean NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: cost_types id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_types ALTER COLUMN id SET DEFAULT nextval('public.cost_types_id_seq'::regclass);


--
-- Name: customers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers ALTER COLUMN id SET DEFAULT nextval('public.customers_id_seq'::regclass);


--
-- Name: suppliers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers ALTER COLUMN id SET DEFAULT nextval('public.suppliers_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
60450842d0e5
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_logs (user_id, username, action, entity_type, entity_id, details, ip_address, "timestamp", id) FROM stdin;
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 13:10:47.197166+03:30	3
1	admin	LOGOUT	\N	\N	خروج	\N	2026-08-03 13:10:47.394694+03:30	4
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 13:12:16.197937+03:30	5
\N	nobody	LOGIN_FAILED	\N	\N	ورود ناموفق: کاربر یافت نشد	\N	2026-08-03 13:12:16.204334+03:30	6
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 13:12:16.405693+03:30	7
1	admin	LOGOUT	\N	\N	خروج	\N	2026-08-03 13:12:16.407683+03:30	8
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 13:16:22.523492+03:30	9
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 13:16:27.478558+03:30	10
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 14:52:23.212936+03:30	11
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 14:57:47.521004+03:30	12
1	admin	LOGOUT	\N	\N	خروج	\N	2026-08-03 14:58:02.478901+03:30	13
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 14:58:33.04731+03:30	14
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 14:58:39.895091+03:30	15
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 15:08:17.460874+03:30	16
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 15:30:57.41351+03:30	17
1	admin	LOGOUT	\N	\N	خروج	\N	2026-08-03 15:43:07.983064+03:30	18
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 15:45:54.410099+03:30	19
1	admin	LOGOUT	\N	\N	خروج	\N	2026-08-03 15:46:43.135168+03:30	20
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 15:51:21.707134+03:30	21
1	admin	LOGOUT	\N	\N	خروج	\N	2026-08-03 15:51:25.606486+03:30	22
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 15:51:52.668807+03:30	23
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 15:51:58.066235+03:30	24
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 15:52:01.82903+03:30	25
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 18:36:21.176896+03:30	26
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 18:43:17.352296+03:30	27
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 18:43:22.253782+03:30	28
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 18:43:26.315564+03:30	29
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 18:45:33.069661+03:30	30
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 18:52:25.677517+03:30	31
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 19:03:52.561657+03:30	32
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 19:44:21.896409+03:30	33
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 20:07:29.443005+03:30	34
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 20:08:33.50314+03:30	35
1	admin	LOGOUT	\N	\N	خروج	\N	2026-08-03 20:09:35.294903+03:30	36
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 20:11:37.620995+03:30	37
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 20:25:03.863543+03:30	38
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 20:25:10.855006+03:30	39
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 20:34:18.503127+03:30	40
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 20:34:22.474826+03:30	41
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 20:40:33.022834+03:30	42
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 20:43:35.119442+03:30	43
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 20:44:40.020063+03:30	44
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 20:47:02.873617+03:30	45
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 20:49:21.323+03:30	46
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 20:49:25.462513+03:30	47
\N	Admin	LOGIN_FAILED	\N	\N	ورود ناموفق: کاربر یافت نشد	\N	2026-08-03 20:51:56.504699+03:30	48
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 20:52:05.056493+03:30	49
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 20:52:10.221229+03:30	50
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 20:55:03.946487+03:30	51
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 20:57:33.324566+03:30	52
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 21:05:16.39644+03:30	53
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 21:08:01.140978+03:30	54
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 21:10:55.330227+03:30	55
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 21:13:43.065503+03:30	56
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 21:18:05.099582+03:30	57
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 21:20:16.520859+03:30	58
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 21:21:21.330803+03:30	59
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 21:23:57.964584+03:30	60
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 21:24:02.753959+03:30	61
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 21:41:15.938346+03:30	62
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 21:41:19.554136+03:30	63
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 21:44:25.372802+03:30	64
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 21:46:45.424652+03:30	65
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 21:50:19.626235+03:30	66
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 21:55:46.335357+03:30	67
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 21:55:53.097801+03:30	68
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 21:55:58.059171+03:30	69
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 22:16:16.898223+03:30	70
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 22:16:20.805037+03:30	71
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 22:18:50.769566+03:30	72
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 22:35:53.432441+03:30	73
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 22:35:57.070163+03:30	74
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-03 23:26:18.086287+03:30	75
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-03 23:26:22.597131+03:30	76
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-04 00:08:00.604687+03:30	77
\N	admin	LOGIN_FAILED	\N	\N	ورود ناموفق: پسورد اشتباه	\N	2026-08-04 00:12:58.655768+03:30	78
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-04 00:13:12.425088+03:30	79
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-04 00:15:53.961716+03:30	80
1	admin	LOGIN_SUCCESS	\N	\N	ورود موفق	\N	2026-08-04 00:28:37.0978+03:30	81
\.


--
-- Data for Name: cost_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cost_types (id, code, name, category, cost_behavior, unit, default_amount, allocation_method, account_code, taxable, parent_id, description, status, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customers (name, trade_name, customer_type, status, contact_name, contact_title, contact_mobile, phone, mobile, email, address, postal_code, national_id, notes, id, created_at, updated_at) FROM stdin;
رحمتی	\N	REAL	ACTIVE	\N	\N	\N	\N	\N	\N	\N	\N	0946974667	\N	1	2026-08-03 20:13:16.506521+03:30	2026-08-03 21:44:30.190593+03:30
\.


--
-- Data for Name: suppliers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.suppliers (id, code, name, trade_name, supplier_types, subcategories, specialty_description, tier, status, cooperation_start, contact_name, contact_position, mobile, phone, email, website, province, city, office_address, factory_address, national_id, account_number, bank_name, payment_terms, credit_days, credit_limit, currency, has_active_contract, contract_start, contract_end, description, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (username, full_name, email, password_hash, role, is_active, id, created_at, updated_at) FROM stdin;
admin	مدیر سیستم	admin@localhost	$2b$12$udLbIaYzgbMrc2tPfSW/KeL5YhLUqjih./kYtzIqHZMtTqzOjt/SC	admin	t	1	2026-08-03 13:05:14.209687+03:30	2026-08-03 13:05:14.209687+03:30
\.


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 81, true);


--
-- Name: cost_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cost_types_id_seq', 1, false);


--
-- Name: customers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customers_id_seq', 1, true);


--
-- Name: suppliers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.suppliers_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: cost_types cost_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_types
    ADD CONSTRAINT cost_types_pkey PRIMARY KEY (id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: suppliers suppliers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_audit_logs_action; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_action ON public.audit_logs USING btree (action);


--
-- Name: ix_audit_logs_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_timestamp ON public.audit_logs USING btree ("timestamp");


--
-- Name: ix_audit_logs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_user_id ON public.audit_logs USING btree (user_id);


--
-- Name: ix_cost_types_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_cost_types_code ON public.cost_types USING btree (code);


--
-- Name: ix_cost_types_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_types_name ON public.cost_types USING btree (name);


--
-- Name: ix_suppliers_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_suppliers_code ON public.suppliers USING btree (code);


--
-- Name: ix_suppliers_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suppliers_name ON public.suppliers USING btree (name);


--
-- Name: ix_suppliers_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suppliers_status ON public.suppliers USING btree (status);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: cost_types cost_types_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_types
    ADD CONSTRAINT cost_types_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.cost_types(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict VGwmUzqnK7DDwFhqZDkvGMPd6AaafJchsR8qufe0DMurQJm14wBtXZVeon2FD0V

