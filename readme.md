# Readme
**Load monitor** został napisany jako wprawka w poruszaniu i przetwarzaniu
plików systemowych, a - przy okazji - jako zaliczenie
przedmiotu. Jako że jest to mój pierwszy tak rozbudowany program
i nie mam zbyt dużego doświadczenia w programowaniu w Pythonie,
bardzo proszę o wyrozumiałość (tak, to do Pana, Panie Doktorze).

Jeśli widzisz, ze coś nie jest: _as Pythonic as it could be_
- daj znać. Wszelkie uwagi dotyczące stylu programowania
i innych kwestii technicznych bardzo mile widziane. :)

## Wykorzystane moduły:
* **psutil**
  * powierzenie parsowania katalogu `/proc/` ludziom, którzy
   bardziej znają się na optymalizacji otwierania
   270 katalogów i efektywnym parsowaniu plików uważam
   za dobrą decyzję. Przekonują: rozbudowana dokumentacja oraz
   bardzo dobry interfejs, dzięki czemu kod od procesów
   wygląda jasno, klarownie i stabilnie działa.
* **kivy**
  * biblioteka graficzna w pełni oparta na OpenGL-u, której
  główną zaletą jest multiplatformowość i proste konstruowanie
  interfejsu przez kv lang - mieszankę CSS-a i XML-a (sic!).
  Na wypadek, gdybym miała ochotę przenosić aplikację na
  Raspberry Pi albo Androida.Poza tym TKinter jest brzydki,
  QT to QT, a GTK rzekomo także urodą nie grzeszy...
* **glob**
  * moduł z biblioteki standardowej udostępniający nieco
  przyjaźniejszy interfejs niż funkcje modułu `os`. Użyty
  aby w dosyć prosty sposób zapewnić elastyczność w
   określaniu dostępności  i ilości rdzeni procesora,
   baterii, obszarów monitorowania temperatury, etc.
* **time**
  * podstawowe funkcje operujące na Unixtime i umożliwiające
  szybką konwersję z/do UTC, a także klasyczny `sleep`... ;-)
* **re**
  * parsowanie plików poprzez wyrażenia regularne wzięte żywcem
  z Perla - po takiej wprawce można spokojnie zaczynać naukę języka _write-only_ ;-)
* **os**
  * funkcje _daemonizujące_ i  inne systemowe, czasem wprowadzające
   element zaskoczenia co do użycia, w większości działają
   zgodnie z Linuksowym manualem
* **signal**
  * obsługa nieśmiertelnego (dosłownie i w przenośni) sygnału
  SIGHUP daemona
* **logging**
  * generowanie logów przez daemon, formatowanie zawartości,
  priorytety komunikatów, etc. Jeśli widzisz coś w logu, to
  na 99% sprawka tego modułu.
* **functools**
  * podstawowo, standardowo przy pisaniu dekoratorów `wraps`,
   który chroni dekorowaną funkcję przed utratą metainformacji:
   w szczególności nazwy i docstringów (których trochę w kodzie
   jest)
* **socket**
  * zapewnia kanał komunikacyjny na linii daemon - aplikacja

## Dlaczego:

### Copyright
(C) 2016/2017, Dominika Kałafut, wszelkie prawa zastrze(ż|l)one