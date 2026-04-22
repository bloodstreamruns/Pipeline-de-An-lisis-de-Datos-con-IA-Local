import pandas as pd

def abrir_item_logica(nombre_archivo):

    # Simulación de DataFrame según el archivo
    if nombre_archivo == "📄 distribucion_region":
        df = pd.DataFrame({
            "Region": ["Norte", "Sur", "Este", "Oeste"],
            "Ventas": [1200, 950, 1100, 780]
        })
        return True, df
    elif nombre_archivo == "📄 tendencia_mensual":
        df = pd.DataFrame({
            "Mes": ["Ene", "Feb", "Mar", "Abr"],
            "Ventas": [300, 450, 500, 600]
        })
        return True, df
    else:
        return False, "Archivo no encontrado"

def eliminar_item_logica(tree, item):
    if not item:
        return False, "Selecciona un elemento para eliminar"

    parent = item.parent()
    if parent:
        parent.removeChild(item)
    else:
        index = tree.indexOfTopLevelItem(item)
        tree.takeTopLevelItem(index)

    return True, f"Elemento '{item.text(0)}' eliminado"

def exportar_archivo_logica(ruta, df):
    if ruta and not df.empty:
        df.to_csv(ruta, index=False)
        return True, "Archivo exportado correctamente"
    return False, "No se seleccionó archivo o DataFrame vacío"