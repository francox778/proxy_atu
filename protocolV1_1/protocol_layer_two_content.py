import os
import sys

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)
    
import typing
import struct
import protocolV1_1.protocol_headers as protocol_headers
import echos
import protocolV1_1.utils as utils


class alerta_data_tuple(typing.NamedTuple):
    timestamp: int


class alerta_data():
    def __init__(buf):
        pass
    @staticmethod
    def read(alerta) -> alerta_data_tuple:
        timestamp = struct.unpack(f"{protocol_headers.ENDIANESS}Q", alerta)[0]
        return alerta_data_tuple(timestamp)

    @staticmethod
    def write( alerta: alerta_data_tuple) -> bytearray: 
        return struct.pack(f"{protocol_headers.ENDIANESS}Q", alerta.timestamp)



class authentication_data_tuple(typing.NamedTuple):
    name :          bytearray
    lastname:       bytearray
    doc_number:     bytearray
    pattern_code:   bytearray
    route_code:     bytearray
    name_company:   bytearray
    logo:           bytearray
    ruc:            bytearray
    ruc_soat:       bytearray
    policy:         bytearray
    company:        bytearray
    token:          bytearray
    ticket_init:    int
    from_time:      int
    to_time:        int
    
    def __str__(self):
        return   f"""name :         {self.name.decode('latin-1')}
                    lastname:       {self.lastname.decode('latin-1')}
                    doc_number:     {self.doc_number.decode('latin-1')}
                    pattern_code:   {self.pattern_code.decode('latin-1')}
                    route_code:     {self.route_code.decode('latin-1')}
                    name_company:   {self.name_company.decode('latin-1')}
                    logo:           {self.logo.decode('latin-1')}
                    ruc:            {self.ruc.decode('latin-1')}
                    ruc_soat:       {self.ruc_soat.decode('latin-1')}
                    policy:         {self.policy.decode('latin-1')}
                    company:        {self.company.decode('latin-1')}
                    token:          {self.token.decode('latin-1')}
                    ticket_init:    {self.ticket_init}
                    from_time:      {self.from_time}
                    to_time:        {self.to_time}"""


class authentication_data():
    def __init__(buf):
        pass
    @staticmethod
    def read( authentication: bytearray) -> authentication_data_tuple:
        ans = bytearray()
        idx = 0
        data_txt = []
        for _ in range(12):
            data_end = authentication.find(0, idx)
            data = authentication[idx: data_end]
            idx+= len(data) + 1
            data_txt.append(data)
        [ticket_init, from_time, to_time] = struct.unpack(f"{protocol_headers.ENDIANESS}QII", authentication[idx:idx+16])
        
        auth_tuple = authentication_data_tuple(*data_txt, ticket_init, from_time, to_time)
        return auth_tuple

    @staticmethod
    def write( authentication: authentication_data_tuple) -> bytearray:
        name            = authentication.name + bytearray([0])          
        lastname        = authentication.lastname + bytearray([0])      
        doc_number      = authentication.doc_number + bytearray([0])      
        pattern_code    = authentication.pattern_code + bytearray([0])      
        route_code      = authentication.route_code + bytearray([0])      
        name_company    = authentication.name_company + bytearray([0])      
        logo            = authentication.logo + bytearray([0])      
        ruc             = authentication.ruc + bytearray([0])      
        ruc_soat        = authentication.ruc_soat + bytearray([0])      
        policy          = authentication.policy + bytearray([0])      
        company         = authentication.company + bytearray([0])   
        token           = authentication.token + bytearray([0])     
        ticket_init     = struct.pack(f"{protocol_headers.ENDIANESS}Q", utils.trunc_number(authentication.ticket_init,8))
        from_time       = struct.pack(f"{protocol_headers.ENDIANESS}I", authentication.from_time)
        to_time         = struct.pack(f"{protocol_headers.ENDIANESS}I", authentication.to_time)
        return name+lastname+doc_number+pattern_code+route_code+name_company+ logo+ruc+ruc_soat+policy+company+ token +ticket_init+from_time+to_time
    #name 		 char array termina en 0
	#lastname	 char array termina en 0
	#docnumber	 char array termina en 0
	#patter_code  char array termina en 0
	#route_code   char array termina en 0
	#name		 char array termina en 0
	#logo 		 char array termina en 0
	#ruc 		 char array termina en 0
	#ruc_soat	 char array termina en 0
	#policy       char array termina en 0
	#company 	 char array termina en 0
	#ticket_init  uint64_t
	#from 		 uint32_t  
	#to			 uint32_t

        



