from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                (
                    'priority',
                    models.CharField(
                        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                        default='medium',
                        max_length=10,
                    ),
                ),
                (
                    'category',
                    models.CharField(
                        blank=True,
                        help_text='Optional grouping, e.g. "Work" or "Groceries".',
                        max_length=60,
                    ),
                ),
                ('due_date', models.DateField(blank=True, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['completed', 'due_date', '-created_at'],
                'indexes': [
                    models.Index(fields=['completed'], name='list_item_complet_3f7a1c_idx'),
                    models.Index(fields=['due_date'], name='list_item_due_dat_5b2e94_idx'),
                    models.Index(fields=['priority'], name='list_item_priorit_a1d8f0_idx'),
                ],
            },
        ),
    ]
