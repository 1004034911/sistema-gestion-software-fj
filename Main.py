from abc import ABC, abstractmethod
from datetime import datetime

# ==========================================
# 1. EXCEPCIONES PERSONALIZADAS Y ARCHIVO DE LOGS
# ==========================================

class SoftwareFJException(Exception):
    """Excepción base personalizada para el sistema Software FJ."""
    def __init__(self, mensaje):
        super().__init__(mensaje)
        self.registrar_log(mensaje)

    def registrar_log(self, mensaje):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open("sistema_log.txt", "a", encoding="utf-8") as archivo:
                archivo.write(f"[LOG ERROR - {timestamp}] {mensaje}\n")
        except Exception as e:
            print(f"Error crítico al escribir en el log: {e}")

class ReservaInvalidaError(SoftwareFJException):
    """Excepción lanzada cuando una reserva no cumple con las validaciones."""
    pass

class ServicioNoDisponibleError(SoftwareFJException):
    """Excepción lanzada cuando un servicio seleccionado no está activo o disponible."""
    pass


# ==========================================
# 2. CLASE ABSTRACTA ENTIDAD Y CLASE CLIENTE
# ==========================================

class EntidadBase(ABC):
    """Clase abstracta que representa entidades generales del sistema."""
    @abstractmethod
    def obtener_detalles(self):
        pass

class Cliente(EntidadBase):
    def __init__(self, cedula, nombre, correo):
        self.validar_datos(cedula, nombre, correo)
        self.__cedula = cedula
        self.__nombre = nombre
        self.__correo = correo

    def validar_datos(self, cedula, nombre, correo):
        if not cedula or not str(cedula).isdigit():
            raise ValueError("La cédula del cliente debe contener solo dígitos.")
        if not nombre or len(nombre.strip()) < 3:
            raise ValueError("El nombre del cliente no es válido.")
        if "@" not in correo or "." not in correo:
            raise ValueError("El formato del correo electrónico no es válido.")

    @property
    def cedula(self):
        return self.__cedula

    @property
    def nombre(self):
        return self.__nombre

    def obtener_detalles(self):
        return f"Cliente: {self.__nombre} (Cédula: {self.__cedula}, Correo: {self.__correo})"


# ==========================================
# 3. CLASE ABSTRACTA SERVICIO Y SERVICIOS ESPECIALIZADOS (POLIMORFISMO)
# ==========================================

class Servicio(ABC):
    def __init__(self, id_servicio, nombre, costo_base):
        self._id_servicio = id_servicio
        self._nombre = nombre
        self._costo_base = costo_base
        self._disponible = True

    @abstractmethod
    def calcular_costo(self, *args, **kwargs):
        """Método abstracto sobreescrito en las clases hijas para polimorfismo."""
        pass

    def obtener_detalles(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return f"Servicio: {self._nombre} | Costo Base: ${self._costo_base} | Estado: {estado}"

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, estado):
        self._disponible = estado


class ReservaSalas(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, capacidad):
        super().__init__(id_servicio, nombre, costo_base)
        self.capacidad = capacidad

    # Método sobrecargado (permite calcular con o sin descuento por horas)
    def calcular_costo(self, horas=1, aplicar_descuento=False):
        try:
            if horas <= 0:
                raise ValueError("Las horas de reserva deben ser mayores a cero.")
            
            total = self._costo_base * horas
            if aplicar_descuento and horas >= 4:
                total *= 0.85  # 15% de descuento por más de 4 horas
            return float(total)
        except Exception as e:
            raise ReservaInvalidaError(f"Error en cálculo de Reserva de Salas: {e}")


class AlquilerEquipos(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, tipo_equipo):
        super().__init__(id_servicio, nombre, costo_base)
        self.tipo_equipo = tipo_equipo

    def calcular_costo(self, dias=1, seguro=0.0):
        try:
            if dias <= 0:
                raise ValueError("Los días de alquiler deben ser mayores a cero.")
            total = (self._costo_base * dias) + seguro
            return float(total)
        except Exception as e:
            raise ReservaInvalidaError(f"Error en cálculo de Alquiler de Equipos: {e}")


class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, area):
        super().__init__(id_servicio, nombre, costo_base)
        self.area = area

    def calcular_costo(self, sesiones=1):
        try:
            if sesiones <= 0:
                raise ValueError("El número de sesiones debe ser mayor a cero.")
            total = self._costo_base * sesiones
            return float(total)
        except Exception as e:
            raise ReservaInvalidaError(f"Error en cálculo de Asesoría: {e}")


# ==========================================
# 4. CLASE RESERVA CON MANEJO AVANZADO DE EXCEPCIONES
# ==========================================

