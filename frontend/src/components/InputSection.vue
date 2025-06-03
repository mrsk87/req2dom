<template>
  <section class="input-section">
    <h3>Introduza os Requisitos</h3>
    <textarea 
      v-model="requirementsText" 
      placeholder="Exemplo: O sistema deve permitir aos utilizadores registarem-se com nome, email e password. Cada utilizador pode criar vários projetos..."
      rows="10"
      @keydown.ctrl.enter="emitProcess"
    ></textarea>
    <div class="controls">
      <div class="input-group">
        <label for="model-path">Caminho para o modelo Llama (opcional):</label>
        <input 
          id="model-path"
          type="text" 
          v-model="modelPath" 
          placeholder="Caminho para o modelo Llama (opcional)" 
        />
      </div>
      <div class="input-group">
        <label for="processing-method">Método de processamento:</label>
        <select id="processing-method" v-model="processingMethod">
          <option value="llm">LLM (Modelo de Linguagem)</option>
          <option value="nlp">NLP (Processamento de Linguagem Natural)</option>
          <option value="hybrid">Híbrido (NLP + LLM)</option>
        </select>
      </div>
      <button 
        @click="emitProcess" 
        :disabled="processing"
      >
        {{ processing ? 'A processar...' : 'Processar' }}
      </button>
    </div>
  </section>
</template>

<script>
export default {
  name: 'InputSection',
  data() {
    return {
      requirementsText: '',
      modelPath: '',
      processingMethod: 'llm',
      processing: false
    }
  },
  methods: {
    emitProcess() {
      if (!this.requirementsText.trim()) {
        alert("Por favor, introduza os requisitos para processar.");
        return;
      }
      
      this.processing = true;
      
      // Emitir evento para o componente pai
      this.$emit('process-requirements', {
        text: this.requirementsText,
        modelPath: this.modelPath,
        processingMethod: this.processingMethod
      });
      
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
}
</style>