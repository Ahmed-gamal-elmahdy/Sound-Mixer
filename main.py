import cmath
import logging as log
import sys

import numpy as np
import pyqtgraph as pg
import sounddevice as sd
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy.fft import rfft, rfftfreq, irfft
from scipy.io.wavfile import read, write
import warnings

warnings.filterwarnings("error")
log.basicConfig(filename='mainLogs.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
from gui import Ui_MainWindow
cursor_method = {'triangle': 'thin', 'left_bongo': 'l_bongo_oneshot', 'right_bongo': 'r_bongo_oneshot'}
class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        sliders = [self.ui.guitar_slider, self.ui.drum_slider, self.ui.piano_slider, self.ui.trumpet_slider]
        slidersdata = [[self.ui.guitar_slider,0,1000], [self.ui.drum_slider,3000,11000], [self.ui.piano_slider,1000,2000], [self.ui.trumpet_slider,0,400]]
        maingraph = {}
        maingraph["ispaused"] = True
        maingraph["amp"] = maingraph["sound"] = np.zeros(1000)
        maingraph["rate"] = maingraph["time"]=np.arange(0,10,0.01)
        self.ui.actionOpen.triggered.connect(lambda: open_file())
        self.ui.actionExport.triggered.connect(lambda: export())
        self.ui.signal_slider.valueChanged.connect(lambda: line.setPos(self.ui.signal_slider.value()))
        self.ui.signal_slider.sliderPressed.connect(lambda: pause())
        self.ui.signal_slider.sliderReleased.connect(lambda: playsound())
        self.ui.signal_slider.sliderReleased.connect(lambda: playsound())
        self.ui.signal_slider.setPageStep(0)
        line = pg.InfiniteLine(pos=0, name="line", pen="k")
        self.ui.toggle_play.clicked.connect(lambda: playsound())
        self.ui.stop_btn.clicked.connect(lambda: stop())
        timer = QTimer()
        timer.setInterval(1000)
        timer.timeout.connect(lambda: moveslider())
        try:
            self.ui.toggle_mute.clicked.connect(lambda: adjustvolume("toggle"))
            self.ui.volume_slider.sliderReleased.connect(lambda: adjustvolume())
            self.ui.guitar_slider.sliderReleased.connect( lambda:adjustdata())
                #lambda: adjustdata(guitar[0], guitar[1], self.ui.guitar_slider.value()))
            self.ui.drum_slider.sliderReleased.connect( lambda:adjustdata())
                #lambda: adjustdata(drums_Timpani[0], drums_Timpani[1], self.ui.drum_slider.value()))
            self.ui.piano_slider.sliderReleased.connect( lambda:adjustdata())
                #lambda: adjustdata(piano[0], piano[1], self.ui.piano_slider.value()))
            self.ui.trumpet_slider.sliderReleased.connect( lambda:adjustdata())
                #lambda: adjustdata(trumpett[0], trumpett[1], self.ui.trumpet_slider.value()))
        except:
            pass
        instruments = ["Bongo", "Triangle", "Drums"]
        self.ui.instrument_combobox.addItems(instruments)
        self.ui.instrument_combobox.currentIndexChanged.connect(lambda: self.ui.instrument_stacked_tab.setCurrentIndex(
            self.ui.instrument_combobox.currentIndex()))
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.instrument_stacked_tab.setCurrentIndex(0)
        self.ui.left_trigger.mousePressEvent = lambda event: bongo(method=cursor_method['left_bongo'])
        self.ui.right_trigger.mousePressEvent = lambda event: bongo(method=cursor_method['right_bongo'])
        self.ui.l_bongo_oneshot.mousePressEvent = lambda event: bongo(method="l_bongo_oneshot")
        self.ui.l_bongo_dry.mousePressEvent = lambda event: bongo(method="l_bongo_dry")
        self.ui.l_bongo_strong.mousePressEvent = lambda event: bongo(method="l_bongo_strong")
        self.ui.r_bongo_oneshot.mousePressEvent = lambda event: bongo(method="r_bongo_oneshot")
        self.ui.r_bongo_dry.mousePressEvent = lambda event: bongo(method="r_bongo_dry")
        self.ui.r_bongo_strong.mousePressEvent = lambda event: bongo(method="r_bongo_strong")
        self.ui.mostleft.mousePressEvent = lambda event: drums(method="mostleft")
        self.ui.left_2.mousePressEvent = lambda event: drums(method="left")
        self.ui.right_2.mousePressEvent = lambda event: drums(method="right")
        self.ui.mostright.mousePressEvent = lambda event: drums(method="mostright")
        self.ui.left_drum.mousePressEvent = lambda event: drums(method="left_drum")
        self.ui.right_drum.mousePressEvent = lambda event: drums(method="right_drum")
        self.ui.triangle_trigger.mousePressEvent = lambda event: triangle(method = cursor_method['triangle'])
        self.ui.triangle_thin.mousePressEvent = lambda event: triangle(method="thin")
        self.ui.triangle_shaky.mousePressEvent = lambda event: triangle(method="shaky")
        self.ui.triangle_loud.mousePressEvent = lambda event: triangle(method="loud")
        self.ui.lowerleft_drum.mousePressEvent = lambda event: drums(method="lowerleft_drum")
        self.ui.lowerright_drum.mousePressEvent = lambda event: drums(method="lowerright_drum")
        self.ui.big_drum.mousePressEvent = lambda event: drums(method="big_drum")

        def bongo(method):
            global cursor_method
            if method.startswith('l'):
                self.ui.bongo_instrument.setStyleSheet("#bongo_instrument{\n"
                                                       "    background-image:url(:/bongo/bongo_left.png);\n"
                                                       "    background-size:     cover;\n"
                                                       "    background-repeat:   no-repeat;\n"
                                                       "    background-position: bottom;\n"
                                                       "}")
                if method == 'l_bongo_oneshot':
                    pixmap = QPixmap(":/cursor/bongo_oneshot_cur.png")
                    cursor_method['left_bongo'] = "l_bongo_oneshot"
                    generate_karplus_sound(50, 1000, 0.2)
                elif method == 'l_bongo_dry':
                    pixmap = QPixmap(":/cursor/bongo_dry_cur.png")
                    cursor_method['left_bongo'] = "l_bongo_dry"
                    generate_karplus_sound(50, 2000)
                elif method == 'l_bongo_strong':
                    generate_karplus_sound(50, 3000,0.2)
                    pixmap = QPixmap(":/cursor/bongo_strong_cur.png")
                    cursor_method['left_bongo'] = "l_bongo_strong"
                cursor = QCursor(pixmap)
                self.ui.left_trigger.setCursor(cursor)

            if method.startswith('r'):
                self.ui.bongo_instrument.setStyleSheet("#bongo_instrument{\n"
                                                       "    background-image:url(:/bongo/bongo_right.png);\n"
                                                       "    background-size:     cover;\n"
                                                       "    background-repeat:   no-repeat;\n"
                                                       "    background-position: bottom;\n"
                                                       "}")
                if method == 'r_bongo_oneshot':
                    pixmap = QPixmap(":/cursor/bongo_oneshot_cur.png")
                    cursor_method['right_bongo'] = "r_bongo_oneshot"
                    generate_karplus_sound(100, 1000, 0.2)
                elif method == 'r_bongo_dry':
                    pixmap = QPixmap(":/cursor/bongo_dry_cur.png")
                    cursor_method['right_bongo'] = "r_bongo_dry"
                    generate_karplus_sound(100, 2000)
                elif method == 'r_bongo_strong':
                    generate_karplus_sound(100, 3000,0.2)
                    pixmap = QPixmap(":/cursor/bongo_strong_cur.png")
                    cursor_method['right_bongo'] = "r_bongo_strong"
                cursor = QCursor(pixmap)
                self.ui.right_trigger.setCursor(cursor)
            clear(method="bongo")

        def triangle(method):
            global cursor_method
            self.ui.triangle_trigger.setStyleSheet("#triangle_trigger{\n"
                                                   "    background-image:url(:/triangle/triangle_hit.png);\n"
                                                   "    background-size:     cover;\n"
                                                   "    background-repeat:   no-repeat;\n"
                                                   "    background-position: center center;\n"
                                                   "}")
            if method == "thin":
                pixmap = QPixmap(":/cursor/triangle_thin_cur.png")
                generate_karplus_sound(550, 10000, 0.001)
                cursor_method['triangle'] = "thin"
            elif method == "shaky":
                pixmap = QPixmap(":/cursor/triangle_shaky_cur.png")
                generate_karplus_sound(550, 5000, 0.005)
                cursor_method['triangle'] = "shaky"
            elif method == "loud":
                pixmap = QPixmap(":/cursor/triangle_loud_cur.png")
                generate_karplus_sound(550, 6000, 0.001)
                cursor_method['triangle'] = "loud"
            cursor = QCursor(pixmap)
            self.ui.triangle_instrument.setCursor(cursor)
            clear(method="triangle")

        def drums(method):
            pixmap = QPixmap(":/cursor/drum_stick_cur.png")
            cursor = QCursor(pixmap)
            self.ui.drums_instrument.setCursor(cursor)
            if method == "mostleft":
                self.ui.drums_instrument.setStyleSheet("#drums_instrument{\n"
                                                       "    background-image:url(:/drums/mostleft.png);\n"
                                                       "    background-size:     cover;\n"
                                                       "    background-repeat:   no-repeat;\n"
                                                       "    background-position: center center;\n"
                                                       "}\n")
                generate_karplus_sound(10, 50000, 0.3)
                # instrumentsound("assets/8.wav",False)
            if method == "left":
                self.ui.drums_instrument.setStyleSheet("#drums_instrument{\n"
                                                       "    background-image:url(:/drums/left.png);\n"
                                                       "    background-size:     cover;\n"
                                                       "    background-repeat:   no-repeat;\n"
                                                       "    background-position: center center;\n"
                                                       "}\n")
                generate_karplus_sound(90, 30000, 0.3)
                # instrumentsound("assets/7.wav",False)

            if method == "right":
                self.ui.drums_instrument.setStyleSheet("#drums_instrument{\n"
                                                       "    background-image:url(:/drums/right.png);\n"
                                                       "    background-size:     cover;\n"
                                                       "    background-repeat:   no-repeat;\n"
                                                       "    background-position: center center;\n"
                                                       "}\n")
                generate_karplus_sound(180, 30000, 0.3)
                # instrumentsound("assets/6.wav",False)

            if method == "mostright":
                self.ui.drums_instrument.setStyleSheet("#drums_instrument{\n"
                                                       "    background-image:url(:/drums/mostright.png);\n"
                                                       "    background-size:     cover;\n"
                                                       "    background-repeat:   no-repeat;\n"
                                                       "    background-position: center center;\n"
                                                       "}\n")
                generate_karplus_sound(10, 40000, 0.2)
                # instrumentsound("assets/5.wav",False)

            if method == "left_drum":
                self.ui.drums_instrument.setStyleSheet("#drums_instrument{\n"
                                                       "    background-image:url(:/drums/left_drum.png);\n"
                                                       "    background-size:     cover;\n"
                                                       "    background-repeat:   no-repeat;\n"
                                                       "    background-position: center center;\n"
                                                       "}\n")
                generate_karplus_sound(100, 1000, 0.7)
                # instrumentsound("assets/4.wav",False)

            if method == "right_drum":
                self.ui.drums_instrument.setStyleSheet("#drums_instrument{\n"
                                                       "    background-image:url(:/drums/right_drum.png);\n"
                                                       "    background-size:     cover;\n"
                                                       "    background-repeat:   no-repeat;\n"
                                                       "    background-position: center center;\n"
                                                       "}\n")
                generate_karplus_sound(100, 1500, 0.8)
                # instrumentsound("assets/3.wav",False)

            if method == "lowerleft_drum":
                self.ui.drums_instrument.setStyleSheet("#drums_instrument{\n"
                                                       "    background-image:url(:/drums/lowerleft_drum.png);\n"
                                                       "    background-size:     cover;\n"
                                                       "    background-repeat:   no-repeat;\n"
                                                       "    background-position: center center;\n"
                                                       "}\n")
                generate_karplus_sound(100, 1000, 0.9)
                # instrumentsound("assets/2.wav",False)
            if method == "lowerright_drum":
                self.ui.drums_instrument.setStyleSheet("#drums_instrument{\n"
                                                       "    background-image:url(:/drums/lowerright_drum.png);\n"
                                                       "    background-size:     cover;\n"
                                                       "    background-repeat:   no-repeat;\n"
                                                       "    background-position: center center;\n"
                                                       "}\n")
                generate_karplus_sound(100, 2000, 0.9)
                # instrumentsound("assets/1.wav",False)
            if method == "big_drum":
                self.ui.drums_instrument.setStyleSheet("#drums_instrument{\n"
                                                       "    background-image:url(:/drums/big_drum.png);\n"
                                                       "    background-size:     cover;\n"
                                                       "    background-repeat:   no-repeat;\n"
                                                       "    background-position: center center;\n"
                                                       "}\n")
                generate_karplus_sound(20, 1000, 0.3)
            clear(method="drums")

        def clear(method):
            self.timer = QTimer()
            self.timer.setInterval(100)
            if method == "bongo":
                self.timer.timeout.connect(lambda: self.ui.bongo_instrument.setStyleSheet("#bongo_instrument{\n"
                                                                                          "background-image:url("
                                                                                          ":/bongo/bongo.png);\n "
                                                                                          "background-size:     "
                                                                                          "cover;\n "
                                                                                          "background-repeat:   "
                                                                                          "no-repeat;\n "
                                                                                          "background-position: "
                                                                                          "bottom;\n "
                                                                                          "}"))
            if method == "triangle":
                self.timer.timeout.connect(lambda: self.ui.triangle_trigger.setStyleSheet("#triangle_trigger{\n"
                                                                                          "background-image:url("
                                                                                          ":/triangle/triangle.png"
                                                                                          ");\n "
                                                                                          "background-size:     "
                                                                                          "cover;\n "
                                                                                          "background-repeat:   "
                                                                                          "no-repeat;\n "
                                                                                          "background-position: "
                                                                                          "center center;\n "
                                                                                          "}"))
            if method == "drums":
                self.timer.timeout.connect(lambda: self.ui.drums_instrument.setStyleSheet("#drums_instrument{\n"
                                                                                          "background-image:url("
                                                                                          ":/drums/drums.png);\n "
                                                                                          "background-size: cover;\n"
                                                                                          "background-repeat: "
                                                                                          "no-repeat;\n "
                                                                                          "background-position: "
                                                                                          "center center;\n "
                                                                                          "}\n"))
            self.timer.start()

        def open_file():
            filename = QFileDialog.getOpenFileName(filter="wav(*.wav)")
            if filename[1] != "wav(*.wav)":
                print("Please choose a .wav file")
                error = QMessageBox()
                error.setWindowTitle("File format Error!")
                error.setText("Please choose a .wav file!")
                popup = error.exec_()
            else:
                rate, data = read(filename[0])
                try:
                    maingraph["amp"] = (data[:, 0]).astype(np.int32)
                except:
                    maingraph["amp"] = data.astype(np.int32)

                log.warning("File path = " + filename[0])
                maingraph["rate"] = rate
                duration = len(maingraph["amp"]) / rate
                maingraph["time"] = np.arange(1 / rate, duration, 1 / rate)
                maingraph["startpoint"] =0
                maingraph["endpoint"] = maingraph["rate"] * duration
                maingraph["ispaused"] = True
                maingraph["sound"] = maingraph["amp"]
                maingraph["modified"] = ["amp"]
                self.ui.signal_slider.setRange(0, int(duration))
                self.ui.signal_slider.setSingleStep(1)
                adjustvolume()

        def plotsignal():
            self.ui.signal_graph.clear()
            self.ui.signal_graph.setLimits(xMin=min(maingraph["time"]), xMax=max(maingraph["time"]),
                                           yMin=min(maingraph["sound"]), yMax=max(maingraph["sound"]))
            self.ui.signal_graph.plot(maingraph["time"], maingraph["sound"][0:len(maingraph["time"])])
            self.ui.signal_graph.getPlotItem().hideAxis('bottom')
            self.ui.signal_graph.getPlotItem().hideAxis('left')
            # self.ui.signal_graph.addItem(line)

        def plotspectrogram():
            time = maingraph["time"]
            amplitude = maingraph["sound"]
            fig = plt.figure()
            canvas = FigureCanvas(fig)
            try:  # For handling a RuntimeWarning for when the song is muted
                for i in reversed(range(self.ui.lay.count())):
                    self.ui.lay.itemAt(i).widget().setParent(None)

                self.ui.lay.addWidget(canvas)
                fs = 1 / abs(abs(time[1]) - abs(time[0]))
                plt.specgram(amplitude, Fs=fs, cmap="plasma")
                plt.xlabel('Time')
                plt.ylabel('Frequency')
                plt.colorbar()
            except RuntimeWarning:
                pass

        plotspectrogram()

        def export():
            filename = QFileDialog.getSaveFileName(self, 'export wav', "Output",
                                                   'Wav files(.wav);;All files()')
            maingraph["sound"] = maingraph["sound"].astype(np.int16)
            log.warning("Exported File path = " + filename[0])
            write(str(filename[0] + ".wav"), maingraph["rate"], maingraph["sound"])

        def setSliders():
            for i in range(len(sliders)):
                sliders[i].setRange(0, 10)
                sliders[i].setSingleStep(1)
                sliders[i].setValue(1)

        def playsound():
            if maingraph["ispaused"]:
                sd.stop()
                self.ui.toggle_play.setIcon(self.ui.iconpause)
                maingraph["startpoint"] = self.ui.signal_slider.value()
                try:  # For handling a RuntimeWarning for when the song is muted
                    # startpoint = the point where we paused the signal to start from it , instead of starting from 0
                    try:  # For handling a KeyError if the pause/play button is pressed
                        data = maingraph["modified"][int(maingraph["rate"] * maingraph["startpoint"]):int(
                            maingraph["rate"] * maingraph["endpoint"])] / (maingraph["modified"].max())
                        sd.play(data, maingraph["rate"])
                    except:
                        pass
                except RuntimeWarning:
                    data = np.zeros(len(maingraph["modified"]))
                    sd.play(data, maingraph["rate"])
                maingraph["ispaused"] = False
                timer.start()
            else:
                maingraph["ispaused"] = True
                self.ui.toggle_play.setIcon(self.ui.iconplay)
                timer.stop()
                sd.stop()

        def moveslider():
            currentpos = self.ui.signal_slider.value() + 1
            self.ui.signal_slider.setValue(currentpos)
            maingraph["startpoint"] = self.ui.signal_slider.value()
            slider_values = ""
            for slider in sliders:
                slider_values = slider_values + " " + str(slider.value()) + " "
            log.warning("Slider values = " + slider_values)
            self.ui.signal_graph.setXRange(currentpos - 1, currentpos + 1)

        def pause():
            sd.stop()
            timer.stop()
            self.ui.toggle_play.setIcon(self.ui.iconplay)

        def stop():
            sd.stop()
            timer.stop()
            self.ui.signal_slider.setValue(0)
            self.ui.toggle_play.setIcon(self.ui.iconplay)
            maingraph["startpoint"] = 0

        def valueslideradjusted(method, data):
            volumefactor = self.ui.volume_slider.value() / 100
            if method == "adjusted":  # values changed by the instrument sliders
                fftArray = rfft(data)
            if method == "else":  # values changed by the volume
                fftArray = rfft(maingraph["sound"])
            length = len(fftArray)
            if volumefactor == 0:
                fftArray = np.multiply(fftArray, 0)
            else:
                for i in range(0, int((length) / 2)):
                    fftArray[i] = volumefactor * fftArray[i]
            sig = irfft(fftArray).astype(np.int32)
            volumechange(sig)

        def adjustvolume(method=""):
            if method == "toggle":
                currenct_volume = self.ui.volume_slider.value()
                if currenct_volume > 0:
                    self.ui.volume_slider.setValue(0)
                else:
                    self.ui.volume_slider.setValue(50)
            if self.ui.volume_slider.value() == 0:
                self.ui.toggle_mute.setIcon(self.ui.iconmute)
            else:
                self.ui.toggle_mute.setIcon(self.ui.iconvolume)
            volumefactor = self.ui.volume_slider.value() / 100
            self.ui.volume_level_label.setText(str(round(volumefactor * 200)) + "%")
            valueslideradjusted(method="else", data=maingraph["amp"])

        def volumechange(data):
            pause()
            maingraph["modified"] = data
            plotspectrogram()
            plotsignal()
            playsound()
        # adjust data, adjust volume , value slider adjusted
        #def adjustdata(low, high, factor):
        def adjustdata():
            pause()
            signal = maingraph["amp"]
            length = len(maingraph["amp"])
            sig_rfft = rfft(signal)
            sig_rfft_amp = np.abs(sig_rfft)
            sig_rfft_angle = np.angle(sig_rfft)
            try:
                freqs = rfftfreq(length, 1 / maingraph["rate"])
                points_per_freq = len(freqs) / (maingraph["rate"] / 2)
                for slider in slidersdata:
                    factor = float(slider[0].value())
                    low = int(slider[1])
                    high = int(slider[2])
                    for f in freqs:
                        if low < f < high:
                            index = int(points_per_freq * f)
                            sig_rfft_amp[index] = sig_rfft_amp[index] * factor
                        else:
                            pass
                # combine amplitude and angles again
                sig_rfft_reconstructed = np.zeros((len(freqs),), dtype=complex)
                for f in freqs:
                    try:
                        index = int(points_per_freq * f)
                        sig_rfft_reconstructed[index] = sig_rfft_amp[index] * cmath.exp(1j * sig_rfft_angle[index])
                    except:
                        pass
                signal = irfft(sig_rfft_reconstructed)
            except:
                pass
            maingraph["sound"] = signal
            valueslideradjusted(method="adjusted", data=signal)

        def generate_karplus_sound(base=100, fs=10000, factor=0.6):
            wavetable_size = fs // base
            wavetable = np.ones(wavetable_size)
            n_samples = 5000
            samples = []
            current_sample = 0
            previous_value = 0
            while len(samples) < n_samples:
                r = np.random.binomial(1, factor)
                sign = float(r == 1) * 2 - 1
                wavetable[current_sample] = sign * 0.5 * (wavetable[current_sample] + previous_value)
                samples.append(wavetable[current_sample])
                previous_value = samples[-1]
                current_sample += 1
                current_sample = current_sample % wavetable.size
            data = np.array(samples)
            sd.play(data / data.max(), fs)

        setSliders()


def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    app.exec_()


if __name__ == "__main__":
    main()
