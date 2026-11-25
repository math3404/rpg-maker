-- Diagnostico somente leitura para conferir a tabela public.integrantes.
-- Execute depois de supabase_integrantes.sql no SQL Editor do Supabase.

-- 1) Estrutura da tabela.
select column_name, data_type, is_nullable, column_default
from information_schema.columns
where table_schema = 'public'
  and table_name = 'integrantes'
order by ordinal_position;

-- 2) RLS ativado?
select n.nspname as schema_name,
       c.relname as table_name,
       c.relrowsecurity as rls_enabled,
       c.relforcerowsecurity as rls_forced
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'public'
  and c.relname = 'integrantes';

-- 3) Quantidade de integrantes cadastrados.
select count(*) as total_integrantes
from public.integrantes;