class tarifa_data_tuple(typing.NamedTuple):
    id: int
    type:int
    ticket_type:int
    value:int
    ticket_description: bytearray


    def __str__(self) -> str:
        return   f"""id :                {self.id}
type:               {self.type}
ticket_type:        {self.ticket_type}
value:              {self.value}
ticket_description: {self.ticket_description.decode('latin-1')}"""

class tarifa_data():
    def __init__():
        pass
    
    @staticmethod
    def read(tarifa: bytearray) -> "list[tarifa_data_tuple]":
        n_tarifas = struct.unpack(f"{protocol_headers.ENDIANESS}B", tarifa[:1])[0]
        idx = 1
        ans = list()
        for _ in range(n_tarifas):
            [_id, type, ticket_type, value] = struct.unpack(f"{protocol_headers.ENDIANESS}BBBH", tarifa[idx:idx+5])
            idx+=5
            ticket_description_end = tarifa.find(0, idx)
            ticket_description = tarifa[idx: ticket_description_end]
            idx+= len(ticket_description)+1 
            ans.append(tarifa_data_tuple(_id, type, ticket_type, value, ticket_description))
            
        return ans

    @staticmethod
    def write(tarifas: "list[tarifa_data_tuple]"):
        buff = struct.pack(f"{protocol_headers.ENDIANESS}B", len(tarifas))
        for tarifa in tarifas:
            _id                 = struct.pack(f"{protocol_headers.ENDIANESS}B", tarifa.id)
            type                = struct.pack(f"{protocol_headers.ENDIANESS}B", tarifa.type)
            ticket_type         = struct.pack(f"{protocol_headers.ENDIANESS}B", tarifa.ticket_type) 
            value               = struct.pack(f"{protocol_headers.ENDIANESS}H", tarifa.value)
            ticket_description  = tarifa.ticket_description + bytearray([0])
            
            buff += _id + type + ticket_type + value + ticket_description 
        #id 					uint8_t
        #type 				uint8_t 1 0
        #ticket type 		uint8_t 1 0
        #ticket_description	char array termina en 0
        #name	(X)
        #value 				uint16_t precio x 100 = 1.5 soles seria 1500
        return buff


class tickets_data_tuple(typing.NamedTuple):
    type: int           # 1 payed 2 canceled
    tariff_id: int  
    ticket_n: int
    timestamp: int
    def __str__(self) -> str:
        return   f"""type :                  {self.type}
tariff_id:              {self.tariff_id}
ticket_n:               {self.ticket_n}
timestamp:              {self.timestamp}"""

class tickets_data():
    def __init__(buf):
        pass

    def read(tickets) -> "list[tickets_data_tuple]":
        n_tickets = tickets[0]
        idx = 1
        ans = []
        for ticket in range(n_tickets):
            [type, tariff_id, ticket_n, timestamp] = struct.unpack(f"{protocol_headers.ENDIANESS}BBQQ", tickets[idx:idx+18])
            idx += 18
            ticket = tickets_data_tuple(type, tariff_id, ticket_n, timestamp)
            ans.append(ticket)
        return ans

    @staticmethod
    def write(tickets: "list[tickets_data_tuple]"):
        buff= struct.pack(f"{protocol_headers.ENDIANESS}B", len(tickets))
        for ticket in tickets:
            type = struct.pack(f"{protocol_headers.ENDIANESS}B", ticket.type)
            tariff_id = struct.pack(f"{protocol_headers.ENDIANESS}B", ticket.tariff_id)
            ticket_n = struct.pack(f"{protocol_headers.ENDIANESS}Q", ticket.ticket_n)
            timestamp = struct.pack(f"{protocol_headers.ENDIANESS}Q", ticket.timestamp)
            buff += type + tariff_id + ticket_n + timestamp

        #type 				uint8_t  payed = 1, uint8_t canceled = 2 
        #ticket				uint64_t ticket_number
        #timestamp			uint64_t timestamp
        return buff


class hoja_de_ruta_data_tuple(typing.NamedTuple):
    stop:bytearray
    estimated_time:int
    arrival_time:int
    state:int
    difference:int
    def __str__(self) -> str:
        return   f"""stop :              {self.stop.decode('latin-1')}
estimated_time:     {self.estimated_time}
arrival_time:       {self.arrival_time}
state:              {self.state}
difference:         {self.difference}"""

