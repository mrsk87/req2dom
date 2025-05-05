<template>
  <div class="app">
    <header>
      <h1>req2dom</h1>
      <h2>Conversão de Requisitos para Classes de Domínio</h2>
    </header>
    
    <main>
      <InputSection @process-requirements="processRequirements" />
      
      <OutputSection 
        :xml-content="xmlContent"
        :loading="loading"
        :error="error"
      />
    </main>
    
    <footer>
      <p>req2dom - Projeto de conversão de requisitos para classes de domínio</p>
    </footer>
  </div>
</template>

<script>
import InputSection from './components/InputSection.vue'
import OutputSection from './components/OutputSection.vue'

export default {
  name: 'App',
  components: {
    InputSection,
    OutputSection
  },
  data() {
    return {
      xmlContent: '',
      loading: false,
      error: null,
      apiUrl: 'http://localhost:8000/api'
    }
  },
  methods: {
    async processRequirements({ text, modelPath }) {
      this.loading = true
      this.error = null
      this.xmlContent = ''
      
      try {
        console.log("A enviar pedido para:", `${this.apiUrl}/process`)
        
        const response = await fetch(`${this.apiUrl}/process`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            text,
            model_path: modelPath || undefined
          })
        })
        
        if (!response.ok) {
          throw new Error(`Erro HTTP: ${response.status} - ${response.statusText}`)
        }

        const result = await response.json()
        
        if (result.success) {
          this.xmlContent = result.xml_content
        } else {
          this.error = result.error || "Ocorreu um problema ao processar os requisitos."
        }
      } catch (error) {
        console.error("Erro ao comunicar com a API:", error)
        this.error = `Erro de comunicação com o servidor: ${error.message}.\nVerifique se o backend está em execução em ${this.apiUrl}.`
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style>
/* Os estilos globais serão importados no main.js */
</style>