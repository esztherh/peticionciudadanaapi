from xlsxwriter.workbook import Workbook

def peticiones_header():
    return (
        "ID",
        "Folio",
        "No. de Turno Asignado",
        "Asunto",
        "Fecha de la Solicitud",
        "Fecha de Captura",
        "Medios de Captación",
        "Lugar de Expedición",
        "Prioridad",
        "Canalización",
        "Requiere Audiencia",
        "Descripción",
        "Estado de la Petición",
        "Nombre",
        "Apellido Paterno",
        "Apellido Materno",
        "CURP",
        "Clave de Elector",
        "RFC",
        "Teléfono",
        "Organización",
        "Puesto en la Organización",
        "Correo Electrónico",
        "Calle",
        "Número Exterior",
        "Número Interior",
        "Código Postal",
        "Estado",
        "Municipio",
        "Colonia",
        "Fecha de Nacimiento",
        "Género",
    )

def seguimientos_header():
    return (
        "Petición ID",
        "Enlace Institucional",
        "Observación",
        "Fecha de Creación",
    )

def xlsx_solicitudes(response, data):
    book = Workbook(response, {'in_memory': True, 'remove_timezone': True})
    sheet_peticiones = book.add_worksheet('Listado de Peticiones')
    sheet_seguimientos = book.add_worksheet('Listado de Seguimientos')

    header_format = book.add_format({'bold': True, 'fg_color': '#A8123E', 'color': 'white'})
    sheet_peticiones.write_row('A1', peticiones_header(), header_format)
    sheet_seguimientos.write_row('A1', seguimientos_header(), header_format)

    date_time_format = book.add_format({'num_format': 'dd/mm/yyyy hh:mm AM/PM'})
    date_format = book.add_format({'num_format': 'dd/mm/yyyy'})

    row_peticiones = 1
    row_seguimientos = 1

    for peticion in data:
        canalizaciones = '';
        for canalizacion in peticion.canalizacion.all():
            canalizaciones += f"{canalizacion}\n"

        sheet_peticiones.write(row_peticiones, 0, peticion.pk)
        sheet_peticiones.write(row_peticiones, 1, peticion.folio)
        sheet_peticiones.write(row_peticiones, 2, peticion.numero_turno)
        sheet_peticiones.write(row_peticiones, 3, peticion.asunto)
        sheet_peticiones.write(row_peticiones, 4, peticion.fecha_solicitud, date_format)
        sheet_peticiones.write(row_peticiones, 5, peticion.fecha_captura, date_time_format)
        sheet_peticiones.write(row_peticiones, 6, peticion.medios_captacion.medio_captacion)
        sheet_peticiones.write(row_peticiones, 7, peticion.lugar_expedicion)
        sheet_peticiones.write_boolean(row_peticiones, 8, peticion.prioridad_urgente)
        sheet_peticiones.write(row_peticiones, 9, canalizaciones)
        sheet_peticiones.write_boolean(row_peticiones, 10, peticion.requiere_audiencia)
        sheet_peticiones.write(row_peticiones, 11, peticion.descripcion.replace("\r", ""))
        sheet_peticiones.write(row_peticiones, 12, peticion.status.status)
        sheet_peticiones.write(row_peticiones, 13, peticion.solicitante.nombre)
        sheet_peticiones.write(row_peticiones, 14, peticion.solicitante.apellido_paterno)
        sheet_peticiones.write(row_peticiones, 15, peticion.solicitante.apellido_materno)
        sheet_peticiones.write(row_peticiones, 16, peticion.solicitante.curp)
        sheet_peticiones.write(row_peticiones, 17, peticion.solicitante.clave_lector)
        sheet_peticiones.write(row_peticiones, 18, peticion.solicitante.rfc)
        sheet_peticiones.write(row_peticiones, 19, peticion.solicitante.telefono)
        sheet_peticiones.write(row_peticiones, 20, peticion.solicitante.organizacion)
        sheet_peticiones.write(row_peticiones, 21, peticion.solicitante.puesto_organizacion)
        sheet_peticiones.write(row_peticiones, 22, peticion.solicitante.correo_electronico)
        sheet_peticiones.write(row_peticiones, 23, peticion.solicitante.calle)
        sheet_peticiones.write(row_peticiones, 24, peticion.solicitante.numero_exterior)
        sheet_peticiones.write(row_peticiones, 25, peticion.solicitante.numero_interior)
        sheet_peticiones.write(row_peticiones, 26, peticion.solicitante.codigo_postal)
        sheet_peticiones.write(row_peticiones, 27, peticion.solicitante.estado)
        sheet_peticiones.write(row_peticiones, 28, peticion.solicitante.municipio.municipio)
        sheet_peticiones.write(row_peticiones, 29, peticion.solicitante.colonia)
        sheet_peticiones.write(row_peticiones, 30, peticion.solicitante.fecha_nacimiento, date_format)
        sheet_peticiones.write(row_peticiones, 31, peticion.solicitante.genero_id.genero)

        for grupo_seguimientos in peticion.grupo_seguimiento_set.all():
            for seguimientos in grupo_seguimientos.seguimiento_set.all():
                sheet_seguimientos.write(row_seguimientos, 0, grupo_seguimientos.solicitud.pk)
                sheet_seguimientos.write(row_seguimientos, 1, grupo_seguimientos.enlace_institucional.dependencia)
                sheet_seguimientos.write(row_seguimientos, 2, seguimientos.observaciones.replace("\r", ""))
                sheet_seguimientos.write(row_seguimientos, 3, seguimientos.created_at, date_time_format)

                row_seguimientos += 1

        row_peticiones += 1

    sheet_peticiones.autofilter(0, 0, row_peticiones-1, len(peticiones_header())-1)
    sheet_seguimientos.autofilter(0, 0, row_seguimientos-1, len(seguimientos_header())-1)

    book.close()
