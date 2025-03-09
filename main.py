import flet as ft
import boto3
import io
import os

# Configurar conexión con MinIO
s3 = boto3.client(
    "s3",
    endpoint_url="http://172.17.0.2:9000",
    aws_access_key_id="adminuser",
    aws_secret_access_key="supersecurepass"
)


BUCKET_NAME = "imagenes"
EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}

def es_extension_permitida(nombre_archivo):
    return os.path.splitext(nombre_archivo)[1].lower() in EXTENSIONES_PERMITIDAS

def main(page: ft.Page):
    page.title = "Subir imágenes a MinIO"
    page.window_width = 400
    page.window_height = 250

    def seleccionar_archivo(e):
        file_picker.pick_files(allow_multiple=False)

    def subir_archivo(e: ft.FilePickerResultEvent):
        if e.files:
            file = e.files[0]
            with open(file.path, "rb") as f:
                file_bytes = f.read()
                print(f"Read {len(file_bytes)} bytes from {file.name}")
        print("Selected files:", e.files)
        print(e)
        print("Selected file or directory:", e.path)
        if not file_picker.result or not file_picker.result.files:
            mensaje.value = "❌ No se seleccionó ningún archivo."
            page.update()
            return

        archivo = file_picker.result.files[0]

        archivo_nombre = archivo.name
        print(archivo_nombre)
        print(archivo)
        print(file_picker.result)
        if not es_extension_permitida(archivo_nombre):
            mensaje.value = "❌ Solo se permiten imágenes (jpg, png, gif, etc.)."
            page.update()
            return

        try:
            if archivo.path and os.path.exists(archivo.path):
                # Subir archivo desde el sistema de archivos (escritorio)
                s3.upload_file(archivo.path, BUCKET_NAME, archivo_nombre)
            else:
                # Para navegador, leer el archivo y subirlo directamente
                file_data = io.BytesIO(archivo.path)
                s3.upload_fileobj(file_data, BUCKET_NAME, archivo_nombre)

            mensaje.value = f"✅ Archivo '{archivo_nombre}' subido correctamente."
        except Exception as ex:
            mensaje.value = f"❌ Error al subir el archivo: {ex}"

        page.update()

    file_picker = ft.FilePicker(on_result=subir_archivo)
    mensaje = ft.Text("")

    page.overlay.append(file_picker)
    page.add(
        ft.Column([
            ft.Text("Selecciona una imagen para subir a MinIO"),
            ft.ElevatedButton("Seleccionar archivo", on_click=seleccionar_archivo),
            mensaje
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main, view=ft.WEB_BROWSER, port=5000)