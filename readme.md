# Readme
**Load monitor** będzie pozwalał na monitorowanie temperatur i ich zależności od obciążenia systemu i innych parametrów oraz umożliwi szybkie reagowanie na przegrzane (w szczególności to spowodowane intensywnym zużywaniem zasobów przez procesy)

 W chwili obecnej w 100% pewnym i przetestowanym modułem jest 'monitor' - moduł parsujący pliki VFS Linuksa. Na dniach powstanie interfejs graficzny (mały problem z odświeżaniem w Kivy).


## Wykorzystane moduły:
* **psutil**
  * powierzenie parsowania katalogu `/proc/` ludziom, którzy
   bardziej znają się na optymalizacji otwierania
   270 katalogów i efektywnym parsowaniu plików uważam
   za dobrą decyzję. Przekonują: rozbudowana dokumentacja oraz bardzo dobry interfejs, dzięki czemu kod od procesów
   wygląda jasno, klarownie i stabilnie działa.
* **kivy**
  * biblioteka graficzna w pełni oparta na OpenGL-u, której
  główną zaletą jest multiplatformowość i proste konstruowanie interfejsu przez kv lang - mieszankę CSS-a i XML-a (sic!).
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
  * podstawowe funkcje operujące na Unixtime i umożliwiające szybką konwersję z/do UTC, a także klasyczny `sleep`... ;-)
* **re**
  * parsowanie plików poprzez wyrażenia regularne wzięte żywcem z Perla - po takiej wprawce można spokojnie zaczynać naukę języka _write-only_ ;-)
* **os**
  * funkcje _daemonizujące_ i  inne systemowe, czasem wprowadzające
   element zaskoczenia co do użycia, w większości działają
   zgodnie z Linuksowym manualem
* **pySMART**
  * umożliwia dostęp do informacji o podpiętych dyskach (w szczególności temperaturach) poprzez S.M.A.R.T

#### W późniejszych etapach wystapią:
* **signal**
  * obsługa nieśmiertelnego (dosłownie i w przenośni) sygnału
  SIGHUP daemona
* **logging**
  * generowanie logów przez daemon, formatowanie zawartości,
  priorytety komunikatów, etc. Jeśli widzisz coś w logu, to
  na 99% sprawka tego modułu.

* **socket**
  * zapewnia kanał komunikacyjny na linii daemon - aplikacja


### Copyright
(C) 2016/2017, Dominika Kałafut, wszelkie prawa zastrze(ż|l)one