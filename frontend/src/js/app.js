/**
 * req2dom - Aplicação para conversão de requisitos em classes de domínio
 * Script principal do frontend
 */

// Configuração da API
const API_URL = "http://localhost:8000/api";

// Elements do DOM
const requirementsInput = document.getElementById("requirements-input");
const modelPathInput = document.getElementById("model-path");
const processBtn = document.getElementById("process-btn");
const xmlOutput = document.getElementById("xml-output");
const copyBtn = document.getElementById("copy-btn");
const downloadBtn = document.getElementById("download-btn");
const loadingElement = document.getElementById("loading");

/**
 * Processa os requisitos submetidos e obtém resultado do servidor
 */
async function processRequirements() {
    // Feedback para o utilizador
    console.log("Iniciando processamento dos requisitos...");
    xmlOutput.value = "A iniciar processamento...";
    
    // Obter texto dos requisitos
    const requirementsText = requirementsInput.value.trim();
    if (!requirementsText) {
        alert("Por favor, introduza os requisitos para processar.");
        return;
    }

    // Preparar pedido
    const requestData = {
        text: requirementsText,
        model_path: modelPathInput.value.trim() || undefined
    };
    
    console.log("Dados do pedido:", requestData);

    // Mostrar indicador de carregamento
    loadingElement.classList.remove("hidden");
    xmlOutput.value = "A comunicar com o servidor...\nEste processo pode demorar alguns segundos dependendo da complexidade dos requisitos.";
    
    // Desativar botão durante o processamento
    processBtn.disabled = true;
    processBtn.textContent = "A processar...";

    try {
        console.log("A enviar pedido para:", `${API_URL}/process`);
        
        // Enviar pedido para a API
        const response = await fetch(`${API_URL}/process`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestData)
        });
        
        console.log("Resposta recebida, status:", response.status);
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status} - ${response.statusText}`);
        }

        // Processar resposta
        const result = await response.json();
        console.log("Resultado processado:", result);
        
        if (result.success) {
            // Mostrar XML resultante
            xmlOutput.value = result.xml_content;
            console.log("XML gerado com sucesso");
        } else {
            // Mostrar erro
            xmlOutput.value = `Erro: ${result.error || "Ocorreu um problema ao processar os requisitos."}`;
            console.error("Erro retornado pelo servidor:", result.error);
        }
    } catch (error) {
        console.error("Erro ao comunicar com a API:", error);
        xmlOutput.value = `Erro de comunicação com o servidor: ${error.message}.\nVerifique se o backend está em execução em ${API_URL}.`;
    } finally {
        // Restaurar estado do botão
        processBtn.disabled = false;
        processBtn.textContent = "Processar";
        
        // Esconder indicador de carregamento
        loadingElement.classList.add("hidden");
    }
}

/**
 * Copia o conteúdo XML para a área de transferência
 */
function copyXmlToClipboard() {
    if (!xmlOutput.value) {
        alert("Não há conteúdo XML para copiar.");
        return;
    }

    // Selecionar e copiar o texto
    xmlOutput.select();
    document.execCommand("copy");
    
    // Feedback ao utilizador
    const originalText = copyBtn.textContent;
    copyBtn.textContent = "Copiado!";
    setTimeout(() => {
        copyBtn.textContent = originalText;
    }, 2000);
}

/**
 * Descarrega o XML como um ficheiro
 */
function downloadXmlFile() {
    if (!xmlOutput.value) {
        alert("Não há conteúdo XML para guardar.");
        return;
    }

    // Criar um objeto Blob com o conteúdo XML
    const blob = new Blob([xmlOutput.value], { type: "application/xml" });
    
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
}

// Adicionar event listeners
processBtn.addEventListener("click", processRequirements);
copyBtn.addEventListener("click", copyXmlToClipboard);
downloadBtn.addEventListener("click", downloadXmlFile);

// Permitir submeter com Enter no campo de texto
requirementsInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter" && event.ctrlKey) {
        processRequirements();
    }
});