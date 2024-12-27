import pygame
import random
import time
import math
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Firebase bağlantısını kurma
cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://starraiders-5ce09-default-rtdb.europe-west1.firebasedatabase.app/'
})

# Skoru kaydetme fonksiyonu
def skoru_kaydet(nickname, puan):
    ref = db.reference('skorlar')
    ref.push({
        'Nickname': nickname,
        'Skor': puan
    })
    print(f"Skor kaydedildi: Nickname={nickname}, Skor={puan}")

#Pygame Hazırlık
pygame.init()

#Pencere
GENISLIK, YUKSEKLIK = 1080,750
pencere = pygame.display.set_mode((GENISLIK,YUKSEKLIK))
pygame.display.set_caption("Star Raiders")
icon = pygame.image.load("ufo.png")
pygame.display.set_icon(icon)

#FPS
FPS = 60
saat = pygame.time.Clock()

# Yazı Fontu
oyun_font = pygame.font.Font("oyun_font.ttf", 50)

def metin_yaz(metin, x, y, renk=(0, 0, 0)):
    yazi = oyun_font.render(metin, True, renk)
    pencere.blit(yazi, (x, y))

# Arka Plan Resimleri
giris_arka_plan = pygame.image.load("giris_ekrani.png")
liderlik_arka_plan = pygame.image.load("liderlik_arka_plan.jpg")
bitis_arka_plan = pygame.image.load("win_arka_plan.jpg")
baslama_arka_plan = pygame.image.load("baslama_arka_plan.jpg")
arka_plan_resmi = pygame.image.load("arka_plan2.jpg")
kaybetme_ekrani = pygame.image.load("kaybetme_ekrani.png")
pygame.mixer.music.load("oyun_muzigi_yeni.mp3")
pygame.mixer.music.play(-1)

# Buton Sınıfı
class Buton:
    def __init__(self, x, y, genislik, yukseklik, metin):
        self.rect = pygame.Rect(x, y, genislik, yukseklik)
        self.metin = metin
        self.renk = (255, 68, 78)
        self.font = oyun_font
        self.kose_yaricapi = 20

    def ciz(self, pencere):
        self.draw_rounded_rect(pencere, self.rect, self.renk, self.kose_yaricapi)
        metin_yazi = self.font.render(self.metin, True, (0, 0, 0))
        pencere.blit(metin_yazi, (self.rect.x + 10, self.rect.y + 10))

    def draw_rounded_rect(self, surface, rect, color,radius):
        """ Pygame üzerinde köşeleri yuvarlatılmış dikdörtgen çizme """
        # Ortadaki dikdörtgeni çiz
        pygame.draw.rect(surface, color, rect.inflate(-radius * 2, 0))
        pygame.draw.rect(surface, color, rect.inflate(0, -radius * 2))

        # Köşelerdeki dört ovali çiz
        pygame.draw.ellipse(surface, color, pygame.Rect(rect.topleft, (radius * 2, radius * 2)))
        pygame.draw.ellipse(surface, color, pygame.Rect((rect.topright[0] - radius * 2, rect.topright[1]), (radius * 2, radius * 2)))
        pygame.draw.ellipse(surface, color, pygame.Rect((rect.bottomleft[0], rect.bottomleft[1] - radius * 2), (radius * 2, radius * 2)))
        pygame.draw.ellipse(surface, color, pygame.Rect((rect.bottomright[0] - radius * 2, rect.bottomright[1] - radius * 2), (radius * 2, radius * 2)))

    def tiklandi_mi(self, pos):
        return self.rect.collidepoint(pos)

# Giriş Ekranı
nickname = ""

baslat_buton = Buton(350, 550, 250, 80, "Oyunu Başlat")
liderlik_buton = Buton(350, 650, 300, 80, "Liderlik Tablosu")

