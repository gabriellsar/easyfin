<script lang="ts">
  import type { ResumoCarteira } from '../api/carteira'
  import { fmtBRL, fmtPct, fmtPctAbs } from '../utils/format'

  let {
    resumo,
    periodo = null,
  }: { resumo: ResumoCarteira | null; periodo?: string | null } = $props()

  let diaPositivo = $derived(resumo ? Number(resumo.resultado_dia) >= 0 : true)
</script>

<div class="kpis">
  <div class="card">
    <div class="kpi-label">Patrimônio total</div>
    <div class="kpi-value gold">{resumo ? fmtBRL(resumo.patrimonio) : '—'}</div>
    <div class="kpi-note">
      {resumo
        ? `${resumo.quantidade_posicoes} posições em ${resumo.quantidade_classes} classes`
        : '—'}
    </div>
  </div>
  <div class="card">
    <div class="kpi-label">Resultado do dia</div>
    <div class="kpi-value {diaPositivo ? 'up' : 'down'}">
      {resumo
        ? (diaPositivo ? '+' : '−') + fmtBRL(Math.abs(Number(resumo.resultado_dia)))
        : '—'}
    </div>
    <div class="kpi-note {diaPositivo ? 'up' : 'down'}">
      {resumo ? `${fmtPct(resumo.resultado_dia_pct, 2)} sobre o fechamento anterior` : '—'}
    </div>
  </div>
  <div class="card">
    <div class="kpi-label">Rentabilidade 12m</div>
    <div class="kpi-value">{resumo ? fmtPct(resumo.rentabilidade_12m) : '—'}</div>
    <div class="kpi-note">{periodo ?? 'acumulada nos últimos 12 meses'}</div>
  </div>
  <div class="card">
    <div class="kpi-label">Retorno vs CDI</div>
    <div class="kpi-value">{resumo ? `${fmtPctAbs(resumo.percentual_cdi, 0)} do CDI` : '—'}</div>
    <div class="kpi-note">carteira ÷ CDI no período</div>
  </div>
</div>
