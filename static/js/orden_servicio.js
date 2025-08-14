// ==============================
// Variables globales
// ==============================
const listaMarcas = [
    "Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "Volkswagen",
    "BMW", "Mercedes-Benz", "Audi", "Mazda", "Hyundai", "Kia",
    "Jeep", "Subaru", "Peugeot", "Renault", "Mitsubishi", "Volvo",
    "Fiat", "Land Rover"
];

const marcaInput = document.getElementById("marcaInput");
const sugerenciasDiv = document.getElementById("sugerenciasMarca");
const vinInput = document.getElementById("vinInput");
const btnBuscarVin = document.getElementById("buscarVin");
const buscarServicioInput = document.getElementById("buscarServicio");
const contenedorSeleccionados = document.getElementById("serviciosSeleccionados");

// ==============================
// Funciones auxiliares
// ==============================

// Mostrar sugerencias de marca
function mostrarSugerenciasMarcas() {
    const valor = marcaInput.value.toLowerCase().trim();
    sugerenciasDiv.innerHTML = "";

    if (!valor) return;

    listaMarcas
        .filter(marca => marca.toLowerCase().includes(valor))
        .forEach(marca => {
            const item = document.createElement("button");
            item.type = "button";
            item.classList.add("list-group-item", "list-group-item-action");
            item.textContent = marca;
            item.onclick = () => {
                marcaInput.value = marca;
                sugerenciasDiv.innerHTML = "";
            };
            sugerenciasDiv.appendChild(item);
        });
}

// Buscar datos por VIN
function buscarPorVIN() {
    const vin = vinInput.value.trim();
    if (!vin) {
        alert("Por favor ingresa un VIN válido.");
        return;
    }

    fetch(`/api/vin/${vin}`)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            document.querySelector("[name='marca']").value = data.marca || "";
            document.querySelector("[name='modelo']").value = data.modelo || "";
            document.querySelector("[name='ano']").value = data.ano || ""
        })
        .catch(err => alert("Error al buscar VIN: " + err));
}

// Actualizar lista de servicios seleccionados
function actualizarSeleccionados() {
    const seleccionados = Array.from(document.querySelectorAll('.servicio-checkbox:checked'))
        .map(c => c.value);

    contenedorSeleccionados.innerHTML = "";
    if (seleccionados.length === 0) {
        contenedorSeleccionados.innerHTML = '<span class="text-muted small">Ningún servicio seleccionado</span>';
        return;
    }

    seleccionados.forEach(servicio => agregarTagServicio(servicio));
}

// Agregar tag visual de servicio
function agregarTagServicio(servicio) {
    // Evitar duplicados
    if (document.querySelector(`input[name="servicios"][value="${servicio}"]`)) {
        return; // Ya existe, no hacemos nada
    }

    const tag = document.createElement("span");
    tag.className = "badge bg-primary me-1 mb-1";
    tag.textContent = servicio;
    tag.style.cursor = "pointer";

    const hidden = document.createElement("input");
    hidden.type = "hidden";
    hidden.name = "servicios";
    hidden.value = servicio;

    tag.onclick = () => {
        tag.remove();
        hidden.remove();
        const chk = document.querySelector(`.servicio-checkbox[value="${servicio}"]`);
        if (chk) chk.checked = false;
    };

    contenedorSeleccionados.appendChild(tag);
    contenedorSeleccionados.appendChild(hidden);
}


// Filtrar servicios y manejar acordeones
function filtrarServicios() {
    const filtro = buscarServicioInput.value.toLowerCase();
    document.querySelectorAll('.accordion-item').forEach(item => {
        const listaServicios = item.querySelectorAll('.lista-servicios .form-check');
        let coincidencias = 0;

        listaServicios.forEach(servicio => {
            const texto = servicio.textContent.toLowerCase();
            if (texto.includes(filtro)) {
                servicio.style.display = "";
                coincidencias++;
            } else {
                servicio.style.display = "none";
            }
        });

        const collapse = item.querySelector('.accordion-collapse');
        const instancia = bootstrap.Collapse.getOrCreateInstance(collapse, { toggle: false });

        if (filtro) {
            coincidencias > 0 ? instancia.show() : instancia.hide();
        } else {
            instancia.hide();
        }
    });
}

// Agregar servicio personalizado
function agregarServicioPersonalizado(btn) {
    const input = btn.closest('.input-group').querySelector('.input-servicio-personalizado');
    const servicio = input.value.trim();
    if (!servicio) return;

    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4';
    col.innerHTML = `
        <div class="form-check">
            <input class="form-check-input servicio-checkbox" type="checkbox" name="servicios" value="${servicio}" checked>
            <label class="form-check-label">${servicio}</label>
        </div>
    `;

    const lista = btn.closest('.accordion-body').querySelector('.lista-servicios');
    lista.appendChild(col);

    agregarTagServicio(servicio);
    input.value = "";
    filtrarServicios();
}

// ==============================
// Eventos
// ==============================

// Autocompletar marcas
marcaInput.addEventListener("input", mostrarSugerenciasMarcas);
document.addEventListener("click", e => {
    if (!marcaInput.contains(e.target) && !sugerenciasDiv.contains(e.target)) {
        sugerenciasDiv.innerHTML = "";
    }
});

// VIN
btnBuscarVin.addEventListener("click", buscarPorVIN);

// Checkbox servicios
document.addEventListener("change", e => {
    if (e.target.classList.contains("servicio-checkbox")) {
        actualizarSeleccionados();
    }
});

// Filtro de servicios
buscarServicioInput.addEventListener("keyup", filtrarServicios);

// Botón agregar servicio personalizado
document.addEventListener("click", e => {
    if (e.target.classList.contains("btn-agregar-servicio") || e.target.closest(".btn-agregar-servicio")) {
        agregarServicioPersonalizado(e.target.closest(".btn-agregar-servicio"));
    }
});
