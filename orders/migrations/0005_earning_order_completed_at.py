from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_alter_order_order_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='earning',
            name='order',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='earning', to='orders.order'),
        ),
        migrations.AddField(
            model_name='earning',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
