<template>
  <div class="api-key-status">
    <h4>Status das Chaves de API</h4>
    <div class="status-item">
      <span class="status-label">OpenRouter:</span>
      <span :class="['status-indicator', apiKeys.openrouter ? 'configured' : 'not-configured']">
        {{ apiKeys.openrouter ? '✓ Configurada' : '✗ Não configurada' }}
      </span>
    </div>
    <p class="status-note">
      As chaves configuradas no servidor podem ser usadas sem necessidade de introduzir novas chaves.
    </p>
  </div>
</template>

<script>
export default {
  name: 'ApiKeyStatus',
  data() {
    return {
      apiKeys: {
        openrouter: false
      }
    }
  },
  async mounted() {
    await this.fetchApiKeysStatus()
  },
  methods: {
    async fetchApiKeysStatus() {
      try {
        const response = await fetch('/api/api-keys')
        if (response.ok) {
          this.apiKeys = await response.json()
        }
      } catch (error) {
        console.error('Erro ao buscar status das chaves de API:', error)
      }
    }
  }
}
</script>

<style scoped>
.api-key-status {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.api-key-status h4 {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  color: #495057;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.status-label {
  font-weight: 600;
  color: #495057;
}

.status-indicator {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-indicator.configured {
  background: #d4edda;
  color: #155724;
}

.status-indicator.not-configured {
  background: #f8d7da;
  color: #721c24;
}

.status-note {
  margin: 0.75rem 0 0 0;
  font-size: 0.875rem;
  color: #6c757d;
  font-style: italic;
}
</style>