def giris_ekrani():
    global nickname
    giris_devam = True
    nickname = ""

    while giris_devam:
        pencere.blit(giris_arka_plan, (0, 0))
        metin_yaz("Nickname: " + nickname, 350, 450,450)
        baslat_buton.ciz(pencere)
        liderlik_buton.ciz(pencere)

        for etkinlik in pygame.event.get():
            if etkinlik.type == pygame.QUIT:
                pygame.quit()
                exit()
            if etkinlik.type == pygame.KEYDOWN:
                if etkinlik.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                else:
                    if len(nickname) < 15:
                        nickname += etkinlik.unicode
            if etkinlik.type == pygame.MOUSEBUTTONDOWN:
                if baslat_buton.tiklandi_mi(etkinlik.pos) and nickname:
                    baslangic_ekrani()
                    giris_devam = False
                elif liderlik_buton.tiklandi_mi(etkinlik.pos):
                    liderlik_ekrani()

        pygame.display.update()
        saat.tick(FPS)

# Liderlik Ekranı
def liderlik_ekrani():
    liderlik_devam = True
    while liderlik_devam:
        pencere.blit(liderlik_arka_plan, (0, 0))
        metin_yaz("Liderlik Tablosu:", 300, 50, (0,255,0))
        ref = db.reference('skorlar')
        liderlik_tablosu = ref.get()
        if liderlik_tablosu:
            for key, value in liderlik_tablosu.items():
                print(key, value)  # Verileri kontrol edin

            def parse_score(score):
                try:
                    return int(score) if score else 0
                except ValueError:
                    return

            sirali_liderlik = sorted(liderlik_tablosu.items(), key=lambda x: parse_score(x[1].get('Skor', 0)), reverse=True)
            for sira, (kullanici, skor) in enumerate(sirali_liderlik[:10], 1):
                metin_yaz(f"{sira}. {skor['Nickname']}: {skor['Skor']}", 300, 100 + sira * 50, (0, 0, 0))
                print(f"{sira}. {skor['Nickname']}: {skor['Skor']}")

        metin_yaz("[ESC] Geri", 10, 690, (0,255,0))

        for etkinlik in pygame.event.get():
            if etkinlik.type == pygame.QUIT:
                pygame.quit()
                exit()
            if etkinlik.type == pygame.KEYDOWN and etkinlik.key == pygame.K_ESCAPE:
                liderlik_devam = False

        pygame.display.update()
        saat.tick(FPS)

# Başlangıç Ekranı
def baslangic_ekrani():
    pencere.blit(baslama_arka_plan, (0, 0))
    metin_yaz(f"{nickname},", 240, 310,(153,0,0))
    metin_yaz("Dünyanızı Ele ", 230, 355, (153, 0, 0))
    metin_yaz("  Geçireceğiz!", 220, 395, (153, 0, 0))
    pygame.display.update()
    time.sleep(3)

# Giriş Ekranını Başlat
giris_ekrani()

