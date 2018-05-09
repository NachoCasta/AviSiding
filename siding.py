from collections import defaultdict
from time import sleep

from robobrowser import RoboBrowser


class Siding:

    def __init__(self, usuario, contraseña):
        self.browser = RoboBrowser(parser="html.parser")
        self.usuario = usuario
        self.contraseña = contraseña
        self.ramos_alumno = defaultdict(dict)
        self.ramos_administrador = defaultdict(dict)
        self.ramos_ayudante = defaultdict(dict)

    def __repr__(self):
        return "Siding - " + self.usuario

    def login(self):
        "Inicia sesion en Siding"
        self.browser.open("http://www.ing.uc.cl/")
        forma = self.browser.get_form(id="form-siding")
        forma["login"] = self.usuario
        forma["passwd"] = self.contraseña
        self.browser.submit_form(forma) 
        if "Datos de ingreso incorrectos" in self.browser.parsed.text:
            raise CredencialesIncorrectas()

    def cargar_ramos(self):
        self.browser.open(
            "https://intrawww.ing.puc.cl/siding/" +
            "dirdes/ingcursos/cursos/index.phtml")
        ramos = self.browser.find(class_="ColorFondoZonaTrabajo")
        ramos = ramos.find_all("tr")[1:]
        comenzar = False
        lista = None
        for ramo in ramos:
            titulo = ramo.find("td").text.strip()
            if titulo == "":
                continue
            if "Cursos donde es alumno" in titulo:
                comenzar = True
                dic = self.ramos_alumno
                continue
            if "Cursos donde es administrador" in titulo:
                dic = self.ramos_administrador
                continue
            if "Cursos donde es ayudante" in titulo:
                dic = self.ramos_ayudante
                continue
            if not comenzar:
                continue
            titulo = titulo.split()
            sigla = titulo[0]
            seccion = titulo[1].split(".")[1]
            nombre = " ".join(titulo[2:])
            local_link = ramo.find("a")
            if local_link is not None:
                link = "https://intrawww.ing.puc.cl" + local_link.get("href")
                id_ = link.split("=")[-1]
            else:
                link = local_link
                id_ = None
            dic_ramo = {
                "sigla": sigla,
                "nombre": nombre,
                "seccion": seccion,
                "link": link,
                "id": id_
                }
            dic[sigla][seccion] = dic_ramo

    def subir_anuncio(self, sigla, seccion, asunto, mensaje):
        ramo = self.ramos_administrador[sigla][seccion]
        link = "https://intrawww.ing.puc.cl/siding/dirdes/ingcursos/" + \
               "cursos/index.phtml?accion_curso=avisos&acc_aviso=nuevo" + \
               "&id_curso_ic={}".format(ramo["id"])
        form = None
        while form is None:
            self.browser.open(link)
            form = self.browser.get_form(
                action="?accion_curso=avisos&acc_aviso=ingresar_aviso&" + \
                "id_curso_ic={}".format(ramo["id"]))
        form["asunto"].value = sigla + " - Nuevo aviso - " + asunto
        form["contenido_aviso"].value = mensaje
        print(form["asunto"].value)
        print(form["contenido_aviso"].value)
        #self.browser.submit_form(form)

    def subir_anuncio_multiple(self, sigla, secciones, asunto, mensaje):
        for seccion in secciones:
            self.subir_anuncio(sigla, seccion, asunto, mensaje)
        print("Se han subido todos los anuncios")
    

    


if __name__ == "__main__":
    s = Siding("lfbeltran@uc.cl", "lfbeltran123")
    s.login()
    s.cargar_ramos()
    #s.subir_anuncio("ICS1113", "3", "Hola", "Estimados,\n\n¿Como estan?")
    s.subir_anuncio_multiple("ICS1113", ["1", "2", "3"], "Hola", "Como estan?")
