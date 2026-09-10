#!/usr/bin/env python3
"""Localize CALENDAR_DATA events and patch index.html chrome for UK/PL/EN."""
from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def L(uk: str, pl: str, en: str) -> dict:
    return {"uk": uk, "pl": pl, "en": en}


WEEKDAYS = {
    "uk": ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"],
    "pl": ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
}
WD_SHORT = {
    "uk": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"],
    "pl": ["Pn", "Wt", "Śr", "Cz", "Pt", "So", "Nd"],
    "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
}
MONTHS_NOM = {
    1: L("Січень", "Styczeń", "January"),
    2: L("Лютий", "Luty", "February"),
    3: L("Березень", "Marzec", "March"),
    4: L("Квітень", "Kwiecień", "April"),
    5: L("Травень", "Maj", "May"),
    6: L("Червень", "Czerwiec", "June"),
    7: L("Липень", "Lipiec", "July"),
    8: L("Серпень", "Sierpień", "August"),
    9: L("Вересень", "Wrzesień", "September"),
    10: L("Жовтень", "Październik", "October"),
    11: L("Листопад", "Listopad", "November"),
    12: L("Грудень", "Grudzień", "December"),
}
MONTHS_GEN = {
    1: L("січня", "stycznia", "January"),
    2: L("лютого", "lutego", "February"),
    3: L("березня", "marca", "March"),
    4: L("квітня", "kwietnia", "April"),
    5: L("травня", "maja", "May"),
    6: L("червня", "czerwca", "June"),
    7: L("липня", "lipca", "July"),
    8: L("серпня", "sierpnia", "August"),
    9: L("вересня", "września", "September"),
    10: L("жовтня", "października", "October"),
    11: L("листопада", "listopada", "November"),
    12: L("грудня", "grudnia", "December"),
}


def fmt_d(iso: str, lang: str, with_wd: bool = True) -> str:
    y, m, d = map(int, iso.split("-"))
    dt = date(y, m, d)
    base = f"{d:02d}.{m:02d}.{y}"
    if not with_wd:
        return base
    return f"{base} ({WEEKDAYS[lang][dt.weekday()]})"


def loc_date(iso: str, with_wd: bool = True) -> dict:
    return L(fmt_d(iso, "uk", with_wd), fmt_d(iso, "pl", with_wd), fmt_d(iso, "en", with_wd))


def loc_range(start: str, end: str, with_wd: bool = False) -> dict:
    def one(lang: str) -> str:
        a = fmt_d(start, lang, with_wd)
        b = fmt_d(end, lang, with_wd)
        if start[:7] == end[:7] and not with_wd:
            d1 = start.split("-")[2]
            m = start.split("-")[1]
            y = start.split("-")[0]
            d2, m2, y2 = end.split("-")[2], end.split("-")[1], end.split("-")[0]
            return f"{d1}.{m} – {d2}.{m2}.{y2}"
        return f"{a} – {b}"

    return L(one("uk"), one("pl"), one("en"))


def loc_until(iso: str) -> dict:
    return L(
        f"До {fmt_d(iso, 'uk')}",
        f"Do {fmt_d(iso, 'pl')}",
        f"By {fmt_d(iso, 'en')}",
    )


