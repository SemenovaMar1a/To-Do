from fastapi import HTTPException
from schemas.users import Role


def user_verification_error(current_user, user_id):
    if not current_user or (current_user.role != Role.ADMIN and current_user.id != user_id):
        raise HTTPException(status_code=404, detail="Пользователь не найден или нет доступа")
    
def task_verification_error(task, current_user):
    if not task or (current_user.role != Role.ADMIN and task.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Задача не найдена или нет доступа")