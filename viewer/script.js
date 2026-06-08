document.addEventListener('DOMContentLoaded', () => {
    const urlDatos = '../data/horario_optimizado.json';
    const contenedorHorario = document.getElementById('contenedorHorario');
    const selectorGrupo = document.getElementById('selectorGrupo');
    
    // Configuración
    const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];
    const horas = ['7:00', '8:00', '9:00', '10:00', '11:00', '12:00'];
    
    // Mantener registro de colores para diferentes materias
    const coloresMaterias = {};
    let indiceColor = 0;

    // Obtener datos
    contenedorHorario.innerHTML = '<div class="loading">Cargando horario...</div>';
    
    fetch(urlDatos)
        .then(respuesta => {
            if (!respuesta.ok) {
                throw new Error(`¡Error HTTP! estado: ${respuesta.status}`);
            }
            return respuesta.json();
        })
        .then(datos => {
            procesarDatosHorario(datos);
        })
        .catch(error => {
            console.error('Error al obtener datos:', error);
            contenedorHorario.innerHTML = `
                <div class="error-message">
                    <h3>No se pudo cargar el horario</h3>
                    <p>Si estás abriendo este archivo directamente desde el explorador (file://), tu navegador podría estar bloqueando la carga del JSON por seguridad.</p>
                    <br/>
                    <p><strong>Solución:</strong> Ejecuta el script <code>serve.py</code> para iniciar un servidor local y ver el horario correctamente.</p>
                </div>
            `;
        });

    function procesarDatosHorario(datos) {
        // Agrupar datos por grupo_id
        const grupos = {};
        
        datos.forEach(sesion => {
            if (!grupos[sesion.grupo_id]) {
                grupos[sesion.grupo_id] = {};
                // Inicializar matriz vacía
                horas.forEach(h => {
                    grupos[sesion.grupo_id][h] = {};
                    dias.forEach(d => {
                        grupos[sesion.grupo_id][h][d] = null;
                    });
                });
            }
            
            // Asignar sesión a la matriz
            grupos[sesion.grupo_id][sesion.hora][sesion.dia] = sesion;
            
            // Asignar clase de color a la materia si no está asignada
            if (!coloresMaterias[sesion.materia_id]) {
                coloresMaterias[sesion.materia_id] = `materia-color-${indiceColor % 6}`;
                indiceColor++;
            }
        });
        
        renderizarInterfaz(grupos);
    }

    function renderizarInterfaz(grupos) {
        contenedorHorario.innerHTML = '';
        selectorGrupo.innerHTML = '';
        
        const idsGrupos = Object.keys(grupos).sort();
        
        idsGrupos.forEach((idGrupo, indice) => {
            // Crear Botón de Pestaña
            const boton = document.createElement('button');
            boton.className = `group-btn ${indice === 0 ? 'active' : ''}`;
            boton.textContent = `Grupo ${idGrupo.replace('GRP', '')}`;
            boton.onclick = () => cambiarPestana(idGrupo);
            selectorGrupo.appendChild(boton);
            
            // Crear Tabla
            const contenedorTabla = document.createElement('div');
            contenedorTabla.className = `schedule-table-wrapper ${indice === 0 ? 'active' : ''}`;
            contenedorTabla.id = `tabla-${idGrupo}`;
            
            let htmlTabla = `
                <table>
                    <thead>
                        <tr>
                            <th>Hora</th>
                            ${dias.map(d => `<th>${d}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            horas.forEach(h => {
                htmlTabla += `<tr>
                    <td class="time-col">${h}</td>
                `;
                
                dias.forEach(d => {
                    const sesion = grupos[idGrupo][h][d];
                    if (sesion) {
                        const claseColor = coloresMaterias[sesion.materia_id];
                        htmlTabla += `
                            <td>
                                <div class="class-card ${claseColor}">
                                    <div class="class-materia">${sesion.materia_id}</div>
                                    <div class="class-details">
                                        <div>
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                                            ${sesion.profesor_id}
                                        </div>
                                        <div>
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
                                            ${sesion.aula_id}
                                        </div>
                                    </div>
                                </div>
                            </td>
                        `;
                    } else {
                        htmlTabla += `
                            <td>
                                <div class="empty-cell">Libre</div>
                            </td>
                        `;
                    }
                });
                
                htmlTabla += `</tr>`;
            });
            
            htmlTabla += `
                    </tbody>
                </table>
            `;
            
            contenedorTabla.innerHTML = htmlTabla;
            contenedorHorario.appendChild(contenedorTabla);
        });
    }

    // Función global para cambiar de pestaña
    window.cambiarPestana = function(idGrupoActivo) {
        // Actualizar botones
        document.querySelectorAll('.group-btn').forEach(boton => {
            if (boton.textContent.includes(idGrupoActivo.replace('GRP', ''))) {
                boton.classList.add('active');
            } else {
                boton.classList.remove('active');
            }
        });
        
        // Actualizar tablas
        document.querySelectorAll('.schedule-table-wrapper').forEach(contenedor => {
            if (contenedor.id === `tabla-${idGrupoActivo}`) {
                contenedor.classList.add('active');
            } else {
                contenedor.classList.remove('active');
            }
        });
    }
});
