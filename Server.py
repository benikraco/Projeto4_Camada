import sys
from enlace import *
import time
from Depara import makeHeader
import datetime

print("ESTAMOS NO SERVER")
#   python -m serial.tools.list_ports

serialName = "/dev/cu.usbmodem14401"  # Mac    (variacao de) server 
#serialName = "COM2"                  # Windows(variacao de)

def main():
    log = open("server_log.txt","w")
    #print("oi")

    try:
        com1 = enlace(serialName)
        
        com1.enable()

        print("Porta COM {} habilitada.".format(serialName))


        funcionando = True
        ESTADO = "COMECO"
        imageW = "./imgRecebida.png"
        ft = bytes(0)
        pacote_anterior = 0 #MUDAR NUMERO DO PACOTE ANTERIOR ERRO 2
        id_server = 1
        TIMEOUT = False

        while funcionando:
            #print(com1.rx.getBufferLen())
            #print("Entrou")

            if ESTADO == "COMECO":

                handsk = True
                #print("oi")

                while handsk:
                    
                    rxBuffer, nRx = com1.getData(14)
                    #print("hello")
                    certo = rxBuffer[0]
                    #print("oiiii")cl
                    #print(com1.rx.getBufferLen())
                    

                    log.write("{} / recebimento / 1 / {}\n".format(datetime.datetime.now(), rxBuffer[1]))
                    print("{} / recebimento / 1 / {}\n".format(datetime.datetime.now(), rxBuffer[1]))

                    time.sleep(0.1)
                    print("Foram recebidos {} bytes de dados.".format(rxBuffer[1]))

                    if rxBuffer[0] == 1 and rxBuffer[2] == 0:
                        print("Entrou")

                        header = makeHeader(2, 0, id_server, rxBuffer[3], 0, 0, 0, 0, 0, 0)
                        #print(header)
                        #print(eop)
                        eop = (0).to_bytes(4, byteorder="big")
                        pacote = header[0] + eop
                        #print(pacote)
                        print(len(pacote))
                        com1.sendData(pacote)
                        #teste = (1024).to_bytes(2, byteorder = "big")
                        #com1.sendData(teste)
                        #time.sleep(0.5)
                        print("Comunicação Handshake...")

                        log.write("{} / envio / 2 / 0 / {}\n".format(datetime.datetime.now(), int.from_bytes(header[1],byteorder="big")))
                        print("{} / envio / 2 / 0 / {}\n".format(datetime.datetime.now(), int.from_bytes(header[1],byteorder="big")))

                        ESTADO = "LIVE"
                        print("O ESTADO atual é {}".format(ESTADO))
                        handsk = False

                    else:
                        print("Header identificou erro no tipo de mensagem ou no identificador.")
            #print("oi", ESTADO, TIMEOUT)
            if ESTADO == "LIVE" and TIMEOUT == False:

                #print("oi")

                rxBuffer, nRx = com1.getData(10)
                
                certo = rxBuffer[0]

                if rxBuffer == "TIMEOUT":
                    header = (5,0,0,0,0,0,0,0,0,0)
                    log.write("{} / envio / 5\n".format(datetime.datetime.now()))
                    print("{} / envio / 5\n".format(datetime.datetime.now()))

                    TIMEOUT = True
                    print("TIMEOUT activated")

                    ESTADO = "DESCONECTADO"
                    print("Estado atual: {}".format(ESTADO))
                    funcionando = False
                
                else:

                    msg_tp = rxBuffer[0]
                    id_client = rxBuffer[2]
                    pacotes_total = rxBuffer[3]
                    pacote_atual = rxBuffer[4]
                    sz = rxBuffer[5]
                    pacote_resto = rxBuffer[6]
                    ultimo_pacote = rxBuffer[7]
                    CRC1 = rxBuffer[8]
                    CRC2 = rxBuffer[9]

                    print("Pacote Atual: {}".format(pacote_atual))
                    print("Tamanho: {}".format(sz))

                    txBuffer, nTx = com1.getData(sz)
                    #print(ft)
                    ft += txBuffer
                    
                    #print(txBuffer)
                    #print(ft)

                    print("Payload Size: {}".format((nTx)))
                    eop, nEop = com1.getData(4)
                    eop_A = eop

                    log.write("{} / recebimento / 3 / {} / {} / 0 / {}\n".format(datetime.datetime.now(), sz, pacote_atual, pacotes_total))

                    header = makeHeader(4, 0, id_server, pacotes_total, pacote_atual, sz, pacote_resto, ultimo_pacote, CRC1, CRC2)
                    payload = 0
                    pacote = header[0] + eop_A
                    #print(pacote)

                    if pacote_atual == pacote_anterior +1:
                        pacote_anterior += 1 
                        com1.sendData(pacote)
                        log.write("{} / envio / 4 / 14\n".format(datetime.datetime.now()))
                        print("{} / envio / 4 / 14 - LOGADO".format(datetime.datetime.now()))
                    
                    else:

                        print("Ordem dos pacotes está errada.")
                        header = makeHeader(6 , 0 , id_server, pacotes_total, pacote_atual, sz, pacote_resto, ultimo_pacote, CRC1, CRC2)
                        pacote = header[0] + eop_A
                        com1.sendData(pacote)

                        log.write("{} / envio / 6 / {}".format(datetime.datetime.now(), pacote_resto))

                    if sz < 114:

                        com1.disable()
                        print("Transmissão finalizada com último pacote recebido.")
                        break

        if ESTADO == "DESCONETCADO":
            print("Conexão encerrada, tempo máximo esgotado.")
            print("-------------------------")
            print("Comunicação encerrada às {}\n".format(datetime.datetime.now()))
            print("-------------------------")
            log.close()
            com1.disable()
            
        print("Dados sendo salvos no arquivo {}".format(imageW))
        f = open(imageW, 'wb')
        f.write(ft)
        print("Imagem salva!")

        com1.sendData((0).to_bytes(1, byteorder="big"))
        time.sleep(0.2)
        print("Processo finalizado com resposta final CHECK.")

        # Encerra comunicação
    except Exception as e:
        print("Algo deu errado...")
        log.close()
        com1.disable()
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno

        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)
    
    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()