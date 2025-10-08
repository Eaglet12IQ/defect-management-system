from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.profile import Profile
from app.models.user import User
from app.core.security import get_payload_from_refresh_token
from app.models.auditlog import AuditLog
from app.models.project import Project
from app.models.defect import Defect, DefectStatusEnum

router = APIRouter()

@router.get("/dashboard")
async def dashboard(response: Response, request: Request, db: Session = Depends(get_db)):
    payload = get_payload_from_refresh_token(request)
    access_user_id = payload.get("sub")
    role_id = payload.get("role")

    data = {}

    profile = Profile.get_profile(db, access_user_id)
    fio_parts = [profile.last_name, profile.first_name]
    if profile.middle_name:
        fio_parts.append(profile.middle_name)
    data["fio"] = " ".join(fio_parts)

    # Fetch audit log activities based on role

    activities = []

    if role_id == 2:  # (Manager)
        # Get projects managed by user
        projects = db.query(Project).filter(Project.manager_id == access_user_id).all()
        project_ids = [p.id for p in projects]

        # Get defects related to these projects
        defects = db.query(Defect).filter(Defect.project_id.in_(project_ids)).all()
        defect_ids = [d.id for d in defects]

        # Get audit logs related to these defects or projects
        activities = db.query(AuditLog).filter(
            ((AuditLog.table_name == 'defects') & (AuditLog.record_id.in_(defect_ids))) |
            ((AuditLog.table_name == 'projects') & (AuditLog.record_id.in_(project_ids)))
        ).order_by(AuditLog.timestamp.desc()).limit(10).all()

    elif role_id == 1:  # Инженер (Engineer)
        # Get defects assigned to user
        defects = db.query(Defect).filter(Defect.creator_id == str(access_user_id)).all()
        defect_ids = [d.id for d in defects]

        # Get audit logs related to these defects
        activities = db.query(AuditLog).filter(
            (AuditLog.table_name == 'defects') & (AuditLog.record_id.in_(defect_ids))
        ).order_by(AuditLog.timestamp.desc()).limit(10).all()

    elif role_id == 3:  # Руководитель (Leader)
        # Get audit logs for all projects and defects
        activities = db.query(AuditLog).filter(
            (AuditLog.table_name == 'projects') | (AuditLog.table_name == 'defects')
        ).order_by(AuditLog.timestamp.desc()).limit(20).all()
    else:  # Others
        # Get all audit logs
        activities = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10).all()

    # Format activities for frontend
    def format_changes(activity):
        if not activity.changed_fields or not activity.old_data or not activity.new_data:
            return "Нет данных об изменениях"
        # Translation dict for field names
        field_translations = {
            'name': 'Название',
            'description': 'Описание',
            'status': 'Статус',
            'manager_id': 'Менеджер',
            'title': 'Заголовок',
            'assignee': 'Исполнитель',
            'due_date': 'Срок выполенниея',
            'priority': 'Приоритет',
            'creator_id': 'Создатель',
            'project_id': 'Проект',
            'attachments': 'Вложения'
        }
        def format_value(value, field):
            if value is None:
                return 'не указано'
            if field == 'status':
                status_translations = {
                    'NEW': 'Новый',
                    'IN_PROGRESS': 'В работе',
                    'UNDER_REVIEW': 'На проверке',
                    'CLOSED': 'Закрыт',
                    'CANCELED': 'Отменен'
                }
                return status_translations.get(str(value), str(value))
            if field == 'due_date':
                if value:
                    from datetime import datetime
                    if isinstance(value, str):
                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    return value.strftime('%d.%m.%Y')
                return 'не указано'
            if field == 'attachments' and isinstance(value, list):
                return ', '.join([v.split('/')[-1] for v in value])
            return str(value)

        changes = []
        for field in activity.changed_fields:
            translated_field = field_translations.get(field, field)
            old_val = format_value(activity.old_data.get(field), field)
            new_val = format_value(activity.new_data.get(field), field)
            changes.append(f"<span style='font-size:14px;'>{translated_field}:</span> <span style='color:#dc143c; font-size:14px;'>{old_val}</span> → <span style='color:#00ff00; font-size:14px;'>{new_val}</span>")
        return "<br>".join(changes)

    def translate_action(action, table_name, record_id):
        action_translations = {
            'INSERT': 'Создание',
            'UPDATE': 'Обновление',
            'DELETE': 'Удаление'
        }
        table_translations = {
            'projects': 'Проект',
            'defects': 'Дефект'
        }
        translated_action = action_translations.get(action.upper(), action)
        translated_table = table_translations.get(table_name, table_name)
        return f"{translated_action} | {translated_table} {record_id}"

    data["team_activity"] = [
        {
            "id": a.id,
            "table_name": a.table_name,
            "record_id": a.record_id,
            "action": translate_action(a.action, a.table_name, a.record_id),
            "changes_detail": format_changes(a),
            "timestamp": a.timestamp.isoformat()
        }
        for a in activities
    ]

    # Fetch recent defects
    if role_id == 1:
        defects_query = db.query(Defect).filter(Defect.status == 'В работе')
        data["recent_defects"] = []
        for defect in defects_query:
            project = db.query(Project).filter(Project.id == defect.project_id).first()
            creator = db.query(User).filter(User.id == defect.creator_id).first()

            data["recent_defects"].append({
                "id": defect.id,
                "title": defect.title,
                "description": defect.description,
                "status": defect.status.value,
                "priority": defect.priority.value,
                "assignee": defect.assignee,
                "due_date": defect.due_date.date().isoformat() if defect.due_date else None,
                "attachments": ["http://localhost:8000/" + path['path'] if isinstance(path, dict) else "http://localhost:8000/" + path for path in (defect.attachments or [])],
                "project_id": defect.project_id,
                "project_name": project.name if project else "Неизвестно",
                "creator_id": defect.creator_id,
                "creator_name": f"{creator.profile.first_name} {creator.profile.last_name}" if creator and creator.profile else "Неизвестно",
                "location": project.name if project else "Неизвестно"
            })
    elif role_id == 2:
        # For managers, separate defects into two blocks: "Новые" and "На проверке"
        new_defects_query = db.query(Defect).filter(Defect.status == 'Новый')
        under_review_defects_query = db.query(Defect).filter(Defect.status == 'На проверке')

        data["new_defects"] = []
        for defect in new_defects_query:
            project = db.query(Project).filter(Project.id == defect.project_id).first()
            creator = db.query(User).filter(User.id == defect.creator_id).first()

            data["new_defects"].append({
                "id": defect.id,
                "title": defect.title,
                "description": defect.description,
                "status": defect.status.value,
                "priority": defect.priority.value,
                "assignee": defect.assignee,
                "due_date": defect.due_date.date().isoformat() if defect.due_date else None,
                "attachments": ["http://localhost:8000/" + path['path'] if isinstance(path, dict) else "http://localhost:8000/" + path for path in (defect.attachments or [])],
                "project_id": defect.project_id,
                "project_name": project.name if project else "Неизвестно",
                "creator_id": defect.creator_id,
                "creator_name": f"{creator.profile.first_name} {creator.profile.last_name}" if creator and creator.profile else "Неизвестно",
                "location": project.name if project else "Неизвестно"
            })

        data["under_review_defects"] = []
        for defect in under_review_defects_query:
            project = db.query(Project).filter(Project.id == defect.project_id).first()
            creator = db.query(User).filter(User.id == defect.creator_id).first()

            data["under_review_defects"].append({
                "id": defect.id,
                "title": defect.title,
                "description": defect.description,
                "status": defect.status.value,
                "priority": defect.priority.value,
                "assignee": defect.assignee,
                "due_date": defect.due_date.date().isoformat() if defect.due_date else None,
                "attachments": ["http://localhost:8000/" + path['path'] if isinstance(path, dict) else "http://localhost:8000/" + path for path in (defect.attachments or [])],
                "project_id": defect.project_id,
                "project_name": project.name if project else "Неизвестно",
                "creator_id": defect.creator_id,
                "creator_name": f"{creator.profile.first_name} {creator.profile.last_name}" if creator and creator.profile else "Неизвестно",
                "location": project.name if project else "Неизвестно"
            })
    elif role_id == 3:  # Руководитель (Leader)
        # Get chart data for defects
        from sqlalchemy import func

        # Defect status distribution
        defect_status_counts = db.query(
            Defect.status,
            func.count(Defect.id).label('count')
        ).group_by(Defect.status).all()

        data["defect_status_chart"] = [
            {"status": status.value, "count": count}
            for status, count in defect_status_counts
        ]

        # Defect priority distribution
        defect_priority_counts = db.query(
            Defect.priority,
            func.count(Defect.id).label('count')
        ).group_by(Defect.priority).all()

        data["defect_priority_chart"] = [
            {"priority": priority.value, "count": count}
            for priority, count in defect_priority_counts
        ]

        # Project status distribution
        project_status_counts = db.query(
            Project.status,
            func.count(Project.id).label('count')
        ).group_by(Project.status).all()

        data["project_status_chart"] = [
            {"status": status.value, "count": count}
            for status, count in project_status_counts
        ]
    else:
        defects_query = db.query(Defect)
        data["recent_defects"] = []
        for defect in defects_query:
            project = db.query(Project).filter(Project.id == defect.project_id).first()
            creator = db.query(User).filter(User.id == defect.creator_id).first()

            data["recent_defects"].append({
                "id": defect.id,
                "title": defect.title,
                "description": defect.description,
                "status": defect.status.value,
                "priority": defect.priority.value,
                "assignee": defect.assignee,
                "due_date": defect.due_date.date().isoformat() if defect.due_date else None,
                "attachments": ["http://localhost:8000/" + path['path'] if isinstance(path, dict) else "http://localhost:8000/" + path for path in (defect.attachments or [])],
                "project_id": defect.project_id,
                "project_name": project.name if project else "Неизвестно",
                "creator_id": defect.creator_id,
                "creator_name": f"{creator.profile.first_name} {creator.profile.last_name}" if creator and creator.profile else "Неизвестно",
                "location": project.name if project else "Неизвестно"
            })

    return data
