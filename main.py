import logging

#MRHP - Most Resource-Hungry Processes

def main():
    logging.basicConfig(format="%(levelname)s|%(asctime)s|%(message)s", datefmt="%d/%m/%Y %H:%M:%S",filename="log/first.log",level=logging.DEBUG)
    logging.warning("Your computer is overheating!")
    logging.info("Temp:72C")
    logging.debug("Total|CPU:85%;RAM:100%;SWAP:5.5GB/7.85GB;NOTE:Lorem ipsum dolor sit amet")
    logging.debug("MRHP|PIDs:2420,1313,2424,2425,242;CPU:21%,22%,34%,10%,2%;RAM:45%,10%,15%,10%,20%")


if __name__ == '__main__':
    main()
