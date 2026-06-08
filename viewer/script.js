document.addEventListener('DOMContentLoaded', () => {
    const dataUrl = '../data/horario_optimizado.json';
    const scheduleContainer = document.getElementById('scheduleContainer');
    const groupSelector = document.getElementById('groupSelector');
    
    // Config
    const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];
    const hours = ['7:00', '8:00', '9:00', '10:00', '11:00', '12:00'];
    
    // Keep track of colors for different subjects
    const subjectColors = {};
    let colorIndex = 0;

    // Fetch data
    scheduleContainer.innerHTML = '<div class="loading">Cargando horario...</div>';
    
    fetch(dataUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            processScheduleData(data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            scheduleContainer.innerHTML = `
                <div class="error-message">
                    <h3>No se pudo cargar el horario</h3>
                    <p>Si estás abriendo este archivo directamente desde el explorador (file://), tu navegador podría estar bloqueando la carga del JSON por seguridad.</p>
                    <br/>
                    <p><strong>Solución:</strong> Ejecuta el script <code>serve.py</code> para iniciar un servidor local y ver el horario correctamente.</p>
                </div>
            `;
        });

    function processScheduleData(data) {
        // Group data by group_id
        const groups = {};
        
        data.forEach(session => {
            if (!groups[session.grupo_id]) {
                groups[session.grupo_id] = {};
                // Initialize empty matrix
                hours.forEach(h => {
                    groups[session.grupo_id][h] = {};
                    days.forEach(d => {
                        groups[session.grupo_id][h][d] = null;
                    });
                });
            }
            
            // Assign session to matrix
            groups[session.grupo_id][session.hora][session.dia] = session;
            
            // Assign color class to subject if not assigned
            if (!subjectColors[session.materia_id]) {
                subjectColors[session.materia_id] = `materia-color-${colorIndex % 6}`;
                colorIndex++;
            }
        });
        
        renderUI(groups);
    }

    function renderUI(groups) {
        scheduleContainer.innerHTML = '';
        groupSelector.innerHTML = '';
        
        const groupIds = Object.keys(groups).sort();
        
        groupIds.forEach((groupId, index) => {
            // Create Tab Button
            const btn = document.createElement('button');
            btn.className = `group-btn ${index === 0 ? 'active' : ''}`;
            btn.textContent = `Grupo ${groupId.replace('GRP', '')}`;
            btn.onclick = () => switchTab(groupId);
            groupSelector.appendChild(btn);
            
            // Create Table
            const tableWrapper = document.createElement('div');
            tableWrapper.className = `schedule-table-wrapper ${index === 0 ? 'active' : ''}`;
            tableWrapper.id = `table-${groupId}`;
            
            let tableHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Hora</th>
                            ${days.map(d => `<th>${d}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            hours.forEach(h => {
                tableHTML += `<tr>
                    <td class="time-col">${h}</td>
                `;
                
                days.forEach(d => {
                    const session = groups[groupId][h][d];
                    if (session) {
                        const colorClass = subjectColors[session.materia_id];
                        tableHTML += `
                            <td>
                                <div class="class-card ${colorClass}">
                                    <div class="class-materia">${session.materia_id}</div>
                                    <div class="class-details">
                                        <div>
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                                            ${session.profesor_id}
                                        </div>
                                        <div>
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
                                            ${session.aula_id}
                                        </div>
                                    </div>
                                </div>
                            </td>
                        `;
                    } else {
                        tableHTML += `
                            <td>
                                <div class="empty-cell">Libre</div>
                            </td>
                        `;
                    }
                });
                
                tableHTML += `</tr>`;
            });
            
            tableHTML += `
                    </tbody>
                </table>
            `;
            
            tableWrapper.innerHTML = tableHTML;
            scheduleContainer.appendChild(tableWrapper);
        });
    }

    // Global tab switcher function
    window.switchTab = function(activeGroupId) {
        // Update buttons
        document.querySelectorAll('.group-btn').forEach(btn => {
            if (btn.textContent.includes(activeGroupId.replace('GRP', ''))) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Update tables
        document.querySelectorAll('.schedule-table-wrapper').forEach(wrapper => {
            if (wrapper.id === `table-${activeGroupId}`) {
                wrapper.classList.add('active');
            } else {
                wrapper.classList.remove('active');
            }
        });
    }
});
