-- Row locks exigem UPDATE; esta fronteira evita conceder UPDATE em app_users
-- ao runtime. SQL estatico, dados minimos e search_path imutavel.
CREATE FUNCTION public.web_lock_emitter(p_issuer text, p_subject text)
RETURNS TABLE(active boolean, role text)
LANGUAGE sql VOLATILE SECURITY DEFINER
SET search_path = pg_catalog, public
AS $function$
    SELECT u.active, u.role
    FROM public.app_users AS u
    WHERE u.issuer = p_issuer AND u.subject = p_subject
    FOR SHARE OF u
$function$;
REVOKE ALL ON FUNCTION public.web_lock_emitter(text, text) FROM PUBLIC;
