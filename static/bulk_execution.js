/**
 * Funcionalidad de Ejecución Masiva desde Excel
 * Maneja la carga, análisis y ejecución de casos de prueba desde archivos Excel
 */

class BulkExecutionManager {
    constructor() {
        this.testCases = [];
        this.analysisResults = null;
        this.currentEditingCase = null;
        
        this.initializeEventListeners();
        this.initializeTooltips();
    }
    
    initializeEventListeners() {
        // Formulario de carga de Excel
        const excelForm = document.getElementById('excelUploadForm');
        if (excelForm) {
            excelForm.addEventListener('submit', this.handleExcelUpload.bind(this));
        }
        
        // Botones de acción
        const executeValidBtn = document.getElementById('executeValidCases');
        if (executeValidBtn) {
            executeValidBtn.addEventListener('click', this.executeValidCases.bind(this));
        }
        
        const executeAllBtn = document.getElementById('executeAllCases');
        if (executeAllBtn) {
            executeAllBtn.addEventListener('click', this.executeAllCases.bind(this));
        }
        
        const editCasesBtn = document.getElementById('editCases');
        if (editCasesBtn) {
            editCasesBtn.addEventListener('click', this.openCaseEditor.bind(this));
        }
        
        const saveAsSuiteBtn = document.getElementById('saveAsSuite');
        if (saveAsSuiteBtn) {
            saveAsSuiteBtn.addEventListener('click', this.openSaveAsSuiteModal.bind(this));
        }
        
        // Modal de edición
        const saveCaseBtn = document.getElementById('saveCaseChanges');
        if (saveCaseBtn) {
            saveCaseBtn.addEventListener('click', this.saveCaseChanges.bind(this));
        }
        
        const reanalyzeCaseBtn = document.getElementById('reanalyzeCaseChanges');
        if (reanalyzeCaseBtn) {
            reanalyzeCaseBtn.addEventListener('click', this.reanalyzeCase.bind(this));
        }
        
        // Modal de guardar suite
        const confirmSaveBtn = document.getElementById('confirmSaveAsSuite');
        if (confirmSaveBtn) {
            confirmSaveBtn.addEventListener('click', this.saveAsSuite.bind(this));
        }
        
        // Botón de descarga de reporte
        const downloadReportBtn = document.getElementById('downloadExecutionReport');
        if (downloadReportBtn) {
            downloadReportBtn.addEventListener('click', this.downloadExecutionReport.bind(this));
        }
    }
    
    initializeTooltips() {
        // Inicializar tooltips de Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    async handleExcelUpload(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const fileInput = document.getElementById('excelFile');
        
        if (!fileInput.files[0]) {
            this.showAlert('Por favor selecciona un archivo Excel', 'warning');
            return;
        }
        
        // Obtener modo de datos seleccionado
        const dataMode = document.querySelector('input[name="dataMode"]:checked').value;
        formData.append('data_mode', dataMode);
        
        console.log('📊 Modo de datos seleccionado:', dataMode);
        
        // Mostrar progreso de análisis
        this.showAnalysisProgress('Iniciando análisis del archivo Excel...');
        
        try {
            const response = await fetch('/api/analyze_excel', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                console.log('📊 Resultado del análisis:', result);
                
                this.testCases = result.test_cases;
                this.analysisResults = result.summary;
                
                console.log('📋 Casos de prueba cargados:', this.testCases.length);
                console.log('📈 Resumen del análisis:', this.analysisResults);
                
                // Mostrar estadísticas finales
                const stats = {
                    total: result.test_cases.length,
                    valid: result.summary.casos_validos,
                    problematic: result.summary.casos_invalidos || (result.test_cases.length - result.summary.casos_validos)
                };
                
                this.updateAnalysisProgress(100, `Análisis completado: ${result.test_cases.length} casos procesados`, 
                                          `${result.summary.casos_validos} casos válidos, ${stats.problematic} con problemas`, stats);
                
                // Pequeña pausa para mostrar el 100% antes de ocultar
                setTimeout(() => {
                    console.log('🎯 Ocultando progreso y mostrando resultados...');
                    console.log('📊 Estado antes de ocultar overlay:', {
                        overlay: document.getElementById('analysisProgressOverlay'),
                        resultsPanel: document.getElementById('analysisResults')
                    });
                    
                    this.hideAnalysisProgress();
                    this.displayAnalysisResults();
                    
                    const analysisType = result.analysis_type === 'ia' ? 'con IA' : 'básico';
                    this.showAlert(`Análisis ${analysisType} completado: ${result.test_cases.length} casos encontrados (${result.summary.casos_validos} válidos)`, 'success');
                }, 1000);
            } else {
                throw new Error(result.error || 'Error desconocido al analizar el archivo');
            }
            
        } catch (error) {
            console.error('Error al analizar Excel:', error);
            this.hideAnalysisProgress();
            this.showAlert(`Error al analizar el archivo: ${error.message}`, 'danger');
        }
    }
    
    displayAnalysisResults() {
        console.log('🔍 Iniciando displayAnalysisResults...');
        
        const resultsPanel = document.getElementById('analysisResults');
        if (!resultsPanel) {
            console.error('❌ No se encontró el elemento analysisResults');
            return;
        }
        
        console.log('✅ Elemento analysisResults encontrado');
        
        // Mostrar panel de resultados
        resultsPanel.style.display = 'block';
        console.log('👁️ Panel de resultados mostrado');
        
        // Actualizar estadísticas
        console.log('📊 Actualizando estadísticas...');
        this.updateStatistics();
        
        // Mostrar casos en las diferentes pestañas
        console.log('📋 Mostrando casos válidos...');
        this.displayValidCases();
        
        console.log('⚠️ Mostrando casos inválidos...');
        this.displayInvalidCases();
        
        console.log('📄 Mostrando todos los casos...');
        this.displayAllCases();
        
        // Habilitar botones según corresponda
        console.log('🔘 Actualizando botones de acción...');
        this.updateActionButtons();
        
        // Scroll al panel de resultados
        console.log('📜 Haciendo scroll al panel de resultados...');
        resultsPanel.scrollIntoView({ behavior: 'smooth' });
        
        console.log('✅ displayAnalysisResults completado');
    }
    
    updateStatistics() {
        const summary = this.analysisResults;
        
        console.log('📊 Actualizando estadísticas con:', summary);
        
        document.getElementById('totalCases').textContent = summary.total_casos;
        document.getElementById('validCases').textContent = summary.casos_validos;
        document.getElementById('invalidCases').textContent = summary.casos_invalidos;
        document.getElementById('successRate').textContent = `${summary.porcentaje_validos}%`;
        
        // Actualizar contadores en tabs
        document.getElementById('validCasesCount').textContent = summary.casos_validos;
        document.getElementById('invalidCasesCount').textContent = summary.casos_invalidos;
        
        console.log('✅ Estadísticas actualizadas');
    }
    
    displayValidCases() {
        const container = document.getElementById('validCasesList');
        if (!container) return;
        
        const validCases = this.testCases.filter(tc => tc.es_valido);
        container.innerHTML = '';
        
        if (validCases.length === 0) {
            container.innerHTML = `
                <div class="alert tech-alert tech-alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    No se encontraron casos válidos para ejecutar.
                </div>
            `;
            return;
        }
        
        validCases.forEach(testCase => {
            const caseElement = this.createCaseElement(testCase, true);
            container.appendChild(caseElement);
        });
    }
    
