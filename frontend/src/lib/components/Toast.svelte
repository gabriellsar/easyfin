<script lang="ts">
  import { toast } from '../state/toast.svelte'
</script>

<div class="toast" class:show={toast.visivel} role="status" aria-live="polite">
  {toast.mensagem}
</div>
