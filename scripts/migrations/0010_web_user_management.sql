-- Administracao WEB sem conceder DML de app_users ao papel de runtime.
-- Operacoes fechadas, ator revalidado e protecao do ultimo admin na mesma transacao.
CREATE FUNCTION public.web_manage_user(
    p_operation text, p_actor_issuer text, p_actor_subject text,
    p_issuer text, p_subject text, p_role text, p_email text, p_active boolean
)
RETURNS text
LANGUAGE plpgsql VOLATILE SECURITY DEFINER
SET search_path = pg_catalog, public
AS $function$
BEGIN
    IF p_operation IS NULL OR p_operation NOT IN ('create', 'update') THEN
        RETURN 'forbidden';
    END IF;
    LOCK TABLE public.app_users IN SHARE ROW EXCLUSIVE MODE;
    IF NOT EXISTS (
        SELECT 1 FROM public.app_users
        WHERE issuer = p_actor_issuer AND subject = p_actor_subject
          AND active AND role = 'administracao'
    ) THEN
        RETURN 'forbidden';
    END IF;
    IF p_operation = 'create' THEN
        INSERT INTO public.app_users
            (issuer, subject, role, email, created_by_issuer, created_by_subject)
        VALUES (p_issuer, p_subject, p_role, p_email, p_actor_issuer, p_actor_subject);
    ELSE
        IF NOT EXISTS (
            SELECT 1 FROM public.app_users WHERE issuer = p_issuer AND subject = p_subject
        ) THEN
            RETURN 'missing';
        END IF;
        IF (p_role <> 'administracao' OR NOT p_active) AND NOT EXISTS (
            SELECT 1 FROM public.app_users
            WHERE active AND role = 'administracao'
              AND NOT (issuer = p_issuer AND subject = p_subject)
        ) THEN
            RETURN 'last_admin';
        END IF;
        UPDATE public.app_users
        SET role = p_role, email = p_email, active = p_active,
            updated_at = CURRENT_TIMESTAMP
        WHERE issuer = p_issuer AND subject = p_subject;
    END IF;
    INSERT INTO public.auth_audit_events
        (issuer, subject, action, outcome, request_id)
    VALUES (p_actor_issuer, p_actor_subject, 'manage_users', 'success', gen_random_uuid());
    RETURN CASE WHEN p_operation = 'create' THEN 'created' ELSE 'updated' END;
END
$function$;
REVOKE ALL ON FUNCTION public.web_manage_user(text,text,text,text,text,text,text,boolean) FROM PUBLIC;
