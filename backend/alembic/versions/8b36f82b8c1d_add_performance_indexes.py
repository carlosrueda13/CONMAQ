"""add_performance_indexes

Revision ID: 8b36f82b8c1d
Revises: 7a25e71a7f05
Create Date: 2025-12-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b36f82b8c1d'
down_revision: Union[str, None] = '7a25e71a7f05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Composite index for availability searches
    op.create_index(
        'ix_availabilityslot_machine_time',
        'availabilityslot',
        ['machine_id', 'start_time', 'end_time'],
        unique=False
    )
    
    # Indexes for status filtering (used in metrics and dashboards)
    op.create_index(
        'ix_booking_status',
        'booking',
        ['status'],
        unique=False
    )
    
    op.create_index(
        'ix_transaction_status',
        'transaction',
        ['status'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_transaction_status', table_name='transaction')
    op.drop_index('ix_booking_status', table_name='booking')
    op.drop_index('ix_availabilityslot_machine_time', table_name='availabilityslot')
