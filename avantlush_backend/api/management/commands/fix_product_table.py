# avantlush_backend/api/management/commands/fix_product_table.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix product table by adding main_image column if missing'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            if connection.vendor == 'sqlite':
                # SQLite implementation
                cursor.execute("""
                    SELECT sql FROM sqlite_master 
                    WHERE type='table' AND name='api_product';
                """)
                create_table_sql = cursor.fetchone()[0]
                column_exists = 'main_image' in create_table_sql
            else:
                # PostgreSQL implementation
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'api_product' 
                    AND column_name = 'main_image';
                """)
                column_exists = cursor.fetchone() is not None

            if not column_exists:
                try:
                    cursor.execute("""
                        ALTER TABLE api_product 
                        ADD COLUMN main_image varchar(100) NULL;
                    """)
                    self.stdout.write(self.style.SUCCESS('Successfully added main_image column'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error adding column: {str(e)}'))
            else:
                self.stdout.write(self.style.SUCCESS('main_image column already exists'))