"""empty message

Revision ID: 441176dff2f
Revises: None
Create Date: 2015-10-04 11:41:07.888768

"""

# revision identifiers, used by Alembic.
revision = '441176dff2f'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=True),
    sa.PrimaryKeyConstraint('_id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('users',
    sa.Column('_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=30), nullable=True),
    sa.Column('email', sa.String(length=30), nullable=True),
    sa.Column('created_on', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_on', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('_password', sa.String(length=64), nullable=True),
    sa.Column('authenticated', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('_id')
    )
    op.create_table('bookmarks',
    sa.Column('_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=50), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('created_on', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_on', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories._id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users._id'], ),
    sa.PrimaryKeyConstraint('_id'),
    sa.UniqueConstraint('url')
    )
    op.create_table('votes',
    sa.Column('_id', sa.Integer(), nullable=False),
    sa.Column('direction', sa.Boolean(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('bookmark_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['bookmark_id'], ['bookmarks._id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users._id'], ),
    sa.PrimaryKeyConstraint('_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('votes')
    op.drop_table('bookmarks')
    op.drop_table('users')
    op.drop_table('categories')
    ### end Alembic commands ###