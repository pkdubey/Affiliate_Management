from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('invoicing', '0008_invoice_bank_account_name_and_more'),
    ]
    operations = [
        migrations.CreateModel(
            name='InvoiceLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_description', models.CharField(max_length=200, default='Service')),
                ('hsn_sac', models.CharField(max_length=20, blank=True, null=True)),
                ('quantity', models.DecimalField(max_digits=10, decimal_places=2, default=1)),
                ('rate', models.DecimalField(max_digits=10, decimal_places=2, default=0)),
                ('amount', models.DecimalField(max_digits=12, decimal_places=2, default=0)),
                ('cgst_rate', models.DecimalField(max_digits=5, decimal_places=2, default=9.00)),
                ('sgst_rate', models.DecimalField(max_digits=5, decimal_places=2, default=9.00)),
                ('cgst_amount', models.DecimalField(max_digits=12, decimal_places=2, default=0)),
                ('sgst_amount', models.DecimalField(max_digits=12, decimal_places=2, default=0)),
                ('sort_order', models.IntegerField(default=1)),
                ('invoice', models.ForeignKey(on_delete=models.CASCADE, related_name='lines', to='invoicing.Invoice')),
            ],
            options={'ordering': ['sort_order','id']},
        ),
    ]
