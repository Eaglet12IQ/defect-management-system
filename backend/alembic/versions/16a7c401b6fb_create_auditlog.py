"""Create auditlog

Revision ID: 16a7c401b6fb
Revises: f3f9a4602871
Create Date: 2025-09-17 16:32:13.285260
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '16a7c401b6fb'
down_revision: Union[str, None] = 'f3f9a4602871'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('table_name', sa.String(length=100), nullable=False),
        sa.Column('record_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('old_data', sa.JSON(), nullable=True),
        sa.Column('new_data', sa.JSON(), nullable=True),
        sa.Column('changed_fields', sa.JSON(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('comment', sa.String(length=1000), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_table_name'), 'audit_logs', ['table_name'], unique=False)
    op.create_index(op.f('ix_audit_logs_record_id'), 'audit_logs', ['record_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_timestamp'), 'audit_logs', ['timestamp'], unique=False)

    # Create audit trigger function
    op.execute("""
    CREATE OR REPLACE FUNCTION audit_trigger_function()
    RETURNS TRIGGER AS $$
    DECLARE
        old_row JSONB;
        new_row JSONB;
        changed_fields JSONB := '[]'::jsonb;
        action_type TEXT;
        table_name_ru TEXT;
    BEGIN
        -- Determine action type
        IF TG_OP = 'INSERT' THEN
            action_type := 'INSERT';
            old_row := NULL;
            new_row := row_to_json(NEW)::JSONB;
        ELSIF TG_OP = 'UPDATE' THEN
            action_type := 'UPDATE';
            old_row := row_to_json(OLD)::JSONB;
            new_row := row_to_json(NEW)::JSONB;

            -- Calculate changed fields
            SELECT jsonb_object_keys(new_row - old_row) INTO changed_fields;
        ELSIF TG_OP = 'DELETE' THEN
            action_type := 'DELETE';
            old_row := row_to_json(OLD)::JSONB;
            new_row := NULL;
        END IF;

        -- Translate table name to Russian
        table_name_ru := CASE 
            WHEN TG_TABLE_NAME = 'users' THEN 'пользователи'
            WHEN TG_TABLE_NAME = 'defects' THEN 'дефекты'
            WHEN TG_TABLE_NAME = 'projects' THEN 'проекты'
            WHEN TG_TABLE_NAME = 'profiles' THEN 'профили'
            WHEN TG_TABLE_NAME = 'roles' THEN 'роли'
            WHEN TG_TABLE_NAME = 'reports' THEN 'отчеты'
            ELSE TG_TABLE_NAME
        END;

        -- Insert audit log entry
        INSERT INTO audit_logs (
            table_name,
            record_id,
            action,
            old_data,
            new_data,
            changed_fields,
            user_id,
            comment
        ) VALUES (
            TG_TABLE_NAME,
            COALESCE(NEW.id, OLD.id),
            action_type,
            old_row,
            new_row,
            CASE WHEN action_type = 'UPDATE' THEN changed_fields ELSE NULL END,
            NULL, -- user_id will be set by application when possible
            CASE 
                WHEN action_type = 'INSERT' THEN 'ВСТАВКА' 
                WHEN action_type = 'UPDATE' THEN 'ОБНОВЛЕНИЕ' 
                WHEN action_type = 'DELETE' THEN 'УДАЛЕНИЕ' 
            END || ' в ' || table_name_ru
        );

        -- Return appropriate row based on operation
        IF TG_OP = 'DELETE' THEN
            RETURN OLD;
        ELSE
            RETURN NEW;
        END IF;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Create triggers for main tables
    tables_to_audit = ['users', 'defects', 'projects', 'profiles', 'roles', 'reports']

    for table_name in tables_to_audit:
        op.execute(f"""
        CREATE TRIGGER audit_trigger_{table_name}
            AFTER INSERT OR UPDATE OR DELETE ON {table_name}
            FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
        """)

def downgrade() -> None:
    # Drop triggers
    tables_to_audit = ['users', 'defects', 'projects', 'profiles', 'roles', 'reports']

    for table_name in tables_to_audit:
        op.execute(f"DROP TRIGGER IF EXISTS audit_trigger_{table_name} ON {table_name};")

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS audit_trigger_function();")

    # Drop indexes and table
    op.drop_index(op.f('ix_audit_logs_timestamp'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_record_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_table_name'), table_name='audit_logs')
    op.drop_table('audit_logs')