class hoja_de_ruta_data():
    def __init__(buf):
        pass

    def read(hoja_de_ruta: bytearray) -> "list[hoja_de_ruta_data_tuple]":
        n_paraderos = struct.unpack(f"{protocol_headers.ENDIANESS}B", hoja_de_ruta[:1])[0]
        idx = 1
        ans = []
        for _ in range(n_paraderos):
            stop_end = hoja_de_ruta.find(0, idx)
            stop = hoja_de_ruta[idx : stop_end]
            idx += len(stop) + 1
            [estimated_time, arrival_time, state, difference] = struct.unpack(f"{protocol_headers.ENDIANESS}HHBh", hoja_de_ruta[idx:idx+7])
            idx += 7
            paradero = hoja_de_ruta_data_tuple(stop, estimated_time, arrival_time, state, difference)
            ans.append(paradero)
        return ans

    @staticmethod
    def write(paraderos: "list[hoja_de_ruta_data_tuple]"):
        buff = struct.pack(f"{protocol_headers.ENDIANESS}B", len(paraderos))
        for paradero in paraderos:
            stop = paradero.stop + bytearray([0])
            estimated_time = struct.pack(f"{protocol_headers.ENDIANESS}H", paradero.estimated_time)
            arrival_time   = struct.pack(f"{protocol_headers.ENDIANESS}H", paradero.arrival_time) 
            state       = struct.pack(f"{protocol_headers.ENDIANESS}B", paradero.state)
            difference     = struct.pack(f"{protocol_headers.ENDIANESS}h", paradero.difference)
            buff += stop + estimated_time + arrival_time + state + difference
        return buff
        #n.paraderos uint8_t
        #stop 	 		char array termina en 0 
		#estimated time	uint16_t	09:41 hora X 1000 + minutos.	0 = --.--
		#arrival time	uint16_t	09:41 hora X 1000 + minutos.	0 = --.--
		#complete current previous next
		#				uint8_t complete(3) current(2) previous(1) next(0)
		#diference		int8? o int16?
        


class posiciones_data_tuple(typing.NamedTuple):
    type: int
    plate: bytearray
    difference: int
    def __str__(self) -> str:
        return   f"""   
    type       :{self.type}
    plate:     {self.plate.decode('latin-1')}
    difference:{self.difference}"""

class posiciones_data():
    def __init__(buf):
        pass
    
    def read( posiciones: bytearray) -> "list[posiciones_data_tuple]":
        n_posiciones = struct.unpack(f"{protocol_headers.ENDIANESS}B", posiciones[:1])[0]
        ans = []
        idx = 1
        for _ in range(n_posiciones):
            type = struct.unpack(f"{protocol_headers.ENDIANESS}B", posiciones[idx:idx+1])[0]
            idx+=1
            plate_end = posiciones.find(0, idx)
            plate = posiciones[idx: plate_end]
            idx+= len(plate) + 1
            difference = struct.unpack(f"{protocol_headers.ENDIANESS}h", posiciones[idx:idx+2])[0]
            idx+=2
            ans.append(posiciones_data_tuple(type, plate, difference))
        return ans

    @staticmethod
    def write(posiciones: "list[posiciones_data_tuple]"):
        buff = struct.pack(f"{protocol_headers.ENDIANESS}B", len(posiciones))
        for posicion in posiciones:
            type  = struct.pack(f"{protocol_headers.ENDIANESS}B", posicion.type)
            plate = bytearray(posicion.plate) + bytearray([0])
            difference = struct.pack(f"{protocol_headers.ENDIANESS}h", posicion.difference)
            buff += type + plate + difference
        #type	0: next 1: current 2: before
        #plate	char array termina en 0
        #vehicle (X)
        #arrival (X)
        #color	(X)
        #difference int8 o int16?
        return buff
    



if __name__ == "__main__":
    print("ALERTA TEST INICIO")
    # TEST ALERTA
    alerta = alerta_data_tuple(161616516)
    Balerta = alerta_data.write(alerta)
    BalertaLen = len(Balerta)
    print(f"{Balerta}")
    print(alerta_data.read(Balerta))

    # TEST AUTH
    authentication = authentication_data_tuple(    
                name =          b'name',
                lastname =      b'lastname',
                doc_number =    b'doc_number',
                pattern_code =  b'pattern_code',
                route_code =    b'route_code',
                name_company =  b'name_company',
                logo =          b'logo',
                ruc =           b'ruc',
                ruc_soat =      b'ruc_soat',
                policy =        b'policy',
                company =       b'company',
                token=          b'1561565165169196165161651616',
                ticket_init =   10000000001,
                from_time =     1200,
                to_time =       1500)
    Bauth = authentication_data.write(authentication)
    print(echos.bytearray2str(Bauth))

    BauthLen = len(Bauth)
    print(Bauth)
    buff = authentication_data.read(Bauth)
    print(buff)
    print("ALERTA TEST FIN\n\n")
    print("TARIFA TEST INICIO")

    # TEST TARIFA DATA
    tarifa0 = tarifa_data_tuple(
                id = 1, 
                type = 1, 
                ticket_type = 0, 
                value = 100,
                ticket_description = b"Escolar"
                )
    tarifa1 = tarifa_data_tuple(
                id = 2, 
                type = 1, 
                ticket_type = 0, 
                value = 150,
                ticket_description = b"Zonal/Social"
                ) 
    tarifa2 = tarifa_data_tuple(
                id = 2, 
                type = 1, 
                ticket_type = 0, 
                value = 200,
                ticket_description = b"Urbano"
                )    
    tarifa3 = tarifa_data_tuple(
                id = 2, 
                type = 1, 
                ticket_type = 0, 
                value = 250,
                ticket_description = b"Interurbano"
                )        
    tarifa = [ tarifa0, tarifa1, tarifa2, tarifa3 ]     
    
    buff = tarifa_data.write(tarifa)
    Btarifax1 = len(buff)/4
    print(echos.bytearray2str(buff))
    buff = tarifa_data.read(buff)
    for t in buff:
        print(t)

    print("TARIFA TEST FIN \n\n")
    print("TICKETS TEST INICIO")
