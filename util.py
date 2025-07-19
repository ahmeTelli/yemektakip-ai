import sys
import cv2
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QStatusBar, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QFont
from deeplearning import detect_yolov8
from collections import Counter
from datetime import datetime
from db import  garson_ata
from db import setup_tables, masa_ac, masa_bosalt, siparis_ekle, toplam_tutar_getir,garson_ceza_ver,rapor_verilerini_getir, garson_performans_raporu,garson_id_bul
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel

class RestaurantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Restoran Görü Sistemi")
        self.setGeometry(200, 200, 1200, 800)
        self.scale_factor = 1.0
        self.current_image = None
        self.processed_image = None
        self.video_capture = None
        
        self.init_ui()

    def init_ui(self):

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        main_layout = QVBoxLayout(self.main_widget)


   
        kamera_btn = QPushButton("KAMERA BAŞLAT")
        kamera_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        kamera_btn.clicked.connect(self.start_webcam)
        main_layout.addWidget(kamera_btn)

        self.garson_labels = {}
        garson_layout = QHBoxLayout()
        for garson_id, garson_ad in [(1, "Ahmet"), (2, "Burcu")]:
            label = QLabel(f"Garson: {garson_ad}\nID: {garson_id}\nPuan: 0\nMasa: -")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            label.setFixedSize(210, 110)
            label.setStyleSheet("background-color: #448aff; color: white; border: 4px solid black; border-radius: 12px;")
            self.garson_labels[garson_id] = label
            garson_layout.addWidget(label)
        main_layout.addLayout(garson_layout)
        
        self.LABEL_MAP = {0:"arnavutcigeri",1:"ayran",2:"domatescorbasi",3:"ezogelincorbasi",4:"karniyarik",5:"kola"}
        self.PRICES = {"arnavutcigeri":110,"ayran":25,"domatescorbasi":60,"ezogelincorbasi":65,"karniyarik":120,"kola":35}
        self.MASA_STATE = {
                        1: {"dolu": False, "fiyat": 0, "yemekler": {}, "eklenen_yemekler": set()},
                        2: {"dolu": False, "fiyat": 0, "yemekler": {}, "eklenen_yemekler": set()},
                        3: {"dolu": False, "fiyat": 0, "yemekler": {}, "eklenen_yemekler": set()},
                        4: {"dolu": False, "fiyat": 0, "yemekler": {}, "eklenen_yemekler": set()}
                    }
        
        self.masa_acilis_zamani = {}  
        self.masa_labels = {}
        masa_layout = QHBoxLayout()
        for masa_id in range(1, 5):
            label = QLabel(f"masa {masa_id}\n0 TL")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            label.setFixedSize(110, 110)
            label.setStyleSheet("background-color: red; color: white; border: 5px solid black;")
            self.masa_labels[masa_id] = label
            masa_layout.addWidget(label)
        main_layout.addLayout(masa_layout)  # Ana layout'a ekle

        # İki panel: Gerçek görüntü & Nesne tespiti
        display_layout = QHBoxLayout()

        # Gerçek görüntü
        input_group = QGroupBox("Gerçek Görüntü")
        input_layout = QVBoxLayout()
        self.input_image_label = QLabel()
        self.input_image_label.setMinimumSize(400, 300)
        self.input_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_layout.addWidget(self.input_image_label)
        input_group.setLayout(input_layout)
        display_layout.addWidget(input_group)

        # Nesne tespiti
        output_group = QGroupBox("Nesne Tespiti")
        output_layout = QVBoxLayout()
        self.output_image_label = QLabel()
        self.output_image_label.setMinimumSize(400, 300)
        self.output_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        output_layout.addWidget(self.output_image_label)
        output_group.setLayout(output_layout)
        display_layout.addWidget(output_group)

        main_layout.addLayout(display_layout)



        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Webcam için timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_webcam_frame)

        self.rapor_btn = QPushButton("Rapor")
        self.rapor_btn.clicked.connect(self.rapor_penceresi_ac)
        main_layout.addWidget(self.rapor_btn)

    def display_image(self, image, label):
        if image is None:
            label.clear()
            return
        h, w = image.shape[:2]
        qimg = QImage(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), w, h, 3*w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        pixmap = pixmap.scaled(label.width(), label.height(), Qt.AspectRatioMode.KeepAspectRatio)
        label.setPixmap(pixmap)

    def start_webcam(self):
        # Kameradan değil, video dosyasından oku
        self.video_capture = cv2.VideoCapture("rest10.mp4")
        if not self.video_capture.isOpened():
            self.show_error("Video açılamadı!")
            return
        self.timer.start(30)
        self.status_bar.showMessage("Video oynatılıyor")

    def process_qr(self,image, masa_id):
        # image: Kameradan alınan (veya video frame) görsel
        qrDecoder = cv2.QRCodeDetector()
        data, points, _ = qrDecoder.detectAndDecode(image)
        if data:
            if data == "1":
                masa_ac(masa_id)
                garson_ata(masa_id)
                self.masa_labels[masa_id].setStyleSheet("background-color: green; color: white; border: 2px solid black;")
            elif data == "0":
                masa_bosalt(masa_id)
                self.masa_labels[masa_id].setStyleSheet("background-color: red; color: white; border: 2px solid black;")


    from datetime import datetime


    def hesap_ac(self, masa_id):
        masa_ac(masa_id)
        self.masa_acilis_zamani[masa_id] = datetime.now()
        garson_id = garson_ata(masa_id)
        self.garson_bekleniyor = True
        self.garson_beklenilen_masa = masa_id

    def update_webcam_frame(self):
        if self.video_capture is not None:
            ret, frame = self.video_capture.read()
            if not ret:
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                return
            self.current_image = frame
            self.display_image(frame, self.input_image_label)

            self.process_qr(frame, masa_id=1)

            self.frame_counter = getattr(self, "frame_counter", 0) + 1
            if self.frame_counter % 20 == 0:
                detected_img, detected_classes = detect_yolov8(frame.copy(), conf_thresh=0.3, fine_tuned=True)
                print("olduuuuuuu")
                print(detected_classes)
              
            else:
                detected_img, detected_classes = frame.copy(), []
                print("olmadııııııııı")

            # YOLO ile nesne tespiti
            self.display_image(detected_img, self.output_image_label)

            masa_id = 1 
            if detected_classes:
                self.update_yemekler_and_price_db(detected_classes, masa_id)
            else:

                toplam = toplam_tutar_getir(1)
                label = self.masa_labels[1]
                label.setText(f"masa 1\n{toplam} TL")

    def garson_geldi(self, masa_id):
        if masa_id in self.masa_acilis_zamani:
            gecen_sure = (datetime.now() - self.masa_acilis_zamani[masa_id]).total_seconds()
            if gecen_sure > 3:

                garson_id = garson_id_bul(masa_id)  # Bu masa için atanan garson
                garson_ceza_ver(garson_id, puan_dusur=10)

            else:
    
                pass

            del self.masa_acilis_zamani[masa_id]
        

    def show_error(self, msg):
        QMessageBox.critical(self, "Hata", msg)

    def closeEvent(self, event):
        if self.video_capture is not None:
            self.video_capture.release()
            self.timer.stop()
        event.accept()

    def update_yemekler_and_price_db(self, detected_classes, masa_id):
        for yemek_id in set(detected_classes):
            siparis_ekle(masa_id, yemek_id)
        toplam = toplam_tutar_getir(masa_id)
        label = self.masa_labels[masa_id]
        label.setText(f"masa {masa_id}\n{toplam} TL")



        if not hasattr(self, "masa_garsonlari"):
            self.masa_garsonlari = {}
        if masa_id not in self.masa_garsonlari or self.masa_garsonlari[masa_id] is None:
            garson_id = garson_ata(masa_id)
            self.masa_garsonlari[masa_id] = garson_id
            self.update_garson_label(garson_id)
        
    def update_masa_label(self, masa_id, fiyat, dolu=True):
        renk = "green" if dolu else "red"
        self.masa_labels[masa_id].setText(f"masa {masa_id}\n{fiyat} TL")
        self.masa_labels[masa_id].setStyleSheet(
            f"background-color: {renk}; color: white; border: 5px solid black;"
        )

    def clear_masa(self, masa_id):
        self.MASA_STATE[masa_id] = {
            "dolu": False,
            "fiyat": 0,
            "yemekler": {},
            "eklenen_yemekler": set()
        }
        label = self.masa_labels[masa_id]
        label.setText(f"masa {masa_id}\n0 TL")
        label.setStyleSheet("background-color: red; color: white; border: 5px solid black;")
        for garson_id in self.garson_labels:
            self.update_garson_label(garson_id)

    def update_garson_label(self, garson_id):
        from db import c
        c.execute("SELECT isim, puan, aktif_masa FROM garsonlar WHERE garson_id=?", (garson_id,))
        garson = c.fetchone()
        if garson:
            isim, puan, aktif_masa = garson
            masa_txt = f"masa{aktif_masa}" if aktif_masa else "-"
            label = self.garson_labels[garson_id]
            label.setText(f"Garson: {isim}\nID: {garson_id}\nPuan: {puan}\nMasa: {masa_txt}")

    def rapor_penceresi_ac(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Aylık Rapor")

        layout = QVBoxLayout(dlg)


        table = QTableWidget()

        raporlar = rapor_verilerini_getir()  
        table.setRowCount(len(raporlar))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Masa", "Yemek", "Adet", "Tarih", "Garson"])
        for i, row in enumerate(raporlar):
            for j, value in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(str(value)))
        layout.addWidget(QLabel("Tüm Siparişler"))
        layout.addWidget(table)


        garsonlar = garson_performans_raporu()  # db.py'den fonksiyon
        garson_table = QTableWidget()
        garson_table.setRowCount(len(garsonlar))
        garson_table.setColumnCount(4)
        garson_table.setHorizontalHeaderLabels(["Garson", "Puan", "Baktığı Masa", "Geç Kaldığı Sayı"])
        for i, row in enumerate(garsonlar):
            for j, value in enumerate(row):
                garson_table.setItem(i, j, QTableWidgetItem(str(value)))
        layout.addWidget(QLabel("Garson Performansları"))
        layout.addWidget(garson_table)

        dlg.setLayout(layout)
        dlg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RestaurantGUI()
    setup_tables()
    win.show()
    sys.exit(app.exec())
