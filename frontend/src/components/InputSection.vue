<template>
  <section class="input-section">
    <h3>Introduza os Requisitos</h3>
    <textarea 
      v-model="requirementsText" 
      placeholder="Exemplo: O sistema deve permitir aos utilizadores registarem-se com nome, email e password. Cada utilizador pode criar vários projetos..."
      rows="10"
      @keydown.ctrl.enter="emitProcess"
    ></textarea>
    
    <ApiKeyStatus :show="processingMethod === 'llm_chatgpt'" />
    <div class="controls">
      <div class="input-group">
        <label for="processing-method">Método de processamento:</label>
        <select id="processing-method" v-model="processingMethod" @change="handleMethodChange">
          <option value="llm">LLM Local (Llama)</option>
          <option value="llm_chatgpt">LLM Externo</option>
          <option value="nlp">NLP (spaCy)</option>
          <option value="hybrid">Híbrido (NLP + LLM)</option>
          <option value="spacy_textacy">NLP Avançado (spaCy + textacy)</option>
        </select>
      </div>
      
      <div class="input-group" v-if="processingMethod === 'llm' || processingMethod === 'hybrid'">
        <label for="model-path">Caminho para o modelo Llama (opcional):</label>
        <input 
          id="model-path"
          type="text" 
          v-model="modelPath" 
          placeholder="Caminho para o modelo Llama (opcional)" 
        />
      </div>
      
      <div class="input-group" v-if="processingMethod === 'llm_chatgpt'">
        <label for="llm-provider">Provedor LLM:</label>
        <select id="llm-provider" v-model="llmProvider">
          <option value="openai">OpenAI (ChatGPT)</option>
          <option value="deepseek">Deepseek</option>
          <option value="qwen">Qwen (Alibaba Cloud)</option>
          <option value="gemini">Google Gemini Pro</option>
        </select>
      </div>
      
      <div class="input-group" v-if="processingMethod === 'llm_chatgpt'">
        <label for="api-key">Chave da API (opcional):</label>
        <input 
          id="api-key"
          type="password" 
          v-model="apiKey" 
          :placeholder="'Nova chave para ' + getProviderName() + ' (opcional)'" 
        />
        <small class="help-text">Deixe vazio para usar a chave configurada no servidor (se disponível)</small>
      </div>
      
      <div class="buttons" v-if="processingMethod === 'llm_chatgpt'">
        <button 
          @click="emitProcessWithEnvKey" 
          :disabled="processing"
          class="env-key-button"
          :title="'Usar a chave do ' + getProviderName() + ' configurada no servidor'"
        >
          {{ processing ? 'A processar...' : `Processar com chave do servidor` }}
        </button>

        <button 
          @click="emitProcess" 
          :disabled="processing || !apiKey"
          class="custom-key-button"
          :title="'Usar a chave do ' + getProviderName() + ' inserida acima'"
        >
          {{ processing ? 'A processar...' : `Processar com nova chave` }}
        </button>
      </div>
      <button 
        v-else
        @click="emitProcess" 
        :disabled="processing"
      >
        {{ processing ? 'A processar...' : 'Processar' }}
      </button>
    </div>
  </section>
</template>

<script>
import ApiKeyStatus from './ApiKeyStatus.vue';

export default {
  name: 'InputSection',
  components: {
    ApiKeyStatus
  },
  data() {
    return {
      requirementsText: '',
      modelPath: '',
      apiKey: '',
      processingMethod: 'llm',
      llmProvider: 'openai',
      processing: false
    }
  },
  methods: {
    getProviderName() {
      switch(this.llmProvider) {
        case 'openai':
          return 'do ChatGPT';
        case 'deepseek':
          return 'do Deepseek';
        case 'qwen':
          return 'do Qwen';
        case 'gemini':
          return 'do Google Gemini Pro';
        default:
          return 'do LLM';
      }
    },
    getButtonText() {
      if (this.processingMethod === 'llm_chatgpt') {
        const provider = this.llmProvider === 'openai' ? 'ChatGPT' : 
                        this.llmProvider === 'deepseek' ? 'Deepseek' : 
                        this.llmProvider === 'qwen' ? 'Qwen' :
                        this.llmProvider === 'gemini' ? 'Gemini Pro' : 'LLM';
        return `Processar com ${provider}`;
      }
      return 'Processar';
    },
    handleMethodChange() {
      // Limpar a chave da API quando trocar de ChatGPT para outros métodos
      if (this.processingMethod !== 'llm_chatgpt') {
        this.apiKey = '';
      }
    },
    emitProcess() {
      if (!this.requirementsText.trim()) {
        alert("Por favor, introduza os requisitos para processar.");
        return;
      }
      
      // Se for método LLM externo com chave personalizada, verificar se tem chave
      if (this.processingMethod === 'llm_chatgpt' && !this.apiKey.trim()) {
        alert(`A chave da API ${this.getProviderName()} é obrigatória para utilizar este método com chave personalizada.`);
        return;
      }
      
      this.processing = true;
      
      // Emitir evento para o componente pai com os parâmetros adequados
      const requestData = {
        text: this.requirementsText,
        processingMethod: this.processingMethod,
        useEnvKey: false // Indica que não deve usar a chave do .env
      };
      
      // Adicionar parâmetros específicos conforme o método selecionado
      if (this.processingMethod === 'llm' || this.processingMethod === 'hybrid') {
        requestData.modelPath = this.modelPath;
      }
      
      if (this.processingMethod === 'llm_chatgpt') {
        requestData.api_key = this.apiKey;
        requestData.llm_provider = this.llmProvider;
      }
      
      this.$emit('process-requirements', requestData);
      
      setTimeout(() => {
        this.processing = false;
      }, 500);
    },
    
    emitProcessWithEnvKey() {
      if (!this.requirementsText.trim()) {
        alert("Por favor, introduza os requisitos para processar.");
        return;
      }
      
      this.processing = true;
      
      // Emitir evento para o componente pai com os parâmetros adequados
      const requestData = {
        text: this.requirementsText,
        processingMethod: this.processingMethod,
        useEnvKey: true, // Indica que deve usar a chave do .env
        llm_provider: this.llmProvider
      };
      
      // Adicionar parâmetros específicos para modelo Llama, se necessário
      if (this.processingMethod === 'llm' || this.processingMethod === 'hybrid') {
        requestData.modelPath = this.modelPath;
      }
      
      this.$emit('process-requirements', requestData);
      
      setTimeout(() => {
        this.processing = false;
      }, 500);
    }
  }
}
</script>

<style scoped>
.controls {
  margin-top: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

label {
  font-size: 0.9rem;
  color: #555;
}

.help-text {
  font-size: 0.8rem;
  color: #666;
  margin-top: 3px;
  font-style: italic;
}

select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  background-color: white;
}

button {
  margin-top: 10px;
  align-self: flex-end;
}

.buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-self: flex-end;
}

.env-key-button {
  background-color: #4caf50;
  color: white;
}

.custom-key-button {
  background-color: #2196f3;
  color: white;
}

@media (min-width: 768px) {
  .controls {
    flex-direction: row;
    align-items: flex-end;
  }

  .input-group {
    flex: 1;
  }
  
  button {
    margin-top: 0;
  }
  
  .buttons {
    flex-direction: row;
    margin-top: 0;
  }
}
</style>