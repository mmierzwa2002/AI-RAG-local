\# Robotyka: Kinematyka, Systemy Sensoryczne, Klasyfikacja i Algorytmy Autonomii



\## 1. Definicja i Fundamenty Systemu Robotycznego

Robotyka to dziedzina inżynierii łącząca mechanikę, automatykę, elektronikę oraz sztuczną inteligencję (AI - od angielskiego Artificial Intelligence). Jej celem jest budowa maszyn zastępujących lub wspierających ludzi. 



Każdy zaawansowany robot działa na podstawie \*\*Pętli Percepcja-Decyzja-Akcja\*\*. Robot zbiera bodźce z otoczenia (Percepcja), przetwarza je w komputerze pokładowym (Decyzja) i wykonuje ruch za pomocą silników (Akcja).



\## 2. Przestrzeń Robocza i Kinematyka



\*\*Pojęcie DoF (Degrees of Freedom)\*\*

DoF to skrót od angielskiego terminu Degrees of Freedom, czyli Stopnie Swobody. Określa on, ile niezależnych osi ruchu posiada robot. Do pełnego, swobodnego poruszania obiektem w przestrzeni trójwymiarowej potrzebne jest minimum 6 DoF (trzy osie do przemieszczania w przód/tył, lewo/prawo, góra/dół oraz trzy osie do obrotu: nachylenie, odchylenie, przechylenie).



\*\*Kinematyka Prosta i Odwrotna\*\*

Do sterowania ruchem manipulatorów (ramion robota) komputery muszą rozwiązywać dwa główne problemy matematyczne:

\*   \*\*Kinematyka prosta (Forward Kinematics):\*\* Proces, w którym komputer oblicza, gdzie w przestrzeni znajdzie się końcówka ramienia robota, jeśli znamy kąty wygięcia wszystkich jego stawów (przegubów).

\*   \*\*Kinematyka odwrotna (Inverse Kinematics):\*\* Proces odwrotny, znacznie trudniejszy. Programista podaje docelowe współrzędne (X, Y, Z), a komputer musi wyliczyć, pod jakimi kątami należy ugiąć wszystkie stawy robota, aby jego końcówka dotarła do zadanego punktu.



\## 3. Architektura Sprzętowa: Sensory i Aktuatory



\### 3.1 Sensory (Układ Percepcji)

Sensory robota dzielimy na proprioceptywne (mierzące stan własny robota, np. jak bardzo zgięte jest jego ramię) oraz eksteroceptywne (mierzące otoczenie). Do najważniejszych z nich należą:

\*   \*\*IMU (Inertial Measurement Unit):\*\* Skrót IMU oznacza inercyjną jednostkę pomiarową. Jest to elektroniczny chip zawierający żyroskopy i akcelerometry, który pozwala robotowi na bieżąco badać własne przyspieszenie i orientację w przestrzeni (żeby np. utrzymać równowagę).

\*   \*\*LiDAR (Light Detection and Ranging):\*\* Akronim LiDAR to zaawansowany czujnik laserowy. Obracający się laser wysyła tysiące wiązek światła wokół robota, a mierząc czas ich odbicia od przeszkód, tworzy niezwykle dokładną, trójwymiarową mapę otoczenia (tzw. chmurę punktów).

\*   \*\*Enkodery:\*\* Czujniki montowane bezpośrednio na osiach silników, które precyzyjnie mierzą i raportują aktualny kąt obrotu danego silnika.



\### 3.2 Aktuatory (Układ Wykonawczy)

Aktuatory to urządzenia zmieniające sygnał elektryczny lub ciśnienie w ruch mechaniczny. Należą do nich:

\*   \*\*Silniki BLDC (Brushless Direct Current):\*\* Skrót BLDC oznacza bezszczotkowy silnik prądu stałego. Są one standardem w robotyce ze względu na ogromną wytrzymałość, precyzję i wydajność.

