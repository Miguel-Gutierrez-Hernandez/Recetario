# utils/listener.py — Reconocimiento de voz (STT)

import threading
import speech_recognition as sr
import flet as ft

on_texto  = None
on_error  = None
on_inicio = None
on_fin    = None

_reconocedor = sr.Recognizer()
_reconocedor.pause_threshold        = 0.5
_reconocedor.non_speaking_duration  = 0.4

_escuchando = False


def esta_escuchando() -> bool:
    return _escuchando


def escuchar(page: ft.Page):
    global _escuchando
    if _escuchando:
        return

    def _proceso():
        global _escuchando
        _escuchando = True

        if on_inicio:
            page.run_task(on_inicio)

        try:
            with sr.Microphone() as fuente:
                audio = _reconocedor.listen(fuente, phrase_time_limit=5)
            texto = _reconocedor.recognize_google(audio, language="es-ES")
            if on_texto:
                page.run_task(on_texto, texto)
        except sr.WaitTimeoutError:
            if on_error:
                page.run_task(on_error, "No detecté ninguna voz.")
        except sr.UnknownValueError:
            if on_error:
                page.run_task(on_error, "No entendí lo que dijiste.")
        except sr.RequestError:
            if on_error:
                page.run_task(on_error, "Sin conexión para el reconocimiento de voz.")
        except Exception as e:
            if on_error:
                page.run_task(on_error, f"Error de micrófono: {e}")
        finally:
            _escuchando = False
            if on_fin:
                page.run_task(on_fin)

    threading.Thread(target=_proceso, daemon=True).start()