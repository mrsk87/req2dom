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
      <input 
        type="text" 
        v-model="modelPath" 
        placeholder="Caminho para o modelo Llama (opcional)" 
      />
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
        modelPath: this.modelPath
      });
      
      setTimeout(() => {
        this.processing = false;
      }, 500);
    }
  }
}
</script>

<style scoped>
/* Os estilos específicos do componente serão mantidos */
</style>