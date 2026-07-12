# Migração escrita à mão: adiciona o dono da operação como FK não nula.
# Segura porque a tabela de operações está vazia neste ponto do projeto;
# em uma base com dados seria preciso um default/backfill em duas etapas.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portfolio", "0002_cotacao_fechamento_anterior"),
    ]

    operations = [
        migrations.AddField(
            model_name="operacao",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="operacoes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
