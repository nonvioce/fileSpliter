import sys, os,  struct
from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QApplication,QLineEdit,QComboBox,QLabel,QFileDialog)
from Crypto.Cipher import AES
try:
    from Crypto.Util.Padding import pad, unpad
except ImportError:
    from Crypto.Util.py3compat import bchr, bord
    def pad(data_to_pad, block_size):
        padding_len = block_size-len(data_to_pad)%block_size
        padding = bchr(padding_len)*padding_len
        return data_to_pad + padding
    def unpad(padded_data, block_size):
        pdata_len = len(padded_data)
        if pdata_len % block_size:
            raise ValueError("Input data is not padded")
        padding_len = bord(padded_data[-1])
        if padding_len<1 or padding_len>min(block_size, pdata_len):
            raise ValueError("Padding is incorrect.")
        if padded_data[-padding_len:]!=bchr(padding_len)*padding_len:
            raise ValueError("PKCS#7 padding is incorrect.")
        return padded_data[:-padding_len]


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

        self.IsEnc = QComboBox(self)
        self.IsEnc.addItem('不加密（下面不用填）')
        self.IsEnc.addItem('加密（请在下面填入密匙）')

        self.EncKey = QLineEdit(self)



        self.tipLable=QLabel('请选择文件',self)

        self.vbox=QVBoxLayout()
        self.vbox.addStretch(1)

        self.vbox.addWidget(self.Mode)
        self.vbox.addWidget(self.selectFile)
        self.vbox.addWidget(self.blockSize)
        self.vbox.addWidget(self.bolckX)
        self.vbox.addWidget(self.IsEnc)
        self.vbox.addWidget(self.EncKey)
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

    def encrypt_file(self, key, in_filename, out_filename=None, chunksize=64 * 1024):
        if not out_filename:
            out_filename = in_filename + '.enc'
        iv = os.urandom(16)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        filesize = os.path.getsize(in_filename)
        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                outfile.write(struct.pack('<Q', filesize))
                outfile.write(iv)
                pos = 0
                while pos < filesize:
                    chunk = infile.read(chunksize)
                    pos += len(chunk)
                    if pos == filesize:
                        chunk = pad(chunk, AES.block_size)
                    outfile.write(encryptor.encrypt(chunk))

    def decrypt_file(self, key, in_filename, out_filename=None, chunksize=64 * 1024):
        if not out_filename:
            out_filename = in_filename + '.dec'
        with open(in_filename, 'rb') as infile:
            filesize = struct.unpack('<Q', infile.read(8))[0]
            iv = infile.read(16)
            encryptor = AES.new(key, AES.MODE_CBC, iv)
            with open(out_filename, 'wb') as outfile:
                encrypted_filesize = os.path.getsize(in_filename)
                pos = 8 + 16  # the filesize and IV.
                while pos < encrypted_filesize:
                    chunk = infile.read(chunksize)
                    pos += len(chunk)
                    chunk = encryptor.decrypt(chunk)
                    if pos == encrypted_filesize:
                        chunk = unpad(chunk, AES.block_size)
                    outfile.write(chunk)

    def getFileName(self):
        self.FileName=QFileDialog.getOpenFileName(self,"请选择要处理的文件",'./',"All Files (*)")[0]

    def OKClicked(self):
        if self.FileName!='':
            if self.Mode.currentIndex()==0:
                if self.IsEnc.currentIndex()==0:
                    pass
                else:
                    if self.EncKey.text()!='':
                        if len(self.EncKey.text())>=16:
                            self.encrypt_file(self.EncKey.text()[:16].encode('utf-8'),self.FileName)
                        else:
                            i = 16 // len(self.EncKey.text())
                            j = 16 % len(self.EncKey.text())
                            self.encrypt_file((self.EncKey.text() * i + self.EncKey.text()[:j]).encode('utf-8'),self.FileName)
                    else:
                        self.encrypt_file('qdghjgj@$#165%qw'.encode('utf-8'),self.FileName)
                    self.FileName = self.FileName + '.enc'
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
                    if self.IsEnc.currentIndex()==1:
                        os.remove(self.FileName)
                        self.FileName = self.FileName[:-4]
                    else:
                        pass
                    self.tipLable.setText("分割成功")
                except:
                    self.tipLable.setText("没填要分几份哦")

            else:
                try:
                    dirName = self.FileName[:self.FileName.rfind('/')]
                    fileName = dirName[dirName.rfind('/') + 1:-5]
                    dirName1 = dirName[:dirName.rfind('/')]
                    self.joinfile(dirName, fileName, dirName1)

                    if self.IsEnc.currentIndex() == 0:
                        self.tipLable.setText("合并成功")
                    else:
                        try:
                            if self.EncKey.text() != '':
                                if len(self.EncKey.text()) >= 16:
                                    self.decrypt_file(self.EncKey.text()[:16].encode('utf-8'),
                                                      dirName1 + '/' + fileName,
                                                      out_filename=dirName1 + '/' + fileName[:-4])
                                else:
                                    i = 16 // len(self.EncKey.text())
                                    j = 16 % len(self.EncKey.text())
                                    self.decrypt_file((self.EncKey.text() * i + self.EncKey.text()[:j]).encode('utf-8'),
                                                      dirName1 + '/' + fileName, out_filename=dirName1 + '/' + fileName[:-4])
                            else:
                                self.decrypt_file('qdghjgj@$#165%qw'.encode('utf-8'), dirName1 + '/' + fileName,
                                                  out_filename=dirName1 + '/' + fileName[:-4])
                            os.remove(dirName1 + '/' + fileName)
                            self.tipLable.setText("合并成功")
                        except:
                            os.remove(dirName1 + '/' + fileName)
                            self.tipLable.setText("密匙不对哦")

                except:
                    self.tipLable.setText("文件选错了")




        else:
            self.tipLable.setText("文件没选哦")






if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainUI()
    sys.exit(app.exec_())
