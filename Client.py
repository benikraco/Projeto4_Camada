import sys
from enlace import *
import time
from Depara import makeHeader
import datetime

print("ESTAMOS NO CLIENT")
#   python -m serial.tools.list_ports

serialName = "/dev/cu.usbmodem143101"  # Mac    (variacao de) server 141101
# serialName = "COM2"                  # Windows(variacao de)


def main():
    try:
        com = enlace(serialName)

        imageR = input("Qual imagem você deseja copiar? (ex: imageB.png): ")
        request = input("Iniciar comunicação? [S/N]: ")

        log = open("client_log.txt","w")
        log.write("Transmissão começou - {}\n".format(datetime.datetime.now()))
        id_server = 0
        TIMEOUT = False
        manda_dnv = 0

        if request == "S":
            comeco = True
            ESTADO = "COMECO"
            com.enable()

        cont = 0

        while comeco:

            if ESTADO == "COMECO":

                txBuffer_A = open(imageR, 'rb').read()
                txSz_A = len(txBuffer_A)

                if txSz_A % 114 == 0:
                    numero_pacotes_handshake = txSz_A//114
                
                else:
                    numero_pacotes_handshake = txSz_A//114 + 1
                
                header = makeHeader(1, 0, id_server, numero_pacotes_handshake, 0, 0, 0, 0, 0, 0)
                eop = (0).to_bytes(4,byteorder="big")
                novo_pacote = header[0] + eop

                com.sendData(novo_pacote)
                print("O pacote envado tinha tamanho de {}".format(len(novo_pacote)))
                log.write('{} / envio / 1 / {} / 0 / {}\n'.format(datetime.datetime.now(), txSz_A, numero_pacotes_handshake))
                # time.sleep(0.2)
                print("Processo de comunicar Handshake")

                print('{} / envio / 1 / {} / 0 / {}\n'.format(datetime.datetime.now(), txSz_A, numero_pacotes_handshake))
                ESTADO = "ESPERANDO"

            if ESTADO == "ESPERANDO":
    
                print("Aguardando sinal do server...")

                espera = True

                while espera:

                    try: 
                        print("entrou")
                        print(com.tx.getBufferLen())
                        rxBuffer, nRx = com.getData(14)
                        print("nRx", nRx)
                        #print("rxBuffer", rxBuffer)
                        #print("nRx", nRx)

                    
                    except:
                        time.sleep(5)
                        dnv = input("Passaram 5 segundos, vamos tentar de novo? [S/N]")
                        if dnv == "S":
                            ESTADO: "ESPERANDO"
                        else:
                            log.write("{} / envio / 5\n".format(datetime.datetime.now()))
                            log.close()
                            print("Conexão encerrada")
                            raise Exception("ERRO")
                    #time.sleep(0.2)

                    log.write('{} / recebimento / 2 / {}\n'.format(datetime.datetime.now(),len(rxBuffer)))
                    #Sz_rxBuffer = rxBuffer[1]
                    
                    if nRx == 14:
                        print("Server respondendo.")
                        ESTADO = "LIVE"

                        print("O estado agora é {}".format(ESTADO))
                        espera = False

                    else:
                        time.sleep(5)
                        dnv = input("Passaram 5 segundos, vamos tentar de novo? [S/N]")
                        if dnv == "S":
                            ESTADO: "ESPERANDO"
                        else:
                            log.write("{} / envio / 5\n".format(datetime.datetime.now()))
                            log.close()
                            print("Conexão encerrada")
                            Exception = True

            #print(ESTADO, TIMEOUT)

            if ESTADO == "LIVE" and TIMEOUT == False:

                start = time.time()
                print("Timer acionado.")

                txBuffer = open (imageR, "rb").read()
                txSz = len(txBuffer)

                print("TxBuffer Size: {}".format(txSz))


                if txSz % 114 == 0:
                    pacotes_total = txSz//114
                else:
                    pacotes_total = txSz//114 + 1

                cont = 0
                pacote_env = 0
                pacotes_rest = pacotes_total
                pacote_atual = 1 #MUDAR PARA 2 ; ERRO 2

                while txSz > 0 and ESTADO != "DESCONECTADO":

                    if txSz >= 114:
                        #print("Chegou")

                        header = makeHeader(3, 0, id_server, pacotes_total, pacote_atual, 114, pacote_atual, pacote_atual - 1, 0, 0)
                        print("Header CHECK")
                        payload = txBuffer[cont:cont+114] 
                        print("Payload CHECK") 
    
                        eop2 = (0).to_bytes(4, byteorder="big")
                        pacote2 = header[0] + payload + eop2

                        com.sendData(pacote2)
                        time.sleep(0.01)

                        log.write("{} / envio / 3 / {} / {} / 0 / {}\n".format(datetime.datetime.now(), txSz, pacote_atual, pacotes_total))
                        print("{} / envio / 3 / {} / {} / 0 / {} - LOGADO".format(datetime.datetime.now(), txSz, pacote_atual, pacotes_total))

                        #print(com.rx.getBufferLen())
                        time.sleep(0.03)
                        # rxBuffer, nRx = com.getData(14)
                        #com.sendData(header)
                        #com.sendData(payload)
                        #com.sendData(eop)

                        RespHeaderServer, HeaderRxBuffer = com.getData(10)
                        print("RespHeaderServer: ", RespHeaderServer[0])
                        print("HeaderRxBuffer", HeaderRxBuffer)

                        log.write("{} / recebimento / 4 / {}\n".format(datetime.datetime.now(), (RespHeaderServer[0])))
                        print("{} / recebimento / 4 / {}\n".format(datetime.datetime.now(), (RespHeaderServer[0])))

                        # TIMEOUT = True
                        # ESTADO = "DESCONECTADO"
                        # comeco = False
                        # print(RespEOPServer[0])


                        if RespHeaderServer[0] == 0: #MUDAR PRA 6 ; ERRO 2  

                            manda_dnv += 1
                            if manda_dnv > 4:
                                print("Desligando server dps de 20 segundos.")
                                raise Exception("passaram 20 segs.")

                            time.sleep(5)
                            
                            header = makeHeader(3, 0, id_server, pacotes_total, pacote_atual, 114, pacote_atual, pacote_atual-1, 0, 0)
                            payload = txBuffer[cont:cont+114]
                            eop2 = (0).to_bytes(4, byteorder="big")
                            pacote2 = header[0] + payload + eop2

                            com.sendData(pacote2)
                            log.write("{} / envio / 3 / {} / {} / 0 / {}\n".format(datetime.datetime.now(), txSz, pacote_atual, pacotes_total))

                            print("{} / envio / 3 / {} / {} / 0 / {}\n".format(datetime.datetime.now(), txSz, pacote_atual, pacotes_total))
                            print("Mandando pacote novamente.")
                            
                        

                        else:
                            # print("oi")
                            RespEOPServer, EOPRxBuffer = com.getData(4)

                            log.write("{} / recebimento / 4 / {}\n".format(datetime.datetime.now(), (RespEOPServer[0])))
                            print("{} / recebimento / 4 / {}\n".format(datetime.datetime.now(), (RespEOPServer[0])))

                            print("RespEOPServeR", RespEOPServer)
                            print("eop2", eop2)

                            if RespEOPServer == eop2:
                                cont += 1
                                txSz -= 114
                                pacote_env += 1
                                pacote_atual += 1
                                pacotes_rest -= 1

                            else:

                                print("Erro. Tamanho de Payload not CHECK e EOP está na posição errada.")
                            
                            print("Pacote atual: {}".format(pacote_atual))
                            print("Pacotes enviados: {}".format(pacote_env))
                            print("O que sobrou do arquivo: {}".format(txSz))
                            
                    else:
                        header = makeHeader(3, 0, id_server, pacotes_total, pacote_atual, txSz, pacote_atual, pacote_atual-1, 0, 0)

                        payload = txBuffer[cont:]
                        eop2 = (0).to_bytes(4, byteorder="big")
                        pacote2 = header[0] + payload + eop2
                        print("Pacote CHECK")

                        com.sendData(pacote2)
                        log.write("{} / envio / 3 / {} / {} / 0 / {}\n".format(datetime.datetime.now(), txSz, pacote_atual, pacotes_total))

                        print("{} / envio / 3 / {} / {} / 0 / {}\n".format(datetime.datetime.now(), txSz, pacote_atual, pacotes_total))
                        print("Último pacote CHECK!")

                        comeco = False
                        ESTADO = "FIM"
                        break

        if ESTADO == "DESCONECTADO":

            print("Tempo acabou. Comunicação encerrada.")
            log.close()
            com.disable()

        if ESTADO == "FIM":
            print("Imagem enviada CHECK")

            rxBuffer, nRx = com.getData(1)
            print("Resposta final CHECK")
            print(rxBuffer)
            print(com.tx.getBufferLen())



            conf = int.from_bytes(rxBuffer, byteorder = "big")
            print("conf", conf)
            print("rxBuffer", rxBuffer[0])
            if conf == 4:
                print("Processo finalizado com SUCESSO!")
            
            finish = time.time()
            duracao = finish - start
            vel = txSz/duracao

            log.write("---------------------------\n")
            log.write("Transmissão encerrada às {}".format(datetime.datetime.now()))
            log.close()

            print("Taxa de transferência: {} bytes/s".format(vel))
            print("-------------------------")
            print("Comunicação encerrada")
            print("-------------------------")
            com.disable()

    except Exception as e:
        log.close()
        print("Algo deu errado...")
        com.disable()

        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print("ERRO: {}".format(e))
        print("Exception type: ", exception_type)
        print("File name: ", filename)
        print("Line number: ", line_number)
    
        # com.disable()

    # so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