# Per-event localized fields (titlePl stays as officialTitle).
PATCH = {
    "ev-sep-1": {
        "title": L(
            "Урочистий початок 2026/2027 навчального року 🔔",
            "Uroczyste rozpoczęcie roku szkolnego 2026/2027 🔔",
            "Ceremonial start of the 2026/2027 school year 🔔",
        ),
        "categoryName": L("Початок навчання", "Początek nauki", "Start of school"),
        "time": L("09:00", "09:00", "09:00"),
        "description": L(
            "Перший дзвоник, урочиста лінійка та знайомство з класним керівником і ліцеєм. Офіційний старт I півріччя.",
            "Pierwszy dzwonek, uroczysta zbiórka oraz poznanie wychowawcy i liceum. Oficjalny start I semestru.",
            "First bell, a ceremonial assembly, and meeting the form tutor and the lyceum. Official start of semester I.",
        ),
        "grade1Note": L(
            "Обов'язкова присутність у святковому одязі. Перший день для першокласників у ліцеї!",
            "Obowiązkowa obecność w stroju galowym. Pierwszy dzień uczniów klasy 1. w liceum!",
            "Formal dress is required. The first day at the lyceum for Year 1 students!",
        ),
        "location": L(
            "LXXVIII LO w Warszawie, ul. Anieli Krzywoń 3",
            "LXXVIII LO w Warszawie, ul. Anieli Krzywoń 3",
            "LXXVIII LO in Warsaw, 3 Anieli Krzywoń Street",
        ),
        "badgeShort": L("🔔 Початок року!", "🔔 Początek roku!", "🔔 Year starts!"),
        "dateFormatted": loc_date("2026-09-01"),
    },
    "ev-sep-8-meeting": {
        "title": L(
            "Батьківські збори 1-х класів із директором 👥",
            "Spotkanie z Dyrektorem (klasy I) i wychowawcami 👥",
            "Year 1 parents’ meeting with the headteacher 👥",
        ),
        "categoryName": L("Батьківські збори", "Zebranie z rodzicami", "Parent meeting"),
        "time": L("17:30", "17:30", "17:30"),
        "description": L(
            "Перша офіційна установча зустріч батьків учнів 1-х класів з керівництвом ліцею та класними керівниками.",
            "Pierwsze oficjalne spotkanie organizacyjne rodziców uczniów klas 1. z dyrekcją i wychowawcami.",
            "The first official organisational meeting of Year 1 parents with the school leadership and form tutors.",
        ),
        "grade1Note": L(
            "Критично важливі збори для батьків 1-х класів: організація навчання, правила ліцею, доступ до електронного щоденника Librus, виїзна інтеграція.",
            "Kluczowe zebranie dla rodziców klas 1.: organizacja nauki, zasady liceum, dostęp do dziennika Librus, integracja wyjazdowa.",
            "Essential for Year 1 parents: how school is organised, lyceum rules, Librus e-register access, and the integration trip.",
        ),
        "location": L("Актова зала / кабінети ліцею", "Sala gimnastyczna / sale liceum", "Assembly hall / lyceum classrooms"),
        "badgeShort": L("👥 Збори 1-х кл. (17:30)", "👥 Zebranie kl. 1 (17:30)", "👥 Year 1 meeting (17:30)"),
        "dateFormatted": loc_date("2026-09-08"),
    },
    "ev-sep-8-council": {
        "title": L(
            "Організаційна педагогічна рада ліцею 📋",
            "Rada pedagogiczna organizacyjna 📋",
            "Organisational teaching-staff council 📋",
        ),
        "categoryName": L("Педагогічна рада", "Rada pedagogiczna", "Staff council"),
        "time": L("15:00", "15:00", "15:00"),
        "description": L(
            "Затвердження плану педагогічного нагляду та організація навчального процесу на рік.",
            "Zatwierdzenie planu nadzoru pedagogicznego i organizacji procesu nauczania na rok.",
            "Approval of the pedagogical-supervision plan and organisation of teaching for the year.",
        ),
        "grade1Note": L("Педагогічна рада вчителів ліцею.", "Rada pedagogiczna nauczycieli liceum.", "Lyceum teaching-staff council."),
        "location": L("Учительська ліцею", "Pokój nauczycielski", "Staff room"),
        "badgeShort": L("📋 Організаційна педрада", "📋 Rada organizacyjna", "📋 Organisational council"),
        "dateFormatted": loc_date("2026-09-08"),
    },
    "ev-sep-photo": {
        "title": L("Фото з класом 📷", "Zdjęcie klasowe 📷", "Class photo 📷"),
        "categoryName": L("Шкільна подія", "Wydarzenie szkolne", "School event"),
        "time": L("Упродовж дня", "W ciągu dnia", "During the day"),
        "description": L(
            "Класне фото для шкільного альбому та документів ліцею.",
            "Zdjęcie klasowe do albumu szkolnego i dokumentacji liceum.",
            "Class photo for the school album and lyceum records.",
        ),
        "grade1Note": L(
            "Варто бути в охайному повсякденному або шкільному одязі — точне місце й час уточнить класний керівник.",
            "Warto być w schludnym stroju codziennym lub szkolnym — dokładne miejsce i godzinę poda wychowawca.",
            "Come in neat everyday or school clothes — the form tutor will confirm the exact place and time.",
        ),
        "location": L("Ліцей", "Liceum", "Lyceum"),
        "badgeShort": L("📷 Фото з класом", "📷 Zdjęcie klasowe", "📷 Class photo"),
        "dateFormatted": loc_date("2026-09-29"),
    },
    "ev-sep-legit": {
        "title": L("Легітимація 🪪", "Legitymacja 🪪", "Student ID card 🪪"),
        "categoryName": L("Шкільна подія", "Wydarzenie szkolne", "School event"),
        "time": L("Упродовж дня", "W ciągu dnia", "During the day"),
        "description": L(
            "Видача учнівської легітимації (шкільного посвідчення).",
            "Wydanie legitymacji szkolnej.",
            "Issue of the student ID card (legitymacja).",
        ),
        "grade1Note": L(
            "Легітимація потрібна для знижок у транспорті та входу до ліцею — уточніть у класного керівника, чи треба фото або документи.",
            "Legitymacja jest potrzebna do zniżek w transporcie i wejścia do liceum — wychowawca powie, czy trzeba zdjęcie lub dokumenty.",
            "The student ID is used for transport discounts and entering the lyceum — the form tutor will say if a photo or documents are needed.",
        ),
        "location": L("Ліцей", "Liceum", "Lyceum"),
        "badgeShort": L("🪪 Легітимація", "🪪 Legitymacja", "🪪 Student ID"),
        "dateFormatted": loc_date("2026-09-30"),
    },
    "ev-oct-integ": {
        "title": L(
            "Дні виїзної інтеграції перших класів 🎒🤝",
            "Dni integracji wyjazdowej klas pierwszych 🎒🤝",
            "Year 1 residential integration days 🎒🤝",
        ),
        "categoryName": L("Інтеграція 1-х класів", "Integracja klas 1.", "Year 1 integration"),
        "time": L("2 дні", "2 dni", "2 days"),
        "description": L(
            "Головна виїзна подія для новоприбулих учнів: тренінги на згуртування, знайомство, командоутворення, спортивні та творчі квести.",
            "Główne wydarzenie wyjazdowe dla nowych uczniów: warsztaty integracyjne, poznawanie się, budowanie zespołu, questy sportowe i twórcze.",
            "The main off-site event for new students: bonding workshops, getting to know one another, team-building, sports and creative quests.",
        ),
        "grade1Note": L(
            "Подія СТОСУЄТЬСЯ ВИКЛЮЧНО 1-Х КЛАСІВ! Допомагає новачкам швидко подружитися та влитися в атмосферу ліцею.",
            "Wydarzenie TYLKO DLA KLAS 1.! Pomaga nowym uczniom szybko się zaprzyjaźnić i wejść w atmosferę liceum.",
            "This event is FOR YEAR 1 ONLY. It helps newcomers make friends quickly and settle into lyceum life.",
        ),
        "location": L("Заміська інтеграційна база ліцею", "Pozamiejska baza integracyjna liceum", "Lyceum off-site integration venue"),
        "badgeShort": L("🎒 Інтеграція 1-х класів", "🎒 Integracja klas 1.", "🎒 Year 1 integration"),
        "dateFormatted": L(
            "01.10 – 02.10.2026 (Четвер – П'ятниця)",
            "01.10 – 02.10.2026 (Czwartek – Piątek)",
            "01.10 – 02.10.2026 (Thursday – Friday)",
        ),
    },
    "ev-oct-14-den": {
        "title": L(
            "День національної освіти в Польщі (DEN) 💐",
            "Dzień Edukacji Narodowej 💐",
            "National Education Day (DEN) 💐",
        ),
        "categoryName": L("Шкільне свято", "Święto szkolne", "School celebration"),
        "time": L("Весь день", "Cały dzień", "All day"),
        "description": L(
            "Урочистий день вчителів та всієї шкільної спільноти. Традиційно проводяться шкільні урочистості, посвята першокласників (ślubowanie) або святкові заходи.",
            "Uroczysty dzień nauczycieli i całej społeczności szkolnej. Tradycyjnie odbywają się uroczystości, ślubowanie klas pierwszych lub inne święta szkolne.",
            "A ceremonial day for teachers and the whole school community. Traditionally there are school celebrations, the Year 1 pledge (ślubowanie), or festive events.",
        ),
        "grade1Note": L("Урочистий день у ліцеї.", "Uroczysty dzień w liceum.", "A ceremonial day at the lyceum."),
        "location": L("LXXVIII LO", "LXXVIII LO", "LXXVIII LO"),
        "badgeShort": L("💐 День освіти (DEN)", "💐 Dzień Edukacji", "💐 Education Day"),
        "dateFormatted": loc_date("2026-10-14"),
    },
    "ev-nov-1-all-saints": {
        "title": L("День усіх святих 🛑", "Wszystkich Świętych 🛑", "All Saints’ Day 🛑"),
        "categoryName": L("Державне свято", "Święto państwowe", "Public holiday"),
        "time": L("Весь день", "Cały dzień", "All day"),
        "description": L(
            "Офіційне державне свято та вихідний день у всій Польщі.",
            "Oficjalne święto państwowe i dzień wolny w całej Polsce.",
            "An official public holiday and a day off across Poland.",
        ),
        "grade1Note": L("Вихідний день.", "Dzień wolny.", "A day off."),
        "location": L("Польща", "Polska", "Poland"),
        "badgeShort": L("🛑 Всіх Святих", "🛑 Wszystkich Świętych", "🛑 All Saints’ Day"),
        "dateFormatted": loc_date("2026-11-01"),
    },
    "ev-nov-3-meeting": {
        "title": L(
            "Батьківські збори: перші результати навчання 👥",
            "Zebranie z rodzicami: informacja o postępach i wynikach 👥",
            "Parent meeting: first learning results 👥",
        ),
        "categoryName": L("Батьківські збори", "Zebranie z rodzicami", "Parent meeting"),
        "time": L("17:30", "17:30", "17:30"),
        "description": L(
            "Аналіз перших двох місяців навчання в ліцеї, поточні оцінки учнів, зауваження вчителів-предметників та рекомендації.",
            "Omówienie pierwszych dwóch miesięcy nauki w liceum, bieżące oceny, uwagi nauczycieli przedmiotów i rekomendacje.",
            "A review of the first two months at the lyceum, current marks, subject-teacher comments and recommendations.",
        ),
        "grade1Note": L(
            "Важлива перевірка адаптації першокласників до навантаження в ліцеї.",
            "Ważne sprawdzenie adaptacji uczniów klasy 1. do obciążenia w liceum.",
            "An important check on how Year 1 students are adapting to lyceum workload.",
        ),
        "location": L("Кабінети класних керівників", "Sale wychowawców", "Form tutors’ classrooms"),
        "badgeShort": L("👥 Батьківські збори (17:30)", "👥 Zebranie z rodzicami (17:30)", "👥 Parent meeting (17:30)"),
        "dateFormatted": loc_date("2026-11-03"),
    },
    "ev-nov-11-independence": {
        "title": L(
            "Національне свято незалежності Польщі 🇵🇱🛑",
            "Narodowe Święto Niepodległości 🇵🇱🛑",
            "Poland’s National Independence Day 🇵🇱🛑",
        ),
        "categoryName": L("Державне свято", "Święto państwowe", "Public holiday"),
        "time": L("Весь день", "Cały dzień", "All day"),
        "description": L("Державний вихідний день. Занять немає.", "Państwowy dzień wolny. Brak zajęć.", "A national day off. No lessons."),
        "grade1Note": L("Офіційний вихідний день у ліцеї.", "Oficjalny dzień wolny w liceum.", "An official day off at the lyceum."),
        "location": L("Польща", "Polska", "Poland"),
        "badgeShort": L("🛑 День Незалежності", "🛑 Święto Niepodległości", "🛑 Independence Day"),
        "dateFormatted": loc_date("2026-11-11"),
    },
    "ev-dec-15-grade": {
        "title": L(
            "Повідомлення про загрозу незадовільних оцінок ⚠️",
            "Poinformowanie o zagrożeniach ocenami niedostatecznymi ⚠️",
            "Notice of risk of failing grades ⚠️",
        ),
        "categoryName": L("Оцінювання", "Ocenianie", "Assessment"),
        "time": L("Дедлайн", "Termin", "Deadline"),
        "description": L(
            "Офіційне письмове сповіщення батьків про ризик отримання учнем незадовільної семестрової оцінки або незадовільної оцінки з поведінки.",
            "Oficjalne pisemne poinformowanie rodziców o ryzyku oceny niedostatecznej semestralnej lub nieodpowiedniej oceny z zachowania.",
            "Official written notice to parents if a student is at risk of a failing semester grade or an unsatisfactory behaviour grade.",
        ),
        "grade1Note": L(
            "Батькам необхідно перевірити електронний щоденник Librus та звернутися до вчителів у разі заборгованостей.",
            "Rodzice powinni sprawdzić dziennik Librus i skontaktować się z nauczycielami w razie braków.",
            "Parents should check the Librus e-register and contact teachers if work is outstanding.",
        ),
        "location": L("Librus / Ліцей", "Librus / Liceum", "Librus / lyceum"),
        "badgeShort": L("⚠️ Загрози оцінок", "⚠️ Zagrożenia ocenami", "⚠️ Grade warnings"),
        "dateFormatted": loc_until("2026-12-15"),
    },
    "ev-dec-15-meeting": {
        "title": L(
            "Батьківські збори: попередження щодо оцінок 👥",
            "Zebranie z rodzicami: zagrożenia ocenami 👥",
            "Parent meeting: grade warnings 👥",
        ),
        "categoryName": L("Батьківські збори", "Zebranie z rodzicami", "Parent meeting"),
        "time": L("17:30", "17:30", "17:30"),
        "description": L(
            "Очні консультації батьків з класними керівниками та вчителями щодо виправлення оцінок до кінця I семестру.",
            "Stacjonarne konsultacje rodziców z wychowawcami i nauczycielami w sprawie poprawy ocen do końca I semestru.",
            "In-person consultations with form tutors and teachers about improving marks before the end of semester I.",
        ),
        "grade1Note": L(
            "Можливість узгодити графік перездач та консультацій перед семестровою класифікацією.",
            "Możliwość ustalenia harmonogramu popraw i konsultacji przed klasyfikacją semestralną.",
            "A chance to agree retake and consultation dates before semester classification.",
        ),
        "location": L("Кабінети ліцею", "Sale liceum", "Lyceum classrooms"),
        "badgeShort": L("👥 Збори батьків (17:30)", "👥 Zebranie z rodzicami (17:30)", "👥 Parent meeting (17:30)"),
        "dateFormatted": loc_date("2026-12-15"),
    },
    "ev-dec-21-off": {
        "title": L(
            "Вільні від уроків дні (Директорські вихідні) 🛑",
            "Dodatkowe dni wolne od zajęć dydaktyczno-wychowawczych 🛑",
            "Days off lessons (headteacher’s extra days) 🛑",
        ),
        "categoryName": L("Вільні дні", "Dni wolne", "Days off"),
        "time": L("2 дні", "2 dni", "2 days"),
        "description": L(
            "Додаткові вихідні дні, встановлені дирекцією ліцею перед різдвяними канікулами. Занять немає.",
            "Dodatkowe dni wolne ustalone przez dyrekcję liceum przed feriami świątecznymi. Brak zajęć.",
            "Extra days off set by the lyceum leadership before the Christmas break. No lessons.",
        ),
        "grade1Note": L("Учні 1-х класів відпочивають.", "Uczniowie klas 1. odpoczywają.", "Year 1 students have a rest."),
        "location": L("Ліцей", "Liceum", "Lyceum"),
        "badgeShort": L("🛑 Вільний день", "🛑 Dzień wolny", "🛑 Day off"),
        "dateFormatted": L(
            "21.12 – 22.12.2026 (Понеділок – Вівторок)",
            "21.12 – 22.12.2026 (Poniedziałek – Wtorek)",
            "21.12 – 22.12.2026 (Monday – Tuesday)",
        ),
    },
    "ev-dec-23-vacation": {
        "title": L(
            "Зимова різдвяна святкова перерва 🎄❄️",
            "Zimowa przerwa świąteczna (Boże Narodzenie) 🎄❄️",
            "Christmas winter break 🎄❄️",
        ),
        "categoryName": L("Канікули", "Ferie / przerwa", "School break"),
        "time": L("Святкові канікули", "Przerwa świąteczna", "Holiday break"),
        "description": L(
            "Різдвяні шкільні канікули. 24 грудня — Святвечір (Wigilia), 25–26 грудня — Різдво Христове (Boże Narodzenie), 31 грудня — Сильвестр.",
            "Szkolna przerwa świąteczna. 24 grudnia — Wigilia, 25–26 grudnia — Boże Narodzenie, 31 grudnia — Sylwester.",
            "The school Christmas break. 24 December is Christmas Eve (Wigilia), 25–26 December is Christmas, 31 December is New Year’s Eve.",
        ),
        "grade1Note": L(
            "Шкільні канікули для всіх учнів ліцею.",
            "Przerwa świąteczna dla wszystkich uczniów liceum.",
            "A school break for all lyceum students.",
        ),
        "location": L("Польща", "Polska", "Poland"),
        "badgeShort": L("🎄 Зимові канікули", "🎄 Zimowa przerwa", "🎄 Winter break"),
        "dateFormatted": loc_range("2026-12-23", "2026-12-31"),
        "badgeByDate": {
            "2026-12-24": L("🎄 Святвечір", "🎄 Wigilia", "🎄 Christmas Eve"),
            "2026-12-25": L("🛑 Різдво Христове", "🛑 Boże Narodzenie", "🛑 Christmas Day"),
            "2026-12-26": L("🛑 2-й день Різдва", "🛑 2. dzień Świąt", "🛑 Boxing Day"),
        },
    },
    "ev-jan-1-newyear": {
        "title": L("Новий Рік 2027! 🎆🛑", "Nowy Rok 2027! 🎆🛑", "New Year 2027! 🎆🛑"),
        "categoryName": L("Державне свято", "Święto państwowe", "Public holiday"),
        "time": L("Весь день", "Cały dzień", "All day"),
        "description": L(
            "Державне свято та офіційний вихідний день.",
            "Święto państwowe i oficjalny dzień wolny.",
            "A public holiday and an official day off.",
        ),
        "grade1Note": L("Вихідний день.", "Dzień wolny.", "A day off."),
        "location": L("Польща", "Polska", "Poland"),
        "badgeShort": L("🛑 Новий рік!", "🛑 Nowy Rok!", "🛑 New Year!"),
        "dateFormatted": loc_date("2027-01-01"),
    },
    "ev-jan-4-off": {
        "title": L(
            "Вільні від уроків дні (Директорські вихідні) 🛑",
            "Dodatkowe dni wolne od zajęć dydaktycznych 🛑",
            "Days off lessons (headteacher’s extra days) 🛑",
        ),
        "categoryName": L("Вільні дні", "Dni wolne", "Days off"),
        "time": L("2 дні", "2 dni", "2 days"),
        "description": L(
            "Директорські вихідні між Новим Роком та Водохрещем/Трьома Королями. Уроки не проводяться.",
            "Dni wolne dyrektorskie między Nowym Rokiem a Świętem Trzech Króli. Brak lekcji.",
            "Headteacher’s extra days between New Year and Epiphany / Three Kings. No lessons.",
        ),
        "grade1Note": L("Вихідні дні для 1-х класів.", "Dni wolne dla klas 1.", "Days off for Year 1."),
        "location": L("Ліцей", "Liceum", "Lyceum"),
        "badgeShort": L("🛑 Вільний день", "🛑 Dzień wolny", "🛑 Day off"),
        "dateFormatted": L(
            "04.01 – 05.01.2027 (Понеділок – Вівторок)",
            "04.01 – 05.01.2027 (Poniedziałek – Wtorek)",
            "04.01 – 05.01.2027 (Monday – Tuesday)",
        ),
    },
    "ev-jan-6-kings": {
        "title": L(
            "Свято Трьох Королів (Богоявлення) 👑🛑",
            "Święto Trzech Króli (Objawienie Pańskie) 👑🛑",
            "Epiphany (Three Kings’ Day) 👑🛑",
        ),
        "categoryName": L("Державне свято", "Święto państwowe", "Public holiday"),
        "time": L("Весь день", "Cały dzień", "All day"),
        "description": L(
            "Державне свято та вихідний день у всій Польщі.",
            "Święto państwowe i dzień wolny w całej Polsce.",
            "A public holiday and a day off across Poland.",
        ),
        "grade1Note": L("Вихідний день.", "Dzień wolny.", "A day off."),
        "location": L("Польща", "Polska", "Poland"),
        "badgeShort": L("🛑 Три Королі", "🛑 Trzech Króli", "🛑 Three Kings"),
        "dateFormatted": loc_date("2027-01-06"),
    },
    "ev-jan-22-grade": {
        "title": L(
            "Остаточне виставлення підсумкових оцінок за I півріччя 📝",
            "Ostateczne wystawienie ocen za I półrocze 📝",
            "Final semester-I grades recorded 📝",
        ),
        "categoryName": L("Оцінювання", "Ocenianie", "Assessment"),
        "time": L("Дедлайн", "Termin", "Deadline"),
        "description": L(
            "Закриття семестрового журналу оцінок для 1-х та 2-х класів. Усі оцінки мають бути зафіксовані в системі.",
            "Zamknięcie dziennika ocen semestralnych dla klas 1. i 2. Wszystkie oceny muszą być wpisane w systemie.",
            "Semester gradebook closes for Years 1 and 2. All marks must be recorded in the system.",
        ),
        "grade1Note": L(
            "Фіксація підсумкових семестрових балів першокласників.",
            "Zapisanie ocen semestralnych uczniów klasy 1.",
            "Year 1 semester totals are locked in.",
        ),
        "location": L("Librus", "Librus", "Librus"),
        "badgeShort": L("📝 Виставлення оцінок", "📝 Wystawienie ocen", "📝 Grades posted"),
        "dateFormatted": loc_until("2027-01-22"),
    },
    "ev-jan-26-council": {
        "title": L(
            "Класифікаційна педрада для 1-х і 2-х класів 📋",
            "Klasyfikacyjna rada pedagogiczna (klasy 1 i 2) 📋",
            "Classification staff council (Years 1 and 2) 📋",
        ),
        "categoryName": L("Педагогічна рада", "Rada pedagogiczna", "Staff council"),
        "time": L("15:00", "15:00", "15:00"),
        "description": L(
            "Затвердження результатів класифікації за I семестр учнів 1-х та 2-х класів.",
            "Zatwierdzenie wyników klasyfikacji za I semestr uczniów klas 1. i 2.",
            "Approval of semester-I classification results for Years 1 and 2.",
        ),
        "grade1Note": L("Педагогічна рада ліцею.", "Rada pedagogiczna liceum.", "Lyceum staff council."),
        "location": L("Учительська", "Pokój nauczycielski", "Staff room"),
        "badgeShort": L("📋 Педрада 1–2 кл.", "📋 Rada kl. 1–2", "📋 Council Years 1–2"),
        "dateFormatted": loc_date("2027-01-26"),
    },
    "ev-jan-26-meeting": {
        "title": L(
            "Батьківські збори: підсумки I півріччя 👥",
            "Zebranie z rodzicami: wyniki klasyfikacji za I półrocze 👥",
            "Parent meeting: semester-I results 👥",
        ),
        "categoryName": L("Батьківські збори", "Zebranie z rodzicami", "Parent meeting"),
        "time": L("17:30", "17:30", "17:30"),
        "description": L(
            "Оголошення підсумкових семестрових оцінок, аналіз успішності учнів 1-х класів за перше півріччя.",
            "Ogłoszenie ocen semestralnych i omówienie wyników uczniów klas 1. za pierwsze półrocze.",
            "Announcement of semester grades and a review of Year 1 progress in the first half-year.",
        ),
        "grade1Note": L(
            "Ключові збори за підсумками першого півріччя ліцею.",
            "Kluczowe zebranie podsumowujące pierwsze półrocze w liceum.",
            "The key meeting after the first half-year at the lyceum.",
        ),
        "location": L("Кабінети ліцею", "Sale liceum", "Lyceum classrooms"),
        "badgeShort": L("👥 Збори батьків (17:30)", "👥 Zebranie z rodzicami (17:30)", "👥 Parent meeting (17:30)"),
        "dateFormatted": loc_date("2027-01-26"),
    },
    "ev-jan-29-endsem": {
        "title": L("Завершення занять I півріччя 🏁", "Koniec zajęć I półrocza 🏁", "End of semester-I lessons 🏁"),
        "categoryName": L("Кінець семестру", "Koniec semestru", "End of semester"),
        "time": L("Останній день семестру", "Ostatni dzień semestru", "Last day of the semester"),
        "description": L(
            "Офіційне завершення навчальних занять у першому семестрі.",
            "Oficjalne zakończenie zajęć dydaktycznych w pierwszym semestrze.",
            "Official end of teaching in semester I.",
        ),
        "grade1Note": L("Завершення I семестру.", "Zakończenie I semestru.", "End of semester I."),
        "location": L("Ліцей", "Liceum", "Lyceum"),
        "badgeShort": L("🏁 Кінець I півріччя", "🏁 Koniec I semestru", "🏁 End of semester I"),
        "dateFormatted": loc_date("2027-01-29"),
    },
    "ev-feb-1-start2": {
        "title": L("Офіційний початок II півріччя 🚀", "Początek II półrocza 🚀", "Official start of semester II 🚀"),
        "categoryName": L("Початок семестру", "Początek semestru", "Start of semester"),
        "time": L("Старт II півріччя", "Start II semestru", "Start of semester II"),
        "description": L(
            "Офіційний старт навчального процесу другого півріччя (дидактичні заняття відновлюються після канікул 15 лютого).",
            "Oficjalny start procesu nauczania w drugim semestrze (zajęcia dydaktyczne wracają po feriach 15 lutego).",
            "Official start of semester II (lessons resume after the winter break on 15 February).",
        ),
        "grade1Note": L("Юридичний початок II семестру.", "Formalny początek II semestru.", "The legal start of semester II."),
        "location": L("Ліцей", "Liceum", "Lyceum"),
        "badgeShort": L("🚀 Старт II півріччя", "🚀 Start II semestru", "🚀 Semester II starts"),
        "dateFormatted": loc_date("2027-02-01"),
    },
    "ev-feb-vacation": {
        "title": L(
            "Зимові канікули (Ferie zimowe) ⛷️❄️",
            "Ferie zimowe (woj. mazowieckie) ⛷️❄️",
            "Winter holidays (Mazovia) ⛷️❄️",
        ),
        "categoryName": L("Канікули", "Ferie", "School holidays"),
        "time": L("2 повних тижні", "2 pełne tygodnie", "2 full weeks"),
        "description": L(
            "Офіційні зимові канікули для шкіл Мазовецького воєводства (Варшава). 2 повні тижні відпочинку для учнів.",
            "Oficjalne ferie zimowe dla szkół województwa mazowieckiego (Warszawa). Dwa pełne tygodnie odpoczynku.",
            "Official winter holidays for Mazovian voivodeship schools (Warsaw). Two full weeks off for students.",
        ),
        "grade1Note": L(
            "Уроки не проводяться. Відпочинок для всіх учнів 1-х класів.",
            "Brak lekcji. Odpoczynek dla wszystkich uczniów klas 1.",
            "No lessons. Rest for all Year 1 students.",
        ),
        "location": L("Польща", "Polska", "Poland"),
        "badgeShort": L("❄️ Зимові канікули", "❄️ Ferie zimowe", "❄️ Winter holidays"),
        "dateFormatted": loc_range("2027-02-01", "2027-02-14"),
    },
    "ev-feb-15-resume": {
        "title": L("Відновлення аудиторних занять 📚", "Wznowienie zajęć po feriach zimowych 📚", "Lessons resume 📚"),
        "categoryName": L("Навчання", "Zajęcia", "Lessons"),
        "time": L("08:00", "08:00", "08:00"),
        "description": L(
            "Повернення учнів до занять за розкладом II півріччя після зимових канікул.",
            "Powrót uczniów do zajęć według planu II semestru po feriach zimowych.",
            "Students return to the semester-II timetable after the winter holidays.",
        ),
        "grade1Note": L(
            "Перший навчальний день після зимових канікул.",
            "Pierwszy dzień nauki po feriach zimowych.",
            "First school day after the winter holidays.",
        ),
        "location": L("Ліцей", "Liceum", "Lyceum"),
        "badgeShort": L("📚 Початок занять", "📚 Powrót do zajęć", "📚 Lessons resume"),
        "dateFormatted": loc_date("2027-02-15"),
    },
    "ev-feb-16-council": {
        "title": L(
            "Підсумкова педагогічна рада за I півріччя 📋",
            "Podsumowująca rada pedagogiczna za I półrocze 📋",
            "Summary staff council for semester I 📋",
        ),
        "categoryName": L("Педагогічна рада", "Rada pedagogiczna", "Staff council"),
        "time": L("15:00", "15:00", "15:00"),
        "description": L(
            "Аналіз педагогічних та виховних результатів ліцею за перше півріччя.",
            "Analiza wyników dydaktycznych i wychowawczych liceum za pierwsze półrocze.",
            "Review of the lyceum’s teaching and pastoral results for the first half-year.",
        ),
        "grade1Note": L("Педрада вчителів.", "Rada pedagogiczna nauczycieli.", "Teaching-staff council."),
        "location": L("Учительська", "Pokój nauczycielski", "Staff room"),
        "badgeShort": L("📋 Підсумкова педрада", "📋 Rada podsumowująca", "📋 Summary council"),
        "dateFormatted": loc_date("2027-02-16"),
    },
    "ev-mar-easter": {
        "title": L(
            "Весняна великодня святкова перерва 🐣🌷",
            "Wiosenna przerwa świąteczna (Wielkanoc) 🐣🌷",
            "Spring Easter break 🐣🌷",
        ),
        "categoryName": L("Канікули", "Przerwa świąteczna", "School break"),
        "time": L("Святкові дні", "Dni świąteczne", "Holiday days"),
        "description": L(
            "Весняні великодні канікули. 28 березня — Великдень (Wielkanoc), 29 березня — Великодній понеділок (Poniedziałek Wielkanocny).",
            "Wiosenna przerwa wielkanocna. 28 marca — Wielkanoc, 29 marca — Poniedziałek Wielkanocny.",
            "The spring Easter break. 28 March is Easter Sunday, 29 March is Easter Monday.",
        ),
        "grade1Note": L(
            "Шкільні великодні канікули. Занять немає.",
            "Szkolna przerwa wielkanocna. Brak zajęć.",
            "School Easter break. No lessons.",
        ),
        "location": L("Польща", "Polska", "Poland"),
        "badgeShort": L("🐣 Великодні канікули", "🐣 Przerwa wielkanocna", "🐣 Easter break"),
        "dateFormatted": loc_range("2027-03-25", "2027-03-30"),
        "badgeByDate": {
            "2027-03-28": L("🛑 Великдень!", "🛑 Wielkanoc!", "🛑 Easter Sunday!"),
            "2027-03-29": L("🛑 Великодній понеділок", "🛑 Poniedziałek Wielkanocny", "🛑 Easter Monday"),
        },
    },
    "ev-mar-31-resume": {
        "title": L(
            "Відновлення аудиторних занять після Великодня 📚",
            "Wznowienie zajęć dydaktycznych 📚",
            "Lessons resume after Easter 📚",
        ),
        "categoryName": L("Навчання", "Zajęcia", "Lessons"),
        "time": L("08:00", "08:00", "08:00"),
        "description": L(
            "Повернення до навчання після Великодніх свят.",
            "Powrót do nauki po świętach wielkanocnych.",
            "Return to lessons after Easter.",
        ),
        "grade1Note": L(
            "Усі уроки за звичайним розкладом середи.",
            "Wszystkie lekcje według zwykłego planu środy.",
            "All lessons follow the usual Wednesday timetable.",
        ),
        "location": L("Ліцей", "Liceum", "Lyceum"),
        "badgeShort": L("📚 Відновлення занять", "📚 Powrót do zajęć", "📚 Lessons resume"),
        "dateFormatted": loc_date("2027-03-31"),
    },
    "ev-apr-6-meeting": {
        "title": L(
            "Батьківські збори: поточна успішність у II семестрі 👥",
            "Zebranie z rodzicami: informacja o postępach w nauce 👥",
            "Parent meeting: semester-II progress 👥",
        ),
        "categoryName": L("Батьківські збори", "Zebranie z rodzicami", "Parent meeting"),
        "time": L("17:30", "17:30", "17:30"),
        "description": L(
            "Зустріч батьків із класними керівниками: поточні весняні оцінки, відвідуваність та підготовка до річної атестації.",
            "Spotkanie rodziców z wychowawcami: bieżące oceny wiosenne, frekwencja i przygotowanie do klasyfikacji rocznej.",
            "Parents meet form tutors: current spring marks, attendance, and preparation for year-end assessment.",
        ),
        "grade1Note": L(
            "Батьківські збори для 1-х, 2-х та 3-х класів.",
            "Zebranie z rodzicami klas 1., 2. i 3.",
            "Parent meeting for Years 1, 2 and 3.",
        ),
        "location": L("Кабінети ліцею", "Sale liceum", "Lyceum classrooms"),
        "badgeShort": L("👥 Збори 1–3 кл. (17:30)", "👥 Zebranie kl. 1–3 (17:30)", "👥 Years 1–3 meeting (17:30)"),
        "dateFormatted": loc_date("2027-04-06"),
    },
    "ev-apr-8-openday": {
        "title": L(
            "День відкритих дверей у Ліцеї 🏫✨",
            "Dzień otwarty w LXXVIII LO 🏫✨",
            "Open day at the lyceum 🏫✨",
        ),
        "categoryName": L("Шкільний захід", "Wydarzenie szkolne", "School event"),
        "time": L("17:00", "17:00", "17:00"),
        "description": L(
            "Презентація ліцею для майбутніх абітурієнтів. Першокласники часто беруть участь у презентації своїх профілів та напрямів.",
            "Prezentacja liceum dla przyszłych kandydatów. Uczniowie klas 1. często prezentują swoje profile i kierunki.",
            "A presentation of the lyceum for prospective applicants. Year 1 students often help present their profiles and tracks.",
        ),
        "grade1Note": L("Захід ліцею.", "Wydarzenie liceum.", "A lyceum event."),
        "location": L("LXXVIII LO", "LXXVIII LO", "LXXVIII LO"),
        "badgeShort": L("🏫 День відкритих дверей", "🏫 Dzień otwarty", "🏫 Open day"),
        "dateFormatted": loc_date("2027-04-08"),
    },
    "ev-apr-trip": {
        "title": L(
            "Весняний виїзний (екскурсійний) тиждень ліцею 🚌🌸",
            "Wiosenny tydzień wyjazdowy / wycieczkowy 🚌🌸",
            "Spring trip / excursion week 🚌🌸",
        ),
        "categoryName": L("Виїзди та екскурсії", "Wyjazdy i wycieczki", "Trips and excursions"),
        "time": L("Весь тиждень", "Cały tydzień", "All week"),
        "description": L(
            "Весняний тиждень виїзних освітніх програм, екскурсій містами Польщі та природоохоронними парками.",
            "Wiosenny tydzień wyjazdów edukacyjnych, wycieczek po miastach Polski i parkach przyrodniczych.",
            "A spring week of educational trips, city excursions in Poland and nature-park visits.",
        ),
        "grade1Note": L(
            "Виїзні активності для учнів 1-х класів.",
            "Aktywności wyjazdowe dla uczniów klas 1.",
            "Off-site activities for Year 1 students.",
        ),
        "location": L("Виїзні маршрути", "Trasy wyjazdowe", "Off-site itineraries"),
        "badgeShort": L("🚌 Екскурсійний тиждень", "🚌 Tydzień wycieczkowy", "🚌 Trip week"),
        "dateFormatted": loc_range("2027-04-26", "2027-04-30"),
    },
    "ev-may-1-labor": {
        "title": L("Свято Праці 🛑", "Święto Pracy 🛑", "Labour Day 🛑"),
        "categoryName": L("Державне свято", "Święto państwowe", "Public holiday"),
        "time": L("Весь день", "Cały dzień", "All day"),
        "description": L("Державне свято та вихідний день.", "Święto państwowe i dzień wolny.", "A public holiday and a day off."),
        "grade1Note": L("Вихідний день.", "Dzień wolny.", "A day off."),
        "location": L("Польща", "Polska", "Poland"),
        "badgeShort": L("🛑 Свято Праці", "🛑 Święto Pracy", "🛑 Labour Day"),
        "dateFormatted": loc_date("2027-05-01"),
    },
    "ev-may-3-const": {
        "title": L(
            "Свято Національної Конституції 3 Травня 🇵🇱🛑",
            "Święto Narodowe Trzeciego Maja 🇵🇱🛑",
            "Constitution Day (3 May) 🇵🇱🛑",
        ),
        "categoryName": L("Державне свято", "Święto państwowe", "Public holiday"),
        "time": L("Весь день", "Cały день", "All day"),
        "description": L(
            "Державне свято Польщі, офіційний вихідний день.",
            "Święto państwowe Polski, oficjalny dzień wolny.",
            "A Polish national holiday and an official day off.",
        ),
        "grade1Note": L("Вихідний день.", "Dzień wolny.", "A day off."),
        "location": L("Польща", "Polska", "Poland"),
        "badgeShort": L("🛑 Конституція 3 Травня", "🛑 Święto 3 Maja", "🛑 3 May Constitution"),
        "dateFormatted": loc_date("2027-05-03"),
    },
    "ev-may-matura-off": {
        "title": L(
            "Вільні від уроків дні для 1-х класів (Період Матури 4-х кл.) 🛑🎓",
            "Dni wolne od zajęć dydaktycznych (Pisemne egzaminy maturalne) 🛑🎓",
            "Days off for Year 1 (Year 4 Matura written exams) 🛑🎓",
        ),
        "categoryName": L("Вільні дні", "Dni wolne", "Days off"),
        "time": L("4 дні", "4 dni", "4 days"),
        "description": L(
            "У ці дні у приміщеннях ліцею проходять обов'язкові письмові іспити на атестат зрілості (Матура) для випускників 4-х класів. Згідно із розпорядженням дирекції, для учнів 1-х, 2-х та 3-х класів навчальні заняття скасовані!",
            "W tych dniach w budynku liceum odbywają się obowiązkowe pisemne egzaminy maturalne klas 4. Zgodnie z decyzją dyrekcji zajęcia dla klas 1., 2. i 3. są odwołane!",
            "Compulsory written Matura exams for Year 4 take place in the lyceum building. By the headteacher’s decision, lessons for Years 1, 2 and 3 are cancelled!",
        ),
        "grade1Note": L(
            "ВЕЛИКИЙ БОНУС ДЛЯ 1-Х КЛАСІВ: 4 повних дні без занять (разом із 3 травня — 9 днів весняного відпочинку поспіль)!",
            "DUŻY BONUS DLA KLAS 1.: 4 pełne dni bez zajęć (wraz z 3 maja — 9 dni wiosennego odpoczynku z rzędu)!",
            "A BIG PLUS FOR YEAR 1: 4 full days without lessons (together with 3 May — 9 consecutive spring days off)!",
        ),
        "location": L("Ліцей зайнятий екзаменами", "Liceum zajęte egzaminami", "Lyceum occupied by exams"),
        "badgeShort": L("🛑 Вільний день (Матура)", "🛑 Dzień wolny (Matura)", "🛑 Day off (Matura)"),
        "dateFormatted": L(
            "04.05 – 07.05.2027 (Вівторок – П'ятниця)",
            "04.05 – 07.05.2027 (Wtorek – Piątek)",
            "04.05 – 07.05.2027 (Tuesday – Friday)",
        ),
    },
    "ev-may-27-corpus": {
        "title": L(
            "Свято Тіла і Крові Христових (Boże Ciało) 🌿🛑",
            "Uroczystość Najświętszego Ciała i Krwi Chrystusa (Boże Ciało) 🌿🛑",
            "Corpus Christi 🌿🛑",
        ),
        "categoryName": L("Державне свято", "Święto państwowe", "Public holiday"),
        "time": L("Весь день", "Cały dzień", "All day"),
        "description": L(
            "Державне та релігійне свято, офіційний вихідний день у всій Польщі.",
            "Święto państwowe i religijne, oficjalny dzień wolny w całej Polsce.",
            "A national and religious holiday, an official day off across Poland.",
        ),
        "grade1Note": L("Вихідний день.", "Dzień wolny.", "A day off."),
        "location": L("Польща", "Polska", "Poland"),
        "badgeShort": L("🛑 Боже Тіло", "🛑 Boże Ciało", "🛑 Corpus Christi"),
        "dateFormatted": loc_date("2027-05-27"),
    },
    "ev-may-28-longwknd": {
        "title": L(
            "Вільний від уроків день (Директорський довгий вікенд) 🛑☀️",
            "Dodatkowy dzień wolny od zajęć dydaktycznych 🛑☀️",
            "Day off lessons (long weekend) 🛑☀️",
        ),
        "categoryName": L("Вільні дні", "Dni wolne", "Days off"),
        "time": L("Весь день", "Cały dzień", "All day"),
        "description": L(
            "Директорський вихідний день між Божим Тілом та вихідними. Утворюється 4-денний вікенд (27–30 травня).",
            "Dyrektorski dzień wolny między Bożym Ciałem a weekendem. Powstaje 4-dniowy weekend (27–30 maja).",
            "A headteacher’s day off between Corpus Christi and the weekend. A 4-day weekend (27–30 May).",
        ),
        "grade1Note": L(
            "Вільний від уроків день для 1-х класів.",
            "Dzień wolny od lekcji dla klas 1.",
            "A lesson-free day for Year 1.",
        ),
        "location": L("Ліцей", "Liceum", "Lyceum"),
        "badgeShort": L("🛑 Вільний день", "🛑 Dzień wolny", "🛑 Day off"),
        "dateFormatted": loc_date("2027-05-28"),
    },
    "ev-jun-1-grade": {
        "title": L(
            "Попередження про річні оцінки в електронному щоденнику ⚠️",
            "Poinformowanie o przewidywanych ocenach rocznych ⚠️",
            "Predicted year grades in the e-register ⚠️",
        ),
        "categoryName": L("Оцінювання", "Ocenianie", "Assessment"),
        "time": L("Дедлайн", "Termin", "Deadline"),
        "description": L(
            "Вчителі вносять до системи Librus орієнтовні річні бали та загрози незадовільних оцінок з предметів і поведінки.",
            "Nauczyciele wpisują do Librusa przewidywane oceny roczne oraz zagrożenia ocenami niedostatecznymi z przedmiotów i zachowania.",
            "Teachers enter predicted year grades in Librus, including any risk of failing subject or behaviour grades.",
        ),
        "grade1Note": L(
            "Батькам необхідно перевірити прогнозовані річні оцінки в системі.",
            "Rodzice powinni sprawdzić przewidywane oceny roczne w systemie.",
            "Parents should check predicted year grades in the system.",
        ),
        "location": L("Librus", "Librus", "Librus"),
        "badgeShort": L("⚠️ Попередження / оцінки", "⚠️ Przewidywane oceny", "⚠️ Predicted grades"),
        "dateFormatted": loc_until("2027-06-01"),
    },
    "ev-jun-1-meeting": {
        "title": L(
            "Батьківські збори: прогнозовані річні оцінки 👥",
            "Zebranie z rodzicami: przewidywane oceny roczne 👥",
            "Parent meeting: predicted year grades 👥",
        ),
        "categoryName": L("Батьківські збори", "Zebranie z rodzicami", "Parent meeting"),
        "time": L("17:30", "17:30", "17:30"),
        "description": L(
            "Останні регулярні батьківські збори навчального року: обговорення річних результатів, процедури покращення балів.",
            "Ostatnie regularne zebranie z rodzicami w roku szkolnym: omówienie wyników rocznych i procedur poprawy ocen.",
            "The last regular parent meeting of the school year: year results and how marks can still be improved.",
        ),
        "grade1Note": L(
            "Фінальні батьківські збори першого навчального року в ліцеї.",
            "Ostatnie zebranie z rodzicami pierwszego roku w liceum.",
            "The final parent meeting of the first year at the lyceum.",
        ),
        "location": L("Кабінети ліцею", "Sale liceum", "Lyceum classrooms"),
        "badgeShort": L("👥 Збори 1–3 кл. (17:30)", "👥 Zebranie kl. 1–3 (17:30)", "👥 Years 1–3 meeting (17:30)"),
        "dateFormatted": loc_date("2027-06-01"),
    },
    "ev-jun-18-finalgrade": {
        "title": L(
            "Дедлайн остаточного виставлення річних оцінок 📝",
            "Ostateczne wystawienie ocen rocznych (klasy 1, 2, 3) 📝",
            "Deadline for final year grades 📝",
        ),
        "categoryName": L("Оцінювання", "Ocenianie", "Assessment"),
        "time": L("Дедлайн", "Termin", "Deadline"),
        "description": L(
            "Журнали оцінювання закриваються. Усі річні оцінки зафіксовані остаточно.",
            "Dzienniki ocen są zamykane. Wszystkie oceny roczne są wpisane ostatecznie.",
            "Gradebooks close. All year grades are locked as final.",
        ),
        "grade1Note": L("Фінальні річні оцінки 1-х класів.", "Ostateczne oceny roczne klas 1.", "Final Year 1 year grades."),
        "location": L("Librus", "Librus", "Librus"),
        "badgeShort": L("📝 Виставлення оцінок", "📝 Wystawienie ocen", "📝 Grades posted"),
        "dateFormatted": loc_until("2027-06-18"),
    },
    "ev-jun-22-council": {
        "title": L(
            "Класифікаційна педагогічна рада 1-х класів 📋",
            "Klasyfikacyjna rada pedagogiczna (klasy 1) 📋",
            "Year 1 classification staff council 📋",
        ),
        "categoryName": L("Педагогічна рада", "Rada pedagogiczna", "Staff council"),
        "time": L("15:00", "15:00", "15:00"),
        "description": L(
            "Офіційне затвердження переведення учнів 1-х класів до 2-го класу ліцею.",
            "Oficjalne zatwierdzenie promocji uczniów klas 1. do klasy 2. liceum.",
            "Official approval of Year 1 students progressing to Year 2.",
        ),
        "grade1Note": L(
            "Переведення першокласників до 2-го класу ліцею!",
            "Promocja uczniów klasy 1. do klasy 2. liceum!",
            "Year 1 students move up to Year 2!",
        ),
        "location": L("Учительська", "Pokój nauczycielski", "Staff room"),
        "badgeShort": L("📋 Педрада 1-х класів", "📋 Rada klas 1.", "📋 Year 1 council"),
        "dateFormatted": loc_date("2027-06-22"),
    },
    "ev-jun-24-council": {
        "title": L(
            "Підсумкова педагогічна рада ліцею за весь рік 🏛️",
            "Podsumowująca rada pedagogiczna 🏛️",
            "Year-end summary staff council 🏛️",
        ),
        "categoryName": L("Педагогічна рада", "Rada pedagogiczna", "Staff council"),
        "time": L("15:00", "15:00", "15:00"),
        "description": L(
            "Підбиття загальних підсумків 2026/2027 навчального року в ліцеї.",
            "Podsumowanie całego roku szkolnego 2026/2027 w liceum.",
            "A review of the whole 2026/2027 school year at the lyceum.",
        ),
        "grade1Note": L("Педагогічна рада вчителів ліцею.", "Rada pedagogiczna nauczycieli liceum.", "Lyceum teaching-staff council."),
        "location": L("Актова зала", "Sala gimnastyczna / aula", "Assembly hall"),
        "badgeShort": L("📋 Підсумкова педрада", "📋 Rada podsumowująca", "📋 Summary council"),
        "dateFormatted": loc_date("2027-06-24"),
    },
    "ev-jun-25-triumph": {
        "title": L(
            "Урочисте завершення навчального року для 1-х класів! 🎉🏆",
            "Uroczyste zakończenie roku szkolnego 2026/2027 🎉🏆",
            "Ceremonial end of the school year for Year 1! 🎉🏆",
        ),
        "categoryName": L("Закінчення року", "Zakończenie roku", "End of year"),
        "time": L("10:00", "10:00", "10:00"),
        "description": L(
            "Урочисте вручення свідоцтв, нагородження відмінників та активістів, святкова лінійка та перехід до 2-го класу ліцею!",
            "Uroczyste wręczenie świadectw, nagrody dla wyróżnionych i aktywnych uczniów, święto szkolne i przejście do klasy 2.!",
            "Certificates are presented, outstanding and active students are honoured, there is a festive assembly, and students move up to Year 2!",
        ),
        "grade1Note": L(
            "Грандіозний фінал першого навчального року в ліцеї! Вітаємо першокласників із переходом у 2-й клас!",
            "Wielki finał pierwszego roku w liceum! Gratulacje z okazji promocji do klasy 2.!",
            "A grand finale to the first year at the lyceum! Congratulations to Year 1 on moving up to Year 2!",
        ),
        "location": L("LXXVIII LO w Warszawie", "LXXVIII LO w Warszawie", "LXXVIII LO in Warsaw"),
        "badgeShort": L("🎉 Закінчення року!", "🎉 Zakończenie roku!", "🎉 End of year!"),
        "dateFormatted": loc_date("2027-06-25"),
    },
    "ev-jun-26-vacation": {
        "title": L(
            "Літні канікули (Ferie letnie) 🏖️🌊☀️",
            "Ferie letnie (Wakacje szkolne) 🏖️🌊☀️",
            "Summer holidays 🏖️🌊☀️",
        ),
        "categoryName": L("Канікули", "Ferie letnie", "School holidays"),
        "time": L("Понад 2 місяці", "Ponad 2 miesiące", "Over 2 months"),
        "description": L(
            "Заслужений літній відпочинок тривалістю понад два місяці.",
            "Zasłużony letni odpoczynek trwający ponad dwa miesiące.",
            "A well-earned summer rest lasting more than two months.",
        ),
        "grade1Note": L(
            "Повні літні канікули до 31 серпня 2027 року.",
            "Pełne wakacje letnie do 31 sierpnia 2027 r.",
            "Full summer holidays until 31 August 2027.",
        ),
        "location": L("Відпочинок", "Odpoczynek", "Holiday"),
        "badgeShort": L("🏖️ Літні канікули", "🏖️ Wakacje letnie", "🏖️ Summer holidays"),
        "dateFormatted": loc_range("2027-06-26", "2027-08-31"),
        "badgeByDate": {},
    },
    "ev-aug-15-army": {
        "title": L(
            "Свято Війська Польського та Успіння Богородиці 🇵🇱🛑",
            "Święto Wojska Polskiego i Wniebowzięcie NMP 🇵🇱🛑",
            "Polish Armed Forces Day and Assumption 🇵🇱🛑",
        ),
        "categoryName": L("Державне свято", "Święто państwowe", "Public holiday"),
        "time": L("Весь день", "Cały dzień", "All day"),
        "description": L(
            "Державне та релігійне свято Польщі.",
            "Święto państwowe i religijne Polski.",
            "A Polish national and religious holiday.",
        ),
        "grade1Note": L(
            "Державне свято в період канікул.",
            "Święto państwowe w czasie wakacji.",
            "A public holiday during the summer break.",
        ),
        "location": L("Польща", "Polska", "Poland"),
        "badgeShort": L("🛑 Свято Війська Польського", "🛑 Święto Wojska Polskiego", "🛑 Armed Forces Day"),
        "dateFormatted": loc_date("2027-08-15"),
    },
}

