from protocolV1_1.protocol_layer_two_content import *
import datetime
import json
import time

import logging
import colorama as cr
import colored_logger

# auth_json.get('datas',{}).get('user', {}).get('name')
logger = colored_logger.Logger("http2pro", logging.DEBUG, cr.Fore.RED)
logger.add_stderr(logging.ERROR)


class http2protocol():
    @staticmethod
    def auth(res) -> authentication_data_tuple:
        # "{'status': True, 'msg': 'Autenticacion exitosa', 'data': {'user': {'name': 'JOJHAN JORGE', 'lastname': 'GOMEZ MEZA', 'doc_number': '45418515', 'status_id': 1, 'pattern_code': 'G2188', 'route_id': 1, 'license': '45418515', 'license_expired_at': '2025-11-21'}, 'route_code': 'IO-52', 'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjozOTgsInBsYXRlX2lkIjoxNjYsInBsYXRlIjoiQkZHOTQxIiwicm91dGVfaWQiOjEsImNvbXBhbnlfaWQiOjEsInNlcmllX2lkIjozMTI3MCwibmFtZSI6IkpPSkhBTiBKT1JHRSIsInByb2dyYW1hdGlvbl9pZCI6MSwiaWF0IjoxNzE2MzU2NDQyMjQzfQ._Lv-Bv0NGuJ9krOaDzDHlzj-aFXOWCm0rwX0QSvcuQo', 'ticket_init': 10000012222, 'company': {'name': 'TRANSPORTES HUASCAR S.A.', 'logo': 'https://res.cloudinary.com/dbdvax88n/image/upload/v1705960400/dn7r3lww19trwqq9wj92.jpg', 'ruc': '20121952140', 'soat': {'ruc': '20100041953', 'policy': 'RC TPU NORMA 1599 - 2016-502183', 'company': 'RIMAC SEGUROS Y REASEGUROS S.A.', 'valid_from': '2023-08-20', 'valid_to': '2024-08-20'}}}}"
        try:
            # "valid_from": "2023-08-20",
            # "valid_to": "2024-08-20"
            valid_from = res.get('data').get('company').get('soat').get('valid_from')
            valid_from = [ int(x) for x in valid_from.split("-")]
            valid_from = datetime.datetime(valid_from[0], valid_from[1], valid_from[2])
            valid_from = time.mktime(valid_from.timetuple())

            valid_to   = res.get('data').get('company').get('soat').get('valid_to')
            valid_to   = [ int(x) for x in valid_to.split("-")]
            valid_to   = datetime.datetime(valid_to[0], valid_to[1], valid_to[2])
            valid_to = time.mktime(valid_to.timetuple())
            
            authentication = authentication_data_tuple(    
                    name =          res.get('data').get('user').get('name').encode('latin-1'),
                    lastname =      res.get('data').get('user').get('lastname').encode('latin-1'),
                    doc_number =    res.get('data').get('user').get('doc_number').encode('latin-1'),
                    pattern_code =  res.get('data').get('user').get('pattern_code').encode('latin-1'),
                    route_code =    res.get('data').get('route_code').encode('latin-1'),
                    name_company =  res.get('data').get('company').get('name').encode('latin-1'),
                    logo =          res.get('data').get('company').get('logo').encode('latin-1'),
                    ruc =           res.get('data').get('company').get('ruc').encode('latin-1'),
                    ruc_soat =      res.get('data').get('company').get('soat').get('ruc').encode('latin-1'),
                    policy =        res.get('data').get('company').get('soat').get('policy').encode('latin-1'),
                    company =       res.get('data').get('company').get('soat').get('company').encode('latin-1'),
                    token =         res.get('data').get('token').encode('latin-1'),
                    ticket_init =   int(res.get('data').get('ticket_init')),
                    from_time =     int(valid_from), 
                    to_time =       int(valid_to)) 
        except Exception as e:
            raise e
        return authentication

    @staticmethod 
    def tarifa(res) -> "list[tarifa_data_tuple]":
        #tarifa = {"status":true,"msg":"Solicitud exitosa","data":[{"id":22,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"SOCIAL","status_id":1,"name":"S/ 1.00","value":"1.00"},{"id":20,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"URBANO","status_id":1,"name":"S/ 1.20","value":"1.20"},{"id":18,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"INTERURBANO I","status_id":1,"name":"S/ 1.50","value":"1.50"},{"id":16,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"INTERURBANO II","status_id":1,"name":"S/ 2.00","value":"2.00"},{"id":14,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"DIRECTO","status_id":1,"name":"S/ 2.50","value":"2.50"},{"id":23,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"ESCOLAR","status_id":1,"name":"S/ 1.00","value":"1.00"},{"id":21,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"SOCIAL","status_id":1,"name":"S/ 2.00","value":"2.00"},{"id":19,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"URBANO","status_id":1,"name":"S/ 2.50","value":"2.50"},{"id":17,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"INTERURBANO I","status_id":1,"name":"S/ 3.00","value":"3.00"},{"id":15,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"INTERURBANO II","status_id":1,"name":"S/ 4.00","value":"4.00"},{"id":13,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"DIRECTO","status_id":1,"name":"S/ 5.00","value":"5.00"}]}
        try:
            tarifas = res.get("data", {})
            result = list()
            for tarifa in tarifas:
                ticket_type = 0
                if tarifa.get("ticket_type") == "regular":
                    ticket_type = 0
                elif tarifa.get("ticket_type") == "academic":
                    ticket_type = 1
                value = [ int(x) for x in tarifa.get("value").split(".")]
                value = value[0]*100 + value[1]
                t  = tarifa_data_tuple(
                        id = tarifa.get("id"), 
                        type = tarifa.get("type"), 
                        ticket_type = ticket_type, 
                        value = value,
                        ticket_description = tarifa.get("ticket_description").encode('latin-1')
                        )
                result.append(t)
            return result
        except Exception as e:
            raise e 

    @staticmethod 
    def hoja_de_ruta(res) -> "list[hoja_de_ruta_data_tuple]":
        try:
            #class hoja_de_ruta_data_tuple(typing.NamedTuple):
            #    stop:bytearray
            #    estimated_time:int
            #    arrival_time:int
            #    state:int
            #    difference:int

            rutas = res.get("data", {})
            result = list()
            for ruta in rutas:
                
                try:
                    estimatedTime = [int(x) for x in ruta.get("estimatedTime").split(":")]
                    estimatedTime = estimatedTime[0]*100 + estimatedTime[1]
                except ValueError:
                    estimatedTime = 0
                try:
                    arrivalTime = [ int(x) for x in ruta.get("arrival").split(":")]
                    arrivalTime = arrivalTime[0]*100 + arrivalTime[1]
                except ValueError:
                    arrivalTime = 0
                
                difference = int(ruta.get("difference")) if ruta.get("difference") else 0
                t  = hoja_de_ruta_data_tuple(
                        ruta.get("stop").encode("latin-1"),
                        estimatedTime, 
                        arrivalTime,
                        2 if  res.get("current") == "true" else 0,
                        difference
                        )
                
                result.append(t)
            return result
        except Exception as e:
            raise e 
    
    @staticmethod 
    def obtener_posiciones(res, version) -> "list[posiciones_data_tuple]":
        try:
            #type: int              0: next 1: current 2: before
            #plate: bytearray       
            #stop: bytearray        
            #difference: int        
            posiciones = res.get("data", {})
            result = list()
            for posicion in posiciones:
                #2024-03-23 09:42:00
                #[date, clock] = [ int(x) for x in posicion.get("arrival").split(":")]
                #date  = [ int(x) for x in posicion.get("arrival").split("-")]
                #clock = [ int(x) for x in posicion.get("arrival").split(":")]
                #arrival = datetime.datetime(date[0], date[1], date[2], clock[0], clock[1], clock[2])
                posType = 0
                if posicion.get("type") == "next":
                    posType = 0
                elif posicion.get("type") == "current":
                    posType = 1
                else:   #before
                    posType = 2


                diff: str = posicion.get("difference")
                difference = 0

                if version == 1: #solo recibe el numero
                    if not diff:
                        diff = ""
                    
                    if diff.startswith("+-"):
                        diff = diff.replace("-","")   

                    try:
                        difference = int(diff) if diff else 0
                    except ValueError as e:
                        print(f"ValueError {diff}")
                        difference = 0
                        
                elif version == 2: 
                    flag_no_symbol  = False
                    flag_send_empty = False
                    if not diff:
                        diff = ""
                        flag_send_empty = True
                    
                    if diff.startswith("+-"):
                        diff = diff.replace("-","")  

                    if not diff.startswith("+") and not diff.startswith("-"):
                        flag_no_symbol = True
                    
                    ### VERSION SPECIFIC 2 END
                    try:
                        difference = int(diff) if diff else 0
                    except ValueError as e:
                        print(f"ValueError {diff}")
                        difference = 0

                    ### VERSION SPECIFIC 2 START
                    if flag_no_symbol and difference != 0:
                        difference += 2000

                    if flag_send_empty:
                        difference = 1000


                t  = posiciones_data_tuple(
                        posType,
                        posicion.get("stop").encode("latin-1") if  posType == 1 else posicion.get("plate").encode("latin-1"), 
                        difference
                        )
                
                result.append(t)
            return result
        except Exception as e:
            logger.error(f"{e}", exc_info=True) 
            return [] 