#Sınıflar
class Oyun():

    def __init__(self, oyuncu, uzayli_grup, oyuncu_mermi_grup, uzayli_mermi_grup):
        # Oyun Değişkenleri
        self.bolum_no = 1
        self.puan = 0

        # Nesneler
        self.oyuncu = oyuncu
        self.uzayli_grup = uzayli_grup
        self.uzayli_mermi_grup = uzayli_mermi_grup
        self.oyuncu_mermi_grup = oyuncu_mermi_grup
        self.boss = Boss(GENISLIK // 2 - 75, 50, 4, self.uzayli_mermi_grup)  # Boss'u ekle

        # Arka Plan
        self.giris_arka_plan = pygame.image.load("giris_ekrani.png")
        self.arka_plan1 = pygame.image.load("arka_plan1.jpg")
        self.arka_plan2 = pygame.image.load("arka_plan2.jpg")
        self.arka_plan3 = pygame.image.load("arka_plan3.jpg")
        self.bitis_arka_plan = pygame.image.load("win_arka_plan.jpg")

        # Ses Efektleri ve Müzik
        self.uzayli_vurus = pygame.mixer.Sound("uzayli_vurus_yeni2.mp3")
        self.oyuncu_vurus = pygame.mixer.Sound("oyuncu_vurus.wav")
        pygame.mixer.music.load("oyun_muzigi_yeni.mp3")
        pygame.mixer.music.play(-1)
        #Font
        self.oyun_font = pygame.font.Font("oyun_font.ttf", 64)

    def update(self):
        self.uzaylı_konum_degistirme()
        self.temas()
        self.tamamlandi ()


    def cizdir(self):
        puan_yazisi = self.oyun_font.render("Skor:" + str(self.puan), True, (255, 0, 255), (0, 0, 0))
        puan_yazi_konum = puan_yazisi.get_rect()
        puan_yazi_konum.topleft = (10, 10)

        bolum_no_yazisi = self.oyun_font.render("Bölüm:" + str(self.bolum_no), True, (255, 0, 255), (0, 0, 0))
        bolum_no_yazi_konum = bolum_no_yazisi.get_rect()
        bolum_no_yazi_konum.topleft = (GENISLIK - 250, 10)

        can_yazisi = self.oyun_font.render("Can:" + str(self.oyuncu.can), True, (255, 0, 255), (0, 0, 0))  # Can yazısı
        can_yazi_konum = can_yazisi.get_rect()
        can_yazi_konum.topright = (600, 10)

        if self.bolum_no == 1:
            pencere.blit(self.arka_plan1, (0, 0))
        elif self.bolum_no == 2:
            pencere.blit(self.arka_plan2, (0, 0))
        elif self.bolum_no == 3:
            pencere.blit(self.arka_plan3, (0, 0))
        elif self.bolum_no == 4:
            self.bitir()
            self.bolum_no = 1

        pencere.blit(puan_yazisi, puan_yazi_konum)
        pencere.blit(bolum_no_yazisi, bolum_no_yazi_konum)
        pencere.blit(can_yazisi, can_yazi_konum)  # Can bilgisi de ekrana yazdırılıyor

    def uzaylı_konum_degistirme(self):
        hareket, carpisma = False, False
        for uzayli in self.uzayli_grup.sprites():
            if uzayli.rect.left <= 0 or uzayli.rect.right >= GENISLIK:
                hareket = True
        if hareket == True:
            for uzayli in self.uzayli_grup.sprites():
                uzayli.rect.y += 10 * self.bolum_no
                uzayli.yon *= -1
                if uzayli.rect.bottom >= YUKSEKLIK - 70:
                    carpisma = True
        if carpisma == True:
            self.oyuncu.can -= 1
            self.oyun_durumu()

    def temas(self):
        # Oyuncu mermisi ve uzaylı çarpışması
        collisions = pygame.sprite.groupcollide(self.oyuncu_mermi_grup, self.uzayli_grup, True, False)
        for mermi, uzaylilar in collisions.items():
            for uzayli in uzaylilar:
                uzayli.vuruldu()

        # Boss mermisi ve oyuncu çarpışması
        if pygame.sprite.spritecollide(self.oyuncu, self.uzayli_mermi_grup, True):
            self.uzayli_vurus.play()
            self.oyuncu.can -= 1
            self.puan -= 1000
            self.oyun_durumu()

        # Boss'a vuruş kontrolü
        if pygame.sprite.spritecollide(self.boss, self.oyuncu_mermi_grup,False):
            self.boss.vuruldu()  # Boss vurulduğunda vuruldu() fonksiyonunu çağır

    def bitir(self):
        skoru_kaydet(nickname, self.puan)
        self.bolum_no = 1
        self.puan = 0
        self.oyuncu.can = 5

        self.uzayli_grup.empty()
        self.uzayli_mermi_grup.empty()
        self.oyuncu_mermi_grup.empty()

        self.bolum()

        bittimi = True
        pencere.blit(self.bitis_arka_plan,(0,0))
        yazi1 = self.oyun_font.render("Tebrikler! Dünyanızı Kurtardınız!", True, (0, 255, 0), (0, 0, 0))
        yazi1_konum = yazi1.get_rect(center=(GENISLIK // 2, YUKSEKLIK // 2 - 290))
        yazi2 = self.oyun_font.render("Baştan Başlamak İçin 'ENTER' Tuşuna Basınız!", True, (0, 255, 0), (0, 0, 0))
        yazi2_konum = yazi2.get_rect(center=(GENISLIK // 2, YUKSEKLIK // 2 + 330))
        pencere.blit(yazi1, yazi1_konum)
        pencere.blit(yazi2, yazi2_konum)
        pygame.display.update()

        while bittimi:
            for etkinlik in pygame.event.get():
               if etkinlik.type == pygame.QUIT:
                   pygame.quit()
                   exit()
               if etkinlik.type == pygame.KEYDOWN:
                   if etkinlik.key == pygame.K_RETURN:
                       bittimi = False
                       giris_ekrani()

    def bolum(self):
        self.uzayli_mermi_grup.empty()
        self.oyuncu_mermi_grup.empty()
        self.uzayli_grup.empty()

        if self.bolum_no == 3:  # Eğer üçüncü bölüme geçildiyse
            boss = Boss(GENISLIK // 2 - 75, 100, 4, self.uzayli_mermi_grup)  # Boss'u ekle
            self.uzayli_grup.add(boss)
            for i in range(2):
                for j in range(3):
                    uzayli = Uzayli(GENISLIK // 2 - 170 + i * 64, 100 + j * 64, 4, self.uzayli_mermi_grup)
                    self.uzayli_grup.add(uzayli)
            for i in range(2):
                for j in range(3):
                    uzayli = Uzayli(GENISLIK // 2 + 100 + i * 64, 100 + j * 64, 4, self.uzayli_mermi_grup)
                    self.uzayli_grup.add(uzayli)

        else:  # Diğer bölümler için normal uzaylılar ekle
            for i in range(10):
                for j in range(4):
                    uzayli = Uzayli(64 + i * 64, 100 + j * 64, self.bolum_no, self.uzayli_mermi_grup)
                    self.uzayli_grup.add(uzayli)

    def oyun_durumu(self):
        self.uzayli_mermi_grup.empty()
        self.oyuncu_mermi_grup.empty()
        self.oyuncu.reset()
        for uzayli in self.uzayli_grup.sprites():
            uzayli.reset()
        if self.oyuncu.can == 0:
            self.oyun_resetleme()
        else:
            self.durdur()

    def tamamlandi(self):
        if not self.uzayli_grup:
            self.bolum_no += 1
            time.sleep(1)
            self.bolum()

    def durdur(self):
        durdumu = True
        global durum
        yazi1 = self.oyun_font.render("Uzaylılar yüzünden " + str(self.oyuncu.can) + " canınız kaldı!",True,(0,255,0),(0,0,0))
        yazi1_konum = yazi1.get_rect()
        yazi1_konum.topleft = (100,150)

        yazi2=self.oyun_font.render("Devam etmek için 'ENTER' tuşuna basınız!",True,(0,255,0),(0,0,0))
        yazi2_konum = (yazi2.get_rect())
        yazi2_konum.topleft = (100, 250)

        pencere.blit(yazi1,yazi1_konum)
        pencere.blit(yazi2,yazi2_konum)
        pygame.display.update()
        while durdumu:
            for etkinlik in pygame.event.get():
                if etkinlik.type == pygame.KEYDOWN:
                    if etkinlik.key == pygame.K_RETURN:
                        durdumu=False
                if etkinlik.type == pygame.QUIT:
                    durdumu = False
                    durum = False

    def oyun_resetleme(self):
        skoru_kaydet(nickname, self.puan)
        # Oyun değişkenlerini sıfırla
        self.bolum_no = 1
        self.puan = 0
        self.oyuncu.can = 5

        # Grupları temizle
        self.uzayli_grup.empty()
        self.uzayli_mermi_grup.empty()
        self.oyuncu_mermi_grup.empty()

        # Yeni bölümü başlat
        self.bolum()

        #Ekrana mesaj yazdır
        durdumu = True
        yazi1 = self.oyun_font.render("Dünyanız Ele Geçirildi!", True, (0, 255, 0),(0,0,0))
        yazi1_konum = yazi1.get_rect(center=(GENISLIK // 2, YUKSEKLIK // 2 + 90))
        yazi2 = self.oyun_font.render("Baştan Başlamak İçin 'ENTER' Tuşuna Basınız!", True, (0, 255, 0),(0,0,0))
        yazi2_konum = yazi2.get_rect(center=(GENISLIK // 2, YUKSEKLIK // 2 + 170))

        while durdumu:
            pencere.fill((0, 0, 0))  # Arka planı temizle
            pencere.blit(kaybetme_ekrani, (0, 0))
            pencere.blit(yazi1, yazi1_konum)
            pencere.blit(yazi2, yazi2_konum)
            pygame.display.update()

            for etkinlik in pygame.event.get():
                if etkinlik.type == pygame.KEYDOWN:
                    if etkinlik.key == pygame.K_RETURN:
                        durdumu = False
                if etkinlik.type == pygame.QUIT:
                    durdumu = False
                    pygame.quit()
                    exit()
        giris_ekrani()

class Oyuncu(pygame.sprite.Sprite):

    def __init__(self, oyuncu_mermi_grup):
        super().__init__()
        self.image = pygame.image.load("kedi_biz.png")
        self.rect = self.image.get_rect()
        self.oyuncu_mermi_grup = oyuncu_mermi_grup
        self.rect.centerx = GENISLIK // 2
        self.rect.top = YUKSEKLIK - 70
        #Oyuncu Değişkenleri
        self.hiz = 10
        self.can = 5
        #Mermi ses efekti
        self.mermi_sesi = pygame.mixer.Sound("oyuncu_mermi_yeni.mp3")

    def update(self):
        tus = pygame.key.get_pressed()

        if tus[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.hiz
        if tus[pygame.K_RIGHT] and self.rect.right <= GENISLIK:
            self.rect.x += self.hiz

    def ates(self):
        if len(self.oyuncu_mermi_grup) < 3:
            self.mermi_sesi.play()
            OyuncuMermi(self.rect.centerx,self.rect.top,self.oyuncu_mermi_grup)
            self.oyuncu_mermi_grup.add(oyuncu_mermi)
            self.a = oyun
            self.a.puan += 2

    def reset(self):
        self.rect.centerx = GENISLIK//2

    def check_collision(self, aliens, boss):
        for alien in aliens:
            if self.rect.colliderect(alien.rect):
                self.can -= 1
                aliens.remove(alien)
        if self.rect.colliderect(boss.rect):
            self.can -= 1

class Uzayli(pygame.sprite.Sprite):

    def __init__(self, x, y, hiz, mermi_grup):
        super().__init__()
        self.image = pygame.image.load("uzaylimiz.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        #Uzaylı özel değişkenleri
        self.basx = x
        self.basy = y
        self.yon = 1
        self.hiz = hiz
        self.mermi_grup = mermi_grup
        self.uzayli_mermi_sesi = pygame.mixer.Sound("uzayli_mermi_yeni.mp3")

    def update(self):
        self.rect.x += self.yon * self.hiz
        if random.randint(0,100) > 99 and len(self.mermi_grup) < 3:
            self.uzayli_mermi_sesi.play()
            self.ates()

    def ates(self):
        UzayliMermi(self.rect.centerx,self.rect.bottom,self.mermi_grup)
        self.a=oyun
        self.a.puan+=5

    def reset(self):
        self.rect.topleft = (self.basx,self.basy)
        self.yon = 1

    def vuruldu(self):
        # Uzaylı vurulduğunda puanı artır
        self.a = oyun
        self.a.puan += 100
        self.kill()  # Uzaylıyı yok et

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, hiz, mermi_grup):
        super().__init__()
        self.image = pygame.image.load("boss.png")
        orijinal_genislik, orijinal_yukseklik = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (orijinal_genislik , orijinal_yukseklik))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.basx = x
        self.basy = y
        self.yon = 1
        self.hiz = hiz
        self.mermi_grup = mermi_grup
        self.vurus_sayisi = 0
        self.uzayli_mermi_sesi = pygame.mixer.Sound("uzayli_mermi_yeni.mp3")

    def update(self):
        self.rect.x += self.yon * self.hiz
        if random.randint(0, 100) > 97:
            self.uzayli_mermi_sesi.play()
            self.ates()

    def ates(self):
        UzayliMermi(self.rect.centerx, self.rect.bottom, self.mermi_grup, aci=0)  # Düz mermi
        UzayliMermi(self.rect.centerx, self.rect.bottom, self.mermi_grup, aci=-10)  # Sola doğru eğik mermi
        UzayliMermi(self.rect.centerx, self.rect.bottom, self.mermi_grup, aci=10)  # Sağa doğru eğik mermi
        self.a = oyun
        self.a.puan += 5

    def vuruldu(self):
        self.vurus_sayisi += 1
        if self.vurus_sayisi >= 15:
            self.kill()

    def reset(self):
        self.rect.topleft = (self.basx,self.basy)
        self.yon = 1
        self.vurus_sayisi = 0

class OyuncuMermi(pygame.sprite.Sprite):
    def __init__(self, x, y, oyuncu_mermi_grup):
        super().__init__()
        self.image = pygame.image.load("oyuncu_mermi.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        #Mermi değişkeni
        self.hiz = 10
        oyuncu_mermi_grup.add(self)

    def update(self):
        self.rect.y -= self.hiz
        if self.rect.bottom < 0:
            self.kill()
        pygame.draw.rect(pencere, (255, 0, 0), self.rect, 2)

class UzayliMermi(pygame.sprite.Sprite):
    def __init__(self, x, y, mermi_grup, aci=0):
        super().__init__()
        self.image = pygame.image.load("uzayli_mermi.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.hiz = 10
        self.aci = aci  # Merminin hareket açısı
        mermi_grup.add(self)

    def update(self):
        # Açıyı radyan cinsine çevirip hız bileşenlerini hesapla
        radian = math.radians(self.aci)
        self.rect.x += self.hiz * math.sin(radian)
        self.rect.y += self.hiz * math.cos(radian)
        if self.rect.top > YUKSEKLIK or self.rect.right < 0 or self.rect.left > GENISLIK:
           self.kill()

#Mermi Grup
oyuncu_mermi = pygame.sprite.Group()
uzayli_mermi = pygame.sprite.Group()

#Oyuncu Tanımlama
oyuncu_grup = pygame.sprite.Group()
oyuncu = Oyuncu(oyuncu_mermi)
oyuncu_grup.add(oyuncu)

#Uzaylı Grup
uzayli_grup = pygame.sprite.Group()


#Oyun sınıfı
oyun = Oyun(oyuncu, uzayli_grup, oyuncu_mermi, uzayli_mermi)
oyun.bolum()

#Oyun Döngüsü
durum = True

while durum:
    for etkinlik in pygame.event.get():
      if etkinlik.type == pygame.QUIT:
          durum = False
      if etkinlik.type == pygame.KEYDOWN:
          if etkinlik.key == pygame.K_SPACE:
              oyuncu.ates()

    oyun.update()
    oyun.cizdir()

    oyuncu_grup.update()
    oyuncu_grup.draw(pencere)

    oyuncu_mermi.update()
    oyuncu_mermi.draw(pencere)

    uzayli_grup.update()
    uzayli_grup.draw(pencere)

    uzayli_mermi.update()
    uzayli_mermi.draw(pencere)

    #Pencere güncelleme ve FPS Tanımlama
    pygame.display.update()
    saat.tick(FPS)

pygame.quit()