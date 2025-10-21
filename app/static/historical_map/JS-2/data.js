// 55 исторических событий Беларуси
const historicalEvents = [
    // Основания городов (12 событий)
    {
        id: 1,
        title: "Основание Полоцка",
        date: "862 г.",
        year: 862,
        category: "основания",
        coordinates: [55.4856, 28.7686],
        description: "Первое упоминание Полоцка в летописях как центра Полоцкого княжества",
        importance: "high"
    },
    {
        id: 2,
        title: "Основание Турова",
        date: "980 г.",
        year: 980,
        category: "основания",
        coordinates: [52.0678, 27.7333],
        description: "Первое летописное упоминание Турова как важного политического центра",
        importance: "medium"
    },
    {
        id: 3,
        title: "Основание Витебска",
        date: "974 г.",
        year: 974,
        category: "основания",
        coordinates: [55.1833, 30.1667],
        description: "Легендарная дата основания Витебска княгиней Ольгой",
        importance: "medium"
    },
    {
        id: 4,
        title: "Основание Гродно",
        date: "1128 г.",
        year: 1128,
        category: "основания",
        coordinates: [53.6667, 23.8333],
        description: "Первое летописное упоминание Гродно как важного оборонительного пункта",
        importance: "medium"
    },
    {
        id: 5,
        title: "Основание Бреста",
        date: "1019 г.",
        year: 1019,
        category: "основания",
        coordinates: [52.0833, 23.7],
        description: "Первое летописное упоминание Бреста",
        importance: "medium"
    },
    {
        id: 6,
        title: "Основание Могилёва",
        date: "1267 г.",
        year: 1267,
        category: "основания",
        coordinates: [53.9167, 30.35],
        description: "Первое упоминание Могилёва в летописных источниках",
        importance: "medium"
    },
    {
        id: 7,
        title: "Основание Гомеля",
        date: "1142 г.",
        year: 1142,
        category: "основания",
        coordinates: [52.4417, 31.0],
        description: "Первое упоминание Гомеля в Ипатьевской летописи",
        importance: "medium"
    },
    {
        id: 8,
        title: "Основание Новогрудка",
        date: "1044 г.",
        year: 1044,
        category: "основания",
        coordinates: [53.6, 25.8333],
        description: "Первое упоминание Новогрудка как древнего города",
        importance: "medium"
    },
    {
        id: 9,
        title: "Основание Пинска",
        date: "1097 г.",
        year: 1097,
        category: "основания",
        coordinates: [52.1167, 26.1],
        description: "Первое летописное упоминание Пинска",
        importance: "medium"
    },
    {
        id: 10,
        title: "Основание Лиды",
        date: "1323 г.",
        year: 1323,
        category: "основания",
        coordinates: [53.8833, 25.3],
        description: "Основание города Лида великим князем Гедимином",
        importance: "medium"
    },
    {
        id: 11,
        title: "Основание Барановичей",
        date: "1871 г.",
        year: 1871,
        category: "основания",
        coordinates: [53.1333, 26.0167],
        description: "Основание города в связи со строительством железной дороги",
        importance: "low"
    },
    {
        id: 12,
        title: "Основание Слуцка",
        date: "1116 г.",
        year: 1116,
        category: "основания",
        coordinates: [53.0167, 27.55],
        description: "Первое упоминание Слуцка в летописях",
        importance: "medium"
    },

    // Сражения (12 событий)
    {
        id: 13,
        title: "Грюнвальдская битва",
        date: "1410 г.",
        year: 1410,
        category: "сражения",
        coordinates: [53.4833, 20.1],
        description: "Решающее сражение Великой войны, в котором участвовали белорусские полки",
        importance: "high"
    },
    {
        id: 14,
        title: "Битва под Оршей",
        date: "1514 г.",
        year: 1514,
        category: "сражения",
        coordinates: [54.5, 30.4167],
        description: "Крупное сражение в ходе русско-литовской войны",
        importance: "high"
    },
    {
        id: 15,
        title: "Оборона Брестской крепости",
        date: "1941 г.",
        year: 1941,
        category: "сражения",
        coordinates: [52.0833, 23.65],
        description: "Героическая оборона Брестской крепости в первые дни Великой Отечественной войны",
        importance: "high"
    },
    {
        id: 16,
        title: "Операция Багратион",
        date: "1944 г.",
        year: 1944,
        category: "сражения",
        coordinates: [53.9, 27.5],
        description: "Крупная наступательная операция по освобождению Беларуси от немецко-фашистских захватчиков",
        importance: "high"
    },
    {
        id: 17,
        title: "Битва под Кирхгольмом",
        date: "1605 г.",
        year: 1605,
        category: "сражения",
        coordinates: [56.65, 21.3833],
        description: "Победа войск Речи Посполитой над шведами",
        importance: "medium"
    },
    {
        id: 18,
        title: "Битва под Миром",
        date: "1812 г.",
        year: 1812,
        category: "сражения",
        coordinates: [53.45, 26.4667],
        description: "Сражение во время Отечественной войны 1812 года",
        importance: "medium"
    },
    {
        id: 19,
        title: "Битва под Березиной",
        date: "1812 г.",
        year: 1812,
        category: "сражения",
        coordinates: [53.8333, 29.5],
        description: "Переправа наполеоновской армии через Березину",
        importance: "medium"
    },
    {
        id: 20,
        title: "Сражение под Кобрином",
        date: "1812 г.",
        year: 1812,
        category: "сражения",
        coordinates: [52.2167, 24.3667],
        description: "Первая крупная победа русской армии в Отечественной войне 1812 года",
        importance: "medium"
    },
    {
        id: 21,
        title: "Битва под Лоевом",
        date: "1649 г.",
        year: 1649,
        category: "сражения",
        coordinates: [51.9333, 30.8],
        description: "Сражение во время восстания Хмельницкого",
        importance: "medium"
    },
    {
        id: 22,
        title: "Оборона Могилёва",
        date: "1941 г.",
        year: 1941,
        category: "сражения",
        coordinates: [53.9167, 30.35],
        description: "Героическая оборона Могилёва в годы Великой Отечественной войны",
        importance: "high"
    },
    {
        id: 23,
        title: "Битва под Сморгонью",
        date: "1915-1917 гг.",
        year: 1915,
        category: "сражения",
        coordinates: [54.4833, 26.4],
        description: "Длительные позиционные бои во время Первой мировой войны",
        importance: "medium"
    },
    {
        id: 24,
        title: "Минская операция",
        date: "1920 г.",
        year: 1920,
        category: "сражения",
        coordinates: [53.9, 27.5],
        description: "Наступательная операция во время советско-польской войны",
        importance: "medium"
    },

    // Политика (12 событий)
    {
        id: 25,
        title: "Принятие Статута ВКЛ",
        date: "1529 г.",
        year: 1529,
        category: "политика",
        coordinates: [53.9, 27.5],
        description: "Первый Статут Великого княжества Литовского - один из первых в Европе сводов законов",
        importance: "high"
    },
    {
        id: 26,
        title: "Люблинская уния",
        date: "1569 г.",
        year: 1569,
        category: "политика",
        coordinates: [51.25, 22.5667],
        description: "Создание Речи Посполитой - объединение Польского королевства и ВКЛ",
        importance: "high"
    },
    {
        id: 27,
        title: "Кревская уния",
        date: "1385 г.",
        year: 1385,
        category: "политика",
        coordinates: [54.3167, 26.2833],
        description: "Династический союз между Великим княжеством Литовским и Польшей",
        importance: "high"
    },
    {
        id: 28,
        title: "Образование БССР",
        date: "1919 г.",
        year: 1919,
        category: "политика",
        coordinates: [53.9, 27.5],
        description: "Провозглашение Белорусской Советской Социалистической Республики",
        importance: "high"
    },
    {
        id: 29,
        title: "Провозглашение независимости",
        date: "1991 г.",
        year: 1991,
        category: "политика",
        coordinates: [53.9, 27.5],
        description: "Провозглашение независимости Республики Беларусь",
        importance: "high"
    },
    {
        id: 30,
        title: "Принятие Конституции РБ",
        date: "1994 г.",
        year: 1994,
        category: "политика",
        coordinates: [53.9, 27.5],
        description: "Принятие первой Конституции независимой Беларуси",
        importance: "high"
    },
    {
        id: 31,
        title: "Создание БНР",
        date: "1918 г.",
        year: 1918,
        category: "политика",
        coordinates: [53.9, 27.5],
        description: "Провозглашение Белорусской Народной Республики",
        importance: "high"
    },
    {
        id: 32,
        title: "Виленская уния",
        date: "1499 г.",
        year: 1499,
        category: "политика",
        coordinates: [54.6872, 25.28],
        description: "Обновление унии между Великим княжеством Литовским и Польшей",
        importance: "medium"
    },
    {
        id: 33,
        title: "Городельская уния",
        date: "1413 г.",
        year: 1413,
        category: "политика",
        coordinates: [53.6667, 23.8333],
        description: "Договор между Великим княжеством Литовским и Польским королевством",
        importance: "medium"
    },
    {
        id: 34,
        title: "Разделы Речи Посполитой",
        date: "1772-1795 гг.",
        year: 1772,
        category: "политика",
        coordinates: [53.9, 27.5],
        description: "Три раздела Речи Посполитой между Россией, Пруссией и Австрией",
        importance: "high"
    },
    {
        id: 35,
        title: "Образование ССРБ",
        date: "1919 г.",
        year: 1919,
        category: "политика",
        coordinates: [53.9, 27.5],
        description: "Создание Социалистической Советской Республики Белоруссии",
        importance: "medium"
    },
    {
        id: 36,
        title: "Вхождение в СССР",
        date: "1922 г.",
        year: 1922,
        category: "политика",
        coordinates: [53.9, 27.5],
        description: "БССР вошла в состав Советского Союза",
        importance: "high"
    },

    // Культура (11 событий)
    {
        id: 37,
        title: "Создание БГУ",
        date: "1921 г.",
        year: 1921,
        category: "культура",
        coordinates: [53.9, 27.5],
        description: "Основание Белорусского государственного университета",
        importance: "high"
    },
    {
        id: 38,
        title: "Создание Национальной библиотеки",
        date: "1922 г.",
        year: 1922,
        category: "культура",
        coordinates: [53.9, 27.5],
        description: "Основание главной библиотеки Беларуси",
        importance: "medium"
    },
    {
        id: 39,
        title: "Создание Академии наук",
        date: "1929 г.",
        year: 1929,
        category: "культура",
        coordinates: [53.9, 27.5],
        description: "Основание Академии наук БССР",
        importance: "high"
    },
    {
        id: 40,
        title: "Создание театра им. Янки Купалы",
        date: "1920 г.",
        year: 1920,
        category: "культура",
        coordinates: [53.9, 27.5],
        description: "Основание Национального академического театра им. Янки Купалы",
        importance: "medium"
    },
    {
        id: 41,
        title: "Первая белорусская книга",
        date: "1517 г.",
        year: 1517,
        category: "культура",
        coordinates: [52.0833, 23.7],
        description: "Франциск Скорина издал в Праге первую белорусскую книгу",
        importance: "high"
    },
    {
        id: 42,
        title: "Основание Виленского университета",
        date: "1579 г.",
        year: 1579,
        category: "культура",
        coordinates: [54.6872, 25.28],
        description: "Создание одного из старейших университетов Восточной Европы",
        importance: "high"
    },
    {
        id: 43,
        title: "Создание БГТУ",
        date: "1930 г.",
        year: 1930,
        category: "культура",
        coordinates: [53.9, 27.5],
        description: "Основание Белорусского государственного технологического университета",
        importance: "medium"
    },
    {
        id: 44,
        title: "Открытие Большого театра",
        date: "1933 г.",
        year: 1933,
        category: "культура",
        coordinates: [53.9, 27.5],
        description: "Основание Национального академического Большого театра оперы и балета",
        importance: "medium"
    },
    {
        id: 45,
        title: "Создание Союза писателей",
        date: "1934 г.",
        year: 1934,
        category: "культура",
        coordinates: [53.9, 27.5],
        description: "Основание Союза писателей Беларуси",
        importance: "medium"
    },
    {
        id: 46,
        title: "Открытие Минского метро",
        date: "1984 г.",
        year: 1984,
        description: "Открытие первого участка Минского метрополитена",
        category: "культура",
        coordinates: [53.9, 27.5],
        importance: "medium"
    },
    {
        id: 47,
        title: "Создание БГПУ",
        date: "1914 г.",
        year: 1914,
        category: "культура",
        coordinates: [53.9, 27.5],
        description: "Основание Белорусского государственного педагогического университета",
        importance: "medium"
    },

    // Религия (8 событий)
    {
        id: 48,
        title: "Берестейская уния",
        date: "1596 г.",
        year: 1596,
        category: "религия",
        coordinates: [52.0833, 23.7],
        description: "Создание униатской церкви, объединившей православные и католические традиции",
        importance: "high"
    },
    {
        id: 49,
        title: "Создание Минской епархии",
        date: "1793 г.",
        year: 1793,
        category: "религия",
        coordinates: [53.9, 27.5],
        description: "Учреждение Минской православной епархии",
        importance: "medium"
    },
    {
        id: 50,
        title: "Постройка Софийского собора",
        date: "1030 г.",
        year: 1030,
        category: "религия",
        coordinates: [55.4856, 28.7686],
        description: "Строительство Софийского собора в Полоцке",
        importance: "high"
    },
    {
        id: 51,
        title: "Основание Жировичского монастыря",
        date: "1470 г.",
        year: 1470,
        category: "религия",
        coordinates: [53.0167, 25.35],
        description: "Создание одного из главных православных монастырей Беларуси",
        importance: "medium"
    },
    {
        id: 52,
        title: "Строительство костёла в Гервятах",
        date: "1903 г.",
        year: 1903,
        category: "религия",
        coordinates: [54.6833, 26.1333],
        description: "Возведение одного из красивейших костёлов Беларуси",
        importance: "medium"
    },
    {
        id: 53,
        title: "Восстановление православия",
        date: "1839 г.",
        year: 1839,
        description: "Полоцкий собор и восстановление православия в Беларуси",
        category: "религия",
        coordinates: [55.4856, 28.7686],
        importance: "high"
    },
    {
        id: 54,
        title: "Создание католической архиепархии",
        date: "1991 г.",
        year: 1991,
        category: "религия",
        coordinates: [53.9, 27.5],
        description: "Учреждение Минско-Могилёвской архиепархии",
        importance: "medium"
    },
    {
        id: 55,
        title: "Визит Папы Римского",
        date: "2009 г.",
        year: 2009,
        category: "религия",
        coordinates: [53.9, 27.5],
        description: "Первый визит Папы Римского в Беларусь",
        importance: "medium"
    }
];

// Функция для получения цвета категории
function getCategoryColor(category) {
    const colorMap = {
        'основания': '#34495e',
        'религия': '#9b59b6',
        'сражения': '#e74c3c',
        'реформы': '#27ae60',
        'восстания': '#e67e22',
        'политика': '#2c3e50',
        'технологии': '#d35400',
        'культура': '#8e44ad'
    };
    return colorMap[category] || '#6c757d';
}