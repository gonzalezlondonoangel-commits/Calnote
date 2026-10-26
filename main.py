
# CLASSNOTE
# Calculadora matematica creada por Angel
# Requiere Python 3 y Kivy

import ast
import math
import operator
import re

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

AZUL = "#087BFF"
AZUL_OSCURO = "#06152E"
AMARILLO = "#FFD928"
ROJO = "#F2384B"
NEGRO = "#05070B"
BLANCO = "#FFFFFF"
GRIS = "#AFC7E8"


def color(c):
    return get_color_from_hex(c)


# Funciones matematicas

def promedio(*numeros):
    if not numeros:
        raise ValueError("Ingresa numeros para calcular el promedio.")
    return sum(numeros) / len(numeros)


def porcentaje(numero, tasa):
    return numero * tasa / 100


def raiz(numero):
    if numero < 0:
        raise ValueError("No existe una raiz real de ese numero.")
    return math.sqrt(numero)


OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

UNARIOS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

FUNCIONES = {
    "promedio": promedio,
    "porcentaje": porcentaje,
    "raiz": raiz,
    "sqrt": raiz,
    "abs": abs,
}


def preparar(texto):
    texto = texto.strip()
    if not texto:
        raise ValueError("Escribe una operacion.")

    texto = texto.replace(",", ".")
    texto = texto.replace("×", "*").replace("÷", "/")
    texto = texto.replace("−", "-").replace("^", "**")
    texto = texto.replace("√(", "raiz(")

    # 15% se interpreta como 15/100
    texto = re.sub(
        r"(?<![\w.)])(\d+(?:\.\d+)?)\s*%",
        r"(\1/100)", texto
    )

    # Multiplicacion implicita: 5(7), (2+3)(4)
    texto = re.sub(r"(?<=[0-9.)])\s*(?=\()", "*", texto)
    texto = re.sub(r"(?<=\))\s*(?=[0-9])", "*", texto)
    texto = re.sub(r"(?<=\d)\s*(?=[A-Za-z])", "*", texto)

    # Evitar insertar multiplicacion en nombres de funciones
    for nombre in FUNCIONES:
        texto = texto.replace(nombre + "*(", nombre + "(")

    return texto


def evaluar(nodo):
    if isinstance(nodo, ast.Expression):
        return evaluar(nodo.body)

    if isinstance(nodo, ast.Constant):
        if isinstance(nodo.value, (int, float, bool)):
            return nodo.value

    if isinstance(nodo, ast.Num):
        return nodo.n

    if isinstance(nodo, ast.BinOp):
        tipo = type(nodo.op)
        if tipo not in OPERADORES:
            raise ValueError("Operador no permitido.")

        a = evaluar(nodo.left)
        b = evaluar(nodo.right)

        if tipo == ast.Pow and abs(b) > 1000:
            raise ValueError("Exponente demasiado grande.")

        resultado = OPERADORES[tipo](a, b)

        if isinstance(resultado, complex):
            raise ValueError("El resultado no es real.")

        return resultado

    if isinstance(nodo, ast.UnaryOp):
        tipo = type(nodo.op)
        if tipo not in UNARIOS:
            raise ValueError("Operacion no permitida.")
        return UNARIOS[tipo](evaluar(nodo.operand))

    if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name):
        nombre = nodo.func.id
        if nombre not in FUNCIONES or nodo.keywords:
            raise ValueError("Funcion no permitida.")
        argumentos = [evaluar(x) for x in nodo.args]
        return FUNCIONES[nombre](*argumentos)

    if isinstance(nodo, ast.Compare):
        a = evaluar(nodo.left)
        for op, comp in zip(nodo.ops, nodo.comparators):
            b = evaluar(comp)

            if isinstance(op, ast.Eq):
                ok = a == b
            elif isinstance(op, ast.NotEq):
                ok = a != b
            elif isinstance(op, ast.Lt):
                ok = a < b
            elif isinstance(op, ast.LtE):
                ok = a <= b
            elif isinstance(op, ast.Gt):
                ok = a > b
            elif isinstance(op, ast.GtE):
                ok = a >= b
            else:
                raise ValueError("Comparacion no permitida.")

            if not ok:
                return False
            a = b

        return True

    if isinstance(nodo, ast.BoolOp):
        valores = [bool(evaluar(x)) for x in nodo.values]
        if isinstance(nodo.op, ast.And):
            return all(valores)
        if isinstance(nodo.op, ast.Or):
            return any(valores)

    raise ValueError("Revisa la operacion escrita.")


def calcular(texto):
    expresion = preparar(texto)
    arbol = ast.parse(expresion, mode="eval")
    resultado = evaluar(arbol)

    if isinstance(resultado, float) and not math.isfinite(resultado):
        raise ValueError("Resultado fuera de rango.")

    return resultado


