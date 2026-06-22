# Kompleksowe Podstawy Cyberbezpieczeństwa: Modele, Architektura, Wektory Ataku i Narzędzia

## 1. Fundamenty Bezpieczeństwa Informacji (Modele CIA oraz AAA)
Cyberbezpieczeństwo to wielowarstwowa dziedzina technologii chroniąca systemy, sieci i dane przed atakami. Jej fundamentem są dwa główne modele pojęciowe: Triada CIA oraz Model AAA.

**Triada CIA**
Triada CIA to akronim pochodzący od trzech angielskich słów: Confidentiality (Poufność), Integrity (Integralność) oraz Availability (Dostępność).
*   **Confidentiality (Poufność):** Zasada zapobiegająca nieautoryzowanemu ujawnieniu informacji. Realizuje się ją poprzez szyfrowanie danych (zarówno w spoczynku, jak i w tranzycie) oraz stosowanie ścisłych list kontroli dostępu (ACL - Access Control Lists).
*   **Integrity (Integralność):** Zasada gwarantująca, że dane nie zostały zmodyfikowane w sposób nieuprawniony przez osoby trzecie. Ochronę integralności zapewnia się poprzez podpisy cyfrowe oraz funkcje skrótu (hashing).
*   **Availability (Dostępność):** Zasada zapewniająca niezawodny dostęp do danych dla uprawnionych użytkowników. Osiąga się ją poprzez redundancję (powielanie) serwerów oraz systemy chroniące przed atakami przeciążeniowymi.

**Model AAA**
Model AAA to skrót pochodzący od trzech angielskich słów: Authentication, Authorization oraz Accounting. Zarządza on dostępem do zasobów w sieci.
*   **Authentication (Uwierzytelnianie):** Weryfikacja tożsamości użytkownika. Sprawdza, czy osoba logująca się do systemu jest faktycznie tym, za kogo się podaje (np. za pomocą hasła lub biometrii).
*   **Authorization (Autoryzacja):** Określenie poziomu uprawnień. Decyduje, do jakich konkretnie plików lub systemów uwierzytelniony użytkownik ma dostęp.
*   **Accounting (Rozliczalność):** Śledzenie, logowanie i audytowanie wszelkich akcji, jakie użytkownik wykonuje w systemie.

## 2. Kategorie Zagrożeń i Wektory Ataku

**Malware (Złośliwe oprogramowanie)**
Malware to skrót utworzony z angielskich słów "malicious software". Oznacza wszelkie oprogramowanie stworzone w celu wyrządzenia szkód. W skład Malware wchodzą:
*   **Ransomware:** Oprogramowanie szyfrujące dyski ofiary i żądające okupu za klucz deszyfrujący.
*   **Rootkit:** Złośliwy kod ukrywający swoją obecność na głębokim poziomie systemu operacyjnego (najczęściej w jądrze, czyli kernelu), przez co jest niewidoczny dla zwykłych programów antywirusowych.
*   **Spyware:** Oprogramowanie szpiegujące, które w ukryciu zbiera informacje o użytkowniku (np. rejestruje wciśnięcia klawiszy za pomocą narzędzi typu Keylogger).

**Ataki Sieciowe i Inżynieria Społeczna**
*   **Phishing:** Atak socjotechniczny, w którym przestępca podszywa się pod zaufaną instytucję (np. bank), aby wyłudzić dane. Odmianą celowaną (skierowaną w konkretną osobę) jest **Spear Phishing**, a atakiem na wysokich rangą dyrektorów jest **Whaling**.
*   **MitM (Man-in-the-Middle):** Akronim MitM oznacza atak "Człowiek pośrodku". Polega na niejawnym przechwytywaniu (i często modyfikowaniu) komunikacji między dwiema stronami.
*   **DDoS (Distributed Denial of Service):** Akronim DDoS oznacza rozproszoną odmowę usługi. Jest to atak, w którym tysiące zainfekowanych komputerów (tzw. Botnet) jednocześnie wysyłają fałszywy ruch do jednego serwera, doprowadzając do jego przeciążenia i awarii.
*   **SQLi (SQL Injection):** Skrót SQLi oznacza wstrzyknięcie złośliwego kodu SQL. Polega na wpisaniu komend bazy danych w pola formularzy na stronie internetowej, co pozwala hakerowi na wykradzenie całej bazy danych.
*   **Zero-Day Exploit:** Atak wykorzystujący lukę w oprogramowaniu (tzw. lukę dnia zerowego), o której twórca oprogramowania jeszcze nie wie i dla której nie istnieje żadna poprawka bezpieczeństwa (patch).

## 3. Kryptografia i Ochrona Danych

**Kryptografia Symetryczna**
Rodzaj szyfrowania, który używa dokładnie tego samego klucza do szyfrowania i deszyfrowania wiadomości. Jest bardzo szybka. Najpopularniejszym standardem jest algorytm **AES**, co jest skrótem od Advanced Encryption Standard.

**Kryptografia Asymetryczna**
Rodzaj szyfrowania oparty na dwóch kluczach: publicznym (widocznym dla wszystkich, służącym do szyfrowania) oraz prywatnym (ukrytym, służącym do deszyfrowania). Najpopularniejszym algorytmem asymetrycznym jest **RSA** (skrót od nazwisk twórców: Rivest, Shamir, Adleman).

**PKI (Public Key Infrastructure)**
PKI to akronim od Public Key Infrastructure (Infrastruktura Klucza Publicznego). Jest to system zarządzania zaufaniem w sieci internetowej, oparty na Urzędach Certyfikacji (CA - Certificate Authorities), które wydają cyfrowe certyfikaty bezpieczeństwa dla stron WWW (certyfikaty SSL/TLS).

## 4. Narzędzia Obronne i Systemy SOC
Obecnie bezpieczeństwem w firmach zarządza dział zwany **SOC**, co jest skrótem od Security Operations Center (Centrum Operacji Bezpieczeństwa). Wykorzystuje on szereg systemów:

*   **SIEM (Security Information and Event Management):** Akronim SIEM oznacza systemy zarządzania informacjami i zdarzeniami bezpieczeństwa. SIEM zbiera, agreguje i analizuje logi z setek serwerów i urządzeń w czasie rzeczywistym, wyszukując anomalie.
*   **SOAR (Security Orchestration, Automation, and Response):** Akronim SOAR opisuje platformy, które współpracują z systemem SIEM i automatyzują reakcję na atak (np. skrypt samodzielnie blokuje adres IP hakera na zaporze).
*   **EDR (Endpoint Detection and Response):** Skrót EDR oznacza systemy detekcji i reakcji na punktach końcowych (komputerach). Jest to nowoczesny odpowiednik antywirusa, który analizuje podejrzane zachowania procesów za pomocą sztucznej inteligencji.
*   **DLP (Data Loss Prevention):** Skrót DLP oznacza systemy zapobiegania utracie danych. Blokują one pracownikom możliwość skopiowania poufnych plików na pendrive lub wysłania ich na prywatny adres e-mail.

## 5. Ramy Prawne i Frameworki
*   **GDPR / RODO:** Skrót GDPR oznacza General Data Protection Regulation (w Polsce RODO - Rozporządzenie o Ochronie Danych Osobowych). Wymusza na firmach rygorystyczną ochronę danych prywatnych klientów pod groźbą ogromnych kar finansowych.
*   **NIST Cybersecurity Framework:** Standard stworzony przez rząd USA. Dzieli proces bezpieczeństwa na 5 faz: Identyfikacja, Ochrona, Wykrywanie, Reagowanie oraz Odtwarzanie.