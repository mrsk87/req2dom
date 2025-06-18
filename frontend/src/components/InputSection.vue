<template>
  <section class="input-section">
    <h3>Introduza os Requisitos</h3>
    <textarea 
      v-model="requirementsText" 
      placeholder="Exemplo: RF1. O sistema deve permitir aos utilizadores registarem-se com nome, email e password. RF2. Cada utilizador pode criar vários projetos..."
      rows="10"
      @keydown.ctrl.enter="emitProcess"
    ></textarea>
    
    <div class="controls">
      <div class="input-group">
        <label for="processing-method">Método de processamento:</label>
        <select id="processing-method" v-model="processingMethod" @change="handleMethodChange">
          <option value="llm">LLM Local (Llama)</option>
          <option value="llm_openrouter">LLM Externo (OpenRouter)</option>
          <option value="spacy_textacy">NLP Tradicional (spaCy + textacy)</option>
          <option value="stanza">NLP Avançado (Stanza - PT)</option>
          <option value="hybrid">Híbrido (NLP + LLM)</option>
        </select>
      </div>
      
      <div class="input-group" v-if="processingMethod === 'hybrid'">
        <label for="nlp-engine">Motor NLP para o modo híbrido:</label>
        <select id="nlp-engine" v-model="nlpEngine">
          <option value="stanza">Stanza (Recomendado para Português)</option>
          <option value="spacy">spaCy + textacy</option>
        </select>
        <small class="help-text">
          Stanza oferece melhor precisão para português de Portugal
        </small>
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
      
      <div class="input-group" v-if="processingMethod === 'llm_openrouter'">
        <label for="openrouter-model">Modelo OpenRouter (opcional):</label>
        <select id="openrouter-model" v-model="openrouterModel">
          <option value="">Padrão (gpt-3.5-turbo)</option>
          <option value="openai/gpt-3.5-turbo">GPT-3.5 Turbo</option>
          <option value="openai/gpt-4">GPT-4</option>
          <option value="openai/gpt-4-turbo">GPT-4 Turbo</option>
          <option value="anthropic/claude-3-haiku">Claude 3 Haiku</option>
          <option value="anthropic/claude-3-sonnet">Claude 3 Sonnet</option>
          <option value="meta-llama/llama-3.1-8b-instruct">Llama 3.1 8B</option>
          <option value="meta-llama/llama-3.1-70b-instruct">Llama 3.1 70B</option>
          <option value="google/gemma-2-9b-it">Gemma 2 9B</option>
        </select>
      </div>
      
      <!-- Componente para mostrar status das chaves de API -->
      <ApiKeyStatus v-if="processingMethod === 'llm_openrouter'" />
      
      <div class="input-group" v-if="processingMethod === 'llm_openrouter'">
        <label for="api-key">Chave de API OpenRouter (opcional se configurada no servidor):</label>
        <input 
          id="api-key"
          type="password" 
          v-model="apiKey" 
          placeholder="OpenRouter API Key (sk-or-...)" 
        />
        <small class="help-text">
          Deixe vazio para usar a chave configurada no servidor ou introduza uma nova chave temporária
        </small>
      </div>
      
      <div class="button-group" v-if="processingMethod === 'llm_openrouter'">
        <button 
          @click="emitProcessWithEnvKey" 
          :disabled="processing"
          class="btn-primary"
        >
          {{ processing ? 'A processar...' : 'Processar com chave do servidor' }}
        </button>
        <button 
          @click="emitProcessWithNewKey" 
          :disabled="processing || !apiKey"
          class="btn-secondary"
        >
          {{ processing ? 'A processar...' : 'Processar com nova chave' }}
        </button>
      </div>
      
      <button 
        v-else
        @click="emitProcess" 
        :disabled="processing"
        class="btn-primary"
      >
        {{ processing ? 'A processar...' : 'Processar' }}
      </button>
    </div>
  </section>
</template>

<script>
import ApiKeyStatus from './ApiKeyStatus.vue'

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
      openrouterModel: '',
      processingMethod: 'llm',
      nlpEngine: 'stanza',
      processing: false
    }
  },
  methods: {
    handleMethodChange() {
      // Reset API key when changing from OpenRouter to other methods
      if (this.processingMethod !== 'llm_openrouter') {
        this.apiKey = '';
      }
    },
    emitProcess() {
      if (!this.requirementsText.trim()) {
        alert("Por favor, introduza os requisitos para processar.");
        return;
      }
      
      this.processing = true;
      this.$emit('process-requirements', {
        text: this.requirementsText,
        modelPath: this.modelPath,
        processingMethod: this.processingMethod,
        openrouterModel: this.openrouterModel,
        nlpEngine: this.nlpEngine,
        useEnvKey: true
      });
      
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
      this.$emit('process-requirements', {
        text: this.requirementsText,
        modelPath: this.modelPath,
        processingMethod: this.processingMethod,
        openrouterModel: this.openrouterModel,
        nlpEngine: this.nlpEngine,
        useEnvKey: true
      });
      
      setTimeout(() => {
        this.processing = false;
      }, 500);
    },
    emitProcessWithNewKey() {
      if (!this.requirementsText.trim()) {
        alert("Por favor, introduza os requisitos para processar.");
        return;
      }
      
      if (!this.apiKey.trim()) {
        alert("Por favor, introduza uma chave de API para usar este método.");
        return;
      }
      
      this.processing = true;
      this.$emit('process-requirements', {
        text: this.requirementsText,
        modelPath: this.modelPath,
        processingMethod: this.processingMethod,
        openrouterModel: this.openrouterModel,
        nlpEngine: this.nlpEngine,
        apiKey: this.apiKey,
        useEnvKey: false
      });
      
      setTimeout(() => {
        this.processing = false;
      }, 500);
    }
  }
}
</script>

<style scoped>
.input-section {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.input-section h3 {
  margin-top: 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e0e6ed;
  border-radius: 8px;
  font-size: 1rem;
  line-height: 1.5;
  resize: vertical;
  font-family: inherit;
}

textarea:focus {
  outline: none;
  border-color: #3498db;
}

.controls {
  margin-top: 1rem;
}

.input-group {
  margin-bottom: 1rem;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.input-group input, .input-group select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e6ed;
  border-radius: 6px;
  font-size: 1rem;
}

.input-group input:focus, .input-group select:focus {
  outline: none;
  border-color: #3498db;
}

.help-text {
  display: block;
  margin-top: 0.25rem;
  color: #7f8c8d;
  font-size: 0.875rem;
}

.button-group {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  flex: 1;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

button {
  width: 100%;
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

button:hover:not(:disabled) {
  background: #2980b9;
}
</style>