\*   \*\*Siłowniki pneumatyczne:\*\* Elementy zasilane sprężonym powietrzem, używane najczęściej do napędzania chwytaków (tzw. gripperów) na końcówkach robota. Szybkie, ale trudne w precyzyjnym pozycjonowaniu.



\## 4. Klasyfikacja Robotów Przemysłowych i Mobilnych



\*\*Roboty Przemysłowe (Manipulatory)\*\*

\*   \*\*Roboty Kartezjańskie (Liniowe):\*\* Maszyny poruszające się wyłącznie po trzech osiach prostopadłych (X, Y, Z). Są bardzo sztywne i dokładne, używane m.in. w frezarkach CNC i drukarkach 3D.

\*   \*\*Roboty SCARA:\*\* Akronim SCARA pochodzi od słów Selective Compliance Assembly Robot Arm. Są to roboty niezwykle szybkie w ruchach bocznych (poziomych). Powszechnie wykorzystuje się je przy montażu małej elektroniki (np. lutowaniu płyt głównych).

\*   \*\*Coboty (Roboty Współpracujące):\*\* Specjalna klasa bezpiecznych manipulatorów. Posiadają czujniki siły, dzięki którym natychmiast zatrzymują się przy kontakcie z człowiekiem. Mogą pracować ramię w ramię z operatorami bez konieczności budowania klatek ochronnych.



\*\*Roboty Mobilne i Bezzałogowe\*\*

\*   \*\*AGV (Automated Guided Vehicles):\*\* Skrót AGV oznacza automatycznie kierowane pojazdy. Są to wózki magazynowe, które potrafią jeździć tylko po wyznaczonych fizycznie ścieżkach (np. naklejonych na podłodze taśmach magnetycznych).

\*   \*\*AMR (Autonomous Mobile Robots):\*\* Skrót AMR oznacza autonomiczne roboty mobilne. W przeciwieństwie do AGV, posiadają skanery przestrzeni i potrafią same planować trasy oraz omijać dynamiczne przeszkody (np. ludzi idących korytarzem).

\*   \*\*UAV (Unmanned Aerial Vehicles):\*\* Skrót UAV oznacza bezzałogowe statki powietrzne, potocznie nazywane dronami.



\## 5. Oprogramowanie i Algorytmy Nawigacyjne (Sztuczna Inteligencja)



Do ożywienia fizycznych części robota używa się skomplikowanego oprogramowania i algorytmów algorytmów uczenia maszynowego (Machine Learning).



\*\*System ROS\*\*

ROS to skrót od Robot Operating System (Robotyczny System Operacyjny). Mimo nazwy, nie jest to system taki jak Windows, lecz potężny framework (zestaw darmowych narzędzi i bibliotek programistycznych), który ułatwia programistom tworzenie kodów sterujących kamerami, silnikami i logiką nawigacji.



\*\*Algorytmy SLAM\*\*

SLAM to skrót od Simultaneous Localization and Mapping, co po polsku oznacza: jednoczesne mapowanie i lokalizacja. Jest to kluczowy algorytm dla robotów mobilnych. Pozwala robotowi, który znajduje się w zupełnie obcym pomieszczeniu, na rysowanie cyfrowej mapy tego miejsca przy użyciu skanerów, przy jednoczesnym obliczaniu własnej pozycji na tej nowo powstającej mapie.



\*\*Wizja Maszynowa i Sieci Konwolucyjne\*\*

\*   \*\*Computer Vision (Wizja Maszynowa):\*\* Dziedzina pozwalająca robotom "widzieć" i rozumieć obraz z kamer.

\*   \*\*CNN (Convolutional Neural Networks):\*\* Skrót CNN to konwolucyjne sieci neuronowe. Jest to rodzaj sztucznej inteligencji, która pozwala robotowi rozpoznawać obiekty (np. odróżniać śrubkę od nakrętki na taśmie produkcyjnej), co jest niemożliwe do zaprogramowania tradycyjnym kodem "jeśli-to".