##      TEST TICKETS
    ticket0 = tickets_data_tuple(1, 5, 10000000001, 654646546)
    ticket1 = tickets_data_tuple(1, 6, 10000000002, 654646547)
    ticket2 = tickets_data_tuple(1, 8, 10000000003, 654646548)
    ticket3 = tickets_data_tuple(1, 9, 10000000004, 654646549)
    tickets = [ ticket0, ticket1, ticket2, ticket3]

    buff = tickets_data.write(tickets)
    Bticketx1 = len(buff)/4
    print(buff)
    buff = tickets_data.read(buff)
    print(buff)
    print("TICKETS TEST FIN \n\n")
    print("HOJA DE RUTA TEST INICIO")
# TEST HOJA DE RUTA
    paradero0 = hoja_de_ruta_data_tuple( b"CASABLANCA", 941, 951, 1,-30)
    paradero1 = hoja_de_ruta_data_tuple( b"MI BANCO BAYOVAR", 941, 951, 1,-30)
    paradero2 = hoja_de_ruta_data_tuple( b"5 MARISCAL", 941, 951, 1,-30)
    paradero3 = hoja_de_ruta_data_tuple( b"JOSE C. MARIATEGUI", 941, 951, 1,-30)

    paraderos = [ paradero0, paradero1, paradero2, paradero3]
    buff = hoja_de_ruta_data.write(paraderos)
    Bparaderosx1 = len(buff)/4
    print(echos.bytearray2str(buff))
    buff = hoja_de_ruta_data.read(buff)
    for paradero in buff:
        print(paradero)

    print("HOJA DE RUTA TEST FIN \n\n")
    print("POSICIONES TEST INICIO")       
    posicion0 = posiciones_data_tuple(1, b"B3I-752", -5)
    posicion1 = posiciones_data_tuple(1, b"BAW-915", -6)
    posicion3 = posiciones_data_tuple(1, b"AAU-821", -7)
    posicion3 = posiciones_data_tuple(1, b"AWT-708", -8)
    posicion4 = posiciones_data_tuple(1, b"AHP-813", -9)
    posicion5 = posiciones_data_tuple(1, b"BAW-914", -0)

    posiciones = [posicion0, posicion1, posicion3, posicion4, posicion5]
    buff = posiciones_data.write(posiciones)
    print(echos.bytearray2str(buff))
    BposicionesLen = len(buff)/5
    print(buff)
    buff = posiciones_data.read(buff)
    for placa in buff:
        print(placa)
    print("POSICIONES FIN \n\n")

    print(f"""BalertaLen   = {BalertaLen} 
Bauth        = {BauthLen} 
Btarifax1    = {Btarifax1}
Bticketx1    = {Bticketx1} 
Bparaderosx1 = {Bparaderosx1} 
Bposicionesx1  = {BposicionesLen}""")



    authentication = authentication_data_tuple(    
                name =          b'',
                lastname =      b'',
                doc_number =    b'',
                pattern_code =  b'pattern_code',
                route_code =    b'route_code',
                name_company =  b'name_company',
                logo =          b'logo',
                ruc =           b'ruc',
                ruc_soat =      b'ruc_soat',
                policy =        b'policy',
                company =       b'company',
                token=          b'1561565165169196165161651616',
                ticket_init =   10000000001,
                from_time =     1200,
                to_time =       1500)
    
    Bauth = authentication_data.write(authentication)
    print(echos.bytearray2str(Bauth))

    buff = authentication_data.read(Bauth)
    print(buff)