    displayInvalidCases() {
        console.log('🔍 Iniciando displayInvalidCases...');
        
        const container = document.getElementById('invalidCasesList');
        if (!container) {
            console.error('❌ No se encontró el elemento invalidCasesList');
            return;
        }
        
        console.log('✅ Elemento invalidCasesList encontrado');
        
        const invalidCases = this.testCases.filter(tc => !tc.es_valido);
        console.log(`📊 Casos inválidos encontrados: ${invalidCases.length}`);
        
        container.innerHTML = '';
        
        if (invalidCases.length === 0) {
            console.log('✅ No hay casos inválidos, mostrando mensaje de éxito');
            container.innerHTML = `
                <div class="alert tech-alert tech-alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    ¡Excelente! Todos los casos son válidos.
                </div>
            `;
            return;
        }
        
        console.log(`📋 Creando elementos para ${invalidCases.length} casos inválidos...`);
        invalidCases.forEach((testCase, index) => {
            console.log(`📄 Creando elemento para caso ${index + 1}: ${testCase.id} - ${testCase.nombre}`);
            const caseElement = this.createCaseElement(testCase, false);
            container.appendChild(caseElement);
        });
        
        console.log('✅ displayInvalidCases completado');
    }
    
    displayAllCases() {
        const container = document.getElementById('allCasesList');
        if (!container) return;
        
        container.innerHTML = '';
        
        this.testCases.forEach(testCase => {
            const caseElement = this.createCaseElement(testCase, testCase.es_valido);
            container.appendChild(caseElement);
        });
    }
    
    createCaseElement(testCase, isValid) {
        console.log(`🎯 Creando elemento para caso: ${testCase.id} (${testCase.nombre || 'Sin nombre'})`);
        const div = document.createElement('div');
        div.className = `case-item ${isValid ? 'valid' : 'invalid'}`;
        div.dataset.caseId = testCase.id;
        
        const statusIcon = isValid ? 
            '<i class="fas fa-check-circle text-success"></i>' : 
            '<i class="fas fa-exclamation-triangle text-danger"></i>';
        
        const urlInfo = testCase.url_extraida ? 
            `<span class="badge bg-info"><i class="fas fa-link me-1"></i>${testCase.url_extraida}</span>` : 
            '<span class="badge bg-secondary"><i class="fas fa-unlink me-1"></i>Sin URL</span>';
        
        // Información de resultados de ejecución si están disponibles
        let executionResultInfo = '';
        if (testCase.execution_result) {
            const result = testCase.execution_result;
            const badgeClass = result.success ? 'bg-success' : 'bg-danger';
            const icon = result.success ? 'fa-check-circle' : 'fa-times-circle';
            const timeInfo = result.execution_time ? ` (${Math.round(result.execution_time)}s)` : '';
            
            executionResultInfo = `
                <span class="badge ${badgeClass} ms-2">
                    <i class="fas ${icon} me-1"></i>${result.success ? 'Éxito' : 'Fallo'}${timeInfo}
                </span>
            `;
        }
        
        let problemsHtml = '';
        if (testCase.problemas && testCase.problemas.length > 0) {
            problemsHtml = `
                <div class="case-problems mt-2">
                    <strong class="text-danger">Problemas:</strong>
                    ${testCase.problemas.map(p => `<div class="case-problem">• ${p}</div>`).join('')}
                </div>
            `;
        }
        
        let suggestionsHtml = '';
        if (testCase.sugerencias && testCase.sugerencias.length > 0) {
            suggestionsHtml = `
                <div class="case-suggestions mt-2">
                    <strong class="text-info">Sugerencias:</strong>
                    ${testCase.sugerencias.map(s => `<div class="case-suggestion">• ${s}</div>`).join('')}
                </div>
            `;
        }
        
        div.innerHTML = `
            <div class="case-header">
                <div class="d-flex align-items-center">
                    ${statusIcon}
                    <div class="ms-2">
                        <div class="case-title">${testCase.nombre || 'Sin nombre'}</div>
                        <div class="case-id text-muted">${testCase.id}</div>
                    </div>
                    <div id="executionStatus_${testCase.id}" class="ms-auto me-3" style="display: none;">
                        <span class="badge bg-warning">
                            <i class="fas fa-spinner fa-spin me-1"></i>Ejecutando...
                        </span>
                    </div>
                </div>
                <div class="case-actions">
                    ${urlInfo}
                    ${executionResultInfo}
                    <button class="btn btn-sm tech-btn-success ms-2 execute-single-btn" id="executeBtn_${testCase.id}" onclick="window.bulkManager.executeSingleCase('${testCase.id}')" title="Ejecutar solo este caso">
                        <i class="fas fa-play me-1"></i>Ejecutar
                    </button>
                    <button class="btn btn-sm tech-btn-info ms-2" onclick="window.bulkManager.viewCase('${testCase.id}')" title="Ver detalles completos">
                        <i class="fas fa-eye me-1"></i>Ver
                    </button>
                    <button class="btn btn-sm tech-btn-primary ms-2" onclick="window.bulkManager.editCase('${testCase.id}')" title="Editar caso de prueba">
                        <i class="fas fa-edit me-1"></i>Editar
                    </button>
                </div>
            </div>
            
            <div class="case-content mt-2">
                <div class="row">
                    <div class="col-md-6">
                        <small class="text-muted">Objetivo:</small>
                        <div class="text-light">${testCase.objetivo || 'No especificado'}</div>
                    </div>
                    <div class="col-md-6">
                        <small class="text-muted">Resultado Esperado:</small>
                        <div class="text-light">${testCase.resultado_esperado || 'No especificado'}</div>
                    </div>
                </div>
                
                ${problemsHtml}
                ${suggestionsHtml}
            </div>
        `;
        
        return div;
    }
    
    updateActionButtons() {
        const validCases = this.testCases.filter(tc => tc.es_valido);
        const invalidCases = this.testCases.filter(tc => !tc.es_valido);
        const hasValidCases = validCases.length > 0;
        const hasAnyCases = this.testCases.length > 0;
        
        document.getElementById('executeValidCases').disabled = !hasValidCases;
        document.getElementById('executeAllCases').disabled = !hasAnyCases;
        
        // Actualizar menú de edición de casos problemáticos
        this.updateEditCasesMenu(invalidCases);
    }
    
    updateEditCasesMenu(invalidCases) {
        const menu = document.getElementById('editCasesMenu');
        const dropdown = document.getElementById('editCasesDropdown');
        
        if (!menu || !dropdown) return;
        
        if (invalidCases.length === 0) {
            menu.innerHTML = '<li><a class="dropdown-item text-muted" href="#"><i class="fas fa-check-circle me-2"></i>Todos los casos son válidos</a></li>';
            dropdown.disabled = true;
            dropdown.classList.add('disabled');
        } else {
            dropdown.disabled = false;
            dropdown.classList.remove('disabled');
            
            let menuHtml = `
                <li><h6 class="dropdown-header"><i class="fas fa-exclamation-triangle me-2"></i>${invalidCases.length} casos con problemas</h6></li>
                <li><hr class="dropdown-divider"></li>
            `;
            
            invalidCases.forEach((testCase, index) => {
                const caseName = testCase.nombre || `Caso ${testCase.id}`;
                const truncatedName = caseName.length > 40 ? caseName.substring(0, 40) + '...' : caseName;
                
                menuHtml += `
                    <li>
                        <a class="dropdown-item" href="#" onclick="bulkManager.editCase('${testCase.id}')">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <i class="fas fa-edit me-2 text-warning"></i>
                                    <span>${truncatedName}</span>
                                </div>
                                <small class="text-muted">${testCase.id}</small>
                            </div>
                            ${testCase.problemas && testCase.problemas.length > 0 ? `
                                <small class="text-danger d-block mt-1">
                                    ${testCase.problemas.length} problema${testCase.problemas.length > 1 ? 's' : ''}
                                </small>
                            ` : ''}
                        </a>
                    </li>
                `;
            });
            
            menuHtml += `
                <li><hr class="dropdown-divider"></li>
                <li>
                    <a class="dropdown-item text-primary" href="#" onclick="bulkManager.editAllProblematicCases()">
                        <i class="fas fa-edit me-2"></i>
                        <strong>Editar todos en secuencia</strong>
                    </a>
                </li>
            `;
            
            menu.innerHTML = menuHtml;
        }
    }
    
