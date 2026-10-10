from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for the ported Module-3 (goals -> roadmaps) models.

    Kept separate from the main app's Base so that module-3 model class names
    (Goal, Task, Career, CareerMatch, WeeklyCheckin, ...) never collide with the
    app's existing models in SQLAlchemy's class registry. The only app-backend
    link is an indexed m3_students.user_id column (identity enforced at the app
    layer via ensure_m3_student).
    """