class Reserva:
    def __init__(self, id_reserva, cliente, servicio, cantidad_unidades=1):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad_unidades = cantidad_unidades
        self.estado = "Pendiente"
        self.costo_total = 0.0

    def procesar_reserva(self, *args, **kwargs):
        """Implementa bloques try/except/else/finally exigidos por la guía."""
        try:
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio '{self._nombre_seguro()}' no se encuentra disponible.")
            
            # Cálculo del costo usando polimorfismo
            self.costo_total = self.servicio.calcular_costo(*args, **kwargs)
            self.estado = "Confirmada"
            print(f"-> ÉXITO: Reserva {self.id_reserva} procesada para {self.cliente.nombre}. Total: ${self.costo_total}")

        except ServicioNoDisponibleError as sne:
            self.estado = "Fallida"
            print(f"-> EXCEPCIÓN CONTROLADA: {sne}")
        except ReservaInvalidaError as rie:
            self.estado = "Fallida"
            print(f"-> EXCEPCIÓN CONTROLADA: {rie}")
        except Exception as e:
            self.estado = "Error Crítico"
            # Encadenamiento de excepciones
            raise RuntimeError(f"Error inesperado procesando la reserva {self.id_reserva}") from e
        else:
            print(f"   [INFO] Operación completada sin interrupciones para el cliente {self.cliente.nombre}.")
        finally:
            print(f"   [FINALLY] Registro de intento de reserva {self.id_reserva} finalizado.\n")

    def _nombre_seguro(self):
        return getattr(self.servicio, '_nombre', 'Desconocido')

    def cancelar_reserva(self):
        self.estado = "Cancelada"
        print(f"-> La reserva {self.id_reserva} ha sido cancelada correctamente.")


# ==========================================
# 5. SIMULACIÓN DE 10 OPERACIONES (VÁLIDAS E INVÁLIDAS)
# ==========================================

if __name__ == "__main__":
    print("=== INICIANDO SIMULACIÓN DE 10 OPERACIONES EN SOFTWARE FJ ===\n")

    # Instanciando servicios
    sala_juntas = ReservaSalas("S01", "Sala Ejecutiva", 50000, 10)
    laptop_dev = AlquilerEquipos("E01", "Kit Portátil Desarrollo", 35000, "Computo")
    asesoria_ti = AsesoriaEspecializada("A01", "Asesoría en Arquitectura Software", 120000, "Sistemas")
    asesoria_ti.disponible = False # Servicio marcado como no disponible para probar excepción

    # Operación 1: Registro de cliente válido y reserva exitosa de sala (con descuento)
    try:
        c1 = Cliente("11223344", "Carlos Pérez", "carlos@mail.com")
        r1 = Reserva("R001", c1, sala_juntas, 5)
        r1.procesar_reserva(horas=5, aplicar_descuento=True)
    except Exception as e:
        print(f"Error general capturado: {e}\n")

    # Operación 2: Intento con cédula inválida (Genera ValueError)
    try:
        c_invalido = Cliente("ABC", "María Gómez", "maria@mail.com")
    except ValueError as ve:
        print(f"-> EXCEPCIÓN CAPTURADA (Datos inválidos): {ve}\n")

    # Operación 3: Alquiler de equipos válido por 3 días con seguro
    try:
        c2 = Cliente("99887766", "Ana Rodríguez", "ana@mail.com")
        r3 = Reserva("R003", c2, laptop_dev, 2)
        r3.procesar_reserva(dias=3, seguro=15000)
    except Exception as e:
        print(f"Error: {e}\n")

    # Operación 4: Intento de reserva con horas en negativo (Genera ReservaInvalidaError)
    try:
        r4 = Reserva("R004", c2, sala_juntas, 1)
        r4.procesar_reserva(horas=-2)
    except Exception as e:
        print(f"-> Capturado externamente: {e}\n")

    # Operación 5: Intento de reserva sobre un servicio no disponible (Lanza ServicioNoDisponibleError)
    try:
        r5 = Reserva("R005", c1, asesoria_ti, 1)
        r5.procesar_reserva(sesiones=2)
    except Exception as e:
        print(f"Error: {e}\n")

    # Operación 6: Asesoría especializada exitosa
    try:
        r6 = Reserva("R006", c1, asesoria_ti, 1)
        asesoria_ti.disponible = True  # Activamos el servicio temporalmente
        r6.procesar_reserva(sesiones=2)
    except Exception as e:
        print(f"Error: {e}\n")

    # Operación 7: Cancelación exitosa de una reserva
    try:
        r1.cancelar_reserva()
        print("")
    except Exception as e:
        print(f"Error: {e}\n")

    # Operación 8: Cliente con correo inválido
    try:
        c3 = Cliente("55443322", "Luis Torres", "correo_sin_arroba.com")
    except ValueError as ve:
        print(f"-> EXCEPCIÓN CAPTURADA (Correo inválido): {ve}\n")

    # Operación 9: Alquiler de equipos con días en cero
    try:
        r9 = Reserva("R009", c2, laptop_dev, 1)
        r9.procesar_reserva(dias=0)
    except Exception as e:
        print(f"-> Excepción en alquiler: {e}\n")

    # Operación 10: Reserva de sala sin descuento por pocas horas
    try:
        r10 = Reserva("R010", c2, sala_juntas, 2)
        r10.procesar_reserva(horas=2, aplicar_descuento=False)
    except Exception as e:
        print(f"Error: {e}\n")

    print("=== SIMULACIÓN FINALIZADA. VERIFIQUE EL ARCHIVO 'sistema_log.txt' ===")