# Fix typo in ev-may-3 and ev-aug-15 if I introduced Ukrainian mixed in PL categoryName
PATCH["ev-may-3-const"]["time"] = L("Весь день", "Cały dzień", "All day")
PATCH["ev-aug-15-army"]["categoryName"] = L("Державне свято", "Święto państwowe", "Public holiday")

summer_badges = PATCH["ev-jun-26-vacation"]["badgeByDate"]
summer_badges["2027-06-26"] = L("🏖️ Початок канікул!", "🏖️ Początek wakacji!", "🏖️ Summer starts!")
d = date(2027, 7, 1)
while d.month == 7:
    summer_badges[d.isoformat()] = L(
        "🏖️ Літні канікули (весь місяць)",
        "🏖️ Wakacje letnie (cały miesiąc)",
        "🏖️ Summer holidays (all month)",
    )
    d += timedelta(days=1)
summer_badges["2027-08-31"] = L("🏖️ Фінал літніх канікул", "🏖️ Koniec wakacji", "🏖️ End of summer holidays")


def transform_data() -> dict:
    text = (ROOT / "js" / "calendar-data.js").read_text(encoding="utf-8")
    m = re.search(r"window\.CALENDAR_DATA = (\{.*\});\s*$", text, re.S)
    data = json.loads(m.group(1))
    missing = [e["id"] for e in data["events"] if e["id"] not in PATCH]
    if missing:
        raise SystemExit(f"Missing translations: {missing}")

    for ev in data["events"]:
        p = PATCH[ev["id"]]
        ev["officialTitle"] = ev.pop("titlePl")
        for key, val in p.items():
            ev[key] = val

    for month in data["months"]:
        nom = MONTHS_NOM[month["month"]]
        gen = MONTHS_GEN[month["month"]]
        y = month["year"]
        month["name"] = L(f"{nom['uk']} {y}", f"{nom['pl']} {y}", f"{nom['en']} {y}")
        month["nameGenitive"] = L(f"{gen['uk']} {y}", f"{gen['pl']} {y}", f"{gen['en']} {y}")
        month["navLabel"] = nom

    data["school"]["langStorageKey"] = "lyceum_78_lang"
    return data


