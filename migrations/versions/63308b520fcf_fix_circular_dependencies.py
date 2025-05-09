"""Fix circular dependencies

Revision ID: 63308b520fcf
Revises: 78ada2174bdd
Create Date: 2025-03-18 20:11:11.696282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '63308b520fcf'
down_revision: Union[str, None] = '78ada2174bdd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_appointments_id', table_name='appointments')
    op.drop_table('appointments')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('users_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('hashed_password', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('full_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('phone_number', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('role', postgresql.ENUM('PATIENT', 'DOCTOR', 'ADMIN', 'patient', name='roleenum'), autoincrement=False, nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('registration_number', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_table('appointments',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('patient_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('doctor_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('scheduled_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('status', postgresql.ENUM('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED', name='appointmentstatusenum'), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], name='appointments_doctor_id_fkey'),
    sa.ForeignKeyConstraint(['patient_id'], ['users.id'], name='appointments_patient_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='appointments_pkey')
    )
    op.create_index('ix_appointments_id', 'appointments', ['id'], unique=False)
    # ### end Alembic commands ###
