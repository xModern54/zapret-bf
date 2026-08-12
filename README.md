<div align="left">

<img src="./.github/assets/MainBG.png" width="480" height="270" align="left" />

<h1>Zapret-BF</h1>

<p>
  <a href="https://github.com/xModern54/zapret-bf/releases/">
    <img alt="downloads" src="https://img.shields.io/github/downloads/xModern54/zapret-bf/total?label=DOWNLOADS&labelColor=161616&color=2b2b2b&style=for-the-badge">
  </a>
</p>

<p>
  <a href="https://github.com/xModern54/zapret-bf/releases/latest">
    <img alt="downloads@latest" src="https://img.shields.io/github/downloads/xModern54/zapret-bf/latest/total?label=DOWNLOADS@LATEST&labelColor=161616&color=2b2b2b&style=for-the-badge">
  </a>
</p>

<p>
  <a href="https://github.com/xModern54/zapret-bf/releases/">
    <img alt="release" src="https://img.shields.io/github/v/release/xModern54/zapret-bf?label=RELEASE&labelColor=161616&color=2b2b2b&style=for-the-badge">
  </a>
</p>

<p>
  <a href="https://github.com/xModern54/zapret-bf/tree/main">
    <img alt="code size" src="https://img.shields.io/github/languages/code-size/xModern54/zapret-bf?label=CODE%20SIZE&labelColor=161616&color=2b2b2b&style=for-the-badge">
  </a>
</p>

<br clear="left"/>

</div>

### Форк [Flowseal/zapret-discord-youtube](https://github.com/Flowseal/zapret-discord-youtube), исправляющий проблему с заходом в игру и матчами в серии игр Battlefield.

> [!CAUTION]
> ### Репозиторий не актуален
> В данный момент проблем с доступом к Battlefield не наблюдается, поэтому данный репозиторий на текущий момент не актуален.

> [!IMPORTANT]
> ### Как это работает
> Скрипт подменяет сигнатуру первых пакетов при подключении к матчу в BF 6, чтобы DPI-фильтры разрешили соединение, после установления связи весь трафик идёт напрямую, без влияния на пинг, производительность или потерю пакетов.

---

## ❤ Использование

1. **Скачайте архив** со [страницы последнего релиза](https://github.com/xModern54/zapret-bf/releases/latest)  
2. **Распакуйте** в папку без кириллицы и спецсимволов (например: `C:\zapret-bf`)  
3. **Запустите `General-BF (SIMPLE FAKE)` или `General-BF (ALT 8)` или другую стратегию** — начните с одной из доступных и проверьте, работает ли вход в игру и подключение к матчам.  
   Если не помогает — переходите к следующей, пока не найдёте рабочий вариант для своего провайдера. 
   Стратегия, которая подойдёт именно вам, зависит от вашего провайдера и того, какие паттерны блокировки он использует.  
4. Когда найдёте рабочую — установите её как сервис через `service.bat`

> [!IMPORTANT]
> **General-BF (SIMPLE FAKE)** и **General-BF (ALT 8)** — новые стратегии, которые подойдут большинству пользователей.  
> Результат всегда индивидуален и зависит от работы вашего провайдера и методов блокировки в регионе.  
> Если эти стратегии не сработают — попробуйте остальные, чтобы найти наиболее подходящую для себя.

---

## ⭐ Поддержка проекта

Вы можете поддержать проект, поставив ⭐ этому форку (вверху справа на странице).  

Если хотите, можете добавить меня в стиме 😏 — [мой профиль](https://steamcommunity.com/profiles/76561198899703365/)

Также можно материально поддержать разработчика оригинального zapret  
[здесь](https://github.com/bol-van/zapret/issues/590#issuecomment-2408866758)

💖 Отдельная благодарность разработчику [zapret](https://github.com/bol-van/zapret) — [bol-van](https://github.com/bol-van)

---

> [!IMPORTANT]
> **Zapret-BF — не является средством обхода блокировок.**
> 
> Этот скрипт **не предоставляет доступ к заблокированным в РФ сервисам** и **не нарушает законодательство Российской Федерации**.  
> Он предназначен **исключительно для решения проблемы подключения к матчам в игре Battlefield 6**, сервера которой размещены на Amazon Web Services (AWS).  
> 
> Доступ к игре был ограничен **непреднамеренно**, в результате массовой блокировки IP-адресов AWS, на которых также располагались запрещённые ресурсы.  
> Скрипт **восстанавливает соединение с игровыми серверами**, не затрагивая доступ к иным ресурсам.

> [!CAUTION]
>
> ### АНТИВИРУСЫ
> WinDivert может вызвать реакцию антивируса.  
> WinDivert — это инструмент для перехвата и фильтрации трафика, необходимый для работы zapret.  
> Замена iptables и NFQUEUE в Linux, которых нет под Windows.  
> Он может использоваться как хорошими, так и плохими программами, но сам по себе не является вирусом.  
> Драйвер WinDivert64.sys подписан для возможности загрузки в 64-битное ядро Windows.  
> Но антивирусы склонны относить подобное к классам повышенного риска или хакерским инструментам.  
> В случае проблем используйте исключения или временно отключайте антивирус.
>
> **Выдержка из [`readme.md`](https://github.com/bol-van/zapret-win-bundle/blob/master/readme.md#%D0%B0%D0%BD%D1%82%D0%B8%D0%B2%D0%B8%D1%80%D1%83%D1%81%D1%8B)**  
> репозитория [bol-van/zapret-win-bundle](https://github.com/bol-van/zapret-win-bundle)

> [!IMPORTANT]
> Все файлы в папке [`bin`](./bin) скачиваются из [zapret-win-bundle/zapret-winws](https://github.com/bol-van/zapret-win-bundle/tree/master/zapret-winws).  
> Вы можете это проверить с помощью хэшей/контрольных сумм.
