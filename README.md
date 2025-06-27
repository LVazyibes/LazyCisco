🚀 LazyCisco: Vibe Coding ile Cisco Yönetimine Hızlı Geçiş! 😴💻
Merhaba Geleceğin Network Gurusu! 👋

Burası, %100 Vibe Coding ile yazılmış, 
Cisco cihazlarınızdaki rutinleşen ama bir o kadar da sıkıcı olabilen temel switch ve router yapılandırmalarını otomatikleştiren sihirli GUI aracınız: LazyCisco! 
Eğer komut satırında kaybolmaktan yorulduysanız ve daha çok ağ topolojileri kurup yeni senaryolar denemek istiyorsanız, doğru yerdesiniz.

LazyCisco, her satırı kahve kokusu ve lo-fi hip-hop ritmleriyle yazılmış, sizi manuel yapılandırma çilesinden kurtaran, görsel bir arayüz ile Cisco cihazlarınıza bağlanmanızı sağlayan bir uygulamadır.


✨ LazyCisco Ne İşe Yarar? (Kullanım Alanları ve Kolaylıkları)

Zahmetsiz Bağlantı Yönetimi: 
Farklı Cisco cihazlarına bağlanmak için her seferinde IP, 
kullanıcı adı ve şifre girmekten sıkıldınız mı? LazyCisco, 
kimlik bilgilerini güvenle yönetir ve tek tıklamayla cihazlarınıza bağlanmanızı sağlar.

Görsel Arayüz: PyQt5 ile geliştirilen kullanıcı dostu arayüz sayesinde, cihaz ekleme, düzenleme ve silme işlemleri çocuk oyuncağı.

Güvenli Kimlik Bilgisi Depolama: Hassas bilgilerinizi (şifreleriniz!) sisteminizin anahtarlığına (keyring kütüphanesi ile) güvenli bir şekilde kaydeder. Böylece endişelenmeden işinize odaklanabilirsiniz.

Tek Tıkla Bağlantı ve Komut Gönderme: netmiko gücüyle, cihaza bağlandıktan sonra canlı terminalde komut gönderebilir, çıktıyı anında görebilirsiniz. Artık her şey parmaklarınızın ucunda!
Hata Payını Azaltın: İnsanlık halidir, typo yaparız. 
LazyCisco, otomatik bağlantı ve komut gönderme yetenekleriyle bu riski sıfıra indirir.

%100 Vibe Coding Hissiyatı: Evet, en önemlisi bu! Network yönetiminin keyfini çıkarırken, uygulamanızın ruhunuzu yansıtmasına izin verin. 
Çünkü biliyoruz ki, en iyi uygulamalar, iyi bir vibe ile yazılır!


🛠️ Nasıl Çalışır? (Programın Amacı ve Çalışma Prensibi)
LazyCisco, Python'ın güçlü kütüphanelerini kullanarak network cihazlarıyla etkileşim kurar:

PyQt5: Uygulamanın grafiksel kullanıcı arayüzünü (GUI) oluşturur. Butonlar, listeler, metin kutuları... her şey burada canlanır!

netmiko: Cisco cihazlarınıza SSH veya Telnet üzerinden bağlanır ve komutları sorunsuz bir şekilde göndermenizi sağlar. Otomasyonun kalbi burada atar!

keyring: Kullanıcı adı ve şifre gibi hassas kimlik bilgilerini işletim sisteminizin yerleşik güvenli depolama mekanizmalarında (Windows Credential Manager, macOS Keychain vb.) saklar. 
Böylece şifreleriniz kodda veya düz metin dosyalarında asla tutulmaz.

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
Bu proje, bir "vibe" ile başladı ve sizin katkılarınızla daha da büyüyebilir! 
Eğer projeyi geliştirmek, yeni özellikler eklemek veya bir hata bulmak isterseniz, 
lütfen bir pull request gönderin. Her türlü katkıya açığız ve sizi bu vibe-coding hareketine bekliyoruz!

📜 Lisans
Bu proje MIT Lisansı altında yayınlanmıştır. 
Kopyalayın, değiştirin, kullanın, dağıtın, satın... 
tek ricamız, lisans bildirimini ve telif hakkı ibaresini koruyarak bize atıfta bulunmanızdır. 
Çünkü bir emeğin değeri, atıfla taçlanır! 👑

📞 İletişim
Sorularınız, önerileriniz veya sadece merhaba demek için:

E-posta: betterdisc@hotmail.com
GitHub: https://github.com/LVazyibes