    async executeValidCases() {
        const validCases = this.testCases.filter(tc => tc.es_valido);
        
        if (validCases.length === 0) {
            this.showAlert('No hay casos válidos para ejecutar', 'warning');
            return;
        }
        
        if (!confirm(`¿Estás seguro de que quieres ejecutar ${validCases.length} casos válidos?`)) {
            return;
        }
        
        await this.executeCases(validCases);
    }
    
    async executeAllCases() {
        if (this.testCases.length === 0) {
            this.showAlert('No hay casos para ejecutar', 'warning');
            return;
        }
        
        const invalidCount = this.testCases.filter(tc => !tc.es_valido).length;
        let message = `¿Estás seguro de que quieres ejecutar ${this.testCases.length} casos?`;
        
        if (invalidCount > 0) {
            message += `\n\nNota: ${invalidCount} casos tienen problemas y pueden fallar.`;
        }
        
        if (!confirm(message)) {
            return;
        }
        
        await this.executeCases(this.testCases);
    }
    
    async executeCases(cases) {
        if (!cases || cases.length === 0) {
            this.showAlert('No hay casos para ejecutar', 'warning');
            return;
        }
        
        // Obtener modo de ejecución seleccionado
        const executionMode = document.querySelector('input[name="executionMode"]:checked')?.value || 'sequential';
        
        // Obtener opción de mostrar navegador
        const showBrowser = document.getElementById('showBrowser')?.checked || false;
        
        // Mostrar confirmación con información del modo
        const modeText = executionMode === 'sequential' ? 'secuencial (uno por uno)' : 'paralelo (simultáneo)';
        const browserText = showBrowser ? ' (navegador visible)' : ' (navegador oculto)';
        const confirmed = confirm(`¿Estás seguro de que quieres ejecutar ${cases.length} casos de prueba en modo ${modeText}${browserText}?`);
        if (!confirmed) return;
        
        this.showLoader(`Iniciando ejecución ${modeText} de ${cases.length} casos...`);
        
        try {
            // Crear FormData para enviar tanto JSON como parámetros de formulario
            const formData = new FormData();
            formData.append('test_cases_json', JSON.stringify(cases));
            formData.append('execution_mode', executionMode);
            formData.append('show_browser', showBrowser.toString());
            
            const response = await fetch('/api/execute_bulk_cases', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.hideLoader();
                this.showAlert('Ejecución iniciada correctamente', 'success');
                
                // Mostrar modal de progreso
                this.showExecutionProgressModal(result.execution_id, executionMode, cases.length);
                
                // Iniciar monitoreo del progreso
                this.monitorExecution(result.execution_id, executionMode);
            } else {
                throw new Error(result.error || 'Error desconocido al iniciar la ejecución');
            }
            
        } catch (error) {
            console.error('Error al ejecutar casos:', error);
            this.showAlert(`Error al ejecutar casos: ${error.message}`, 'danger');
        } finally {
            this.hideLoader();
        }
    }
    
    async executeSingleCase(caseId) {
        const testCase = this.testCases.find(tc => tc.id === caseId);
        if (!testCase) {
            this.showAlert('Caso de prueba no encontrado', 'error');
            return;
        }
        
        // Verificar si el caso ya está en ejecución
        if (this.isCaseExecuting(caseId)) {
            this.showAlert('Este caso ya está siendo ejecutado', 'warning');
            return;
        }
        
        // Obtener opción de mostrar navegador
        const showBrowser = document.getElementById('showBrowser')?.checked || false;
        const browserText = showBrowser ? ' (navegador visible)' : ' (navegador oculto)';
        
        // Mostrar confirmación
        const confirmed = confirm(`¿Estás seguro de que quieres ejecutar el caso "${testCase.nombre || testCase.id}"${browserText}?`);
        if (!confirmed) return;
        
        // Mostrar indicadores visuales de ejecución
        this.setCaseExecutionStatus(caseId, true);
        
        try {
            // Crear FormData para enviar el caso individual
            const formData = new FormData();
            formData.append('test_cases_json', JSON.stringify([testCase]));
            formData.append('execution_mode', 'sequential'); // Siempre secuencial para un caso
            formData.append('show_browser', showBrowser.toString());
            
            const response = await fetch('/api/execute_bulk_cases', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert(`Ejecución individual iniciada: ${testCase.nombre || testCase.id}`, 'success');
                
                // Mostrar modal de progreso para caso individual
                this.showExecutionProgressModal(result.execution_id, 'sequential', 1);
                
                // Iniciar monitoreo del progreso
                this.monitorExecution(result.execution_id, 'sequential').then(() => {
                    // Restaurar estado visual cuando termine
                    this.setCaseExecutionStatus(caseId, false);
                });
            } else {
                throw new Error(result.error || 'Error desconocido al iniciar la ejecución');
            }
            
        } catch (error) {
            console.error('Error al ejecutar caso individual:', error);
            this.showAlert(`Error al ejecutar caso: ${error.message}`, 'danger');
            this.setCaseExecutionStatus(caseId, false);
        }
    }
    
    isCaseExecuting(caseId) {
        const statusElement = document.getElementById(`executionStatus_${caseId}`);
        return statusElement && statusElement.style.display !== 'none';
    }
    
    setCaseExecutionStatus(caseId, isExecuting) {
        const statusElement = document.getElementById(`executionStatus_${caseId}`);
        const executeBtn = document.getElementById(`executeBtn_${caseId}`);
        
        if (statusElement) {
            statusElement.style.display = isExecuting ? 'block' : 'none';
        }
        
        if (executeBtn) {
            executeBtn.disabled = isExecuting;
            if (isExecuting) {
                executeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Ejecutando...';
                executeBtn.classList.replace('tech-btn-success', 'tech-btn-secondary');
            } else {
                executeBtn.innerHTML = '<i class="fas fa-play me-1"></i>Ejecutar';
                executeBtn.classList.replace('tech-btn-secondary', 'tech-btn-success');
            }
        }
    }
    
    showExecutionProgressModal(executionId, executionMode, totalCases) {
        // Configurar modal según el modo de ejecución
        const currentCaseSection = document.getElementById('currentCaseSection');
        if (executionMode === 'sequential') {
            currentCaseSection.style.display = 'block';
        } else {
            currentCaseSection.style.display = 'none';
        }
        
        // Resetear valores
        document.getElementById('overallProgressText').textContent = '0%';
        document.getElementById('overallProgressBar').style.width = '0%';
        document.getElementById('totalCasesExecution').textContent = totalCases;
        document.getElementById('completedCases').textContent = '0';
        document.getElementById('successfulCases').textContent = '0';
        document.getElementById('failedCases').textContent = '0';
        document.getElementById('executionResultsList').innerHTML = '';
        document.getElementById('downloadExecutionReport').disabled = true;
        
        if (executionMode === 'sequential') {
            document.getElementById('currentCaseName').textContent = 'Preparando...';
            document.getElementById('currentCaseProgress').textContent = '0%';
            document.getElementById('currentCaseProgressBar').style.width = '0%';
            document.getElementById('currentStepDescription').textContent = 'Iniciando...';
        }
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('executionProgressModal'));
        modal.show();
        