if __name__ == "__main__":
    #tickets {"status":true,"msg":"Solicitud exitosa","data":[{"id":22,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"SOCIAL","status_id":1,"name":"S/ 1.00","value":"1.00"},{"id":20,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"URBANO","status_id":1,"name":"S/ 1.20","value":"1.20"},{"id":18,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"INTERURBANO I","status_id":1,"name":"S/ 1.50","value":"1.50"},{"id":16,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"INTERURBANO II","status_id":1,"name":"S/ 2.00","value":"2.00"},{"id":14,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"DIRECTO","status_id":1,"name":"S/ 2.50","value":"2.50"},{"id":23,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"ESCOLAR","status_id":1,"name":"S/ 1.00","value":"1.00"},{"id":21,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"SOCIAL","status_id":1,"name":"S/ 2.00","value":"2.00"},{"id":19,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"URBANO","status_id":1,"name":"S/ 2.50","value":"2.50"},{"id":17,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"INTERURBANO I","status_id":1,"name":"S/ 3.00","value":"3.00"},{"id":15,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"INTERURBANO II","status_id":1,"name":"S/ 4.00","value":"4.00"},{"id":13,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"DIRECTO","status_id":1,"name":"S/ 5.00","value":"5.00"}]}
    
    auth = '{"status":true,"msg":"Autenticacion exitosa","data":{"user":{"name":"JOJHAN JORGE","lastname":"GOMEZ MEZA","doc_number":"45418515","status_id":1,"pattern_code":"G2188","route_id":1,"license":"45418515","license_expired_at":"2025-11-21"},"route_code":"IO-52","token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjozOTgsInBsYXRlX2lkIjoxNjYsInBsYXRlIjoiQkZHOTQxIiwicm91dGVfaWQiOjEsImNvbXBhbnlfaWQiOjEsInNlcmllX2lkIjozMTI3NCwibmFtZSI6IkpPSkhBTiBKT1JHRSIsInByb2dyYW1hdGlvbl9pZCI6MSwiaWF0IjoxNzE2MzU2Nzc1OTI5fQ.SnZyqksIwSAKOGte8W09TWGGjfTltIX7Og-f5VKNXpQ","ticket_init":10000012222,"company":{"name":"TRANSPORTES HUASCAR S.A.","logo":"https://res.cloudinary.com/dbdvax88n/image/upload/v1705960400/dn7r3lww19trwqq9wj92.jpg","ruc":"20121952140","soat":{"ruc":"20100041953","policy":"RC TPU NORMA 1599 - 2016-502183","company":"RIMAC SEGUROS Y REASEGUROS S.A.","valid_from":"2023-08-20","valid_to":"2024-08-20"}}}}'
    auth_json = json.loads(auth)
    print(json.dumps(auth_json, indent=4))
    ans = http2protocol.auth(auth_json)    
    print(ans)

    tarifa = '{"status":true,"msg":"Solicitud exitosa","data":[{"id":22,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"SOCIAL","status_id":1,"name":"S/ 1.00","value":"1.00"},{"id":20,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"URBANO","status_id":1,"name":"S/ 1.20","value":"1.20"},{"id":18,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"INTERURBANO I","status_id":1,"name":"S/ 1.50","value":"1.50"},{"id":16,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"INTERURBANO II","status_id":1,"name":"S/ 2.00","value":"2.00"},{"id":14,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"academic","ticket_description":"DIRECTO","status_id":1,"name":"S/ 2.50","value":"2.50"},{"id":23,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"ESCOLAR","status_id":1,"name":"S/ 1.00","value":"1.00"},{"id":21,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"SOCIAL","status_id":1,"name":"S/ 2.00","value":"2.00"},{"id":19,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"URBANO","status_id":1,"name":"S/ 2.50","value":"2.50"},{"id":17,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"INTERURBANO I","status_id":1,"name":"S/ 3.00","value":"3.00"},{"id":15,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"INTERURBANO II","status_id":1,"name":"S/ 4.00","value":"4.00"},{"id":13,"route_id":1,"deleted_at":null,"type":1,"ticket_type":"regular","ticket_description":"DIRECTO","status_id":1,"name":"S/ 5.00","value":"5.00"}]}'
    tarifa= json.loads(tarifa)
    print(json.dumps(tarifa, indent=4))
    ans = http2protocol.tarifa(tarifa)
    print(ans)

    hoja_de_ruta = "{\"status\":true,\"msg\":\"Ok\",\"data\":[{\"stop\":\"CASABLANCA\",\"estimatedTime\":\"09:41\",\"arrival\":\"09:38\",\"complete\":true,\"current\":false,\"previus\":true,\"next\":false,\"difference\":\"-2\"},{\"stop\":\"INICIO(B)\",\"estimatedTime\":\"09:44\",\"arrival\":\"09:41\",\"complete\":true,\"current\":true,\"previus\":false,\"next\":false,\"difference\":\"-2\"},{\"stop\":\"5MARISCAL\",\"estimatedTime\":\"09:53\",\"arrival\":\"--.--\",\"complete\":false,\"current\":false,\"previus\":false,\"next\":true,\"difference\":\"\"},{\"stop\":\"MIBANCOBAYOVAR\",\"estimatedTime\":\"09:57\",\"arrival\":\"--.--\",\"complete\":false,\"current\":false,\"previus\":false,\"next\":false,\"difference\":\"\"},{\"stop\":\"JOSEC.MARIATEGUI(B)\",\"estimatedTime\":\"10:00\",\"arrival\":\"--.--\",\"complete\":false,\"current\":false,\"previus\":false,\"next\":false,\"difference\":\"\"}]}"
    hoja_de_ruta = json.loads(hoja_de_ruta)
    print(json.dumps(hoja_de_ruta, indent=4))
    ans = http2protocol.hoja_de_ruta(hoja_de_ruta)
    print(ans)


    obtener_posiciones = '{"status": true, "msg": "Ok", "data": [{"type": "next", "plate": "B3I-752", "vehicleId": "273035", "stop": "5 MARISCAL ", "arrival": "2024-03-23 09:42:00", "color": "ff003e", "difference": "-5"}, {"type": "current", "plate": "BAW-915", "vehicleId": "270803", "stop": "5 MARISCAL ", "arrival": "2024-03-23 09:32:47", "color": "00b338", "difference": "0"}, {"type": "before1", "plate": "AAU-821", "vehicleId": "273010", "stop": "5 MARISCAL ", "arrival": "2024-03-23 09:08:19", "color": "00b338", "difference": "+24"}, {"type": "before2", "plate": "AWT-708", "vehicleId": "273060", "stop": "5 MARISCAL ", "arrival": "2024-03-23 08:48:05", "color": "00b338", "difference": "+44"}, {"type": "before3", "plate": "AHP-813", "vehicleId": "271009", "stop": "5 MARISCAL ", "arrival": "2024-03-23 08:42:59", "color": "00b338", "difference": "+49"}]}'
    obtener_posiciones = json.loads(obtener_posiciones)
    print(json.dumps(obtener_posiciones, indent=4))
    ans = http2protocol.obtener_posiciones(obtener_posiciones)
    print(ans)