
# imageB = "imageB.png"
# txBuffer = open(imageB, 'rb').read()
# tamanho = len(txBuffer)
# dif = round(tamanho/114) 


def makeHeader(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9):
        un0 = (a0).to_bytes(1,byteorder="big") 
        un1 = (a1).to_bytes(1,byteorder="big") # type
        un2 = (a2).to_bytes(1,byteorder="big") # dif
        un3 = (a3).to_bytes(1,byteorder="big") # pacote correspondente do pacote
        un4 = (a4).to_bytes(1,byteorder="big") # size
        un5 = (a5).to_bytes(1,byteorder="big")
        un6 = (a6).to_bytes(1,byteorder="big")
        un7 = (a7).to_bytes(1,byteorder="big")
        un8 = (a8).to_bytes(1,byteorder="big")
        un9 = (a9).to_bytes(1,byteorder="big")

        header = un0 + un1 + un2  + un3 + un4 + un5 + un6 + un7 + un8 + un9

        return [header, un3]

# def makeEOP():
#     return (0).to_bytes(4,byteorder="big")