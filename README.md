🚀 LazyCisco: Vibe Coding ile Cisco Yönetimine Hızlı Geçiş! 😴💻
Merhaba Geleceğin Network Gurusu! 👋

Burası, %100 Vibe Coding ile yazılmış, Cisco cihazlarınızdaki rutinleşen ama bir o kadar da sıkıcı olabilen temel switch ve router yapılandırmalarını otomatikleştiren sihirli GUI aracınız: LazyCisco! Eğer komut satırında kaybolmaktan yorulduysanız ve daha çok ağ topolojileri kurup yeni senaryolar denemek istiyorsanız, doğru yerdesiniz.

LazyCisco, her satırı kahve kokusu ve lo-fi hip-hop ritmleriyle yazılmış, sizi manuel yapılandırma çilesinden kurtaran, görsel bir arayüz ile Cisco cihazlarınıza bağlanmanızı sağlayan bir uygulamadır.

✨ LazyCisco Ne İşe Yarar? (Kullanım Alanları ve Kolaylıkları)
Zahmetsiz Bağlantı Yönetimi: Farklı Cisco cihazlarına bağlanmak için her seferinde IP, kullanıcı adı ve şifre girmekten sıkıldınız mı? LazyCisco, kimlik bilgilerini güvenle yönetir ve tek tıklamayla cihazlarınıza bağlanmanızı sağlar.
Görsel Arayüz: PyQt5 ile geliştirilen kullanıcı dostu arayüz sayesinde, cihaz ekleme, düzenleme ve silme işlemleri çocuk oyuncağı.
Güvenli Kimlik Bilgisi Depolama: Hassas bilgilerinizi (şifreleriniz!) sisteminizin anahtarlığına (keyring kütüphanesi ile) güvenli bir şekilde kaydeder. Böylece endişelenmeden işinize odaklanabilirsiniz.
Tek Tıkla Bağlantı ve Komut Gönderme: netmiko gücüyle, cihaza bağlandıktan sonra canlı terminalde komut gönderebilir, çıktıyı anında görebilirsiniz. Artık her şey parmaklarınızın ucunda!
Hata Payını Azaltın: İnsanlık halidir, typo yaparız. LazyCisco, otomatik bağlantı ve komut gönderme yetenekleriyle bu riski sıfıra indirir.
%100 Vibe Coding Hissiyatı: Evet, en önemlisi bu! Network yönetiminin keyfini çıkarırken, uygulamanızın ruhunuzu yansıtmasına izin verin. Çünkü biliyoruz ki, en iyi uygulamalar, iyi bir vibe ile yazılır!
🛠️ Nasıl Çalışır? (Programın Amacı ve Çalışma Prensibi)
LazyCisco, Python'ın güçlü kütüphanelerini kullanarak network cihazlarıyla etkileşim kurar:

PyQt5: Uygulamanın grafiksel kullanıcı arayüzünü (GUI) oluşturur. Butonlar, listeler, metin kutuları... her şey burada canlanır!
netmiko: Cisco cihazlarınıza SSH veya Telnet üzerinden bağlanır ve komutları sorunsuz bir şekilde göndermenizi sağlar. Otomasyonun kalbi burada atar!
keyring: Kullanıcı adı ve şifre gibi hassas kimlik bilgilerini işletim sisteminizin yerleşik güvenli depolama mekanizmalarında (Windows Credential Manager, macOS Keychain vb.) saklar. Böylece şifreleriniz kodda veya düz metin dosyalarında asla tutulmaz.
json ve os: Cihaz IP'leri gibi yapılandırma bilgilerini switches.json dosyasında düzenli bir şekilde tutar ve uygulama ayarlarını yönetir.
Uygulama basitçe şu adımları izler:

Cihaz listesinden bir IP adresi seçersiniz.
keyring'den ilgili kimlik bilgilerini çeker.
netmiko kullanarak cihaza güvenli bir bağlantı kurar.
Açılan terminal arayüzünden doğrudan komutlarınızı cihaza gönderir ve yanıtları gerçek zamanlı olarak görüntüler.
🚀 Başlangıç (Kurulum ve Çalıştırma)
Gerekli Kütüphaneleri Yükleyin:
LazyCisco'yu çalıştırmak için birkaç Python kütüphanesine ihtiyacınız var. Komut istemcinizde (veya terminalinizde) aşağıdaki komutları çalıştırın:

Bash

pip install PyQt5 netmiko keyring
Repo'yu Klonlayın:

Bash

git clone https://github.com/LVazyibes/LazyCisco.git
Dizine Girin:

Bash

cd LazyCisco
Uygulamayı Çalıştırın:

Bash

python "Lazy Cisco.py"
Ve işte karşınızda LazyCisco GUI'si! Cihaz ekleyip bağlantı kurmaya başlayın!

🔮 Gelecek Planları (Roadmap)
Daha fazla Cisco IOS yapılandırma şablonu.
Loglama ve komut geçmişi özellikleri.
Farklı cihaz türleri için özel modüller.
Daha da fazla vibe! 🧘‍♀️
🤝 Katkıda Bulunun
Bu proje, bir "vibe" ile başladı ve sizin katkılarınızla daha da büyüyebilir! Eğer projeyi geliştirmek, yeni özellikler eklemek veya bir hata bulmak isterseniz, lütfen bir pull request gönderin. Her türlü katkıya açığız ve sizi bu vibe-coding hareketine bekliyoruz!

📜 Lisans
Bu proje MIT Lisansı altında yayınlanmıştır. Kopyalayın, değiştirin, kullanın, dağıtın, satın... tek ricamız, lisans bildirimini ve telif hakkı ibaresini koruyarak bize atıfta bulunmanızdır. Çünkü bir emeğin değeri, atıfla taçlanır! 👑

📞 İletişim
Sorularınız, önerileriniz veya sadece merhaba demek için:

E-posta: betterdisc@hotmail.com
GitHub: https://github.com/LVazyibes
#VibeCoding #Cisco #NetworkAutomation #Python #GUI #LazyCisco