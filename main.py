import sys,os
from PyQt5.QtWidgets import (QWidget, QPushButton,
    QHBoxLayout, QVBoxLayout, QApplication,QLineEdit,QComboBox,QTextEdit,QLabel,QFileDialog)

class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.FileName=''
        self.initUI()


    def initUI(self):

        self.Mode = QComboBox(self)
        self.Mode.addItem('拆分文件')
        self.Mode.addItem('合并文件')


        self.selectFile = QPushButton('请选择输入文件（若要合并请随意选择一个）')
        self.okButton = QPushButton('OK')

        self.selectFile.clicked.connect(lambda:self.getFileName())
        self.okButton.clicked.connect(self.OKClicked)

        self.blockSize = QComboBox(self)
        self.blockSize.addItem('分成 x 块(x填在下面)')
        self.blockSize.addItem('每块 x Bit(x填在下面)')

        self.bolckX=QLineEdit(self)

        self.tipLable=QLabel('请选择文件',self)

        self.vbox=QVBoxLayout()
        self.vbox.addStretch(1)

        self.vbox.addWidget(self.Mode)
        self.vbox.addWidget(self.selectFile)
        self.vbox.addWidget(self.blockSize)
        self.vbox.addWidget(self.bolckX)
        self.vbox.addWidget(self.okButton)
        self.vbox.addWidget(self.tipLable)
        self.setLayout(self.vbox)

        #self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('文件拆分工具')
        self.show()

    def split(self, fromfile, todir, chunksize):
        if not os.path.exists(todir):  # check whether todir exists or not
            os.mkdir(todir)
        else:
            for fname in os.listdir(todir):
                os.remove(os.path.join(todir, fname))
        partnum = 0
        inputfile = open(fromfile, 'rb')  # open the fromfile
        while True:
            chunk = inputfile.read(chunksize)
            if not chunk:  # check the chunk is empty
                break
            partnum += 1
            filename = os.path.join(todir, ('part%04d' % partnum))
            fileobj = open(filename, 'wb')  # make partfile
            fileobj.write(chunk)  # write data into partfile
            fileobj.close()
        return partnum

    def joinfile(self, fromdir, filename, todir):
        if not os.path.exists(todir):
            os.mkdir(todir)
        if not os.path.exists(fromdir):
            print('Wrong directory')
        outfile = open(os.path.join(todir, filename), 'wb')
        files = os.listdir(fromdir)  # list all the part files in the directory
        files.sort()  # sort part files to read in order
        for file in files:
            filepath = os.path.join(fromdir, file)
            infile = open(filepath, 'rb')
            data = infile.read()
            outfile.write(data)
            infile.close()
        outfile.close()

    def getFileName(self):
        self.FileName=QFileDialog.getOpenFileName(self,"请选择要处理的文件",'./',"All Files (*)")[0]

    def OKClicked(self):
        if self.FileName!='':
            if self.Mode.currentIndex()==0:
                try:
                    os.mkdir(self.FileName + 'Split')
                except:
                    pass
                try:
                    if self.blockSize.currentIndex() == 1:
                        ch = int(self.bolckX.text())
                    else:
                        fsize = os.path.getsize(self.FileName)
                        ch = int(fsize / int(self.bolckX.text())) + 1
                    self.split(self.FileName, self.FileName + 'Split', ch)
                    self.tipLable.setText("分割成功")
                except:
                    self.tipLable.setText("没填要分几份哦")

            else:
                try:
                    dirName = self.FileName[:self.FileName.rfind('/')]
                    fileName = dirName[dirName.rfind('/') + 1:-5]
                    dirName1 = dirName[:dirName.rfind('/')]
                    self.joinfile(dirName, fileName, dirName1)
                    self.tipLable.setText("合并成功")
                except:
                    self.tipLable.setText("文件选错了")
        else:
            self.tipLable.setText("文件没选哦")






if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainUI()
    sys.exit(app.exec_())