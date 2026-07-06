-- Tabla principal para almacenar licitaciones OCDS
-- Ejecuta esto en el SQL Editor de Supabase

CREATE TABLE IF NOT EXISTS licitaciones (
    id BIGSERIAL PRIMARY KEY,
    ocid TEXT UNIQUE NOT NULL,
    tender_title TEXT,
    tender_description TEXT,
    tender_status TEXT,
    tender_value_amount NUMERIC,
    tender_value_currency TEXT,
    buyer_name TEXT,
    buyer_id TEXT,
    procurement_method TEXT,
    procurement_method_details TEXT,
    tender_period_start TIMESTAMPTZ,
    tender_period_end TIMESTAMPTZ,
    number_of_tenderers INTEGER,
    date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices útiles
CREATE INDEX IF NOT EXISTS idx_licitaciones_ocid ON licitaciones(ocid);
CREATE INDEX IF NOT EXISTS idx_licitaciones_status ON licitaciones(tender_status);
CREATE INDEX IF NOT EXISTS idx_licitaciones_buyer ON licitaciones(buyer_name);
CREATE INDEX IF NOT EXISTS idx_licitaciones_value ON licitaciones(tender_value_amount);

-- Habilitar RLS (Row Level Security) - recomendado
ALTER TABLE licitaciones ENABLE ROW LEVEL SECURITY;

-- Ejemplo de policy (ajusta según tus necesidades)
-- CREATE POLICY "Enable read access for all users" ON licitaciones FOR SELECT USING (true);

COMMENT ON TABLE licitaciones IS 'Licitaciones públicas procesadas desde OCDS del OECE';
