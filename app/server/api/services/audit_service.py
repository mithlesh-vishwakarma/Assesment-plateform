from api.models import AuditLog, IntegrityEvent

class AuditService:
    @staticmethod
    def log(actor, action, target_model="", target_id="", details=None, request=None):
        """
        Records an audit log entry for security and regulatory tracking.
        """
        ip = None
        ua = ""
        if request:
            ip = request.META.get('REMOTE_ADDR')
            ua = request.META.get('HTTP_USER_AGENT', '')

        return AuditLog.objects.create(
            actor=actor if (actor and actor.is_authenticated) else None,
            action=action,
            target_model=target_model,
            target_id=str(target_id),
            ip_address=ip,
            user_agent=ua,
            details=details or {},
        )

    @staticmethod
    def record_integrity_event(candidate, stage_attempt, event_type, metadata=None):
        """
        Records candidate proctoring / integrity anomalies (e.g. tab switches, blur, copy/paste).
        """
        return IntegrityEvent.objects.create(
            stage_attempt=stage_attempt,
            candidate=candidate,
            event_type=event_type,
            metadata=metadata or {},
        )
