document.addEventListener('DOMContentLoaded', () => {
    const urlsOpciones = [
        '../data/horario_opcion_1.json',
        '../data/horario_opcion_2.json',
        '../data/horario_opcion_3.json'
    ];

    const contenedorHorario = document.getElementById('contenedorHorario');
    const selectorGrupo = document.getElementById('selectorGrupo');

    // Configuración
    const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];
    const horas = ['7:00', '8:00', '9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'];

    // Colores por materia
    const coloresMaterias = {};
    let indiceColor = 0;

    // Mostrar carga
    contenedorHorario.innerHTML = '<div class="loading">Cargando horario...</div>';

    // Obtener datos de todas las opciones
    Promise.all(
        urlsOpciones.map((url, i) =>
            fetch(url)
                .then(r => r.ok ? r.json() : [])
                .then(data => ({
                    opcion: i + 1,
                    sesiones: data
                }))
                .catch(() => ({
                    opcion: i + 1,
                    sesiones: []
                }))
        )
    )
    .then(opciones =>
        procesarOpciones(
            opciones.filter(o => o.sesiones.length > 0)
        )
    );

    function procesarOpciones(opciones) {
        const grupos = {};

        opciones.forEach(({ opcion, sesiones }) => {

            const claveGrupo = `opcion_${opcion}`;

            sesiones.forEach(sesion => {

                if (!grupos[claveGrupo]) {

                    grupos[claveGrupo] = {
                        opcion: opcion,
                        horario: {}
                    };

                    horas.forEach(h => {
                        grupos[claveGrupo].horario[h] = {};

                        dias.forEach(d => {
                            grupos[claveGrupo].horario[h][d] = null;
                        });
                    });
                }

                grupos[claveGrupo]
                    .horario[sesion.hora][sesion.dia] = sesion;

                if (!coloresMaterias[sesion.materia_id]) {
                    coloresMaterias[sesion.materia_id] =
                        `materia-color-${indiceColor % 6}`;
                    indiceColor++;
                }
            });

        });

        renderizarInterfaz(grupos);
    }

    function renderizarInterfaz(grupos) {
        contenedorHorario.innerHTML = '';
        selectorGrupo.innerHTML = '';

        const idsGrupos = Object.keys(grupos).sort();

        idsGrupos.forEach((idGrupo, indice) => {

            // Botón de pestaña
            const boton = document.createElement('button');
            boton.className = `group-btn ${indice === 0 ? 'active' : ''}`;
            boton.textContent = `Opción ${grupos[idGrupo].opcion}`;
            boton.dataset.grupo = idGrupo;
            boton.onclick = () => cambiarPestana(idGrupo);

            selectorGrupo.appendChild(boton);

            // Contenedor de tabla
            const contenedorTabla = document.createElement('div');
            contenedorTabla.className =
                `schedule-table-wrapper ${indice === 0 ? 'active' : ''}`;
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

                htmlTabla += `
                    <tr>
                        <td class="time-col">${h}</td>
                `;

                dias.forEach(d => {

                    const sesion = grupos[idGrupo].horario[h][d];

                    if (sesion) {

                        const claseColor =
                            coloresMaterias[sesion.materia_id];

                        htmlTabla += `
                            <td>
                                <div class="class-card ${claseColor}">
                                    <div class="class-materia">
                                        ${sesion.materia_id}
                                    </div>

                                    <div class="class-details">
                                        <div>
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                                <circle cx="12" cy="7" r="4"></circle>
                                            </svg>
                                            ${sesion.profesor_id}
                                        </div>

                                        <div>
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                                                <polyline points="9 22 9 12 15 12 15 22"></polyline>
                                            </svg>
                                            ${sesion.aula_id}
                                        </div>
                                    </div>
                                </div>
                            </td>
                        `;

                    } else {

                        htmlTabla += `
                            <td>
                                <div class="empty-cell">
                                    Libre
                                </div>
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

    // Cambio de pestañas
    window.cambiarPestana = function(idGrupoActivo) {

        document.querySelectorAll('.group-btn').forEach(boton => {
            boton.classList.toggle(
                'active',
                boton.dataset.grupo === idGrupoActivo
            );
        });

        document.querySelectorAll('.schedule-table-wrapper').forEach(tabla => {
            tabla.classList.toggle(
                'active',
                tabla.id === `tabla-${idGrupoActivo}`
            );
        });
    };
});