class CLASSNOTE(App):

    title = "CLASSNOTE"

    def build(self):
        Window.clearcolor = color(AZUL_OSCURO)
        Window.softinput_mode = "below_target"

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8)
        )

        # Encabezado y logo A+
        encabezado = BoxLayout(
            size_hint_y=None,
            height=dp(65),
            spacing=dp(10)
        )

        logo = Label(
            text="[b][color=087BFF]A[/color][color=FFFFFF]+[/color][/b]",
            markup=True,
            font_size=sp(42),
            size_hint_x=None,
            width=dp(80)
        )
        encabezado.add_widget(logo)

        textos = BoxLayout(orientation="vertical")

        nombre = Label(
            text="[b]CLASSNOTE[/b]",
            markup=True,
            color=color(AMARILLO),
            font_size=sp(25),
            halign="left"
        )
        nombre.bind(size=lambda w, s: setattr(w, "text_size", s))

        subtitulo = Label(
            text="Calculadora matematica",
            color=color(GRIS),
            font_size=sp(14),
            halign="left"
        )
        subtitulo.bind(size=lambda w, s: setattr(w, "text_size", s))

        textos.add_widget(nombre)
        textos.add_widget(subtitulo)
        encabezado.add_widget(textos)
        principal.add_widget(encabezado)

        # Mensaje solicitado
        bienvenida = Label(
            text=(
                "[b]Adelante, Prueba Esta Calculadora "
                "Diseñada Para La Solución De Tus Problemas "
                "Matemáticos Hecha Por Ángel.[/b]"
            ),
            markup=True,
            color=color(BLANCO),
            font_size=sp(16),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(85)
        )
        bienvenida.bind(
            size=lambda w, s: setattr(w, "text_size", (s[0], None))
        )
        principal.add_widget(bienvenida)

        # Pantalla de entrada
        self.entrada = TextInput(
            hint_text="Ingrese amablemente tu número u operación",
            multiline=False,
            font_size=sp(22),
            foreground_color=color(AMARILLO),
            hint_text_color=color(GRIS),
            background_normal="",
            background_active="",
            background_color=color(NEGRO),
            cursor_color=color(AMARILLO),
            padding=[dp(10), dp(15)],
            size_hint_y=None,
            height=dp(58)
        )
        self.entrada.bind(on_text_validate=lambda *_: self.resolver())
        principal.add_widget(self.entrada)

        self.salida = Label(
            text="Resultado: aqui aparecera tu respuesta",
            color=color(AMARILLO),
            font_size=sp(17),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(48)
        )
        self.salida.bind(size=lambda w, s: setattr(w, "text_size", s))
        principal.add_widget(self.salida)

        # Botones
        desplazamiento = ScrollView(do_scroll_x=False)
        teclado = GridLayout(
            cols=4,
            spacing=dp(6),
            size_hint_y=None,
            padding=[0, dp(4)]
        )
        teclado.bind(minimum_height=teclado.setter("height"))

        botones = [
            ("AC", "AC"), ("BORRAR", "BORRAR"), ("(", "("), (")", ")"),
            ("7", "7"), ("8", "8"), ("9", "9"), ("÷", "÷"),
            ("4", "4"), ("5", "5"), ("6", "6"), ("×", "×"),
            ("1", "1"), ("2", "2"), ("3", "3"), ("−", "−"),
            ("0", "0"), (".", "."), ("%", "%"), ("+", "+"),
            ("POTENCIA", "^"), ("RAIZ", "raiz("),
            ("=", "="), ("AND", " and "),
            ("OR", " or "), ("NOT", "not "),
            ("<", "<"), (">", ">"),
        ]

        for titulo, valor in botones:
            fondo = AZUL if valor == "=" else AMARILLO
            if valor in ("AC", "BORRAR"):
                fondo = ROJO

            boton = Button(
                text=titulo,
                font_size=sp(16),
                bold=True,
                color=color(BLANCO if fondo in (AZUL, ROJO) else NEGRO),
                background_normal="",
                background_down="",
                background_color=color(fondo),
                size_hint_y=None,
                height=dp(55)
            )
            boton.bind(
                on_release=lambda instancia, v=valor: self.pulsar(v)
            )
            teclado.add_widget(boton)

        desplazamiento.add_widget(teclado)
        principal.add_widget(desplazamiento)

        ayuda = Label(
            text=(
                "Ejemplos: 5(7) | 2^3 | raiz(81) | "
                "promedio(4,6,8) | porcentaje(200,15)"
            ),
            font_size=sp(12),
            color=color(GRIS),
            size_hint_y=None,
            height=dp(42)
        )
        principal.add_widget(ayuda)

        return principal

    def pulsar(self, valor):
        actual = self.entrada.text

        if valor == "AC":
            self.entrada.text = ""
            self.salida.text = "Resultado: aqui aparecera tu respuesta"

        elif valor == "BORRAR":
            self.entrada.text = actual[:-1]

        elif valor == "=":
            self.resolver()

        else:
            self.entrada.text = actual + valor
            self.entrada.focus = True

    def resolver(self):
        try:
            respuesta = calcular(self.entrada.text)

            if isinstance(respuesta, bool):
                texto = "Verdadero" if respuesta else "Falso"
            elif isinstance(respuesta, float):
                texto = f"{respuesta:.10g}"
            else:
                texto = str(respuesta)

            self.salida.text = "Resultado: " + texto
            print("CLASSNOTE - Resultado:", texto)

        except ZeroDivisionError:
            self.salida.text = "Error: no se puede dividir entre cero."

        except (ValueError, SyntaxError, TypeError, OverflowError) as error:
            self.salida.text = "Revisa la operacion: " + str(error)

        except Exception:
            self.salida.text = "No se pudo calcular la operacion."


if __name__ == "__main__":
    CLASSNOTE().run()
