# main.py
# pylint:disable=E0611
# pylint:disable=E1101
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtGui import QPixmap
from PIL.ImageQt import ImageQt
from uiMainWindow import Ui_MainWindow

from PyQt5 import QtGui

import qrcode
from web3 import Web3

# Address of Ethereum node
nodeAddr = ""
# Address of Ethereum smart contract
contractAddr = "0x7106871829dA3196725AB8B798156512EdC062ea"
# ABI of Ethereum smart contract
abi = '[{"constant":false,"inputs":[],"name":"payout","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getOwner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"price","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_price","type":"uint256"}],"name":"changePrice","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"_price","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"customerAccount","type":"address"},{"indexed":false,"name":"amount","type":"uint256"}],"name":"newOrder","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"oldPrice","type":"uint256"},{"indexed":false,"name":"newPrice","type":"uint256"}],"name":"newPrice","type":"event"}]'
# Connect web3 provider to Ethereum node
web3 = Web3(Web3.HTTPProvider(nodeAddr))


# Main window class
class MainWindow(QMainWindow):
    def __init__(self, uiFile, parent=None):
        super(MainWindow, self).__init__(parent)
        # load ui file
        self.window = Ui_MainWindow()
        self.window.setupUi(self)
        # set count and price
        self.count = 0
        self.price = 0

        # generate qr code from address and set image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=4
        )
        qr.add_data(contractAddr)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        # convert pil image to pixmap
        qim = ImageQt(img)
        pix = QPixmap.fromImage(qim)
        self.window.qrLabel.setPixmap(pix)

        # connect button handlers
        self.window.closeButton.clicked.connect(self.close)
        self.window.pushButton.clicked.connect(self.pour)

    def closeEvent(self, event):
        global thread
        thread.exiting = True
        thread.wait()
        event.accept()  # let the window close

    def pour(self):
        if self.count > 0:
            self.window.pushButton.setEnabled(False)
            self.window.pushButton.setText("Pouring ...")
            self.count -= 1
            print("Pouring...")
            QTimer.singleShot(5000, self.finishPouring)

    def finishPouring(self):
        print("finished Pouring")
        self.window.pushButton.setText("Pour")
        self.window.pushButton.setEnabled(True)

    @property
    def count(self):
        return self._count

    # set count ui when setting count variable
    @count.setter
    def count(self, value):
        self._count = value
        self.setCount(self._count)

    @property
    def price(self):
        return self._price

    # set price ui when setting price variable
    @price.setter
    def price(self, value):
        self._price = value
        self.setPrice(self._price)

    def setCount(self, count):
        self.window.lcdNumber.display(count)

    def setPrice(self, price):
        self.window.priceLabel.setText("1 Drink = " + str(price) + " ETH")


# main functionality
class Thread(QThread):
    def __init__(self, parent=None):
        super(Thread, self).__init__(parent)
        global ui
        self.exiting = False
        # set contract
        self.contract = web3.eth.contract(address=contractAddr, abi=abi)
        if web3.isConnected():
            # get current price in Wei
            price = self.contract.functions.price().call()
            # set price in Ether
            ui.price = web3.fromWei(price, 'ether')
            self.orderFilter = self.contract.events.newOrder.createFilter(
                fromBlock='latest'
            )
            self.priceFilter = self.contract.events.newPrice.createFilter(
                fromBlock='latest'
            )

        else:
            ui.window.nodeInfoLabel.setText("Not connected to Node")

    def run(self):
        global ui
        while self.exiting is False:
            # check if node is up to date
            syncing = web3.eth.syncing
            if syncing is False:
                blockNumber = web3.eth.blockNumber
                ui.window.nodeInfoLabel.setText(
                    "Blocknumber: " + str(blockNumber)
                )
                orderFilter = self.orderFilter.get_new_entries()
                priceFilter = self.priceFilter.get_new_entries()

                if len(orderFilter):
                    ui.count = orderFilter[0].args.amount
                if len(priceFilter):
                    ui.price = web3.fromWei(
                        priceFilter[0].args.newPrice, "ether"
                    )

            else:
                ui.window.nodeInfoLabel.setText(
                    "Syncing: " + str(syncing.currentBlock) +
                    "/" + str(syncing.highestBlock)
                )

            QThread().sleep(1)


def main():
    # start window and ui
    global ui
    global app
    app = QApplication(sys.argv)
    ui = MainWindow("pay2pour/mainwindow.ui")

    # start main thread
    global thread
    thread = Thread()
    thread.start()

    # show ui
    ui.showFullScreen()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