#VibeCoding #Cisco #NetworkAutomation #Python #GUI #LazyCisco

_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

🚀 LazyCisco: Effortless Cisco Management with Pure Vibe Coding! 😴💻
Hello, Future Network Guru! 👋

This is your magical GUI tool, written with 100% Vibe Coding, 
designed to automate the routine yet often tedious basic switch and router configurations on your Cisco devices: 
LazyCisco! If you're tired of getting lost in the command line and want to spend more time building network topologies and experimenting with new scenarios, you've come to the right place.

LazyCisco is an application where every line of code was brewed with coffee aroma and lo-fi hip-hop rhythms. 
It saves you from manual configuration struggles, providing a visual interface to connect to your Cisco devices.

✨ What Does LazyCisco Do? (Use Cases & Conveniences)
Effortless Connection Management: 
Tired of entering IP, username, and password every time you want to connect to different Cisco devices? 
LazyCisco securely manages your credentials and lets you connect to your devices with a single click.

Visual Interface: 
Thanks to the user-friendly interface developed with PyQt5, adding, editing, and deleting devices is child's play.

Secure Credential Storage: 
It securely saves your sensitive information (passwords!) to your system's keyring (using the keyring library). 
This way, you can focus on your work without worry.

One-Click Connection & Command Sending: Powered by netmiko, 
you can send commands directly to the live terminal after connecting to a device and instantly see the output. 
Everything is now at your fingertips!
Reduce Error Margin: We're only human, and typos happen. 
LazyCisco, with its automated connection and command sending capabilities, reduces this risk to zero.

100% Vibe Coding Feeling: Yes, this is the most important part! Enjoy network management while letting your application reflect your soul. 
Because we know the best applications are written with a good vibe!

🛠️ How It Works? (Purpose and Operating Principle)
LazyCisco interacts with network devices using powerful Python libraries:
PyQt5: Creates the graphical user interface (GUI) of the application. 
Buttons, lists, text boxes... everything comes alive here!
netmiko: Connects to your Cisco devices via SSH or Telnet and allows you to send commands seamlessly. The heart of automation beats here!
keyring: Stores sensitive credentials like usernames and passwords in your operating system's built-in secure storage mechanisms (Windows Credential Manager, macOS Keychain, etc.). 
This ensures your passwords are never kept in code or plain text files.
json and os: Organizes configuration information like device IPs in a switches.json file and manages application settings.
The application simply follows these steps:

You select an IP address from the device list.
It retrieves the relevant credentials from the keyring.
Establishes a secure connection to the device using netmiko.
You send your commands directly to the device from the opened terminal interface and view the responses in real-time.

🚀 Getting Started (Installation & Running)
Install Required Libraries: You'll need a few Python libraries to run LazyCisco. 
Run the following commands in your command prompt (or terminal):

Bash

pip install PyQt5 netmiko keyring
Clone the Repo:

Bash

git clone https://github.com/LVazyibes/LazyCisco.git
Navigate to the Directory:

Bash

cd LazyCisco
Run the Application:

Bash

python "Lazy Cisco Eng.py"
And there you have it, the LazyCisco GUI! Start adding devices and connecting!

🔮 Future Plans (Roadmap)
More Cisco IOS configuration templates.
Logging and command history features.
Specialized modules for different device types.
Even more vibe! 🧘‍♀️
🤝 Contribute
This project started with a "vibe" and can grow even bigger with your contributions! 
If you'd like to improve the project, add new features, or find a bug, please send a pull request. 
We welcome all contributions and look forward to having you join this vibe-coding movement!

📜 License
This project is released under the MIT License. Copy, modify, use, distribute, sell... 
our only request is that you cite us by preserving the license notice and copyright statement. 
Because the value of labor is crowned with attribution! 👑

📞 Contact
For questions, suggestions, or just to say hello:

E-posta: betterdisc@hotmail.com
GitHub: https://github.com/LVazyibes

#VibeCoding #Cisco #NetworkAutomation #Python #GUI #LazyCisco
![1](https://github.com/user-attachments/assets/bfaeb301-fae8-4f44-a50c-ea9505ba9247)

![2](https://github.com/user-attachments/assets/0a1cb9db-ad72-4e8d-8718-1014db93bef4)

![3](https://github.com/user-attachments/assets/42f1547b-df78-4910-ac1e-e2da3e34625c)

![4](https://github.com/user-attachments/assets/f8ca7b74-1ab3-4daa-b622-28eb642f592d)





