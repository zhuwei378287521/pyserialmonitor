import sys
import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer
from ui_demo_1 import Ui_Form


class Pyqt5_Serial(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super(Pyqt5_Serial, self).__init__()
        self.setupUi(self)
        self.init()
        self.setWindowTitle("串口小助手")
        self.ser = serial.Serial()
        self.port_check()

        # 接收数据和发送数据数目置零
        self.data_num_received = 0
        self.lineEdit.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))
        self.recvData = {'MinRecv': 10000, 'MaxRecv': 0}

    def init(self):
        # 串口检测按钮
        self.s1__box_1.clicked.connect(self.port_check)

        # 串口信息显示
        self.s1__box_2.currentTextChanged.connect(self.port_imf)

        # 打开串口按钮
        self.open_button.clicked.connect(self.port_open)

        # 关闭串口按钮
        self.close_button.clicked.connect(self.port_close)

        # 发送数据按钮
        self.s3__send_button.clicked.connect(self.data_send)

        # 定时发送数据
        self.timer_send = QTimer()
        self.timer_send.timeout.connect(self.data_send)
        self.timer_send_cb.stateChanged.connect(self.data_send_timer)

        # 定时器接收数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.data_receive)

        # 清除发送窗口
        self.s3__clear_button.clicked.connect(self.send_data_clear)

        # 清除接收窗口
        self.s2__clear_button.clicked.connect(self.receive_data_clear)

    # 串口检测
    def port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())
        self.s1__box_2.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.s1__box_2.addItem(port[0])
        if len(self.Com_Dict) == 0:
            self.state_label.setText(" 无串口")

    # 串口信息
    def port_imf(self):
        # 显示选定的串口的详细信息
        imf_s = self.s1__box_2.currentText()
        if imf_s != "":
            self.state_label.setText(self.Com_Dict[self.s1__box_2.currentText()])

    # 打开串口
    def port_open(self):
        self.ser.port = self.s1__box_2.currentText()
        self.ser.baudrate = int(self.s1__box_3.currentText())
        self.ser.bytesize = int(self.s1__box_4.currentText())
        self.ser.stopbits = int(self.s1__box_6.currentText())
        self.ser.parity = self.s1__box_5.currentText()

        try:
            self.ser.open()
        except:
            QMessageBox.critical(self, "Port Error", "此串口不能被打开！")
            return None

        # 打开串口接收定时器，周期为2ms
        self.timer.start(2)

        if self.ser.isOpen():
            self.open_button.setEnabled(False)
            self.close_button.setEnabled(True)
            self.formGroupBox1.setTitle("串口状态（已开启）")

    # 关闭串口
    def port_close(self):
        self.timer.stop()
        self.timer_send.stop()
        try:
            self.ser.close()
        except:
            pass
        self.open_button.setEnabled(True)
        self.close_button.setEnabled(False)
        self.lineEdit_3.setEnabled(True)
        # 接收数据和发送数据数目置零
        self.data_num_received = 0
        self.lineEdit.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))
        self.formGroupBox1.setTitle("串口状态（已关闭）")

    # 发送数据
    def data_send(self):
        if self.ser.isOpen():
            input_s = self.s3__send_text.toPlainText()
            if input_s != "":
                # 非空字符串
                if self.hex_send.isChecked():
                    # hex发送
                    input_s = input_s.strip()
                    send_list = []
                    while input_s != '':
                        try:
                            num = int(input_s[0:2], 16)
                        except ValueError:
                            QMessageBox.critical(self, 'wrong data', '请输入十六进制数据，以空格分开!')
                            return None
                        input_s = input_s[2:].strip()
                        send_list.append(num)
                    input_s = bytes(send_list)
                else:
                    # ascii发送
                    input_s = (input_s + '\r\n').encode('utf-8')

                num = self.ser.write(input_s)
                self.data_num_sended += num
                self.lineEdit_2.setText(str(self.data_num_sended))
        else:
            pass

    # 接收数据
    def data_receive(self):
        sync_flag = False  # 包头1 叫同步帧
        head_flag = False  # 包头2

        try:
            # 搜索开始数据包  0度 数据包  OXFA 0XA0  开头为0xfa 0xa0,0xfa 0xa1,0xfa 0xa2 ...
            while not sync_flag or not head_flag:
                b = self.ser.read(1)
                print(b)
                if b and b[0] == 0X0D:  # 包头1
                    sync_flag = True
                    head_flag = False
                elif b and sync_flag and b[0] == 0x0A:  # 包头2
                    head_flag = True
                else:
                    sync_flag = False
                    head_flag = False

                # 包头1,2都正确
            # 读出剩下的数据包
            data = self.ser.read(4)
            # 将数据组装成AD值
            out_s1 = int(chr(data[0]), 16) * 256 * 16
            out_s1 = out_s1 + int(chr(data[1]), 16) * 256
            out_s1 = out_s1 + int(chr(data[2]), 16) * 16
            out_s1 = out_s1 + int(chr(data[3]), 16)
            kk = int(chr(data[0]), 16)
            # kk = chr(int(str(data[0]), 16))

            if self.recvData['MinRecv'] > out_s1:
                self.recvData['MinRecv'] = out_s1
                print("MinRecv%d\r\n", out_s1)
            if self.recvData['MaxRecv'] < out_s1:
                self.recvData['MaxRecv'] = out_s1
                print("MaxRecv%d\r\n", out_s1)

            print('{0} {1} {2} {3} data={4},MIN={5},MAX{6}'.format(int(chr(data[0]), 16), int(chr(data[1]), 16),
                                                                   int(chr(data[2]), 16), int(chr(data[3]), 16), out_s1,
                                                                   self.recvData['MinRecv'], self.recvData['MaxRecv']))

            out_s = '{:d}'.format(out_s1) + ' '
            self.s2__receive_text.insertPlainText(out_s)
        except ValueError:
            # self.port_close()
            print("数值有问题")
            return None
        except Exception as ex:
            print("异常%s" % ex)

        num = 0

        # 统计接收字符的数量
        self.data_num_received += num
        self.lineEdit.setText(str(self.data_num_received))

        # 获取到text光标
        textCursor = self.s2__receive_text.textCursor()
        # 滚动到底部
        textCursor.movePosition(textCursor.End)
        # 设置光标到text中去
        self.s2__receive_text.setTextCursor(textCursor)

    # 定时发送数据
    def data_send_timer(self):
        if self.timer_send_cb.isChecked():
            self.timer_send.start(int(self.lineEdit_3.text()))
            self.lineEdit_3.setEnabled(False)
        else:
            self.timer_send.stop()
            self.lineEdit_3.setEnabled(True)

    # 清除显示
    def send_data_clear(self):
        self.s3__send_text.setText("")

    def receive_data_clear(self):
        self.s2__receive_text.setText("")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = Pyqt5_Serial()
    myshow.show()
    sys.exit(app.exec_())
