create table public.download_codes (
  code_hash   text primary key,          -- SHA-256 des normalisierten Codes, nie der Code selbst
  label       text,                      -- optional, z. B. "Code 07", kein Name
  redeemed_at timestamptz,
  device_id   text
);
alter table public.download_codes enable row level security;
-- keine Policies: Browser (anon Schlüssel) kann die Tabelle weder lesen noch schreiben

-- Einlösen in einem einzigen Schritt, damit zwei gleichzeitige Versuche nicht beide durchgehen
create or replace function public.redeem_code(p_hash text, p_device text)
returns text language plpgsql security definer set search_path = public as $$
declare r public.download_codes;
begin
  update public.download_codes
     set redeemed_at = coalesce(redeemed_at, now()),
         device_id   = coalesce(device_id, p_device)
   where code_hash = p_hash
     and (redeemed_at is null
          or (device_id = p_device and redeemed_at > now() - interval '1 hour'))
  returning * into r;
  if found then return 'ok'; end if;
  if exists (select 1 from public.download_codes where code_hash = p_hash) then return 'used'; end if;
  return 'invalid';
end $$;
revoke all on function public.redeem_code(text, text) from public, anon, authenticated;
grant execute on function public.redeem_code(text, text) to service_role;
