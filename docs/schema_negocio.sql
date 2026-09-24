BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;


DO $$ BEGIN
    CREATE TYPE model_status AS ENUM ('APPROVED', 'REJECTED', 'UNDER_ANALYSIS');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


DO $$ BEGIN
    CREATE TYPE supplier_status AS ENUM ('ACTIVE', 'SUSPENDED', 'DEACTIVATED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


DO $$ BEGIN
    CREATE TYPE proposal_status AS ENUM ('OPEN', 'IN_NEGOTIATION', 'ACCEPTED', 'REJECTED', 'CANCELED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


DO $$ BEGIN
    CREATE TYPE subscription_status AS ENUM ('PAID', 'IN_DEBT', 'SUSPENDED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


DO $$ BEGIN
    CREATE TYPE service_status AS ENUM ('OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


DO $$ BEGIN
    CREATE TYPE plan_cycle AS ENUM ('MONTHLY', 'WEEKLY', 'YEARLY');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


DO $$ BEGIN
    CREATE TYPE location_type AS ENUM ('BUILDING', 'HOUSE', 'COMPLEX');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


DO $$ BEGIN
    CREATE TYPE technical_affiliation_type AS ENUM ('INDEPENDENT', 'AFFILIATED', 'PARTNER');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


DO $$ BEGIN
    CREATE TYPE payment_method AS ENUM ('PIX', 'BOLETO', 'CREDIT_CARD', 'TRANSFER');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


DO $$ BEGIN
    CREATE TYPE billing_status AS ENUM ('PENDING', 'PAID', 'CANCELED', 'REFUNDED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


CREATE TABLE IF NOT EXISTS users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    avatar text
);


CREATE TABLE IF NOT EXISTS contact (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email varchar(100),
    phone varchar(12)
);


CREATE TABLE IF NOT EXISTS business_contact (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_email varchar(100) NOT NULL,
    phone varchar(12),
    website text
);


CREATE TABLE IF NOT EXISTS address (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    state varchar(2) NOT NULL,
    city text NOT NULL,
    neighborhood text,
    zip_code varchar(8) NOT NULL,
    street text NOT NULL,
    number varchar(10)
);


CREATE TABLE IF NOT EXISTS geolocalization (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_address uuid,
    latitude numeric(10, 7),
    longitude numeric(10, 7),
    CONSTRAINT fk_geolocalization_address
        FOREIGN KEY (fk_address) REFERENCES address(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS person (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_users uuid,
    fk_contact uuid,
    name varchar(60) NOT NULL,
    cpf varchar(11) NOT NULL UNIQUE,
    birth_date date NOT NULL,
    CONSTRAINT fk_person_user
        FOREIGN KEY (fk_users) REFERENCES users(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_person_contact
        FOREIGN KEY (fk_contact) REFERENCES contact(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS company (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_address uuid NOT NULL,
    fk_business_contact uuid NOT NULL,
    cnpj varchar(14) NOT NULL UNIQUE,
    trade_name varchar(120) NOT NULL,
    corporate_name varchar(120) NOT NULL,
    CONSTRAINT fk_company_address
        FOREIGN KEY (fk_address) REFERENCES address(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_company_business_contact
        FOREIGN KEY (fk_business_contact) REFERENCES business_contact(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS supplier (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_company uuid NOT NULL,
    status supplier_status NOT NULL DEFAULT 'ACTIVE',
    business_type varchar(40),
    CONSTRAINT fk_supplier_company
        FOREIGN KEY (fk_company) REFERENCES company(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS requester (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_company uuid NOT NULL,
    business_type varchar(40),
    CONSTRAINT fk_requester_company
        FOREIGN KEY (fk_company) REFERENCES company(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS technical_company (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_company uuid NOT NULL,
    CONSTRAINT fk_technical_company_company
        FOREIGN KEY (fk_company) REFERENCES company(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS position (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar(12) NOT NULL,
    accesses text NOT NULL
);


CREATE TABLE IF NOT EXISTS company_positions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_company uuid NOT NULL,
    fk_position uuid NOT NULL,
    CONSTRAINT uq_company_positions_company_position UNIQUE (fk_company, fk_position),
    CONSTRAINT fk_company_positions_company
        FOREIGN KEY (fk_company) REFERENCES company(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_company_positions_position
        FOREIGN KEY (fk_position) REFERENCES position(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS user_company (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_company uuid NOT NULL,
    fk_users uuid NOT NULL,
    fk_position uuid NOT NULL,
    CONSTRAINT fk_user_company_company
        FOREIGN KEY (fk_company) REFERENCES company(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_user_company_user
        FOREIGN KEY (fk_users) REFERENCES users(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_user_company_position
        FOREIGN KEY (fk_position) REFERENCES position(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS permission (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    permission_name VARCHAR(100) NOT NULL UNIQUE
);


CREATE TABLE IF NOT EXISTS position_permission (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_position UUID NOT NULL,
    id_permission UUID NOT NULL,
    CONSTRAINT uq_position_permission UNIQUE (id_position, id_permission),
    CONSTRAINT fk_position FOREIGN KEY (id_position) REFERENCES position(id) ON DELETE CASCADE,
    CONSTRAINT fk_permission FOREIGN KEY (id_permission) REFERENCES permission(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS company_plans (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    value numeric(12, 2) NOT NULL,
    cycle plan_cycle NOT NULL
);


CREATE TABLE IF NOT EXISTS subscription (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_supplier uuid NOT NULL,
    fk_plan uuid NOT NULL,
    status subscription_status NOT NULL DEFAULT 'PAID',
    auto_renewal boolean NOT NULL DEFAULT true,
    start_date timestamptz NOT NULL,
    end_date timestamptz,
    CONSTRAINT fk_subscription_supplier
        FOREIGN KEY (fk_supplier) REFERENCES supplier(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_subscription_plan
        FOREIGN KEY (fk_plan) REFERENCES company_plans(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS charge (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_subscription uuid NOT NULL,
    amount numeric(12, 2) NOT NULL,
    payment_method payment_method NOT NULL,
    status billing_status NOT NULL DEFAULT 'PENDING',
    payment_date timestamptz,
    CONSTRAINT fk_charge_subscription
        FOREIGN KEY (fk_subscription) REFERENCES subscription(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS model (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    brand text NOT NULL,
    model text NOT NULL,
    power_wp numeric(7, 2) NOT NULL,
    efficiency numeric(5, 2) NOT NULL CHECK (efficiency BETWEEN 0 AND 100),
    dimension numeric(8, 3) NOT NULL,
    weight numeric(6, 2) NOT NULL,
    status model_status NOT NULL DEFAULT 'UNDER_ANALYSIS'
);


CREATE TABLE IF NOT EXISTS inventory (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_supplier uuid NOT NULL,
    fk_model uuid NOT NULL,
    quantity integer NOT NULL CHECK (quantity >= 0),
    CONSTRAINT uq_inventory_supplier_model UNIQUE (fk_supplier, fk_model),
    CONSTRAINT fk_inventory_supplier
        FOREIGN KEY (fk_supplier) REFERENCES supplier(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_inventory_model
        FOREIGN KEY (fk_model) REFERENCES model(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS offer (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_supplier uuid NOT NULL,
    fk_model uuid NOT NULL,
    unit_price numeric(12, 2) NOT NULL CHECK (unit_price >= 0),
    availability integer NOT NULL CHECK (availability >= 0),
    expiration_date date,
    CONSTRAINT fk_offer_supplier
        FOREIGN KEY (fk_supplier) REFERENCES supplier(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_offer_model
        FOREIGN KEY (fk_model) REFERENCES model(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS local_unit (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_requester uuid NOT NULL,
    fk_address uuid NOT NULL,
    complement text,
    location_type location_type NOT NULL,
    CONSTRAINT fk_local_unit_requester
        FOREIGN KEY (fk_requester) REFERENCES requester(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_local_unit_address
        FOREIGN KEY (fk_address) REFERENCES address(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS unit_specifications (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_local_unit uuid NOT NULL,
    specifications text,
    location_photos text,
    date timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fk_unit_specifications_local_unit
        FOREIGN KEY (fk_local_unit) REFERENCES local_unit(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS energy_bill (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_local_unit uuid NOT NULL,
    consumption numeric NOT NULL CHECK (consumption >= 0),
    price numeric(12, 2) NOT NULL CHECK (price >= 0),
    CONSTRAINT fk_energy_bill_local_unit
        FOREIGN KEY (fk_local_unit) REFERENCES local_unit(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS proposal (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_requester uuid NOT NULL,
    status proposal_status NOT NULL DEFAULT 'OPEN',
    notes text,
    total_amount numeric(12, 2),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz,
    CONSTRAINT fk_proposal_requester
        FOREIGN KEY (fk_requester) REFERENCES requester(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS proposal_item (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_proposal uuid NOT NULL,
    fk_offer uuid NOT NULL,
    quantity integer NOT NULL CHECK (quantity >= 0),
    negotiated_price numeric(12, 2) CHECK (negotiated_price >= 0),
    discount numeric,
    CONSTRAINT fk_proposal_item_proposal
        FOREIGN KEY (fk_proposal) REFERENCES proposal(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_proposal_item_offer
        FOREIGN KEY (fk_offer) REFERENCES offer(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS proposal_unit (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_proposal_item uuid NOT NULL,
    fk_local_unit uuid NOT NULL,
    quantity integer NOT NULL CHECK (quantity >= 0),
    note text,
    CONSTRAINT fk_proposal_unit_item
        FOREIGN KEY (fk_proposal_item) REFERENCES proposal_item(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_proposal_unit_local
        FOREIGN KEY (fk_local_unit) REFERENCES local_unit(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS technician (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_person uuid NOT NULL UNIQUE,
    CONSTRAINT fk_technician_person
        FOREIGN KEY (fk_person) REFERENCES person(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS technician_affiliation (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_company uuid NOT NULL,
    fk_technician uuid NOT NULL,
    affiliation_type technical_affiliation_type NOT NULL,
    CONSTRAINT uq_technician_affiliation_company_technician UNIQUE (fk_company, fk_technician),
    CONSTRAINT fk_technician_affiliation_company
        FOREIGN KEY (fk_company) REFERENCES company(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_technician_affiliation_technician
        FOREIGN KEY (fk_technician) REFERENCES technician(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS profession (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar(100) NOT NULL UNIQUE,
    requires_registration boolean NOT NULL
);


CREATE TABLE IF NOT EXISTS professional_registration (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_technician uuid NOT NULL,
    fk_profession uuid NOT NULL,
    council varchar(60) NOT NULL,
    number varchar(30) NOT NULL,
    expiration_date date NOT NULL,
    CONSTRAINT fk_professional_registration_technician
        FOREIGN KEY (fk_technician) REFERENCES technician(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_professional_registration_profession
        FOREIGN KEY (fk_profession) REFERENCES profession(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS certification (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_technician uuid NOT NULL,
    type varchar(255) NOT NULL,
    information text NOT NULL,
    image text,
    CONSTRAINT fk_certification_technician
        FOREIGN KEY (fk_technician) REFERENCES technician(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS technical_course (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_company uuid,
    title varchar(30) NOT NULL,
    information text,
    link text,
    CONSTRAINT fk_technical_course_company
        FOREIGN KEY (fk_company) REFERENCES company(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS technical_project (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_requester uuid NOT NULL,
    fk_local_unit uuid NOT NULL,
    status service_status NOT NULL DEFAULT 'OPEN',
    start_date timestamptz NOT NULL DEFAULT now(),
    end_date timestamptz,
    CONSTRAINT fk_technical_project_requester
        FOREIGN KEY (fk_requester) REFERENCES requester(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_technical_project_local_unit
        FOREIGN KEY (fk_local_unit) REFERENCES local_unit(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS technical_service (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_technical_project uuid NOT NULL,
    purpose text NOT NULL,
    status service_status NOT NULL DEFAULT 'OPEN',
    created_at timestamptz NOT NULL,
    end_date timestamptz,
    CONSTRAINT fk_technical_service_technical_project
        FOREIGN KEY (fk_technical_project) REFERENCES technical_project(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS service_executor (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_service uuid NOT NULL,
    fk_technician_affiliation uuid NOT NULL,
    function text NOT NULL,
    CONSTRAINT fk_service_executor_service
        FOREIGN KEY (fk_service) REFERENCES technical_service(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT fk_service_executor_technician_affiliation
        FOREIGN KEY (fk_technician_affiliation) REFERENCES technician_affiliation(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE IF NOT EXISTS service_contract (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    fk_service uuid NOT NULL UNIQUE,
    warranty text,
    delivery_deadline date,
    insurance boolean NOT NULL DEFAULT false,
    utility_approval boolean NOT NULL DEFAULT false,
    CONSTRAINT fk_service_contract_service
        FOREIGN KEY (fk_service) REFERENCES technical_service(id)
        ON UPDATE NO ACTION ON DELETE NO ACTION
);


DO $$ BEGIN
    CREATE TYPE audit_operation AS ENUM ('INSERT', 'UPDATE', 'DELETE');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
 
CREATE TABLE IF NOT EXISTS audit_log (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name text NOT NULL,
    operation audit_operation NOT NULL,
    row_id uuid NOT NULL,
    old_data jsonb,
    new_data jsonb,
    changed_by uuid,
    changed_at timestamptz NOT NULL DEFAULT now()
);
 

CREATE INDEX IF NOT EXISTS idx_audit_log_table_row ON audit_log (table_name, row_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_changed_at ON audit_log (changed_at);
 

CREATE OR REPLACE FUNCTION fn_current_app_user()
RETURNS uuid
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_user_id text;
BEGIN
    v_user_id := current_setting('app.current_user_id', true);
 
    IF v_user_id IS NULL OR v_user_id = '' THEN
        RETURN NULL;
    END IF;
 
    RETURN v_user_id::uuid;
EXCEPTION WHEN others THEN
    RETURN NULL;
END;
$$;


CREATE OR REPLACE FUNCTION fn_audit_trigger()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_row_id uuid;
BEGIN
    IF TG_OP = 'DELETE' THEN
        v_row_id := OLD.id;
    ELSE
        v_row_id := NEW.id;
    END IF;
 
    IF TG_OP = 'UPDATE' AND to_jsonb(OLD) = to_jsonb(NEW) THEN
        RETURN NEW;
    END IF;
 
    INSERT INTO audit_log (table_name, operation, row_id, old_data, new_data, changed_by)
    VALUES (
        TG_TABLE_NAME,
        TG_OP::audit_operation,
        v_row_id,
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END,
        fn_current_app_user()
    );
 
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$;


DO $$
DECLARE
    tbl record;
BEGIN
    FOR tbl IN
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
          AND table_name NOT IN ('audit_log')
    LOOP
        EXECUTE format(
            'DROP TRIGGER IF EXISTS trg_audit_%1$s ON %1$I;
             CREATE TRIGGER trg_audit_%1$s
             AFTER INSERT OR UPDATE OR DELETE ON %1$I
             FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();',
            tbl.table_name
        );
    END LOOP;
END $$;
 

CREATE OR REPLACE PROCEDURE sp_purge_audit_log(retention_days integer DEFAULT 365)
LANGUAGE plpgsql
AS $$
BEGIN
    IF retention_days <= 0 THEN
        RAISE EXCEPTION 'retention_days deve ser maior que zero, recebido: %', retention_days;
    END IF;
 
    DELETE FROM audit_log
    WHERE changed_at < now() - (retention_days || ' days')::interval;
 
    RAISE NOTICE 'audit_log: entradas com mais de % dias foram removidas.', retention_days;
END;
$$;


COMMIT;
