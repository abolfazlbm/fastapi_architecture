from celery.backends.database.session import SessionManager as CelerySessionManager


class SessionManager(CelerySessionManager):
    """
    Rewrite celery SessionManager
    """

    def __init__(self) -> None:
        super().__init__()

        # Disable automatic creation of task result tables defined internally by celery
        self.prepared = True