        // Guardar referencia para el monitoreo
        this.currentExecutionModal = modal;
        this.currentExecutionId = executionId;
    }
    
    async monitorExecution(executionId, executionMode) {
        return new Promise((resolve, reject) => {
            const pollInterval = executionMode === 'sequential' ? 2000 : 5000; // 2s para secuencial, 5s para paralelo
            
            const poll = async () => {
                try {
                    const response = await fetch(`/api/execution_status/${executionId}`);
                    const result = await response.json();
                    
                    if (result.success) {
                        console.log(`[POLLING] Estado actual: ${result.execution.status}, Progreso: ${result.execution.progress}%`);
                        
                        this.updateExecutionProgress(result.execution, executionMode);
                        
                        // Continuar polling si no está completado
                        if (result.execution.status === 'en_progreso' || result.execution.status === 'iniciado') {
                            console.log(`[POLLING] Continuando polling... Estado: ${result.execution.status}`);
                            setTimeout(poll, pollInterval);
                        } else {
                            // Ejecución completada
                            console.log(`[POLLING] Ejecución completada detectada. Estado final: ${result.execution.status}`);
                            this.onExecutionCompleted(result.execution);
                            resolve(result.execution);
                        }
                    } else {
                        console.error(`[POLLING] Error en respuesta:`, result.error);
                        throw new Error(result.error || 'Error al obtener estado de ejecución');
                    }
                    
                } catch (error) {
                    console.error('Error monitoreando ejecución:', error);
                    this.showAlert(`Error monitoreando ejecución: ${error.message}`, 'danger');
                    reject(error);
                }
            };
            
            // Iniciar polling
            setTimeout(poll, 1000); // Primer poll después de 1 segundo
        });
    }
    
    updateExecutionProgress(execution, executionMode) {
        // Actualizar progreso general
        document.getElementById('overallProgressText').textContent = `${execution.progress || 0}%`;
        document.getElementById('overallProgressBar').style.width = `${execution.progress || 0}%`;
        document.getElementById('completedCases').textContent = execution.completed_cases || 0;
        document.getElementById('successfulCases').textContent = execution.successful_cases || 0;
        document.getElementById('failedCases').textContent = execution.failed_cases || 0;
        
        // Actualizar caso actual (solo para modo secuencial)
        if (executionMode === 'sequential' && execution.current_case_name) {
            document.getElementById('currentCaseName').textContent = execution.current_case_name;
            document.getElementById('currentCaseProgress').textContent = `${execution.current_case_progress || 0}%`;
            document.getElementById('currentCaseProgressBar').style.width = `${execution.current_case_progress || 0}%`;
            document.getElementById('currentStepDescription').textContent = execution.current_step_description || 'Ejecutando...';
        }
        
        // Actualizar lista de resultados
        this.updateExecutionResultsList(execution.results || []);
    }
    
    updateExecutionResultsList(results) {
        const container = document.getElementById('executionResultsList');
        
        // Solo agregar nuevos resultados para evitar parpadeo
        const currentCount = container.children.length;
        const newResults = results.slice(currentCount);
        
        newResults.forEach(result => {
            const resultElement = this.createExecutionResultElement(result);
            container.appendChild(resultElement);
        });
        
        // Scroll al último resultado
        if (newResults.length > 0) {
            container.scrollTop = container.scrollHeight;
        }
    }
    
    createExecutionResultElement(result) {
        const div = document.createElement('div');
        div.className = `execution-result-item ${result.success ? 'success' : 'failed'} mb-2`;
        
        const statusIcon = result.success ? 
            '<i class="fas fa-check-circle text-success"></i>' : 
            '<i class="fas fa-times-circle text-danger"></i>';
        
        const executionTime = result.execution_time ? 
            (typeof result.execution_time === 'number' ? `${result.execution_time}s` : result.execution_time) : 
            'N/A';
        
        div.innerHTML = `
            <div class="d-flex align-items-center justify-content-between p-2 border rounded">
                <div class="d-flex align-items-center">
                    ${statusIcon}
                    <div class="ms-2">
                        <div class="fw-bold">${result.case_name || result.case_id}</div>
                        <small class="text-muted">${result.message || 'Sin mensaje'}</small>
                    </div>
                </div>
                <div class="text-end">
                    <small class="text-muted">${executionTime}</small>
                    ${result.url_tested ? `<br><small class="text-info">${result.url_tested}</small>` : ''}
                </div>
            </div>
        `;
        
        return div;
    }
    
    onExecutionCompleted(execution) {
        console.log(`[EXECUTION_COMPLETED] Iniciando finalización de ejecución`, execution);
        
        // Actualizar el título del modal para indicar que terminó
        const modalTitle = document.getElementById('executionProgressModalLabel');
        if (modalTitle) {
            const successRate = execution.success_rate || 0;
            const iconClass = successRate >= 80 ? 'fa-check-circle text-success' : successRate >= 50 ? 'fa-exclamation-triangle text-warning' : 'fa-times-circle text-danger';
            modalTitle.innerHTML = `<i class=\"fas ${iconClass} me-2\"></i>Ejecución Completada`;
            console.log(`[EXECUTION_COMPLETED] Título del modal actualizado (éxito: ${successRate}%)`);
        }
        
        // Actualizar estado visual del caso actual para mostrar resumen final
        const currentStepElement = document.getElementById('currentStepDescription');
        if (currentStepElement) {
            const successRate = execution.success_rate || 0;
            const statusText = successRate >= 80 ? 'exitosamente' : successRate >= 50 ? 'con algunos errores' : 'con errores';
            currentStepElement.textContent = `Terminado ${statusText} - ${execution.successful_cases || 0} exitosos de ${execution.total_cases || 0} casos`;
            console.log(`[EXECUTION_COMPLETED] Descripción del paso actualizada: ${currentStepElement.textContent}`);
        }
        
        // Actualizar nombre del caso actual para mostrar estado final
        const currentCaseNameElement = document.getElementById('currentCaseName');
        if (currentCaseNameElement) {
            const successRate = execution.success_rate || 0;
            const emoji = successRate >= 80 ? '✅' : successRate >= 50 ? '⚠️' : '❌';
            currentCaseNameElement.textContent = `${emoji} Ejecución completada (${successRate}% éxito)`;
            console.log(`[EXECUTION_COMPLETED] Nombre del caso actualizado: ${currentCaseNameElement.textContent}`);
        }
        
        // Actualizar progreso del caso actual al 100%
        const currentCaseProgressElement = document.getElementById('currentCaseProgress');
        const currentCaseProgressBar = document.getElementById('currentCaseProgressBar');
        if (currentCaseProgressElement) {
            currentCaseProgressElement.textContent = '100%';
            console.log(`[EXECUTION_COMPLETED] Progreso del caso actualizado a 100%`);
        }
        if (currentCaseProgressBar) {
            currentCaseProgressBar.style.width = '100%';
            // Cambiar color según éxito
            const successRate = execution.success_rate || 0;
            currentCaseProgressBar.className = successRate >= 80 ? 
                'progress-bar bg-success' : 
                successRate >= 50 ? 'progress-bar bg-warning' : 'progress-bar bg-danger';
            console.log(`[EXECUTION_COMPLETED] Barra de progreso actualizada a 100% con clase: ${currentCaseProgressBar.className}`);
        }
        
        // Remover animaciones de progreso para indicar finalización
        const progressBars = document.querySelectorAll('#executionProgressModal .progress-bar-animated');
        progressBars.forEach(bar => {
            bar.classList.remove('progress-bar-animated', 'progress-bar-striped');
        });
        console.log(`[EXECUTION_COMPLETED] Removidas animaciones de ${progressBars.length} barras de progreso`);
        
        // Habilitar botón de descarga de reporte
        document.getElementById('downloadExecutionReport').disabled = false;
        console.log(`[EXECUTION_COMPLETED] Botón de descarga habilitado`);
        
        // Ocultar loader global que se mostró al iniciar la ejecución
        console.log(`[EXECUTION_COMPLETED] Ocultando loader global...`);
        this.hideLoader();
        
        // Agregar botón para cerrar el modal automáticamente
        const modalFooter = document.querySelector('#executionProgressModal .modal-footer');
        if (modalFooter) {
            // Cambiar el texto y funcionalidad del botón Cerrar para que sea más prominente
            const closeButton = modalFooter.querySelector('[data-bs-dismiss="modal"]');
            if (closeButton) {
                closeButton.className = 'btn btn-success btn-lg';
                closeButton.innerHTML = '<i class="fas fa-check me-2"></i>Finalizar y Cerrar';
                console.log(`[EXECUTION_COMPLETED] Botón de cierre actualizado`);
            }
        }
        
        // Programar cierre automático del modal después de 10 segundos
        setTimeout(() => {
            console.log(`[EXECUTION_COMPLETED] Cerrando modal automáticamente después de 10 segundos`);
            const modal = bootstrap.Modal.getInstance(document.getElementById('executionProgressModal'));
            if (modal) {
                modal.hide();
                console.log(`[EXECUTION_COMPLETED] Modal cerrado automáticamente`);
            }
        }, 10000);
        
        // Actualizar resultados de casos con la información de ejecución
        console.log(`[EXECUTION_COMPLETED] Actualizando resultados de casos...`);
        this.updateCasesWithExecutionResults(execution);
        
        // Refrescar la vista principal para mostrar los resultados
        console.log(`[EXECUTION_COMPLETED] Refrescando vista principal...`);
        this.refreshMainView();
        
        // Asegurar que el spinner se oculte definitivamente y limpiar completamente la interfaz
        console.log(`[EXECUTION_COMPLETED] Ocultando spinner definitivamente...`);
        this.hideLoader();
        
        // Limpieza adicional: ocultar mensajes de ejecución específicos
        setTimeout(() => {
            console.log(`[EXECUTION_COMPLETED] Realizando limpieza adicional de la interfaz...`);
            
            try {
                // Buscar elementos específicos con IDs conocidos que puedan contener mensajes de ejecución
                const loaderMessage = document.getElementById('loaderMessage');
                if (loaderMessage && loaderMessage.textContent.includes('Iniciando ejecución')) {
                    console.log(`[EXECUTION_COMPLETED] Ocultando mensaje de loader`);
                    loaderMessage.style.display = 'none';
                }
                
                console.log(`[EXECUTION_COMPLETED] Limpieza adicional completada`);
            } catch (error) {
                console.error(`[EXECUTION_COMPLETED] Error en limpieza adicional:`, error);
            }
        }, 100);
        
        // Mostrar notificación de finalización
        const successRate = execution.success_rate || 0;
        const alertType = successRate >= 80 ? 'success' : successRate >= 50 ? 'warning' : 'danger';
        
        const alertMessage = `Ejecución completada: ${execution.successful_cases || 0} exitosos, ${execution.failed_cases || 0} fallidos (${successRate}% éxito). El modal se cerrará automáticamente en 10 segundos.`;
        console.log(`[EXECUTION_COMPLETED] Mostrando alerta: ${alertMessage}`);
        this.showAlert(alertMessage, alertType);
        
        console.log(`[EXECUTION_COMPLETED] Finalización completada exitosamente`);
    }
    
    updateCasesWithExecutionResults(execution) {
        // Actualiza los casos con los resultados de la ejecución
        try {
            if (!execution.results || !Array.isArray(execution.results)) {
                console.log(`[UPDATE_CASES] No hay resultados de ejecución disponibles`);
                return;
            }
            
            execution.results.forEach((result, index) => {
                const caseId = this.testCases[index]?.id;
                if (caseId && this.testCases[index]) {
                    // Actualizar el caso con el resultado
                    this.testCases[index].execution_result = {
                        status: result.status,
                        success: result.success,
                        message: result.message,
                        execution_time: result.execution_time,
                        screenshots_count: result.screenshots_count,
                        completed_at: result.completed_at
                    };
                    
                    console.log(`[UPDATE_CASES] Caso ${caseId} actualizado: ${result.status} (éxito: ${result.success})`);
                }
            });
            
        } catch (error) {
            console.error(`[UPDATE_CASES] Error actualizando casos:`, error);
        }
    }
    
    refreshMainView() {
        // Refresca la vista principal para mostrar los resultados actualizados
        try {
            console.log(`[REFRESH_VIEW] Refrescando vista principal...`);
            
            // Actualizar estadísticas
            this.updateStatistics();
            
            // Refrescar la vista de casos activa
            const activeTab = document.querySelector('.nav-pills .nav-link.active');
            if (activeTab) {
                const tabId = activeTab.getAttribute('data-bs-target');
                
                if (tabId === '#valid-cases' || activeTab.textContent.includes('Válidos')) {
                    this.displayValidCases();
                } else if (tabId === '#invalid-cases' || activeTab.textContent.includes('Problemas')) {
                    this.displayInvalidCases();
                } else {
                    this.displayAllCases();
                }
            } else {
                // Si no hay tab activo, mostrar todos los casos
                this.displayAllCases();
            }
            
            // Actualizar botones de acción
            this.updateActionButtons();
            
            console.log(`[REFRESH_VIEW] Vista principal refrescada exitosamente`);
            
        } catch (error) {
            console.error(`[REFRESH_VIEW] Error refrescando vista:`, error);
        }
    }
    
    viewCase(caseId) {
        const testCase = this.testCases.find(tc => tc.id === caseId);
        if (!testCase) {
            this.showAlert('Caso de prueba no encontrado', 'error');
            return;
        }
        
        // Crear modal de vista rápida
        const modalHtml = `
            <div class="modal fade" id="viewCaseModal" tabindex="-1" aria-labelledby="viewCaseModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content tech-card">
                        <div class="modal-header tech-panel-header">
                            <h5 class="modal-title tech-panel-title" id="viewCaseModalLabel">
                                <i class="fas fa-eye me-2"></i>
                                Detalles del Caso: ${testCase.id}
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <strong>Nombre:</strong>
                                    <div class="text-light">${testCase.nombre || 'No especificado'}</div>
                                </div>
                                <div class="col-md-6">
                                    <strong>Estado:</strong>
                                    <span class="badge ${testCase.es_valido ? 'bg-success' : 'bg-danger'}">
                                        ${testCase.es_valido ? 'Válido' : 'Con problemas'}
                                    </span>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <strong>Historia de Usuario:</strong>
                                <div class="text-light">${testCase.historia_usuario || 'No especificada'}</div>
                            </div>
                            
                            <div class="mb-3">
                                <strong>Objetivo:</strong>
                                <div class="text-light">${testCase.objetivo || 'No especificado'}</div>
                            </div>
                            
                            <div class="mb-3">
                                <strong>Precondición:</strong>
                                <div class="text-light">${testCase.precondicion || 'No especificada'}</div>
                            </div>
                            
                            <div class="mb-3">
                                <strong>Pasos de Ejecución:</strong>
                                <div class="text-light" style="white-space: pre-wrap;">${testCase.pasos || 'No especificados'}</div>
                            </div>
                            
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <strong>Datos de Prueba:</strong>
                                    <div class="text-light" style="white-space: pre-wrap;">${testCase.datos_prueba || 'No especificados'}</div>
                                </div>
                                <div class="col-md-6">
                                    <strong>Resultado Esperado:</strong>
                                    <div class="text-light" style="white-space: pre-wrap;">${testCase.resultado_esperado || 'No especificado'}</div>
                                </div>
                            </div>
                            
                            ${testCase.url_extraida ? `
                                <div class="mb-3">
                                    <strong>URL Detectada:</strong>
                                    <div class="text-info">${testCase.url_extraida}</div>
                                </div>
                            ` : ''}
                            
                            ${testCase.problemas && testCase.problemas.length > 0 ? `
                                <div class="mb-3">
                                    <strong class="text-danger">Problemas Detectados:</strong>
                                    <ul class="text-danger">
                                        ${testCase.problemas.map(p => `<li>${p}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                            
                            ${testCase.sugerencias && testCase.sugerencias.length > 0 ? `
                                <div class="mb-3">
                                    <strong class="text-info">Sugerencias de Mejora:</strong>
                                    <ul class="text-info">
                                        ${testCase.sugerencias.map(s => `<li>${s}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                            
                            ${testCase.instrucciones_qa_pilot ? `
                                <div class="mb-3">
                                    <strong class="text-success">Instrucciones QA-Pilot:</strong>
                                    <div class="bg-dark p-3 rounded text-light" style="white-space: pre-wrap; font-family: monospace;">${testCase.instrucciones_qa_pilot}</div>
                                </div>
                            ` : ''}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="tech-btn tech-btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                            <button type="button" class="tech-btn tech-btn-primary" onclick="bulkManager.editCase('${testCase.id}')" data-bs-dismiss="modal">
                                <i class="fas fa-edit me-2"></i>Editar Caso
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remover modal anterior si existe
        const existingModal = document.getElementById('viewCaseModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Agregar modal al DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Mostrar el modal
        const modal = new bootstrap.Modal(document.getElementById('viewCaseModal'));
        modal.show();
        
        // Limpiar modal cuando se cierre
        modal._element.addEventListener('hidden.bs.modal', function () {
            this.remove();
        });
    }

    editCase(caseId, isSequence = false) {
        const testCase = this.testCases.find(tc => tc.id === caseId);
        if (!testCase) {
            console.error('❌ Caso de prueba no encontrado:', caseId);
            this.showAlert('Caso de prueba no encontrado', 'error');
            return;
        }
        
        console.log('📝 Editando caso:', testCase);
        this.currentEditingCase = testCase;
        
        // Llenar información del caso
        const displayId = document.getElementById('editCaseDisplayId');
        const statusBadge = document.getElementById('editCaseStatus');
        
        if (displayId) displayId.textContent = testCase.id;
        if (statusBadge) {
            statusBadge.textContent = testCase.es_valido ? 'Válido' : 'Con problemas';
            statusBadge.className = `badge ${testCase.es_valido ? 'bg-success' : 'bg-danger'}`;
        }
        
        // Llenar el formulario de edición con verificación de elementos
        const fields = [
            { id: 'editCaseId', value: testCase.id, required: true },
            { id: 'editCaseName', value: testCase.nombre || '', required: true },
            { id: 'editCaseObjective', value: testCase.objetivo || '', required: true },
            { id: 'editCaseUserStory', value: testCase.historia_usuario || '', required: false },
            { id: 'editCasePrecondition', value: testCase.precondicion || '', required: false },
            { id: 'editCaseSteps', value: testCase.pasos || '', required: true },
            { id: 'editCaseData', value: testCase.datos_prueba || '', required: false },
            { id: 'editCaseExpected', value: testCase.resultado_esperado || '', required: true }
        ];
        
        fields.forEach(field => {
            const element = document.getElementById(field.id);
            if (element) {
                element.value = field.value;
                console.log(`✅ Campo ${field.id} llenado con:`, field.value);
            } else {
                console.warn(`⚠️ Elemento ${field.id} no encontrado`);
            }
        });
        
        // Mostrar problemas y sugerencias
        this.displayCaseProblems(testCase);
        
        // Actualizar título del modal si es parte de una secuencia
        const modalTitle = document.querySelector('#editCaseModal .modal-title');
        if (modalTitle) {
            if (isSequence && this.editingSequence) {
                modalTitle.innerHTML = `
                    <i class="fas fa-edit me-2"></i>
                    Editar Caso ${this.currentEditingIndex + 1} de ${this.editingSequence.length}: ${testCase.id}
                `;
            } else {
                modalTitle.innerHTML = `
                    <i class="fas fa-edit me-2"></i>
                    Editar Caso de Prueba: ${testCase.id}
                `;
            }
        }
        
        // Mostrar/ocultar botones de navegación
        this.updateSequenceNavigationButtons(isSequence);
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('editCaseModal'));
        modal.show();
        
        console.log('✅ Modal de edición mostrado');
    }
    
    updateSequenceNavigationButtons(isSequence) {
        const navContainer = document.getElementById('sequenceNavigationButtons');
        if (!navContainer) {
            console.warn('⚠️ Contenedor de navegación no encontrado');
            return;
        }
        
        let navigationHtml = '';
        
        if (isSequence && this.editingSequence) {
            const hasPrevious = this.currentEditingIndex > 0;
            const hasNext = this.currentEditingIndex < this.editingSequence.length - 1;
            
            navigationHtml = `
                <button type="button" class="tech-btn tech-btn-secondary me-2" 
                        onclick="bulkManager.previousCaseInSequence()" 
                        ${!hasPrevious ? 'disabled' : ''}>
                    <i class="fas fa-chevron-left me-2"></i>Anterior
                </button>
                <button type="button" class="tech-btn tech-btn-secondary me-2" 
                        onclick="bulkManager.nextCaseInSequence()" 
                        ${!hasNext ? 'disabled' : ''}>
                    Siguiente<i class="fas fa-chevron-right ms-2"></i>
                </button>
                <span class="text-muted ms-2">
                    <i class="fas fa-info-circle me-1"></i>
                    Caso ${this.currentEditingIndex + 1} de ${this.editingSequence.length}
                </span>
            `;
        }
        
        navContainer.innerHTML = navigationHtml;
        console.log('🔄 Botones de navegación actualizados:', isSequence);
    }
    
    displayCaseProblems(testCase) {
        const container = document.getElementById('caseProblems');
        if (!container) return;
        
        let html = '';
        
        if (testCase.problemas && testCase.problemas.length > 0) {
            html += `
                <div class="alert alert-danger">
                    <h6><i class="fas fa-exclamation-triangle me-2"></i>Problemas Identificados:</h6>
                    <ul class="mb-0">
                        ${testCase.problemas.map(p => `<li>${p}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        if (testCase.sugerencias && testCase.sugerencias.length > 0) {
            html += `
                <div class="alert alert-info">
                    <h6><i class="fas fa-lightbulb me-2"></i>Sugerencias de Mejora:</h6>
                    <ul class="mb-0">
                        ${testCase.sugerencias.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        container.innerHTML = html;
    }
    
    saveCaseChanges() {
        if (!this.currentEditingCase) {
            console.error('❌ No hay caso actual para guardar');
            return;
        }
        
        console.log('💾 Guardando cambios del caso:', this.currentEditingCase.id);
        
        const form = document.getElementById('editCaseForm');
        if (!form) {
            console.error('❌ Formulario de edición no encontrado');
            return;
        }
        
        const formData = new FormData(form);
        
        // Actualizar el caso actual con todos los campos
        this.currentEditingCase.nombre = formData.get('nombre') || '';
        this.currentEditingCase.objetivo = formData.get('objetivo') || '';
        this.currentEditingCase.historia_usuario = formData.get('historia_usuario') || '';
        this.currentEditingCase.precondicion = formData.get('precondicion') || '';
        this.currentEditingCase.pasos = formData.get('pasos') || '';
        this.currentEditingCase.datos_prueba = formData.get('datos_prueba') || '';
        this.currentEditingCase.resultado_esperado = formData.get('resultado_esperado') || '';
        
        console.log('✅ Caso actualizado:', this.currentEditingCase);
        
        // Actualizar la visualización
        this.displayAnalysisResults();
        
        // Cerrar modal
        const modalInstance = bootstrap.Modal.getInstance(document.getElementById('editCaseModal'));
        if (modalInstance) {
            modalInstance.hide();
        }
        
        this.showAlert('Cambios guardados exitosamente', 'success');
        
        // Si estamos en secuencia, continuar con el siguiente caso
        if (this.editingSequence && this.currentEditingIndex < this.editingSequence.length - 1) {
            setTimeout(() => {
                const continueNext = confirm('¿Deseas continuar editando el siguiente caso?');
                if (continueNext) {
                    this.nextCaseInSequence();
                }
            }, 500);
        }
    }
    
    async reanalyzeCase() {
        if (!this.currentEditingCase) return;
        
        const form = document.getElementById('editCaseForm');
        const formData = new FormData(form);
        
        // Actualizar datos temporalmente
        const updatedCase = {
            ...this.currentEditingCase,
            nombre: formData.get('nombre'),
            objetivo: formData.get('objetivo'),
            pasos: formData.get('pasos'),
            datos_prueba: formData.get('datos_prueba'),
            resultado_esperado: formData.get('resultado_esperado'),
            precondicion: formData.get('precondicion')
        };
        
        this.showLoader('Re-analizando caso...');
        
        try {
            const response = await fetch('/api/reanalyze_case', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    test_case: updatedCase
                })
            });
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                // Actualizar el caso con los nuevos resultados
                Object.assign(this.currentEditingCase, result.analyzed_case);
                
                // Actualizar la visualización del modal
                this.displayCaseProblems(this.currentEditingCase);
                
                // Actualizar la visualización principal
                this.displayAnalysisResults();
                
                this.showAlert('Re-análisis completado', 'success');
            } else {
                throw new Error(result.error || 'Error al re-analizar el caso');
            }
            
        } catch (error) {
            console.error('Error al re-analizar:', error);
            this.showAlert(`Error al re-analizar: ${error.message}`, 'danger');
        } finally {
            this.hideLoader();
        }
    }
    
    editAllProblematicCases() {
        const invalidCases = this.testCases.filter(tc => !tc.es_valido);
        
        if (invalidCases.length === 0) {
            this.showAlert('No hay casos con problemas para editar', 'info');
            return;
        }
        
        // Configurar edición en secuencia
        this.editingSequence = invalidCases.map(tc => tc.id);
        this.currentEditingIndex = 0;
        
        // Mostrar modal de confirmación
        const confirmed = confirm(`¿Deseas editar ${invalidCases.length} casos problemáticos en secuencia?\n\nPodrás navegar entre ellos usando los botones "Anterior" y "Siguiente".`);
        
        if (confirmed) {
            this.editCaseInSequence();
        }
    }
    
    editCaseInSequence() {
        if (!this.editingSequence || this.currentEditingIndex >= this.editingSequence.length) {
            this.showAlert('Edición en secuencia completada', 'success');
            this.editingSequence = null;
            this.currentEditingIndex = 0;
            return;
        }
        
        const caseId = this.editingSequence[this.currentEditingIndex];
        this.editCase(caseId, true); // true indica que es parte de una secuencia
    }
    
    nextCaseInSequence() {
        if (this.editingSequence && this.currentEditingIndex < this.editingSequence.length - 1) {
            this.currentEditingIndex++;
            this.editCaseInSequence();
        }
    }

    previousCaseInSequence() {
        if (this.editingSequence && this.currentEditingIndex > 0) {
            this.currentEditingIndex--;
            this.editCaseInSequence();
        }
    }

    openCaseEditor() {
        const invalidCases = this.testCases.filter(tc => !tc.es_valido);
        
        if (invalidCases.length === 0) {
            this.showAlert('No hay casos con problemas para editar', 'info');
            return;
        }
        
        // Abrir el primer caso con problemas
        this.editCase(invalidCases[0].id);
    }
    
    openSaveAsSuiteModal() {
        if (this.testCases.length === 0) {
            this.showAlert('No hay casos para guardar', 'warning');
            return;
        }
        
        // Generar nombre sugerido
        const timestamp = new Date().toISOString().slice(0, 16).replace('T', ' ');
        document.getElementById('suiteName').value = `Suite desde Excel - ${timestamp}`;
        
        const modal = new bootstrap.Modal(document.getElementById('saveAsSuiteModal'));
        modal.show();
    }
    
    async saveAsSuite() {
        const form = document.getElementById('saveAsSuiteForm');
        const formData = new FormData(form);
        
        const suiteName = formData.get('suite_name');
        const suiteDescription = formData.get('suite_description');
        const includeInvalid = formData.has('include_invalid');
        
        if (!suiteName.trim()) {
            this.showAlert('El nombre de la suite es obligatorio', 'warning');
            return;
        }
        
        const casesToSave = includeInvalid ? 
            this.testCases : 
            this.testCases.filter(tc => tc.es_valido);
        
        if (casesToSave.length === 0) {
            this.showAlert('No hay casos para guardar en la suite', 'warning');
            return;
        }
        
        this.showLoader('Guardando suite...');
        
        try {
            const response = await fetch('/api/save_excel_as_suite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    suite_name: suiteName,
                    suite_description: suiteDescription,
                    test_cases: casesToSave,
                    include_invalid: includeInvalid
                })
            });
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                // Cerrar modal
                bootstrap.Modal.getInstance(document.getElementById('saveAsSuiteModal')).hide();
                
                this.showAlert(`Suite "${suiteName}" guardada exitosamente`, 'success');
                
                // Opcionalmente redirigir a la página de suites
                if (confirm('¿Quieres ir a la página de suites para ver la suite creada?')) {
                    window.location.href = '/suites';
                }
            } else {
                throw new Error(result.error || 'Error al guardar la suite');
            }
            
        } catch (error) {
            console.error('Error al guardar suite:', error);
            this.showAlert(`Error al guardar suite: ${error.message}`, 'danger');
        } finally {
            this.hideLoader();
        }
    }
    
    async downloadExecutionReport() {
        if (!this.currentExecutionId) {
            this.showAlert('No hay ejecución disponible para generar reporte', 'warning');
            return;
        }
        
        const button = document.getElementById('downloadExecutionReport');
        const originalText = button.innerHTML;
        
        try {
            // Mostrar estado de carga
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generando Reporte...';
            button.disabled = true;
            
            this.showAlert('Generando reporte de ejecución masiva...', 'info');
            
            const response = await fetch(`/api/generate_bulk_word_report/${this.currentExecutionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            // Verificar si la respuesta es un archivo
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/vnd.openxmlformats-officedocument.wordprocessingml.document')) {
                // Es un archivo Word, descargarlo
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                
                // Generar nombre de archivo con timestamp
                const timestamp = new Date().toISOString().slice(0, 16).replace('T', '_').replace(/:/g, '-');
                a.download = `Reporte_Ejecucion_Masiva_${timestamp}.docx`;
                
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showAlert('Reporte de ejecución masiva descargado correctamente', 'success');
            } else {
                // Es una respuesta JSON con error
                const result = await response.json();
                throw new Error(result.message || 'Error al generar el reporte');
            }
            
        } catch (error) {
            console.error('Error al generar reporte:', error);
            this.showAlert(`Error al generar reporte: ${error.message}`, 'danger');
        } finally {
            // Restaurar estado del botón
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }
    
    showAnalysisProgress(message = 'Analizando...') {
        // Crear overlay de progreso si no existe
        let overlay = document.getElementById('analysisProgressOverlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'analysisProgressOverlay';
            overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
            overlay.style.cssText = 'background: rgba(0,0,0,0.9); z-index: 10000;';
            overlay.innerHTML = `
                <div class="text-center text-white">
                    <div class="analysis-progress-container">
                        <div class="analysis-icon mb-3">
                            <i class="fas fa-file-excel fa-4x text-primary"></i>
                        </div>
                        <h4 class="analysis-title mb-4">Analizando Casos de Prueba</h4>
                        <div class="progress mb-3" style="height: 25px; width: 400px; background: rgba(255,255,255,0.2);">
                            <div class="progress-bar progress-bar-striped progress-bar-animated bg-primary" 
                                 id="analysisProgressBar" role="progressbar" style="width: 0%"></div>
                        </div>
                        <div class="analysis-message mb-2" id="analysisMessage" style="font-size: 1.1em;">${message}</div>
                        <div class="analysis-details">
                            <small class="text-light" id="analysisDetails" style="opacity: 0.8;">Preparando análisis...</small>
                        </div>
                        <div class="analysis-stats mt-3" id="analysisStats" style="display: none;">
                            <div class="row text-center">
                                <div class="col-4">
                                    <div class="stat-number" id="totalCasesFound">0</div>
                                    <div class="stat-label">Casos Encontrados</div>
                                </div>
                                <div class="col-4">
                                    <div class="stat-number text-success" id="validCasesFound">0</div>
                                    <div class="stat-label">Casos Válidos</div>
                                </div>
                                <div class="col-4">
                                    <div class="stat-number text-warning" id="problematicCasesFound">0</div>
                                    <div class="stat-label">Con Problemas</div>
                                </div>
                            </div>
                        </div>
                        <div class="mt-3">
                            <small class="text-muted" style="opacity: 0.7;">Haz clic aquí para cerrar si el análisis se completa</small>
                        </div>
                    </div>
                </div>
            `;
            
            // Agregar evento de clic para cerrar el overlay manualmente
            overlay.addEventListener('click', () => {
                console.log('👆 Usuario hizo clic en overlay, cerrando...');
                this.hideAnalysisProgress();
            });
            document.body.appendChild(overlay);
        } else {
            // Actualizar mensaje
            const messageElement = overlay.querySelector('#analysisMessage');
            if (messageElement) {
                messageElement.textContent = message;
            }
        }
        
        overlay.style.display = 'flex';
        
        // Simular progreso inicial
        this.simulateAnalysisProgress();
    }
    
    simulateAnalysisProgress() {
        let progress = 0;
        const progressBar = document.getElementById('analysisProgressBar');
        const detailsElement = document.getElementById('analysisDetails');
        const messageElement = document.getElementById('analysisMessage');
        
        // Obtener información del archivo si está disponible
        const fileInput = document.getElementById('excelFile');
        const fileName = fileInput?.files[0]?.name || 'archivo Excel';
        const fileSize = fileInput?.files[0]?.size || 0;
        const fileSizeMB = (fileSize / (1024 * 1024)).toFixed(1);
        
        const steps = [
            { 
                progress: 15, 
                message: `Leyendo ${fileName}...`,
                details: `Procesando archivo de ${fileSizeMB}MB`, 
                delay: 600 
            },
            { 
                progress: 30, 
                message: 'Detectando estructura de datos...',
                details: 'Identificando headers y columnas relevantes', 
                delay: 800 
            },
            { 
                progress: 45, 
                message: 'Extrayendo casos de prueba...',
                details: 'Analizando filas y creando casos', 
                delay: 1000 
            },
            { 
                progress: 60, 
                message: 'Validando campos obligatorios...',
                details: 'Verificando URLs, nombres y objetivos', 
                delay: 700 
            },
            { 
                progress: 75, 
                message: 'Analizando calidad y coherencia...',
                details: 'Aplicando reglas de validación inteligente', 
                delay: 900 
            },
            { 
                progress: 90, 
                message: 'Generando sugerencias de mejora...',
                details: 'Preparando recomendaciones para casos problemáticos', 
                delay: 500 
            }
        ];
        
        let stepIndex = 0;
        
        const updateProgress = () => {
            if (stepIndex < steps.length && document.getElementById('analysisProgressOverlay')?.style.display !== 'none') {
                const step = steps[stepIndex];
                progress = step.progress;
                
                if (progressBar) {
                    progressBar.style.width = `${progress}%`;
                }
                
                if (messageElement) {
                    messageElement.textContent = step.message;
                }
                
                if (detailsElement) {
                    detailsElement.textContent = step.details;
                }
                
                stepIndex++;
                setTimeout(updateProgress, step.delay);
            }
        };
        
        updateProgress();
    }
    
    updateAnalysisProgress(progress, message, details = '', stats = null) {
        const progressBar = document.getElementById('analysisProgressBar');
        const messageElement = document.getElementById('analysisMessage');
        const detailsElement = document.getElementById('analysisDetails');
        const statsElement = document.getElementById('analysisStats');
        
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        
        if (messageElement) {
            messageElement.textContent = message;
        }
        
        if (detailsElement && details) {
            detailsElement.textContent = details;
        }
        
        // Mostrar estadísticas si están disponibles
        if (stats && statsElement) {
            document.getElementById('totalCasesFound').textContent = stats.total || 0;
            document.getElementById('validCasesFound').textContent = stats.valid || 0;
            document.getElementById('problematicCasesFound').textContent = stats.problematic || 0;
            statsElement.style.display = 'block';
        }
    }
    
    hideAnalysisProgress() {
        console.log('🔄 Intentando ocultar overlay de progreso...');
        
        const overlay = document.getElementById('analysisProgressOverlay');
        if (overlay) {
            console.log('✅ Overlay encontrado, ocultando...');
            overlay.style.display = 'none';
            
            // Forzar eliminación del overlay después de un momento
            setTimeout(() => {
                if (overlay.parentNode) {
                    console.log('🗑️ Eliminando overlay del DOM...');
                    overlay.remove();
                }
            }, 100);
            
            console.log('✅ Overlay ocultado correctamente');
        } else {
            console.log('❌ No se encontró el overlay de progreso');
        }
    }
    
    showLoader(message = 'Procesando...') {
        console.log(`[LOADER] Mostrando loader con mensaje: "${message}"`);
        // Crear o mostrar loader
        let loader = document.getElementById('globalLoader');
        if (!loader) {
            console.log(`[LOADER] Creando nuevo loader`);
            loader = document.createElement('div');
            loader.id = 'globalLoader';
            loader.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
            loader.style.cssText = 'background: rgba(0,0,0,0.8); z-index: 9999;';
            loader.innerHTML = `
                <div class="text-center text-white">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <div id="loaderMessage">${message}</div>
                </div>
            `;
            document.body.appendChild(loader);
        } else {
            console.log(`[LOADER] Actualizando loader existente`);
            document.getElementById('loaderMessage').textContent = message;
            loader.style.display = 'flex';
        }
    }
    
    hideLoader() {
        console.log(`[LOADER] Intentando ocultar loader`);
        try {
            const loader = document.getElementById('globalLoader');
            if (loader) {
                console.log(`[LOADER] Loader encontrado, eliminando...`);
                loader.remove();
                console.log(`[LOADER] Loader eliminado exitosamente`);
            } else {
                console.log(`[LOADER] No se encontró loader para ocultar`);
            }
        } catch (error) {
            console.error(`[LOADER] Error al eliminar loader:`, error);
        }
    }
    
    showAlert(message, type = 'info') {
        // Crear alerta temporal
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Inicializando BulkExecutionManager v2025062315...');
    window.bulkManager = new BulkExecutionManager();
    console.log('✅ BulkExecutionManager inicializado correctamente');
});

// Función global para editar casos (llamada desde HTML)
function editCase(caseId) {
    if (window.bulkManager) {
        window.bulkManager.editCase(caseId);
    }
} 