<template>
  <div class="api-key-status" v-if="show">
    <div class="api-key-header" @click="toggleDetails">
      <span>💻 Chaves de API configuradas no servidor</span>
      <span class="toggle-icon">{{ isOpen ? '▼' : '►' }}</span>
    </div>
    <div class="api-key-details" v-if="isOpen">
      <p class="api-key-info">Estas chaves estão configuradas no arquivo <code>.env</code> do servidor:</p>
      <div class="api-key-item" v-for="(status, provider) in apiKeys" :key="provider">
        <span class="provider-name">{{ getProviderName(provider) }}:</span>
        <span class="status" :class="{ 'configured': status, 'not-configured': !status }">
          <i class="icon" v-if="status">✅</i>
          <i class="icon" v-else>❌</i>
          {{ status ? 'Configurada' : 'Não configurada' }}
        </span>
      </div>
      <p class="api-key-help">Selecione "Processar com chave do servidor" para usar estas chaves.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ApiKeyStatus',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isOpen: false,
      apiKeys: {
        openai: false,
        deepseek: false,
        qwen: false,
        gemini: false
      },
      loading: false
    }
  },
  watch: {
    show: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.fetchApiKeyStatus();
        }
      }
    }
  },
  methods: {
    toggleDetails() {
      this.isOpen = !this.isOpen;
      if (this.isOpen) {
        this.fetchApiKeyStatus();
      }
    },
    getProviderName(provider) {
      switch(provider) {
        case 'openai':
          return 'OpenAI (ChatGPT)';
        case 'deepseek':
          return 'Deepseek';
        case 'qwen':
          return 'Qwen (Alibaba)';
        case 'gemini':
          return 'Google Gemini Pro';
        default:
          return provider;
      }
    },
    async fetchApiKeyStatus() {
      if (this.loading) return;
      
      this.loading = true;
      try {
        const response = await fetch('http://localhost:8000/api/api-keys');
        if (response.ok) {
          const data = await response.json();
          this.apiKeys = data;
        } else {
          console.error('Erro ao obter status das chaves de API');
        }
      } catch (error) {
        console.error('Erro ao comunicar com o backend:', error);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.api-key-status {
  margin-bottom: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.api-key-header {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: #f8f8f8;
  cursor: pointer;
  border-radius: 4px;
}

.api-key-details {
  padding: 10px;
  background-color: #fff;
  border-top: 1px solid #ddd;
}

.api-key-info {
  font-size: 0.85rem;
  margin-bottom: 10px;
  color: #555;
}

.api-key-help {
  font-size: 0.85rem;
  margin-top: 10px;
  color: #555;
  font-style: italic;
}

.api-key-item {
  margin: 8px 0;
  display: flex;
  justify-content: space-between;
  padding: 5px;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.provider-name {
  font-weight: bold;
}

.status {
  padding: 2px 6px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.configured {
  background-color: #e6f7e6;
  color: #2e7d32;
}

.not-configured {
  background-color: #ffebee;
  color: #c62828;
}

.icon {
  font-style: normal;
}

.toggle-icon {
  font-weight: bold;
}
</style>
