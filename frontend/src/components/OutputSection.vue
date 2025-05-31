<template>
  <section class="output-section">
    <h3>Classes de Domínio (JSON para draw.io)</h3>
    <div v-if="loading" class="loading">A processar... Por favor aguarde.</div>
    <textarea 
      :value="jsonContent"
      readonly 
      :placeholder="error || 'O resultado em JSON para draw.io aparecerá aqui...'" 
      rows="15"
    ></textarea>
    <div class="controls">
      <button 
        @click="copyToClipboard" 
        :disabled="!hasContent"
      >Copiar JSON</button>
      <button 
        @click="downloadFile" 
        :disabled="!hasContent"
      >Guardar como Ficheiro</button>
      <button 
        @click="openInDrawIo" 
        :disabled="!hasContent"
      >Abrir no draw.io</button>
    </div>
  </section>
</template>

<script>
export default {
  name: 'OutputSection',
  props: {
    jsonContent: {
      type: String,
      default: ''
    },
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: null
    }
  },
  computed: {
    hasContent() {
      return !!this.jsonContent;
    }
  },
  methods: {
    copyToClipboard() {
      if (!this.hasContent) {
        alert("Não há conteúdo JSON para copiar.");
        return;
      }

      navigator.clipboard.writeText(this.jsonContent)
        .then(() => {
          // Criar elemento temporário para feedback
          const button = event.target;
          const originalText = button.textContent;
          button.textContent = "Copiado!";
          
          setTimeout(() => {
            button.textContent = originalText;
          }, 2000);
        })
        .catch(err => {
          console.error('Erro ao copiar texto: ', err);
          alert("Não foi possível copiar o texto para a área de transferência.");
        });
    },
    
    downloadFile() {
      if (!this.hasContent) {
        alert("Não há conteúdo JSON para guardar.");
        return;
      }

      // Criar um objeto Blob com o conteúdo JSON
      const blob = new Blob([this.jsonContent], { type: "application/json" });
      
      // Criar URL para o Blob
      const url = URL.createObjectURL(blob);
      
      // Criar elemento de link para download
      const a = document.createElement("a");
      a.href = url;
      a.download = "domain_classes.json";
      
      // Simular clique para iniciar o download
      document.body.appendChild(a);
      a.click();
      
      // Limpar
      URL.revokeObjectURL(url);
      document.body.removeChild(a);
    },
    
    openInDrawIo() {
      if (!this.hasContent) {
        alert("Não há conteúdo JSON para abrir no draw.io.");
        return;
      }

      // URL do draw.io com o diagrama incorporado
      const drawIoUrl = `https://embed.diagrams.net/?splash=0&ui=kennedy&embed=1&url=data:text/xml;base64,${btoa(this.jsonContent)}`;
      
      // Abrir em nova aba
      window.open(drawIoUrl, '_blank');
    }
  }
}
</script>

<style scoped>
.loading {
  color: #007bff;
  margin-bottom: 10px;
  font-weight: bold;
}
</style>