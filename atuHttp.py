import requests
import datetime
import json
import typing
import struct


class InvalidParameters(Exception):
    """Indicates a problem with the request's arguments.
    """
    pass

class AtuHttp:
    def __init__(self, base_url: str):
        self.session = requests.session()
        self.session.headers['Content-Type'] = 'application/json'
        self.base_url = base_url

    def _request(self, method="POST", url="", body = dict(), **kwargs):
        #session.request("POST", url="https://billingws.gpstracking.pe/v1/api/auth/operator", json=data)
        resp = self.session.request(method, url=f"{url}", json=body)
        self.session.close()
        return resp

    def alerta(self, token = "",**kwargs ):
        self.session = requests.session()
        required=["timestamp"]
        if not all( r in kwargs for r in required):
            raise InvalidParameters("Falta un parametro en alerta " + " ".join(required))
        self.session.headers['Authorization'] = f'Bearer {self.token if not token else token}'
        return self._request("POST", f"{self.base_url}operator/alert", body={**kwargs})

    def login(self, **kwargs):
        self.session = requests.session()
        required = ["pattern_code", "id"]
        if not all( r in kwargs for r in required):
            raise InvalidParameters("Falta un parametro en Login " + " ".join(required))
        res = self._request("POST", f"{self.base_url}auth/operator", body={**kwargs})
        self.token = res.json().get("data", {}).get("token",{})
        return res

    def hoja_de_ruta(self, token ="", **kwargs):
        self.session = requests.session()
        self.session.headers['Authorization'] = f'Bearer {self.token if not token else token}'
        return self._request("GET", f"{self.base_url}arrivals", body={**kwargs})

    def posiciones(self, token= "", **kwargs):
        self.session = requests.session()
        self.session.headers['Authorization'] = f'Bearer {self.token if not token else token}'
        return self._request("GET", f"{self.base_url}position", body={**kwargs})

    def tarifa(self, token= "", **kwargs):
        self.session = requests.session()
        self.session.headers['Authorization'] = f'Bearer {self.token if not token else token}'
        return self._request("GET", f"{self.base_url}tariffs", body={**kwargs})

    def tickets_generados(self, token= "", **kwargs):
        self.session = requests.session()
        required = ["payed", "canceled"]
        if not all( r in kwargs for r in required):
            raise InvalidParameters("Falta un parametro en tickets_generados " + " ".join(required))
        self.session.headers['Authorization'] = f'Bearer {self.token if not token else token}'
        return self._request("POST", f"{self.base_url}tickets", body={**kwargs})

    def getToken(self):
        return self.token

    def setToken(self, token: str):
        self.token = token




if __name__ == "__main__":
    session = requests.session()
    session.headers['Content-Type'] = 'application/json'
    data = {
        "pattern_code": "4053",
        "id": "866989058568582"
    }
    #resp = session.post("https://billingws.gpstracking.pe/v1/api/auth/operator", json=data) funciona
    resp = session.request("POST", url="https://billingws.gpstracking.pe/v1/api/auth/operator", json=data)
    resp = resp.json()
    #print(resp.content)
    print(resp)
    #resp = session.get()