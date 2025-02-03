from django.db import migrations
from django.utils import timezone

def create_initial_articles(apps, schema_editor):
    # Get the model from the versioned app registry
    Article = apps.get_model('api', 'Article')
    
    articles_data = [
        {
            'title': 'Getting Started with Our Store',
            'content': 'Welcome to our online store! This guide will help you navigate through our products and features...',
            'author': 'Store Admin',
        },
        {
            'title': 'Shipping & Returns Policy',
            'content': 'We offer free shipping on all orders over $50. Returns are accepted within 30 days of purchase...',
            'author': 'Customer Service Team',
        },
        {
            'title': 'Latest Fashion Trends 2025',
            'content': 'Discover the hottest fashion trends for 2025. From sustainable materials to smart clothing...',
            'author': 'Fashion Editor',
        },
    ]
    
    for article_data in articles_data:
        Article.objects.create(**article_data)

def remove_articles(apps, schema_editor):
    # Allows the migration to be reversed
    Article = apps.get_model('api', 'Article')
    Article.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0004_supportticket_ticketresponse'),  # This should match your last migration number
    ]

    operations = [
        migrations.RunPython(create_initial_articles, remove_articles),
    ]