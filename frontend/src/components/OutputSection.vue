<template>
  <section class="output-section">
    <h3>Classes de Domínio (XML para draw.io)</h3>
    <div v-if="loading" class="loading">A processar... Por favor aguarde.</div>
    <textarea 
      :value="xmlContent"
      readonly 
      :placeholder="error || 'O resultado em XML para draw.io aparecerá aqui...'" 
      rows="15"
    ></textarea>
    <div class="controls">
      <button 
        @click="copyToClipboard" 
        :disabled="!hasContent"
      >Copiar XML</button>
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
    xmlContent: {
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
      return !!this.xmlContent;
    }
  },
  methods: {
    copyToClipboard() {
      if (!this.hasContent) {
        alert("Não há conteúdo XML para copiar.");
        return;
      }

      navigator.clipboard.writeText(this.xmlContent)
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
        alert("Não há conteúdo XML para guardar.");
        return;
      }

      // Criar um objeto Blob com o conteúdo XML
      const blob = new Blob([this.xmlContent], { type: "application/xml" });
      
      // Criar URL para o Blob
      const url = URL.createObjectURL(blob);
      
      // Criar elemento de link para download
      const a = document.createElement("a");
      a.href = url;
      a.download = "domain_classes.xml";
      
      // Simular clique para iniciar o download
      document.body.appendChild(a);
      a.click();
      
      // Limpar
      URL.revokeObjectURL(url);
      document.body.removeChild(a);
    },
    
    openInDrawIo() {
      if (!this.hasContent) {
        alert("Não há conteúdo XML para abrir no draw.io.");
        return;
      }

      // URL do draw.io com o diagrama incorporado
      const drawIoUrl = `https://embed.diagrams.net/?splash=0&ui=kennedy&embed=1&url=data:text/xml;base64,${btoa(this.xmlContent)}`;
      
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