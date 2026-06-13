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
    const horas = ['7:00', '8:00', '9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '24:00'];

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
        window._gruposData = grupos;
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
    window.generarHorario = function() {
        const btn = document.getElementById('btnGenerar');
        btn.textContent = 'Generando...';
        btn.disabled = true;
        contenedorHorario.innerHTML = '<div class="loading">Corriendo algoritmo, esto puede tardar unos segundos...</div>';

        const maxHorasLibres = parseInt(document.getElementById('maxHorasLibres').value) ?? 3;
        fetch('/generar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ maxHorasLibres })
        })
            .then(r => r.json())
            .then(res => {
                if (res.ok) {
                    btn.textContent = 'Generar horario';
                    btn.disabled = false;
                    console.log('OUTPUT:', res.output);
                    if (res.output && res.output.includes('⚠')) {
                        const advertencias = res.output
                            .split('\n')
                            .filter(l => l.includes('⚠'))
                            .join('\n');
                        contenedorHorario.innerHTML = `<div class="error-message" style="white-space:pre-line;">${advertencias}</div>`;
                        return;
                    }
                    Promise.all(
                        urlsOpciones.map((url, i) =>
                            fetch(url + '?t=' + Date.now())
                                .then(r => r.ok ? r.json() : [])
                                .then(data => ({ opcion: i + 1, sesiones: data }))
                                .catch(() => ({ opcion: i + 1, sesiones: [] }))
                        )
                    ).then(opciones =>
                        procesarOpciones(opciones.filter(o => o.sesiones.length > 0))
                    );
                } else {
                    contenedorHorario.innerHTML = `<div class="error-message">Error al generar: ${res.error}</div>`;
                    btn.textContent = 'Generar horario';
                    btn.disabled = false;
                }
            })
            .catch(() => {
                contenedorHorario.innerHTML = '<div class="error-message">No se pudo conectar con el servidor.</div>';
                btn.textContent = 'Generar horario';
                btn.disabled = false;
            });
    }
    document.getElementById('btnGenerar').addEventListener('click', generarHorario);
    window.descargarPDF = function() {
        const tablaActiva = document.querySelector('.schedule-table-wrapper.active');
        const pestanaActiva = document.querySelector('.group-btn.active');

        if (!tablaActiva) {
            alert('Primero genera un horario.');
            return;
        }

        const nombreOpcion = pestanaActiva ? pestanaActiva.textContent : 'Horario';
        const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];
        const horas1 = ['7:00','8:00','9:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00'];
        const horas2 = ['19:00','20:00','21:00','22:00','23:00','24:00'];

        // Obtener datos de la tabla activa
        const idGrupo = tablaActiva.id.replace('tabla-', '');
        const grupo = window._gruposData[idGrupo];

        function generarTablaHTML(horas, titulo) {
            let html = `
                <div style="font-family: Arial, sans-serif; padding: 16px; background: white;">
                    <h2 style="text-align:center; color:#1a1a2e; margin-bottom:12px;">${nombreOpcion} — ${titulo}</h2>
                    <table style="width:100%; border-collapse:collapse; font-size:11px;">
                        <thead>
                            <tr style="background:#1a1a2e; color:white;">
                                <th style="padding:8px; border:1px solid #ccc;">Hora</th>
                                ${dias.map(d => `<th style="padding:8px; border:1px solid #ccc;">${d}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
            `;

            horas.forEach((h, i) => {
                const bg = i % 2 === 0 ? '#f0f4ff' : '#ffffff';
                html += `<tr style="background:${bg};">
                    <td style="padding:8px; border:1px solid #ccc; font-weight:bold; color:#1a1a2e;">${h}</td>`;

                dias.forEach(d => {
                    const sesion = grupo?.horario[h]?.[d];
                    if (sesion) {
                        html += `
                            <td style="padding:6px; border:1px solid #ccc; background:#dbeafe;">
                                <div style="font-weight:bold; color:#1e3a8a;">${sesion.materia_id}</div>
                                <div style="color:#374151; font-size:10px;">👤 ${sesion.profesor_id}</div>
                                <div style="color:#374151; font-size:10px;">🏫 ${sesion.aula_id}</div>
                            </td>`;
                    } else {
                        html += `<td style="padding:6px; border:1px solid #ccc; color:#9ca3af; text-align:center;">Libre</td>`;
                    }
                });

                html += `</tr>`;
            });

            html += `</tbody></table></div>`;
            return html;
        }

        const opciones = {
            margin: 8,
            filename: `${nombreOpcion}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, backgroundColor: '#ffffff' },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'landscape' }
        };

        const pagina1 = document.createElement('div');
        pagina1.innerHTML = generarTablaHTML(horas1, 'Parte 1 (7:00 – 18:00)');

        const pagina2 = document.createElement('div');
        pagina2.style.pageBreakBefore = 'always';
        pagina2.innerHTML = generarTablaHTML(horas2, 'Parte 2 (19:00 – 24:00)');

        const contenedor = document.createElement('div');
        contenedor.appendChild(pagina1);
        contenedor.appendChild(pagina2);
        document.body.appendChild(contenedor);

        html2pdf().set(opciones).from(contenedor).save().then(() => {
            document.body.removeChild(contenedor);
        });
    };
});