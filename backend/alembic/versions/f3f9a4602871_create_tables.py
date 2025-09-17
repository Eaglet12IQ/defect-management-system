"""Create tables

Revision ID: f3f9a4602871
Revises: 
Create Date: 2025-09-17 15:59:15.623499
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.core.security import get_password_hash  # Импортируем функцию хеширования

# revision identifiers, used by Alembic.
revision: str = 'f3f9a4602871'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Инициализация CryptContext для хэширования пароля
admin_password = get_password_hash("admin123")  # Хешируем пароль

def upgrade() -> None:
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Enum('Инженер', 'Менеджер', 'Руководитель', 'Суперадмин', name='role_name', native_enum=False), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)

    # Insert initial roles
    op.bulk_insert(
        sa.table('roles', sa.column('id', sa.Integer), sa.column('name', sa.String)),
        [
            {'id': 1, 'name': 'ENGINEER'},
            {'id': 2, 'name': 'MANAGER'},
            {'id': 3, 'name': 'LEADER'},
            {'id': 4, 'name': 'SUPERADMIN'},
        ]
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Insert superadmin user
    op.bulk_insert(
        sa.table(
            'users',
            sa.column('id', sa.Integer),
            sa.column('email', sa.String),
            sa.column('username', sa.String),
            sa.column('hashed_password', sa.String),
            sa.column('role_id', sa.Integer)
        ),
        [
            {
                'id': 1,
                'email': 'superadmin@example.com',
                'username': 'superadmin',
                'hashed_password': admin_password,
                'role_id': 4  # Links to Суперадмин role
            }
        ]
    )

    # Create profiles table
    op.create_table(
        'profiles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('avatar_url', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=True),
        sa.Column('last_name', sa.String(length=50), nullable=True),
        sa.Column('middle_name', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )

    # Insert superadmin profile
    op.bulk_insert(
        sa.table(
            'profiles',
            sa.column('user_id', sa.Integer),
            sa.column('avatar_url', sa.String),
            sa.column('first_name', sa.String),
            sa.column('last_name', sa.String),
            sa.column('middle_name', sa.String)
        ),
        [
            {
                'user_id': 1,
                'avatar_url': '/static/avatars/default_avatar.png',
                'first_name': 'Admin',
                'last_name': 'Super',
                'middle_name': None
            }
        ]
    )

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('manager_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['manager_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_manager_id'), 'projects', ['manager_id'], unique=False)
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)

    # Create defects table
    op.create_table(
        'defects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('priority', sa.Enum('Низкий', 'Средний', 'Высокий', 'Критический', name='defect_priority', native_enum=False), nullable=False),
        sa.Column('status', sa.Enum('Новая', 'В работе', 'На проверке', 'Закрыта', 'Отменена', name='defect_status', native_enum=False), nullable=False),
        sa.Column('assignee', sa.String(length=255), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_defects_creator_id'), 'defects', ['creator_id'], unique=False)
    op.create_index(op.f('ix_defects_id'), 'defects', ['id'], unique=False)
    op.create_index(op.f('ix_defects_project_id'), 'defects', ['project_id'], unique=False)
    op.create_index(op.f('ix_defects_title'), 'defects', ['title'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_defects_title'), table_name='defects')
    op.drop_index(op.f('ix_defects_project_id'), table_name='defects')
    op.drop_index(op.f('ix_defects_id'), table_name='defects')
    op.drop_index(op.f('ix_defects_creator_id'), table_name='defects')
    op.drop_table('defects')
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_index(op.f('ix_projects_manager_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    op.drop_table('profiles')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')