NAV = [
    ("sep-2026", "🍁", "nav.sep"),
    ("oct-2026", "🍂", "nav.oct"),
    ("nov-2026", "🕯️", "nav.nov"),
    ("dec-2026", "🎄", "nav.dec"),
    ("jan-2027", "❄️", "nav.jan"),
    ("feb-2027", "⛷️", "nav.feb"),
    ("mar-2027", "🌱", "nav.mar"),
    ("apr-2027", "🌸", "nav.apr"),
    ("may-2027", "☀️", "nav.may"),
    ("jun-2027", "🎉", "nav.jun"),
    ("jul-2027", "🏖️", "nav.jul"),
    ("aug-2027", "🌻", "nav.aug"),
]


def patch_html() -> None:
    path = ROOT / "index.html"
    html = path.read_text(encoding="utf-8")

    html = html.replace(
        "<title>Шкільний Календар 2026/2027 — 1-й Клас — Art Deco Grand Illustrated</title>",
        '<title data-i18n="docTitle">Шкільний календар 2026/2027 — 1-й клас — Art Deco</title>',
    )
    html = html.replace(
        '<div class="hero-pretitle">✨ Офіційний шкільний календар 2026 / 2027 ✨</div>',
        '<div class="hero-pretitle" data-i18n="hero.pretitle">✨ Офіційний шкільний календар 2026 / 2027 ✨</div>',
    )
    html = html.replace(
        '<h1 class="hero-title">1-й Клас • Ліцей</h1>',
        '<h1 class="hero-title" data-i18n="hero.title">1-й Клас • Ліцей</h1>',
    )
    html = html.replace(
        """        <div class="hero-meta">
            <span>📅 I півріччя: 01.09.2026 – 29.01.2027</span>
            <span>📅 II півріччя: 01.02.2027 – 25.06.2027</span>
            <span>🔔 Завершення року: 25.06.2027</span>
        </div>""",
        """        <div class="hero-meta">
            <span data-i18n="hero.sem1">📅 I півріччя: 01.09.2026 – 29.01.2027</span>
            <span data-i18n="hero.sem2">📅 II півріччя: 01.02.2027 – 25.06.2027</span>
            <span data-i18n="hero.end">🔔 Завершення року: 25.06.2027</span>
        </div>""",
    )
    html = html.replace(
        'placeholder="Швидкий пошук (збори, канікули, виїзди, матура, оцінки)..."',
        'placeholder="Швидкий пошук (збори, канікули, виїзди, матура, оцінки)..." data-i18n-placeholder="search.placeholder"',
    )
    html = html.replace(
        """                <div class="mode-toggle-group">
                    <button type="button" class="mode-btn active" id="modeAllBtn" onclick="setViewMode('all')">📜 Всі місяці</button>
                    <button type="button" class="mode-btn" id="modeFocusBtn" onclick="setViewMode('focus')">🎯 Помісячно</button>
                </div>""",
        """                <div class="mode-toggle-group">
                    <button type="button" class="mode-btn active" id="modeAllBtn" onclick="setViewMode('all')" data-i18n="mode.all">📜 Всі місяці</button>
                    <button type="button" class="mode-btn" id="modeFocusBtn" onclick="setViewMode('focus')" data-i18n="mode.focus">🎯 Помісячно</button>
                </div>
                <div class="lang-switch" role="group" aria-label="Language">
                    <button type="button" class="lang-btn active" data-lang="uk" onclick="setLanguage('uk')" title="Українська">UK</button>
                    <button type="button" class="lang-btn" data-lang="pl" onclick="setLanguage('pl')" title="Polski">PL</button>
                    <button type="button" class="lang-btn" data-lang="en" onclick="setLanguage('en')" title="English">EN</button>
                </div>""",
    )
    html = html.replace(
        'onclick="downloadAllEventsICS()">📅 Завантажити .ICS (Google/Apple)</button>',
        'onclick="downloadAllEventsICS()" data-i18n="action.ics">📅 Завантажити .ICS (Google/Apple)</button>',
    )
    html = html.replace(
        '>📄 PDF (13 стор.)</a>',
        ' data-i18n="action.pdf">📄 PDF (13 стор.)</a>',
    )
    html = html.replace(
        'onclick="window.print()">🖨️ Друк</button>',
        'onclick="window.print()" data-i18n="action.print">🖨️ Друк</button>',
    )
    html = html.replace(
        '<span class="filter-label">Категорії подій:</span>',
        '<span class="filter-label" data-i18n="filter.label">Категорії подій:</span>',
    )
    html = html.replace('onclick="filterByCategory(\'all\')">✨ Всі події</button>',
                        'onclick="filterByCategory(\'all\')" data-i18n="filter.all">✨ Всі події</button>')
    html = html.replace('onclick="filterByCategory(\'vacation\')">🏖️ Канікули та свята</button>',
                        'onclick="filterByCategory(\'vacation\')" data-i18n="filter.vacation">🏖️ Канікули та свята</button>')
    html = html.replace('onclick="filterByCategory(\'meeting\')">👥 Батьківські збори</button>',
                        'onclick="filterByCategory(\'meeting\')" data-i18n="filter.meeting">👥 Батьківські збори</button>')
    html = html.replace('onclick="filterByCategory(\'trip\')">🎒 Виїзди та інтеграція</button>',
                        'onclick="filterByCategory(\'trip\')" data-i18n="filter.trip">🎒 Виїзди та інтеграція</button>')
    html = html.replace('onclick="filterByCategory(\'grade\')">📝 Оцінки та педради</button>',
                        'onclick="filterByCategory(\'grade\')" data-i18n="filter.grade">📝 Оцінки та педради</button>')
    html = html.replace(
        'onclick="prevMonthFocus()">◀ Попередній місяць</button>',
        'onclick="prevMonthFocus()" data-i18n="focus.prev">◀ Попередній місяць</button>',
    )
    html = html.replace(
        'onclick="nextMonthFocus()">Наступний місяць ▶</button>',
        'onclick="nextMonthFocus()" data-i18n="focus.next">Наступний місяць ▶</button>',
    )

    nav_buttons = [
        '        <button type="button" class="nav-btn active" onclick="showAllMonths(this)" data-i18n="nav.all">🌟 Всі місяці</button>'
    ]
    for mid, emoji, key in NAV:
        nav_buttons.append(
            f"        <button type=\"button\" class=\"nav-btn\" data-month-id=\"{mid}\" onclick=\"scrollToMonth('{mid}', this)\">{emoji} <span data-i18n=\"{key}\"></span></button>"
        )
    nav_buttons.append(
        '        <button type="button" class="nav-btn btn-print" onclick="window.print()" data-i18n="nav.print">🖨️ Друк / PDF</button>'
    )
    html = re.sub(
        r'<nav class="nav-container" data-glean-id="nav-bar">.*?</nav>',
        '<nav class="nav-container" data-glean-id="nav-bar">\n' + "\n".join(nav_buttons) + "\n    </nav>",
        html,
        count=1,
        flags=re.S,
    )

    weekday_src = (
        '<th><span class="full-day">Понеділок</span><span class="short-day">Пн</span></th>'
        '<th><span class="full-day">Вівторок</span><span class="short-day">Вт</span></th>'
        '<th><span class="full-day">Середа</span><span class="short-day">Ср</span></th>'
        '<th><span class="full-day">Четвер</span><span class="short-day">Чт</span></th>'
        '<th><span class="full-day">П\'ятниця</span><span class="short-day">Пт</span></th>'
        '<th><span class="full-day">Субота</span><span class="short-day">Сб</span></th>'
        '<th><span class="full-day">Неділя</span><span class="short-day">Нд</span></th>'
    )
    weekday_row = "".join(
        f'<th><span class="full-day" data-i18n="wd.full.{i}"></span>'
        f'<span class="short-day" data-i18n="wd.short.{i}"></span></th>'
        for i in range(7)
    )
    if weekday_src not in html:
        raise SystemExit("weekday header row not found")
    html = html.replace(weekday_src, weekday_row)

    html = html.replace(
        '<h3>Розклад подій та зауваги місяця</h3>',
        '<h3 data-i18n="agenda.header">Розклад подій та зауваги місяця</h3>',
    )

    seasons = {
        "season-img-autumn": ("autumn", "Золота осінь в стилі Арт-деко", "Сезон відкриття знань, подорожей та шкільної дружби"),
        "season-img-winter": ("winter", "Зимова казка та різдвяні свята в стилі Арт-деко", "Сезон святкового затишку, відпочинку та піврічних підсумків"),
        "season-img-spring": ("spring", "Весняне пробудження та нові горизонти в стилі Арт-деко", "Сезон натхнення, екскурсій та великодніх свят"),
        "season-img-summer": ("summer", "Розкішне літо та тріумфальні канікули в стилі Арт-деко", "Сезон заслуженого відпочинку, сонця та подорожей"),
    }
    for glean, (sid, title, cap) in seasons.items():
        html = html.replace(
            f'<div class="season-banner-card" data-glean-id="{glean}">',
            f'<div class="season-banner-card" data-glean-id="{glean}" data-season="{sid}">',
        )
        html = html.replace(
            f'<h3 class="season-title">{title}</h3>',
            f'<h3 class="season-title" data-i18n="season.{sid}.title">{title}</h3>',
        )
        html = html.replace(
            f'<p class="season-caption">{cap}</p>',
            f'<p class="season-caption" data-i18n="season.{sid}.caption">{cap}</p>',
        )
        html = html.replace(f'alt="{title}"', f'alt="{title}" data-i18n-alt="season.{sid}.title"')

    for mid, _, _ in NAV:
        html = re.sub(
            rf'(<section class="month-page" id="{mid}"[\s\S]*?<div class="month-quote")(>)([^<]+)(</div>)',
            rf'\1 data-i18n="quote.{mid}"\2\3\4',
            html,
            count=1,
        )

    html = html.replace(
        "❖ LXXVIII Liceum Ogólnokształcące w Warszawie • 2026/2027 • Всі події виключно для 1-х класів або загальношкільні ❖",
        '<span data-i18n="footer">❖ LXXVIII Liceum Ogólnokształcące w Warszawie • 2026/2027 • Всі події виключно для 1-х класів або загальношкільні ❖</span>',
    )
    html = html.replace(
        '<div class="modal-kicker">Шкільний календар 2026/2027 • 1-й клас</div>',
        '<div class="modal-kicker" data-i18n="modal.kicker">Шкільний календар 2026/2027 • 1-й клас</div>',
    )
    html = html.replace(
        '<div class="modal-date-title" id="modalDateTitle">Дата події</div>',
        '<div class="modal-date-title" id="modalDateTitle" data-i18n="modal.dateFallback">Дата події</div>',
    )
    html = html.replace(
        'onclick="closeEventModal()">✕ Закрити</button>',
        'onclick="closeEventModal()" data-i18n="modal.close">✕ Закрити</button>',
    )
    html = html.replace(
        '<div class="modal-notes-title">📝 Особиста замітка батьків для цього дня:</div>',
        '<div class="modal-notes-title" data-i18n="modal.notesTitle">📝 Особиста замітка батьків для цього дня:</div>',
    )
    html = html.replace(
        'placeholder="Наприклад: здати підручники, купити квитки, записатися на консультацію..."',
        'placeholder="Наприклад: здати підручники, купити квитки, записатися на консультацію..." data-i18n-placeholder="modal.notesPlaceholder"',
    )
    html = html.replace(
        'onclick="saveCurrentDayNote()">💾 Зберегти замітку</button>',
        'onclick="saveCurrentDayNote()" data-i18n="modal.saveNote">💾 Зберегти замітку</button>',
    )
    html = html.replace(
        'class="note-saved-status">✓ Збережено в браузері!</span>',
        'class="note-saved-status" data-i18n="modal.saved">✓ Збережено в браузері!</span>',
    )
    html = html.replace(
        '<script src="js/calendar-data.js"></script>\n    <script src="js/calendar.js"></script>',
        '<script src="js/calendar-data.js"></script>\n    <script src="js/i18n.js"></script>\n    <script src="js/calendar.js"></script>',
    )

    path.write_text(html, encoding="utf-8")


def main() -> None:
    data = transform_data()
    out = "window.CALENDAR_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    (ROOT / "js" / "calendar-data.js").write_text(out, encoding="utf-8")
    patch_html()
    print("updated calendar-data.js and index.html")


if __name__ == "__main__":
    main()
