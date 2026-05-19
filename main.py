import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

import logging
import os
import asyncio
import random
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
from datetime import datetime, timedelta
from aiogram import F, types
from aiogram.enums import ParseMode
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

# Скорее всего, у вас было написано что-то вроде default="HTML" — это неверно.
# Правильный вариант:
bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # или ParseMode.MARKDOWN_V2
)

cooldowns = {
    'steal': {},
    'bite': {},
    'duel': {},
    'hunt': {},
}

active_hunts = {}

#настроцки 
ADMIN_ID = 8192576225
BOT_USERNAME = "@ECullen_bot"
GOD_IDS = [8192576225] 
GOD = {}
DAILY_BANK_LIMIT = 4 
#адреса офто (file_id)
PHOTO_IDS = {
    'МЕНЮ_БИЗНЕСОВ': 'ID_ИЗ_БОТА',
    'cafe': 'ID_ИЗ_БОТА',
    'factory': 'ID_ИЗ_БОТА',
    'mine': 'ID_ИЗ_БОТА',
    'проф': 'AgACAgIAAxkBAAI1EGoB8lUiqHM3alD9aj3m4qddtTFKAAJ_FGsbVkYRSP7RS3C7veO9AQADAgADeAADOwQ',
    'инфо': 'AgACAgIAAxkBAAI1EmoB8lvv5XrzzCJW45rOpJIYgECkAAKAFGsbVkYRSN6-Bczbj-GVAQADAgADeQADOwQ',
    'охота': 'AgACAgIAAxkBAAI1CmoB8kAroZORAnm-jSg4D4-CPzIvAAJ8FGsbVkYRSEMBBpNnboLJAQADAgADeAADOwQ',
    'украсть': 'AgACAgIAAxkBAAI1DGoB8k1TbpsAAcGID_PWaMuFi4q7UwACfRRrG1ZGEUhZhQwWBm8BrgEAAwIAA3gAAzsE',
    'укусить': 'AgACAgIAAxkBAAI1DmoB8lEfuCbdSN3yNHr2BnvtTsXCAAJ-FGsbVkYRSCxqr8UiUyuiAQADAgADeAADOwQ',
    'перелить': 'AgACAgIAAxkBAAI1CGoB8jpcxAQjkNK3iouB2W-1NHuhAAJ7FGsbVkYRSGwukXrgCOOeAQADAgADeAADOwQ'
}


# --- 🏢 НАСТРОЙКИ ЦЕН И ПРИБЫЛИ ---
# --- НАСТРОЙКИ БИЗНЕСОВ ---
# Цена, базовая прибыль в час, макс. работников
BIZ_CONFIG = {
    'cafe': {'name': '☕️ Кафе "Вампирский Вкус"', 'price': 30000, 'income': 200, 'max_workers': 5, 'worker_cost': 2500},
    'factory': {'name': '🏭 Завод Синтетической Крови', 'price': 200000, 'income': 800, 'max_workers': 20, 'worker_cost': 5000},
    'mine': {'name': '💎 Кровавые Рудники', 'price': 1000000, 'income': 8000, 'max_workers': 50, 'worker_cost': 16000},
        'coffin_shop': {'name': '⚰️ Салон Элитных Гробов','price': 10000000,'income': 16000,'max_workers': 150,'worker_cost': 50000
    }

}

# Прибыль от одного работника в час (% от базовой прибыли бизнеса)
WORKER_PROFIT_BOOST = 0.20 # +5% за каждого работника

STICKERS = [
    "CAACAgIAAxkBAAERHLtp64plpl8qrNMb9JhGIOXJvddslQAC1H4AAoD-0UiSAAFm9Q3mPaw7BA",
    "CAACAgIAAxkBAAERHLlp64phJfgY7EEliCBLtRAAARhl2RkAApB-AAIZRrBLwtjf_HE-0os7BA",
    "CAACAgIAAxkBAAERHLdp64peJ9Weno8yNI1vKGHR5-jwRgACjD0AAkNICEmP88pqC9uSYTsE", 
    "CAACAgIAAxkBAAERHLVp64pYQuhFahlu-cBSR28eMXqSgwACy38AAmju0EhzYqTM5aAGnDsE", 
    "CAACAgIAAxkBAAERHLNp64pW8BQyhWpP7l7Wc8WOW_28qAACO1QAAo3KIEiuMI5_-hPNhTsE"
] 
VOICE_MESSAGES = [
    "AwACAgIAAxkBAAO6aezimpMpJUcH8FH6r-Zuu4Fs2uIAAveZAAKVAmlL77DFRe2DZNo7BA", 
    "AwACAgIAAxkBAAO4aezii0os6TVUeLMknpV4aJfyFWoAAvWZAAKVAmlLpPyht6YNUrk7BA", 
    "AwACAgIAAxkBAAO2aeziWTOhZXx8R4KqAfT3uWcvniEAAvKZAAKVAmlLKiFYgXzTcPk7BA", 
    "AwACAgIAAyEFAATs5gYyAAJnwGns6jP5RmRibJ7pXLEwwK-Wq-NKAAKBnQACJPBpS0aEgGOuVYaJOwQ"
]

TRIGGERS = {
    "привет": ["Здарова, пузатый :)", "Окак, дарова", "Привет привет, чинпанзе [>:"],
    "как дела": ["Лучше тебя, в разы", "Пойдет.", "Тебе честно сказать или наебать"],
    "бот": ["Че те надо, стапёр", "Че хочешь?", "Сам ты бот.", "Кто меня звал, суки?"],
    "скучно": ["А мне весело", "Иди погуляй.", "Сейчас я вам тут устрою.."],
    "что делаешь": ["Трахаюсь с беллой на медовом месяце", "Общаюсь с вами"],
    "угу": ["За угу, ебут в углу, малышка"],
    "регина": ["Регина? Кто придумал это имя?"],
    "папк": ["Я искрене не понимаю людей, зачем хранить папу в файлах? Лично мы Кальяны, храним в гробу!"],
    "вилка": ["Ужас, свежой кровью завоняло, я сейчас не сдержусь(("],
    "кальян": ["слушаю тебя, пидор", "че те надо смертный"],
    "честно": ["Я очень устал, босс"],
    "зачем": ["Мы еще и должны отчитываться перед тобой!?"],
    "ты кто": ["Твой кошмар", "тот кто следит за этим цирком"], 
    "чат": ["Чат сдох", "это чат или кладбище?"],
    "спасибо": ["Не благодари, нищета 🤡"],
    "админ": ["Админ в тильте, не беспокоить, уроды"],
    "удачи": ["засунь свою удачу себе в жопу"],
    "пока": ["Давай, не теряйся, щегол, ты мне еще деньги должен"],
    "выеб": ["Леее ты кому это адресуешь, леее, щас укушу и кровь выпью из тебя!!!", "Только не мою Беллу"],
    "почему": ["Че те надо со своим почему, не лезь не в своё дело 😡"],
    "дроч": ["Кальян подрочил на вас и кончил в рот. Дроек всего пол миллиарда"],
    "ирис": ["Даже не прикасайся моей любовнице"],
    "а то что": ["А то, выебу тебя во все щели"],
    "что сделаешь": ["Тебя ебать не должно, писька"],
    "наеби": ["Я очень хорошо чувствую себя, босс", "Я прекрасен как никогда", "у меня с Беллой здоровый ребенок"],
    "не сдерживайся": ["Кальян,💢 | Кальян укусил(а) пидора", "Ну.. Раз так настаиваешь то *укусил*, *выпил сладкую кровь с нищеты*"],
    "где белл": ["В моём холодном сердце"],
    "кто ты": ["твой пахан"],
    "давай честно": ["Я устааллл боссссс"],
    "наебать": ["Я очень хорошо чувствую себя, босс", "Я прекрасен как никогда", "у меня с Беллой здоровый ребенок"],
    "схуяли": ["Че те надо со своим «схуяли», не лезь не в своё дело 😡"],
    "трахнуть": ["Леее ты кому это адресуешь, леее, щас укушу и кровь выпью из тебя!!!", "Только не мою Беллу"],
    "покеда": ["Ээ, куда пошел, сучка!!!! Ты мне еще отсос должен"],    
    "досвидос": ["Эу, пиписька! Не вздумай соверщить такую ошибку, покидая нас!"],
    "адьес": ["Мать, ты куда(((, не бросай нас, ты самая лучшая"],
    "виолета": ["Ужас, свежой кровью запахло, я сейчас не сдержусь, укшууу..."],
    "чем занят": ["Общаюсь с вами мои пупсы", "Балуюсь с джуджуликом"],
    "ахуел": ["Ты сучкк, как разговаривешь", "Ты блять как посмел на меня такие буквы повышать", "ты ща ахуел, писька вялая"],
    "здравствуй": ["Здарова, пузатый :)", "Окак, дарова", "Привет привет, чинпанзе [>:"],
    "дарова": ["Здарова, пузатый :)", "окак, дарова", "Привет привет, чинпанзе [>:"],
    "дароу": ["Здарова, пузатый :)", "Окак, дарова", "Привет привет, чинпанзе [>:"],
    "бич": ["Ай фак юур бич, мазер факер", "Ohhhh, bitch"],
    "хай": ["Мы че, типо англичане теперь?!"],
    "нахуй": ["Соси со своим «иди нахуй, блять, сука нахуй, пидор, блять!"],
    "окак": ["Ты типо кот нигер, и который говорит окак?"],
    "ничего": ["Тогдааааа, иди нахуй!"],
    "тебя хочу": ["Меня может хотеть только Белла"],
    "пошел отсюда": ["Ышшшш какой", "еще че хочешь, пошол сам отсюда"],
    "150+150": ["Я смотрю, ты любишь шуточки? Ну тогда... 17 целых 33 в кдварате = 17,33. Схавал?"],
    "800+400": ["ЛЯМММММ ДВЕСТИ, братаан"],
    "схавал": ["Какой же ты нищий", "пыр пыр нищета, чисто"],
    "пидор": ["Соси смертный", "обоссать бы тебя еще"],
    "братан": ["Леее, эшекреее","Еееее баранн", "Дададададада"],
    "выпей": ["Выпил всю кровь из смертной(го)"],
    "давай": ["убил и выпил всю кровь, наслождениееее.."],
    "даваи": ["убил и выпил всю кровь, наслождениееее.."],
    "здарова": ["Здарова, пузатый :)", "окак, дарова", "Привет привет, чинпанзе [>:"],
        "привет": ["Приветствую в нашей обители!", "Рад видеть тебя, путник ночи."],
    "здравствуй": ["Моё почтение, как твои дела?", "Здравствуй! Луна сегодня благосклонна."],
    "ку": ["Привет! Как охота?", "Здравствуй, присаживайся у огня."],
    "хай": ["Салют! Что нового в мире теней?", "Хай! Рад, что ты заглянул."],
    "доброй ночи": ["И тебе мирного сна в склепе.", "Пусть тени оберегают твой покой."],
    "как дела": ["Всё идет своим чередом, вечность не терпит суеты.", "Благодарю, мои дела в порядке. А твои?"],
    "кто ты": ["Я твой верный проводник в этом мрачном мире.", "Лишь тень, помогающая тебе освоиться."],
    "кровь": ["Кровь — это жизнь. Но помни о благородстве.", "Аромат благородной крови всегда кружит голову."],
    "луна": ["Она сегодня особенно прекрасна, не находишь?", "Свет луны указывает нам верный путь."],
    "тьма": ["Тьма — наш дом, здесь мы по-настоящему свободны.", "В тени скрыты величайшие тайны."],
    "замок": ["Стены этого замка помнят еще первых королей.", "Здесь ты в безопасности, пока горит свеча."],
    "склеп": ["Идеальное место для глубоких раздумий.", "Тишина склепа лечит душу."],
    "солнце": ["Оно опасно для нас, но красиво издалека.", "Лучше остаться в тени, пока оно не зайдет."],
    "серебро": ["Будь осторожен с этим металлом, он коварен.", "Красиво блестит, но обжигает плоть."],
    "охота": ["Удачной охоты! Пусть клыки будут остры.", "Сегодня ночь обещает быть богатой на добычу."],
    "дуэль": ["Честь превыше всего. Да победит сильнейший!", "Сталь рассудит ваш спор лучше любых слов."],
    "бой": ["Битва покажет, кто достоин звания мастера.", "В бою закаляется характер вампира."],
    "помощь": ["Я всегда здесь, чтобы подсказать дорогу.", "Нужен совет? Я внимательно слушаю."],
    "спасибо": ["Всегда рад помочь члену нашей семьи.", "Твоя благодарность — лучшая награда."],
    "благодарю": ["Вежливость украшает даже самого древнего из нас.", "Не стоит, мы ведь союзники."],
    "пожалуйста": ["К твоим услугам в любое время ночи.", "Обращайся, когда возникнет нужда."],
    "удачи": ["Пусть фортуна улыбнется тебе в тени.", "Иди с миром, и пусть путь будет легким."],
    "согласен": ["Приятно видеть, что наши мысли сходятся.", "Мудрое решение, я поддержу тебя."],
    "да": ["Бесспорно. Пусть будет так.", "Я тоже так считаю."],
    "нет": ["Твое право. Отказ — тоже выбор.", "Я уважаю твое мнение, пусть будет по-твоему."],
    "прости": ["Обиды — это прах. Забудь о них.", "Всё в порядке, мы все совершаем ошибки."],
    "извини": ["Ничего страшного. Важно, что мы понимаем друг друга.", "Я не держу зла, всё хорошо."],
    "свадьба": ["Прекрасный союз под взором вечности.", "Пусть ваша общая кровь будет крепче стали."],
    "туда": ["Иногда нужно отпустить прошлое, чтобы жить вечно.", "Разлука — это лишь новое начало."],
    "клан": ["Семья — это то, ради чего стоит сражаться.", "В единстве клана наша истинная мощь."],
    "админ": ["Высшие силы всегда на страже твоего спокойствия.", "Патриарх слышит твой зов."],
    "бог": ["Его воля закон в этом чате.", "Приветствуй того, кто сотворил этот мир."],
    "правила": ["Порядок держит хаос на расстоянии.", "Соблюдай кодекс, и будешь в почете."],
    "бан": ["Тень поглотила нарушителя.", "Надеюсь, это был лишь сон, а не реальность."],
    "кик": ["Кто-то покинул нас, не выдержав холода.", "Двери закрылись за тем, кто не чтит закон."],
    "музыка": ["Мелодия ночи звучит в каждом вздохе.", "Слышишь, как поет ветер в башнях?"],
    "время": ["Для нас время — лишь песок между пальцев.", "Наслаждайся моментом, ведь мы бессмертны."],
    "страх": ["Страх — это лишь топливо для твоей силы.", "Не бойся тени, стань её частью."],
    "радость": ["Редкое чувство в наших краях, береги его.", "Твоя улыбка освещает этот зал."],
    "верность": ["Самая дорогая валюта в мире вампиров.", "Верность клану — залог выживания."],
    "предательство": ["Горький вкус, который не забывается.", "Тень никогда не простит измену."],
    "меч": ["Верный спутник в любом путешествии.", "Пусть твой клинок не знает промаха."],
    "кольцо": ["Символ власти или вечной любви.", "Магия камня защитит тебя в пути."],
    "плащ": ["Он скроет тебя от любопытных глаз.", "Шелк и тьма — лучшая одежда."],
    "вино": ["Красное, как сама жизнь. Угощайся.", "В этом кубке скрыта капля мудрости."],
    "книга": ["Знания — это сила, которую нельзя отобрать.", "Древние свитки хранят ответы на все вопросы."],
    "лес": ["Деревья шепчут о тех, кто проходил здесь до нас.", "В чаще леса легко спрятаться от дневного света."],
    "пещера": ["Глубины земли хранят вечный покой.", "Там, где нет света, рождается истина."],
    "звезды": ["Они — глаза тех, кто ушел в вечность.", "Каждая звезда — это чья-то надежда."],
    "туман": ["Он окутывает мир, скрывая правду.", "В тумане мы становимся невидимыми."],
    "огонь": ["Маленький костер согреет душу, но не плоть.", "Огонь красив, но держись от него подальше."],
    "свеча": ["Её свет дрожит, как человеческая жизнь.", "Маленький огонек в океане тьмы."],
    "сон": ["Пусть видения будут яркими и спокойными.", "Во сне мы путешествуем в иные миры."],
    "прощай": ["До новой встречи под покровом ночи.", "Тьма сохранит тебя до нашего свидания."],
    "пока": ["Увидимся, когда луна снова взойдет.", "Иди с миром, друг."],
    "увидимся": ["Я буду ждать тебя на этом же месте.", "Пути ночи всегда пересекаются."],
    "когда": ["Когда тени станут длиннее, мы встретимся.", "Всему свое время в этом мире."],
    "почему": ["На некоторые вопросы ответы приходят сами.", "Таков закон нашей общей судьбы."],
    "зачем": ["Чтобы сохранить величие нашей древней семьи.", "Ради будущего, которое мы строим вместе."],
    "правда": ["Истина горька, но она освобождает.", "Правда — это то, что остается, когда гаснет свет."],
    "ложь": ["Ложь — это яд, не дай ему отравить твое сердце.", "Слова могут обмануть, но чувства — никогда."],
    "легенда": ["Мы сами станем легендой для будущих поколений.", "Сказки — это лишь тень настоящей истории."],
    "магия": ["Она течет в нашей крови с рождения.", "Почувствуй энергию, что окружает нас."],
    "ритуал": ["Таинство, связывающее нас с предками.", "Держи круг закрытым, пока длится обряд."],
    "сердце": ["Оно бьется редко, но любит крепко.", "В холодном теле может жить горячее сердце."],
    "душа": ["Мы не потеряли её, мы просто изменили её суть.", "Береги то светлое, что осталось внутри."],
    "свобода": ["Истинная свобода — в возможности быть собой.", "Сбрось оковы и лети навстречу ночи."],
    "воля": ["Твоя воля — твой главный инструмент.", "Лишь сильный духом познает бессмертие."],
    "выбор": ["Каждый шаг определяет твое будущее.", "Выбирай мудро, ведь вечность не прощает ошибок."],
    "клятва": ["Слово, данное в темноте, нерушимо.", "Нарушить клятву — значит потерять себя."],
    "честь": ["Без чести мы — лишь звери в человечьем обличье.", "Береги свое имя пуще своей крови."],
    "слава": ["Она придет к тем, кто не боится трудностей.", "Твои подвиги будут воспевать в веках."],
    "победа": ["Сладкий вкус успеха после долгой битвы.", "Пусть каждая победа делает тебя мудрее."],
    "финал": ["Конец — это лишь начало новой главы.", "Занавес опускается, но история продолжается."],
    "база": ["Основа нашего мира крепка и незыблема.", "Здесь всё начиналось, здесь всё и живет."],
        "каллены": ["Семья вегетарианцев всегда рада новым лицам.", "Верность и сострадание — это путь Калленов."],
    "вольтури": ["Закон суров, но это закон. Вольтури следят за тобой.", "В Вольтерре не прощают ошибок."],
    "клан": ["Клан — это твоя броня и твоя крепость.", "В одиночку мы тени, в клане мы — буря."],
    "глава": ["Слово главы — закон для каждого в семье.", "Лидер ведет нас сквозь века."],
    "патриарх": ["Патриарх видит всё. Его мудрость безгранична.", "Приветствуй того, кто заложил основы нашего рода."],
    "совет": ["Совет старейшин рассудит любой спор.", "На совете решаются судьбы миров."],
    "закон": ["Наш кодекс написан кровью предков.", "Нарушишь закон — познаешь гнев всей семьи."],
    "семья": ["Семья важнее крови. Мы едины.", "В этом жестоком мире только семья не предаст."],
    "род": ["Твой род твоя гордость. Не посрами его.", "Древние узы связывают нас крепче стали."],
    "союз": ["Крепкий союз залог выживания в битве.", "Вместе мы непобедимы."],
    "враг": ["Враг моего клана мой личный враг.", "Пусть враги трепещут, когда мы выходим на охоту."],
    "битва кланов": ["Пора показать, кто истинный хозяин ночи!", "Сбор объявлен. Готовьтесь к великой резне."],
    "территория": ["Эта земля принадлежит нашему клану.", "Чужакам здесь не место. Уходи, пока можешь."],
    "предатель": ["Для предателей нет места под луной.", "Тень поглотит того, кто обманул доверие семьи."],
    "герб": ["Наш герб символ нашей древней силы.", "Носи знаки клана с честью."],
    "клятва": ["Клятва на крови нерушима веками.", "Твоё слово твоя жизнь перед лицом клана."],
    "верность": ["Верность ценится дороже любого золота.", "Оставайся верным до самого конца."],
    "иерархия": ["Знай своё место и уважай старших.", "Каждая ступень в клане добыта потом и кровью."],
    "старейшина": ["Слушай мудрость тех, кто видел рождение цивилизаций.", "Старейшины помнят то, что другие забыли."],
    "наследник": ["Будущее клана в твоих руках.", "Докажи, что ты достоин продолжить наш род."],
    "собрание": ["Все в круг! Глава хочет сделать объявление.", "Тишина на собрании. Говорит лидер."],
    "штаб": ["Наш штаб место, где рождаются планы захвата мира.", "Здесь мы в полной безопасности."],
    "победа": ["Победа клана это общая слава!", "Мы снова доказали своё превосходство."],
    "честь": ["Потерять честь хуже, чем потерять голову.", "Честь семьи это твоя личная ответственность."],
    "кодекс": ["Читай кодекс, там ответы на все вопросы бытия.", "Наш устав не менялся столетиями."],
    "защита": ["Один за всех, и все за одного!", "Клан защитит тебя, пока ты верен ему."],
    "амбиции": ["Твои амбиции помогут нашему клану расти.", "Стремись к вершине, но не забывай о братьях."],
    "традиция": ["Мы чтим традиции, заложенные еще первыми из нас.", "Традиции это то, что делает нас семьей."],
    "присяга": ["Ты присягнул на верность. Теперь пути назад нет.", "Твоя жизнь теперь принадлежит клану."],
    "единство": ["Разделенные мы падем, единые выстоим.", "Сила клана в его нерушимом единстве."]


}

TWILIGHT_ROLES = ["Вампир", "Оборотень", "Страж Вольтури", "Человек", "Провидец", "Щит"]

broadcast_mode = {}
last_msg_time = {}
chat_message_counters = {}
active_duels = {}
pending_duels = {}
# --- ФУНКЦИЯ ТАЙМЕРА АФК (Вставь перед основными обработчиками) ---
async def check_duel_timeout(duel_id, action_time, chat_id, msg_id):
    await asyncio.sleep(120)  # Ждем ровно 2 минуты (120 секунд)
    
    if duel_id in active_duels:
        duel = active_duels[duel_id]
        # Если время последнего действия не изменилось, значит игрок уснул
        if duel.get('last_action_time') == action_time:
            loser_id = duel['turn']
            me = 'p1' if loser_id == duel['p2'] else 'p2'
            opp = 'p2' if me == 'p1' else 'p1'
            winner_id = duel[me]
            winner_name = duel[f'{me}_name']
            loser_name = duel[f'{opp}_name']
            
            # Перевод крови
            conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
            cursor.execute('UPDATE users SET blood = blood + 100 WHERE user_id = ?', (winner_id,))
            cursor.execute('UPDATE users SET blood = blood - 100 WHERE user_id = ?', (loser_id,))
            conn.commit(); conn.close()
            
            await bot.send_message(
                chat_id,
                f"⏳ <b>ВРЕМЯ ВЫШЛО!</b>\n\n"
                f"Боец <b>{loser_name}</b> уснул на поле боя (AFK более 2 минут) и автоматически проигрывает!\n\n"
                f"🏆 Победитель: <b>{winner_name}</b> забирает 100🩸",
                reply_to_message_id=msg_id, parse_mode="HTML"
            )
        del active_duels[duel_id]
            
# --- БАЗА ДАННЫХ ---
# Предположим, эти переменные у тебя есть выше в коде
# ADMIN_ID = ...
# TWILIGHT_ROLES = [...]
def generate_hunt_map(user_id):
    # Разные визуальные локации
    places = ['🌲', '🌲', '🌲', '🌲', '🏚️', '🌾', '🌾', '🦇', '🏕️']
    random.shuffle(places)
    
    keyboard = []
    row = []
    for i, place in enumerate(places):
        # Кнопка передает: ID пользователя и номер клетки
        btn = InlineKeyboardButton(text=place, callback_data=f"hunt_step_{user_id}_{i}")
        row.append(btn)
        if len(row) == 3:
            keyboard.append(row)
            row = []
    
    # Кнопка побега
    keyboard.append([InlineKeyboardButton(text="🏃‍♂️ Сбежать с охоты", callback_data=f"hunt_escape_{user_id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def init_db():
    
    # Подключаемся к базе
    conn = sqlite3.connect('vocabulary.db')
    # Создаем объект cursor, без которого execute() не работает
    cursor = conn.cursor()

    # Создаем таблицу, если её нет
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        nickname TEXT,
        role TEXT,
        message_count INTEGER DEFAULT 0,
        spouse_id INTEGER,
        blood INTEGER DEFAULT 100,
        bitten_count INTEGER DEFAULT 0,
        clan TEXT DEFAULT 'Одиночка',
        points INTEGER DEFAULT 0,
        referals_count INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        bank INTEGER DEFAULT 0,
        bank_time INTEGER DEFAULT 0,
        bank_ops_count INTEGER DEFAULT 0,
        last_bank_reset TEXT,
        strength INTEGER DEFAULT 10
    )""")

    # Проверяем структуру таблицы
    cursor.execute("PRAGMA table_info(users)")
    cols = [c[1] for c in cursor.fetchall()]

    # Сохраняем изменения
    conn.commit()
    
    # Важно: если вы планируете использовать cursor дальше в коде 
    # за пределами этой функции, его нельзя здесь закрывать.
    # Но для самой функции init_db этого достаточно.

    if 'blood' not in cols: cursor.execute('ALTER TABLE users ADD COLUMN blood INTEGER DEFAULT 100')
    if 'bitten_count' not in cols: cursor.execute('ALTER TABLE users ADD COLUMN bitten_count INTEGER DEFAULT 0')
    # Проверка на случай, если база уже была создана без клана
    if 'clan' not in cols: cursor.execute("ALTER TABLE users ADD COLUMN clan TEXT DEFAULT 'Одиночка'")
    conn.commit(); conn.close()

    # Добавляем колонку для брака безопасно
conn = sqlite3.connect('vocabulary.db')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE user_businesses ADD COLUMN last_collect REAL DEFAULT 0")
    conn.commit()
    cursor.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0")
    conn.commit()
except:
    pass # Если колонка уже есть, ничего не делаем
conn.close()

def process_user(user_id, first_name):
    conn = sqlite3.connect('vocabulary.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. Проверяем наличие пользователя
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        # Определяем роль на основе списка GOD_IDS (нужно только для новых)
        is_god_rank = (user_id in GOD_IDS)
        role_now = "Бог" if is_god_rank else "Человек"
        
        if user:
            # ОБНОВЛЕНИЕ: Строго +1 сообщение и +1 капля крови
            # УБРАЛИ обновление role, чтобы не затирать выданные роли!
            cursor.execute("""
                UPDATE users 
                SET message_count = message_count + 1,
                    blood = blood + 1
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()
            
        else:
            # РЕГИСТРАЦИЯ НОВОГО
            # Стартовый капитал: 5000 для Богов, 100 для Людей
            start_blood = 5000 if is_god_rank else 100
            
            # При регистрации ставим message_count = 1 и присваиваем стартовую роль
            cursor.execute("""INSERT INTO users 
                (user_id, first_name, nickname, role, message_count, blood, bitten_count, clan, points, referals_count, is_banned) 
                VALUES (?, ?, ?, ?, 1, ?, 0, 'Нет', 0, 0, 0)""", 
                (user_id, first_name, first_name, role_now, start_blood))
            conn.commit()

        # 2. ПОЛУЧАЕМ АКТУАЛЬНЫЕ ДАННЫЕ ДЛЯ ВЫВОДА
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        return {
            'id': user_id,
            'nick': row['nickname'],
            'role': row['role'],
            'msgs': row['message_count'],
            'blood': row['blood'],
            'bitten': row['bitten_count'],
            'clan': row['clan'],
            'points': row['points'],
            'refs': row['referals_count'],
            'strength': row['strength'] if 'strength' in row.keys() else 10, # Защита от ошибки, если колонки strength нет
            'spouse_id': row['spouse_id'],
            'is_banned': row['is_banned'] if 'is_banned' in row.keys() else 0
        }
        
    except Exception as e:
        print(f"🔴 Ошибка базы в process_user: {e}")
        return None
    finally:
        conn.close()
        
dp = Dispatcher()

@dp.message(lambda message: message.text and message.text.lower().startswith("плюс "))
async def change_nickname(message: types.Message):
    user_id = message.from_user.id
    new_nickname = message.text[5:].strip()

    #Простая проверка на длину
    if not new_nickname:
        await message.reply("⚠️ Ты не ввел ник! Напиши: <code>плюс ТвойНик</code>", parse_mode="HTML")
        return
    
    if len(new_nickname) > 20:
        await message.reply("⚠️ Слишком длинный ник! Максимум 20 символов.")
        return

    # 2. Обновляем в базе
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    try:
        # Сначала убедимся, что пользователь есть в базе (вызовем нашу функцию)
        process_user(user_id, message.from_user.first_name)
        
        # Теперь меняем именно nickname
        cursor.execute("UPDATE users SET nickname = ? WHERE user_id = ?", (new_nickname, user_id))
        conn.commit()
        
        await message.answer(f"✅ Патриарх одобряет! Твой новый ник в профиле: <b>{new_nickname}</b>", parse_mode="HTML")
        
    except Exception as e:
        print(f"Ошибка смены ника: {e}")
        await message.answer("❌ Не удалось сменить ник. Попробуй позже.")
    finally:
        conn.close()
    
# --- ОБРАБОТЧИК КНОПКИ РАССЫЛКИ ---
@dp.callback_query(F.data == "start_broadcast")
async def start_broadcast_handler(callback: types.CallbackQuery):
    # Проверяем, что нажал именно админ
    if callback.from_user.id == ADMIN_ID:
        broadcast_mode[callback.from_user.id] = True
        await callback.message.answer("🎤 <b>Режим рассылки включен!</b>\nПришли сообщение (текст, фото или пост), и я разошлю его всем вампирам.", parse_mode="HTML")
    else:
        await callback.answer("❌ У тебя нет прав Патриарха для этого!", show_alert=True)
    await callback.answer()

# --- ОБРАБОТЧИК САМОГО ТЕКСТА РАССЫЛКИ ---
@dp.message(lambda msg: broadcast_mode.get(msg.from_user.id) is True)
async def perform_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID: 
        broadcast_mode[message.from_user.id] = False
        return

    broadcast_mode[message.from_user.id] = False
    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    conn.close()

    count = 0
    status_msg = await message.answer("🚀 Начинаю рассылку...")
    
    for (uid,) in users:
        try:
            await message.copy_to(chat_id=uid)
            count += 1
            await asyncio.sleep(0.05) # Защита от бана Телеграма
        except:
            pass

    await status_msg.edit_text(f"✅ Рассылка завершена!\nСообщение получили <b>{count}</b> вампиров.", parse_mode="HTML")
    

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()
    
    # Регистрация самого пользователя
    user_data = process_user(user_id, message.from_user.first_name)
    if user_data == "BANNED":
        return # Бот просто молчит или можно отправить "Ты забанен!"    
    # ПРОВЕРКА РЕФЕРАЛА
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        
        # Нельзя пригласить самого себя
        if referrer_id != user_id:
            conn = sqlite3.connect('vocabulary.db')
            cursor = conn.cursor()
            
            # Проверяем, новый ли это пользователь для базы
            cursor.execute("SELECT message_count FROM users WHERE user_id = ?", (user_id,))
            res = cursor.fetchone()
            
            # Если у пользователя 1 сообщение (он только что создался в process_user)
            if res and res[0] <= 1:
                bonus = random.randint(200, 500) # Случайная награда от 200 до 500
                
                # Даем кровь пригласившему и прибавляем ему реферала
                cursor.execute('''UPDATE users 
                                  SET blood = blood + ?, referals_count = referals_count + 1 
                                  WHERE user_id = ?''', (bonus, referrer_id))
                conn.commit()
                
                # Уведомляем пригласившего (если бот может писать ему в ЛС)
                try:
                    await bot.send_message(referrer_id, f"🩸 Твой реферал зашел в бота! Тебе начислено {bonus} капель крови.")
                except:
                    pass
            conn.close()

    await message.answer("Добро пожаловать в Империю Кальяна! Твоя реферальная ссылка:\n"
                         f"<code>t.me/{(await bot.get_me()).username}?start={user_id}</code>", 
                         parse_mode="HTML")

    
# команды хенллера
@dp.message(F.text)
async def chat_handler(message: types.Message):

# данные один раз
    user_data = process_user(message.from_user.id, message.from_user.first_name)

    #проверка бана
    if user_data is None or user_data == "BANNED":
        return # Бот просто игнорирует забаненного или несуществующего

    # 3. Теперь, когда мы уверены, что данные есть, безопасно их достаём
    ref_count = user_data.get('referals', 0)
    text_low = message.text.lower().strip()
    
    # Тут используем словарь, зная, что он не пустой
    user_tag = f'<a href="tg://user?id={message.from_user.id}">{user_data.get("nick", message.from_user.first_name)}</a>'
    chat_id = message.chat.id

    # ... дальше идет остальной код твоих команд ...


    # Анти-флуд
    now = time.time()
    if now - last_msg_time.get(message.from_user.id, 0) < 2: return
    last_msg_time[message.from_user.id] = now
    chat_message_counters[chat_id] = chat_message_counters.get(chat_id, 0) + 1

    is_private = message.chat.type == "private"
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot.id
    is_mentioned = BOT_USERNAME.lower() in text_low
    

    # === КОМАНДА: СВАДЬБА ===
    if text_low == "свадьба":
        if not message.reply_to_message:
            await message.answer("💍 Чтобы сделать предложение, ответь на сообщение игрока командой «Свадьба».")
            return
        
        partner_id = message.reply_to_message.from_user.id
        user_id = message.from_user.id
        
        if partner_id == user_id:
            await message.answer("🦇 Ты не можешь жениться на самом себе, даже если ты Бог!")
            return
            
        # Кнопки Да/Нет
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💍 Да!", callback_data=f"marry_{user_id}_{partner_id}")],
            [InlineKeyboardButton(text="💔 Нет", callback_data=f"refuse_{user_id}")]
        ])
        
        await message.answer(
            f"💍 Игрок <b>{message.from_user.first_name}</b> делает предложение <b>{message.reply_to_message.from_user.first_name}</b>!\n\nЧто скажешь?", 
            reply_markup=kb, 
            parse_mode="HTML"
        )
        return

    # === КОМАНДА: ТУДА (РАЗВОД) ===
    if text_low == "туда":
        user_id = message.from_user.id
        conn = sqlite3.connect('vocabulary.db')
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT partner FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if not row or not row[0]:
                await message.answer("Ты и так свободен как ветер. Разводиться не с кем!")
            else:
                partner_id = row[0]
                # Стираем партнеров друг у друга
                cursor.execute('UPDATE users SET partner = NULL WHERE user_id = ?', (user_id,))
                cursor.execute('UPDATE users SET partner = NULL WHERE user_id = ?', (partner_id,))
                conn.commit()
                await message.answer("💔 Брак расторгнут. Вы официально разведены и отправлены «Туда».")
        finally:
            conn.close()
        return

    if text_low == "охота":
        user_id = message.from_user.id
        
        # Проверка: не идет ли уже охота
        if user_id in active_hunts:
            return await message.answer("❌ Ты уже в лесу! Закончи текущую охоту.")

        # Главное меню выбора цели
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🦌 На животных (50🩸 | КД: 2ч)", callback_data=f"hunt_start_animal_{user_id}")],
            [InlineKeyboardButton(text="🚶 На людей (100🩸 | КД: 4ч)", callback_data=f"hunt_start_human_{user_id}")]
        ])

        await message.answer(
            f"🦇 <b>Сезон охоты открыт!</b>\nКого будем выслеживать в этот раз?",
            reply_markup=kb,
            parse_mode="HTML"
        )
        return


    # 1. ПРОФИЛЬ
    # 1. ПРОФИЛЬ (С КНОПКОЙ РАССЫЛКИ ДЛЯ АДМИНА
        # --- КОМАНДА СМЕНЫ РОЛИ (ТОЛЬКО ДЛЯ АДМИНА) ---
    if text_low.startswith("сетроль") or text_low.startswith("сменароли"):
        if message.from_user.id != ADMIN_ID:
            return await message.answer("❌ У тебя нет прав Патриарха для изменения судеб!")

        # Разбиваем сообщение на части: команда, ID, роль
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            return await message.answer(
                "⚠️ <b>Формат команды:</b>\n<code>сменароли [ID_пользователя] [Название_роли]</code>\n\n"
                "Пример: <code>сменароли 123456789 Главный вампир</code>", 
                parse_mode="HTML"
            )

        target_id = parts[1]
        new_role = parts[2]

        # Список разрешенных ролей (добавь сюда те, что тебе нужны)
        allowed_roles = TWILIGHT_ROLES + ["Вампир", "Оборотень", "Страж Вольтури", "Человек", "Провидец", "Щит"]

        if new_role not in allowed_roles:
            roles_str = ", ".join(allowed_roles)
            return await message.answer(f"❌ Эту роль нельзя поставить. \n<b>Доступные:</b> {roles_str}", parse_mode="HTML")

        try:
            conn = sqlite3.connect('vocabulary.db')
            cursor = conn.cursor()
            # Проверяем, есть ли такой пользователь в базе
            cursor.execute('UPDATE users SET role = ? WHERE user_id = ?', (new_role, target_id))
            
            if cursor.rowcount == 0:
                await message.answer("❌ Пользователь с таким ID не найден в моей базе данных.")
            else:
                conn.commit()
                await message.answer(f"✅ Судьба изменена! \nПользователь <code>{target_id}</code> теперь <b>{new_role}</b>.", parse_mode="HTML")
            
            conn.close()
        except Exception as e:
            await message.answer(f"⚠️ Ошибка при обновлении базы: {e}")
        return
    
    if text_low == "магазин":
        # Цены распределены по силе (max 30k)
            kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👤 Человек — 1.000🩸", callback_data="buy_role_Человек_1000")],
            [InlineKeyboardButton(text="🧛 Вампир — 35.000🩸", callback_data="buy_role_Вампир_35000")],
            [InlineKeyboardButton(text="🐺 Оборотень — 20.000🩸", callback_data="buy_role_Оборотень_20000")],
            [InlineKeyboardButton(text="🔮 Провидец — 15.000🩸", callback_data="buy_role_Провидец_15000")],
            [InlineKeyboardButton(text="🛡 Щит — 15.000🩸", callback_data="buy_role_Щит_15000")],
            [InlineKeyboardButton(text="⚔️ Страж Вольтури — 20.000🩸", callback_data="buy_role_Страж Вольтури_20000")],
            [InlineKeyboardButton(text="⚡️ Улучшение силы (+1-5) — 5.000🩸", callback_data="buy_boost_strength_5000")],
            [InlineKeyboardButton(text="👑 Стать Богом — 3.000₽", callback_data="buy_god_role")]
        ])
        
            await message.answer(
            "🩸 <b>ТЕНЕВОЙ РЫНОК</b> 🩸\n\n"
            "Здесь ты можешь обрести новую сущность или усилить свою мощь.\n\n"
            "⚠️ <b>ВАЖНО:</b> При покупке новой роли вся накопленная сила (strength) <b>сбрасывается до 10</b>! Выбирай с умом.",
            reply_markup=kb, parse_mode="HTML"
        )
            return
  
    
    # 1. ПРОФИЛЬ (С КНОПКОЙ РАССЫЛКИ ДЛЯ АДМИНА)
    # 1. ПРОФИЛЬ (С КНОПКОЙ РАССЫЛКИ ДЛЯ АДМИНА)
    if text_low == "проф":
        # Поиск имени супруга
        spouse_name = "Одинок(а)"
        spouse_id = user_data.get('spouse_id', 0)

        if spouse_id != 0:
            conn = sqlite3.connect('vocabulary.db')
            cursor = conn.cursor()
            cursor.execute("SELECT first_name FROM users WHERE user_id = ?", (spouse_id,))
            res = cursor.fetchone()
            if res:
                spouse_name = res[0]
            conn.close() # Закрываем базу здесь, чтобы она не висела открытой

        # Работа с клавиатурой для админа
        kb = None
        if message.from_user.id == ADMIN_ID:
            # Создаем клавиатуру с кнопкой рассылки
            buttons = [
                [InlineKeyboardButton(text="📢 Создать рассылку", callback_data="start_broadcast")]
            ]
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)

        # Собираем текст профиля
        # Используем .get(..., 0), чтобы бот не падал, если какой-то колонки нет в базе
        text = (
            f"🩸 <b>ПРОФИЛЬ</b>\n\n"
            f"👤 Ник: {user_data.get('nick', 'Не установлен')}\n"
            f"💍 Брак: <b>{spouse_name}</b>\n"
            f"🦇 Роль: <b>{user_data.get('role', 'Игрок')}</b>\n"
            f"⚔️ Сила: <b>{user_data.get('strength', 10)}</b>\n"
            f"🏰 Клан: {user_data.get('clan', 'Одиночка')}\n"
            f"🏆 Очки: {user_data.get('points', 0)}\n"
            f"💉 Кровь: <b>{user_data.get('blood', 100)}</b>\n"
            f"👥 Пригласил: {ref_count} чел.\n"
            f"🦷 Укусов: {user_data.get('bitten', 0)}\n"
            f"💬 Сообщений: {user_data.get('msgs', 0)}"
        )

        # ОТПРАВКА ФОТО С ТЕКСТОМ
        # ОТПРАВКА ФОТО С ТЕКСТОМ
        # Текст уходит в параметр caption (подпись к фото)
        await message.answer_photo(
            photo=PHOTO_IDS['проф'],
            caption=text,
            parse_mode="HTML",
            reply_markup=kb
        )
        return


    # 🚫 КОМАНДА БАНА (Только Патриарх)
    elif text_low == "в гроб" and message.reply_to_message:
        # Проверка: если пишет не главный админ
        if message.from_user.id != ADMIN_ID:
            await message.answer("❌ Эта власть принадлежит только <b>Патриарху</b>!", parse_mode="HTML")
            return
            
        target_id = message.reply_to_message.from_user.id
        
        # Запрещаем банить самого себя (на всякий случай)
        if target_id == ADMIN_ID:
            await message.answer("🤔 Ты не можешь забанить самого себя.")
            return

        conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
        # Устанавливаем статус бана в базе
        cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (target_id,))
        conn.commit(); conn.close()
        
        await message.answer(f"⛓ По приказу Патриарха игрок был изгнан из Империи!")
        return

    # ✅ КОМАНДА РАЗБАНА (Только Патриарх)
    elif text_low == "вытащить" and message.reply_to_message:
        if message.from_user.id != ADMIN_ID:
            await message.answer("❌ Только <b>Патриарх</b> может даровать прощение!", parse_mode="HTML")
            return
            
        target_id = message.reply_to_message.from_user.id
        conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (target_id,))
        conn.commit(); conn.close()
        
        await message.answer(f"🕊 Милость Патриарха безгранична. Игрок помилован.")
        return


    if text_low == "бизнесы":
        res = "💼 <b>Коммерческая недвижимость</b>\n\n"
        for key, data in BIZ_CONFIG.items():
            res += (
                f"{data['name']}\n"
                f"├ 💰 Цена: <b>{data['price']:,}🩸</b>\n"
                f"├ 📈 Доход: <b>{data['income']}🩸/час</b>\n"
                f"└ 👥 Рабочие: <b>0/{data['max_workers']}</b>\n\n"
            )
        res += "<i>Чтобы купить, пиши:</i>\n<code>приобрести бизнес [название]</code>\n"
        res += "Например: <code>приобрести бизнес кафе</code>"
        return await message.answer(res, parse_mode="HTML")

    elif text_low.startswith("нанять рабочих"):
        user_id = message.from_user.id
        parts = text_low.split()
        # Проверка, команды
        if len(parts) < 4 or not parts[3].isdigit():
            return await message.answer(
                "❓ Неверный формат! Укажи название бизнеса и количество.\n"
                "Пример: <code>нанять рабочих кафе 5</code> или <code>нанять рабочих завод 2</code>"
            )
        
        biz_input = parts[2]       #слово вроде "кафе"
        count_to_hire = int(parts[3]) # количество рабочих
        
        if count_to_hire <= 0:
            return await message.answer("❌ Количество должно быть больше нуля!")

        # Определение
        biz_key = None
        if "кафе" in biz_input or "cafe" in biz_input: biz_key = "cafe"
        elif "завод" in biz_input or "factory" in biz_input: biz_key = "factory"
        elif "рудник" in biz_input or "mine" in biz_input: biz_key = "mine"
        elif "гроб" in biz_input or "coffin" in biz_input: biz_key = "coffin_shop"
        if not biz_key:
            return await message.answer("❓ Такого предприятия нет. Используй: кафе, завод, рудники.")

        config = BIZ_CONFIG[biz_key]

        conn = sqlite3.connect('vocabulary.db')
        cursor = conn.cursor()
        
        # Проверяем, куплен ли именно ЭТОТ бизнес у игрока
        cursor.execute('SELECT workers FROM user_businesses WHERE user_id = ? AND biz_key = ?', (user_id, biz_key))
        biz_row = cursor.fetchone()
        
        if not biz_row:
            conn.close()
            return await message.answer(f"❌ У тебя ещё нет предприятия <b>{config['name']}</b>!")
        
        current_workers = biz_row[0]

        # Считаем лимиты и стоимость конкретно для выбранного бизнеса
        max_limit = config['max_workers']
        cost_per_one = config['worker_cost']
        total_cost = count_to_hire * cost_per_one

        if current_workers + count_to_hire > max_limit:
            conn.close()
            return await message.answer(
                f"❌ В твоём заведении <b>{config['name']}</b> нет столько мест!\n"
                f"Максимум рабочих: {max_limit}, сейчас нанято: {current_workers}."
            )

        # Проверяем баланс игрока
        cursor.execute('SELECT blood FROM users WHERE user_id = ?', (user_id,))
        user_blood = cursor.fetchone()[0]

        if user_blood < total_cost:
            conn.close()
            return await message.answer(f"❌ Не хватает крови! Наём {count_to_hire} рабочих стоит <b>{total_cost:,}🩸</b>")

        # Нанимаем персонал именно на выбранный бизнес
        cursor.execute('UPDATE users SET blood = blood - ? WHERE user_id = ?', (total_cost, user_id))
        cursor.execute(
            'UPDATE user_businesses SET workers = workers + ? WHERE user_id = ? AND biz_key = ?', 
            (count_to_hire, user_id, biz_key)
        )
        
        conn.commit()
        conn.close()
        
        await message.answer(
            f"✅ Ты нанял {count_to_hire} рабочих для <b>{config['name']}</b>!\n"
            f"Списано: <b>{total_cost:,}🩸</b>"
        )
    elif text_low == "собрать доход":
        user_id = message.from_user.id
        now = time.time()
        
        conn = sqlite3.connect('vocabulary.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT biz_key, workers, last_collect FROM user_businesses WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        
        if not rows:
            conn.close()
            return await message.answer("❌ У тебя нет бизнеса, чтобы собирать доход!")
            
        total_collected = 0
        
        for biz_key, workers, last_collect in rows:
            if biz_key in BIZ_CONFIG:
                data = BIZ_CONFIG[biz_key]
                
                if last_collect == 0 or last_collect is None:
                    last_collect = now - 3600 
                
                hours_passed = (now - last_collect) / 3600
                
                # --- МАТЕМАТИКА С КОЭФФИЦИЕНТОМ 50% ---
                base_income = int(data['income'])
                current_workers = int(workers) if workers else 0
                
                # Рабочие приносят по 50% (умножаем на 0.5)
                workers_income = int(current_workers * base_income * 0.5)
                
                hourly_income = base_income + workers_income
                
                collected = int(hours_passed * hourly_income)
                total_collected += collected

        if total_collected <= 0:
            conn.close()
            return await message.answer("⏳ Доход ещё не накопился! Подожди немного.")

        cursor.execute('UPDATE users SET blood = blood + ? WHERE user_id = ?', (total_collected, user_id))
        cursor.execute('UPDATE user_businesses SET last_collect = ? WHERE user_id = ?', (now, user_id))
        
        conn.commit()
        conn.close()
        
        return await message.answer(f"💸 Ты собрал выручку со своих предприятий!\n\nПолучено: <b>{total_collected:,}🩸</b>", parse_mode="HTML")

    elif text_low == "мои бизнесы":
        user_id = message.from_user.id
        
        conn = sqlite3.connect('vocabulary.db')
        cursor = conn.cursor()
        cursor.execute('SELECT biz_key, workers FROM user_businesses WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return await message.answer(f"💼 {user_tag}, у тебя пока нет открытых предприятий. Загляни на рынок!")

        res = f"🏘 <b>Имущество {user_tag}:</b>\n\n"
        total_income = 0

        for biz_key, workers in rows:
            if biz_key in BIZ_CONFIG:
                data = BIZ_CONFIG[biz_key]
                
                # --- МАТЕМАТИКА С КУФФИЦИЕНТОМ 50% ---
                base_income = int(data['income'])
                current_workers = int(workers) if workers else 0
                
                # Рабочие приносят по 50% (умножаем на 0.5)
                workers_income = int(current_workers * base_income * 0.5)
                
                income = base_income + workers_income
                total_income += income
                
                res += (
                    f"🔹 <b>{data['name']}</b>\n"
                    f"   ├ 👥 Персонал: <b>{current_workers}/{data['max_workers']}</b>\n"
                    f"   └ 💰 Приносит: <b>{income:,}🩸/час</b> (из них рабочие: {workers_income:,}🩸)\n\n"
                )

        res += f"💳 Суммарная прибыль: <b>{total_income:,}🩸/час</b>"
        
        return await message.answer(res, parse_mode="HTML")
      
    elif text_low.startswith("приобрести бизнес"):
        user_id = message.from_user.id
        # Убираем лишние слова, чтобы понять, что именно хочет купить юзер
        target = text_low.replace("приобрести бизнес", "").strip()
        
        # Ищем, какой ключ из BIZ_CONFIG (cafe, factory, mine) есть в тексте
        biz_key = None
        if "кафе" in target or "cafe" in target: biz_key = "cafe"
        elif "завод" in target or "factory" in target: biz_key = "factory"
        elif "рудник" in target or "mine" in target: biz_key = "mine"
        elif "гроб" in target or "coffin" in target: biz_key = "coffin_shop"
        
        if not biz_key:
            return await message.answer("❓ Такого предприятия нет. Используй названия: кафе, завод, рудники.")

        biz = BIZ_CONFIG[biz_key]
        
        # Проверяем баланс (замени 'blood' на свою колонку с деньгами)
        conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
        cursor.execute('SELECT blood FROM users WHERE user_id = ?', (user_id,))
        user_blood = cursor.fetchone()[0]

        if user_blood < biz['price']:
            conn.close()
            return await message.answer(f"❌ Недостаточно крови! Нужно {biz['price']:,}🩸")

        # Проверяем, нет ли уже такого бизнеса (если лимит 1 штука)
        cursor.execute('SELECT id FROM user_businesses WHERE user_id = ? AND biz_key = ?', (user_id, biz_key))
        if cursor.fetchone():
            conn.close()
            return await message.answer("❌ У тебя уже есть это предприятие!")

        # Снимаем деньги и добавляем бизнес
        cursor.execute('UPDATE users SET blood = blood - ? WHERE user_id = ?', (biz['price'], user_id))
        cursor.execute('INSERT INTO user_businesses (user_id, biz_key, workers) VALUES (?, ?, ?)', (user_id, biz_key, 0))
        
        conn.commit(); conn.close()
        await message.answer(f"🎉 Поздравляем! Ты приобрел <b>{biz['name']}</b>!")


    # 2. ИНФО
    if text_low == "инфо":
        await message.answer("📖 <a href='https://t.me/ECullenbot'>БАЗА ЗНАНИЙ</a>", parse_mode="HTML"); return

       # 🏦 КОМАНДА: БАНК (Проверка баланса и начисление %)
    elif text_low == "банк":
        conn = sqlite3.connect('vocabulary.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT blood, bank, bank_time FROM users WHERE user_id = ?", (message.from_user.id,))
        u = cursor.fetchone()
        
        now = int(time.time())
        bank_balance = u['bank'] if u['bank'] else 0
        last_time = u['bank_time'] if u['bank_time'] else 0
        
        # Начисляем 5%, если прошло 24 часа (86400 секунд)
        if bank_balance > 0 and (now - last_time) >= 86400:
            profit = int(bank_balance * 0.05)
            bank_balance += profit
            # Обновляем баланс и сбрасываем таймер на текущее время
            cursor.execute("UPDATE users SET bank = ?, bank_time = ? WHERE user_id = ?", (bank_balance, now, message.from_user.id))
            conn.commit()
            await message.answer(f"📈 Твои сбережения принесли прибыль! <b>+{profit}🩸</b>\nТеперь в сейфе: {bank_balance}🩸", parse_mode="HTML")
            conn.close(); return
            
        # Если время еще не пришло, просто показываем баланс
        rem_hours = int(24 - ((now - last_time) / 3600)) if last_time > 0 else 0
        msg = f"🏦 <b>Имперский Банк</b>\n\n"
        msg += f"🩸 На руках: {u['blood']}\n"
        msg += f"🗄 В сейфе: {bank_balance}\n\n"
        if bank_balance > 0:
            msg += f"⏳ До следующих 5%: ~{rem_hours} ч.\n\n"
        msg += "<i>Команды: вложить [число], снять [число]</i>"
        
        await message.answer(msg, parse_mode="HTML")
        conn.close(); return

    # 📥 КОМАНДА: ВЛОЖИТЬ
    elif text_low.startswith("вложить"):
        user_id = message.from_user.id
        parts = message.text.split()
        
        if len(parts) < 2 or not parts[1].isdigit():
            return await message.answer("❌ Напиши: <code>вложить [число]</code>", parse_mode="HTML")

        amount = int(parts[1])
        if amount <= 0:
            return await message.answer("❌ Введите число больше 0.")

        now_dt = datetime.now()
        now_ts = int(time.time()) # Время для таймера прибыли в секундах

        conn = sqlite3.connect('vocabulary.db')
        conn.row_factory = sqlite3.Row # Чтобы обращаться к колонкам по именам, как в других функциях
        cursor = conn.cursor()
        
        # Получаем сразу все нужные данные
        cursor.execute('SELECT blood, bank, bank_time, bank_ops_count, last_bank_reset FROM users WHERE user_id = ?', (user_id,))
        u = cursor.fetchone()
        
        if not u:
            conn.close(); return

        user_blood = u['blood']
        bank_balance = u['bank'] if u['bank'] else 0
        bank_time = u['bank_time'] if u['bank_time'] else 0
        ops_count = u['bank_ops_count'] if u['bank_ops_count'] else 0
        last_reset_str = u['last_bank_reset']

        # --- Проверка баланса перед лимитами (чтобы не тратить попытку зря) ---
        if user_blood < amount:
            conn.close()
            return await message.answer("❌ У тебя нет столько крови!")

        # --- ЛОГИКА ТАЙМЕРА ЛИМИТОВ ОПЕРАЦИЙ ---
        if last_reset_str is None:
            ops_count = 0
            last_reset = now_dt
        else:
            last_reset = datetime.fromisoformat(last_reset_str)

        # Сброс лимита, если прошло 24 часа
        if now_dt > last_reset + timedelta(hours=24):
            ops_count = 0
            last_reset = now_dt
        
        # Проверка лимита (Боги игнорируют)
        if ops_count >= DAILY_BANK_LIMIT and user_id not in GOD_IDS:
            time_left = (last_reset + timedelta(hours=24)) - now_dt
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            conn.close()
            return await message.answer(
                f"🚫 <b>Лимит исчерпан!</b>\n"
                f"Вы можете совершать только {DAILY_BANK_LIMIT} операций в банк за 24 часа.\n"
                f"Лимит обновится через: <b>{hours}ч. {minutes}мин.</b>", 
                parse_mode="HTML"
            )

        # --- ВАЖНЫЙ ФИКС ТАЙМЕРА 5% ПРИБЫЛИ ---
        # Если сейф был пуст, начинаем отсчет времени для 5% именно с этой секунды
        new_bank_time = now_ts if bank_balance == 0 else bank_time

        # --- ВЫПОЛНЕНИЕ ОПЕРАЦИИ ---
        new_ops_count = ops_count + 1
        cursor.execute('''
            UPDATE users 
            SET blood = blood - ?, 
                bank = bank + ?, 
                bank_time = ?,
                bank_ops_count = ?, 
                last_bank_reset = ? 
            WHERE user_id = ?
        ''', (amount, amount, new_bank_time, new_ops_count, last_reset.isoformat(), user_id))
        
        conn.commit()
        conn.close()

        await message.answer(
            f"🏦 Ты надежно спрятал <b>{amount:,}🩸</b> в банк!\n"
            f"Это твоя <b>{new_ops_count}/{DAILY_BANK_LIMIT}</b> операция за сутки.", 
            parse_mode="HTML"
        )
        return


    # 📤 КОМАНДА: СНЯТЬ
    elif text_low.startswith("снять "):
        args = text_low.split()
        if len(args) < 2 or not args[1].isdigit():
            await message.answer("❌ Напиши команду правильно: <b>снять 100</b>", parse_mode="HTML"); return
            
        amount = int(args[1])
        conn = sqlite3.connect('vocabulary.db'); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
        cursor.execute("SELECT bank FROM users WHERE user_id = ?", (message.from_user.id,))
        u = cursor.fetchone()
        
        bank_balance = u['bank'] if u['bank'] else 0
        if bank_balance < amount:
            await message.answer("❌ В твоем сейфе нет столько крови!"); conn.close(); return
            
        cursor.execute("UPDATE users SET blood = blood + ?, bank = bank - ? WHERE user_id = ?", 
                       (amount, amount, message.from_user.id))
        conn.commit(); conn.close()
        
        await message.answer(f"🔓 Ты забрал <b>{amount}🩸</b> из банка.", parse_mode="HTML")
        return

    if text_low.startswith("укусить") and message.reply_to_message:
        now = time.time()
        user_id = message.from_user.id
        # Проверяем, является ли атакующий Богом
        is_god = (user_id in GOD_IDS)

        target = message.reply_to_message.from_user
        target_id = target.id
        
        # 1. ЗАЩИТА БОГА: Тебя нельзя кусать
        if target_id in GOD_IDS:
            return await message.answer_photo(
                photo=PHOTO_IDS['укусить'],
                caption=f"🙏 Смертный, ты посмел обнажить клыки на <b>Бога</b>? Твои зубы рассыпались в прах!",
                parse_mode="HTML"
            )

        # 2. ПРОВЕРКА КУЛДАУНА (Для Бога — без очереди)
        if 'bite' not in cooldowns: cooldowns['bite'] = {} # Защита от вылета
        
        if not is_god:
            if now - cooldowns['bite'].get(user_id, 0) < 30:
                rem = int(30 - (now - cooldowns['bite'][user_id]))
                return await message.answer_photo(
                    photo=PHOTO_IDS['укусить'],
                    caption=f"⏳ {user_tag}, клыки еще не отросли! Жди {rem} сек.",
                    parse_mode="HTML"
                )

        target_tag = f'<a href="tg://user?id={target_id}">{target.first_name}</a>'
        
        # 3. ПРОВЕРКА ЦЕНЫ (Бог кусает бесплатно)
        if not is_god and user_data['blood'] < 10:
            return await message.answer_photo( photo=PHOTO_IDS['укусить'],
                caption=f"🩸 {user_tag}, ты слишком слаб! Нужно минимум 10🩸",
                parse_mode="HTML"
            )
        # Ставим кулдаун (только смертным)
        if not is_god:
            cooldowns['bite'][user_id] = now
        conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
        
        # 4. ОБНОВЛЕНИЕ БАЗЫ
        # Списываем кровь у нападающего (если он не Бог)
        if not is_god:
            cursor.execute('UPDATE users SET blood = blood - 10 WHERE user_id = ?', (user_id,))
        
        # ВАЖНО: Прибавляем укус именно НАПАДАЮЩЕМУ (user_id)
        cursor.execute('UPDATE users SET bitten_count = bitten_count + 1 WHERE user_id = ?', (user_id,))
        
        conn.commit(); conn.close()
        
        # Красивый ответ с фото
        blood_text = "бесплатно (Божественно)" if is_god else "-10🩸"
        
        await message.answer_photo(
            photo=PHOTO_IDS['укусить'],
            caption=f"🧛‍♂️ {user_tag} вонзил клыки в {target_tag}! <b>{blood_text}</b>",
            parse_mode="HTML"
        )
        return


    # 🏆 КОМАНДА: ТОП
    elif text_low == "кровосиси":
        conn = sqlite3.connect('vocabulary.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Считаем сумму крови на руках и в банке, сортируем по убыванию
        cursor.execute("""
            SELECT first_name, role, (blood + IFNULL(bank, 0)) as total_wealth 
            FROM users 
            ORDER BY total_wealth DESC 
            LIMIT 10
        """)
        top_users = cursor.fetchall()
        
        text = "🏆 <b>ТОП-10 БОГАЧЕЙ ИМПЕРИИ:</b>\n\n"
        medals = ["🥇", "🥈", "🥉"]
        
        for i, u in enumerate(top_users):
            medal = medals[i] if i < 3 else f"{i+1}."
            text += f"{medal} <b>{u['first_name']}</b> [{u['role']}] — {u['total_wealth']} 🩸\n"
            
        await message.answer(text, parse_mode="HTML")
        conn.close()
        return

    # --- 2. УКРАСТЬ (Лимит: 5 мин = 300 сек) ---
    if text_low == "украсть" and message.reply_to_message:
        attacker_id = message.from_user.id
        target = message.reply_to_message.from_user
        
        # Проверяем, является ли атакующий Богом
        is_god = (attacker_id in GOD_IDS) 

        # 1. ИММУНИТЕТ БОГА
        if target.id in GOD_IDS:
            return await message.answer_photo(
                photo=PHOTO_IDS['украсть'],
                caption=f"⚡️ {user_tag}, ты посмел покуситься на кровь <b>Бога</b>? Твои руки обратились в пепел!",
                parse_mode="HTML"
            )

        # 2. ПРОВЕРКА КУЛДАУНА
        now = time.time()
        if 'steal' not in cooldowns: cooldowns['steal'] = {} # Защита от вылета бота
        
        if not is_god: 
            if now - cooldowns['steal'].get(attacker_id, 0) < 300:
                rem = int(300 - (now - cooldowns['steal'][attacker_id]))
                return await message.answer_photo(
                    photo=PHOTO_IDS['украсть'],
                    caption=f"⏳ {user_tag}, полиция еще ищет тебя! Жди {rem//60} мин {rem%60} сек.",
                    parse_mode="HTML"
                )
            cooldowns['steal'][attacker_id] = now 

        target_tag = f'<a href="tg://user?id={target.id}">{target.first_name}</a>'
        
        # 3. ШАНС УСПЕХА
        if is_god or random.random() < 0.40:
            amt = random.randint(100,1500) if is_god else random.randint(15, 150)
            
            conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
            cursor.execute('UPDATE users SET blood = blood - ? WHERE user_id = ? AND blood >= ?', (amt, target.id, amt))
            
            if cursor.rowcount > 0:
                cursor.execute('UPDATE users SET blood = blood + ? WHERE user_id = ?', (amt, attacker_id))
                action_text = "божественно изъял" if is_god else "украл"
                final_msg = f"🤫 {user_tag} {action_text} <b>{amt}🩸</b> у {target_tag}!"
            else:
                final_msg = f"🩸 У {target_tag} нет крови для кражи."
            conn.commit(); conn.close()
        else:
            final_msg = f"🤡 {user_tag} облажался при краже у {target_tag}!"

        # ОТПРАВКА ФОТО ВМЕСТЕ С ТЕКСТОМ
        await message.answer_photo(
            photo=PHOTO_IDS['украсть'], 
            caption=final_msg, 
            parse_mode="HTML"
        )
        return



# --- ПРИВЕТСТВИЕ В ЛИЧКЕ БОТА ---
# Если у тебя общий chat_handler, добавь туда:
# --- ПРИВЕТСТВИЕ В ЛИЧКЕ БОТА ---
# Если у тебя общий chat_handler, добавь туда:


    # --- ЭКСКЛЮЗИВ ПАТРИАРХА: Ограбить больницу ---
    # --- ЭКСКЛЮЗИВ ПАТРИАРХА: Ограбить больницу ---
    if text_low.startswith("ограбить"):
        # ИСПРАВЛЕНО: Если ID пользователя НЕТ в списке Богов — отказываем!
        if message.from_user.id not in GOD_IDS:
            return await message.answer("❌ Только Патриарх может отдавать такие приказы!")
        
        parts = message.text.split()
        amt = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1000 # По умолчанию 1000
        
        conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
        cursor.execute('UPDATE users SET blood = blood + ? WHERE user_id = ?', (amt, message.from_user.id))
        conn.commit(); conn.close()
        
        await message.answer(f"🏥 Патриарх ворвался в банк крови и вынес оттуда <b>{amt}🩸</b>!\nЗапасы пополнены.", parse_mode="HTML")
        return

    # 💀 КОМАНДА: ОБНУЛИТЬ (Иссушить игрока до 0)
    elif text_low == "обнулить" and message.reply_to_message:
        # Проверка на права Бога/Админа
        if message.from_user.id not in GOD_IDS:
            return await message.answer("❌ Эта власть принадлежит только <b>Патриарху</b>!", parse_mode="HTML")
            
        target = message.reply_to_message.from_user
        target_id = target.id
        
        # Защита от случайного обнуления самого себя или других Богов
        if target_id in GOD_IDS:
            return await message.answer("⚠️ Нельзя иссушить Бога!")

        conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
        
        # Ставим кровь на 0. Если хочешь заодно обнулить и банк, 
        # то замени запрос на: 'UPDATE users SET blood = 0, bank = 0 WHERE user_id = ?'
        cursor.execute('UPDATE users SET blood = 0 WHERE user_id = ?', (target_id,))
        
        conn.commit(); conn.close()
        
        await message.answer(
            f"💀 По приказу Патриарха, игрок <a href='tg://user?id={target_id}'>{target.first_name}</a> был полностью иссушен!\n"
            f"Все его запасы крови уничтожены. Баланс: <b>0🩸</b>", 
            parse_mode="HTML"
        )
        return

    # --- ПЕРЕЛИВАНИЕ КРОВИ (Для всех) ---
    if text_low.startswith("перелить") and message.reply_to_message:
        parts = message.text.split()
        
        # 1. Проверка правильности написания команды
        if len(parts) < 2 or not parts[1].isdigit():
            return await message.answer_photo(
                photo=PHOTO_IDS['перелить'],
                caption="⚠️ Как использовать: <code>перелить [сумма]</code> реплаем.",
                parse_mode="HTML"
            )
        
        amt = int(parts[1])
        if amt <= 0: return # Игнорируем нулевые или отрицательные суммы
        
        target = message.reply_to_message.from_user
        
        # 2. Проверка: нельзя переливать самому себе
        if target.id == message.from_user.id:
            return await message.answer_photo(
                photo=PHOTO_IDS['перелить'],
                caption="❌ Нельзя перелить кровь самому себе!",
                parse_mode="HTML"
            )
            
        # 3. Проверка баланса
        if user_data['blood'] < amt:
            return await message.answer_photo(
                photo=PHOTO_IDS['перелить'],
                caption=f"❌ {user_tag}, у тебя нет столько крови в венах!",
                parse_mode="HTML"
            )
            
        # 4. Процесс переливания в базе данных
        conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
        cursor.execute('UPDATE users SET blood = blood - ? WHERE user_id = ?', (amt, message.from_user.id))
        cursor.execute('UPDATE users SET blood = blood + ? WHERE user_id = ?', (amt, target.id))
        conn.commit(); conn.close()
        
        # 5. Успешный результат с фото
        await message.answer_photo(
            photo=PHOTO_IDS['перелить'],
            caption=f"💉 {user_tag} пожертвовал <b>{amt}🩸</b> в вены <a href='tg://user?id={target.id}'>{target.first_name}</a>.",
            parse_mode="HTML"
        )
        return
        
    elif text_low == "обнулить банк" and message.reply_to_message:
        user_id = message.from_user.id
        
        # 1. ПРОВЕРКА НА БОГА: Только админы могут обнулять банки
        if user_id not in GOD_IDS:
            return await message.answer("❌ У тебя нет божественной силы, чтобы опустошать чужие хранилища!")

        target = message.reply_to_message.from_user
        
        # 2. ОБНУЛЕНИЕ В БАЗЕ ДАННЫХ
        conn = sqlite3.connect('vocabulary.db')
        cursor = conn.cursor()
        
        # Предполагаем, что колонка в базе называется 'bank_blood' или 'bank'
        # Если у тебя другое название, просто замени слово bank ниже
        cursor.execute('UPDATE users SET bank = 0 WHERE user_id = ?', (target.id,))
        
        conn.commit()
        conn.close()

        # 3. ОТВЕТ С ФОТО
        target_tag = f'<a href="tg://user?id={target.id}">{target.first_name}</a>'
        
        await message.answer_photo(
            photo=PHOTO_IDS.get('обнулить', PHOTO_IDS['инфо']), # Используем фото 'инфо', если нет специального
            caption=f"⚡️ <b>Божественное вмешательство!</b>\n\nБанковское хранилище {target_tag} было полностью очищено. Теперь там 0🩸.",
            parse_mode="HTML"
        )
        return

    # === КОМАНДА: БИТВА КЛАНОВ (Внутри chat_handler) ===
    if text_low == "битва кланов":
        # Проверка на админа (Бога)
        if message.from_user.id != ADMIN_ID:
            await message.answer("❌ Только Бог может объявить сбор на Битву Кланов!")
            return

        # Создаем кнопку для регистрации участников
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚔️ Вступить в бой", callback_data="join_clan_battle")]
        ])
        
        await message.answer(
            "🔥 <b>ВНИМАНИЕ! ОБЪЯВЛЕН СБОР НА БИТВУ КЛАНОВ!</b> 🔥\n\n"
            "Соберите все силы! Жмите кнопку ниже, чтобы заявить о своем участии.",
            reply_markup=kb,
            parse_mode="HTML"
        )
        return

    if text_low == "начать битву":
        if message.from_user.id != ADMIN_ID: return
        
        if not clan_battle_participants:
            await message.answer("Никто не пришел на битву... Сражаться не с кем.")
            return
            
        await message.answer(f"⚔️ Битва начинается! Участвуют {len(clan_battle_participants)} бойцов!")
        # Тут должна быть твоя логика расчета: кто кого побил
        # После битвы не забудь очистить список:
        # clan_battle_participants.clear()

    # --- ОБНОВЛЕННАЯ ДУЭЛЬ (Вызов с кнопками) ---
    if text_low == "битва" and message.reply_to_message:
        target = message.reply_to_message.from_user
        if target.id == message.from_user.id:
            return await message.answer("❌ Нельзя вызвать самого себя!")

        now = time.time()
        if now - cooldowns['duel'].get(message.from_user.id, 0) < 600:
            rem = int(600 - (now - cooldowns['duel'][message.from_user.id]))
            return await message.answer(f"⏳ Жди {rem//60} мин {rem%60} сек до следующей дуэли.")

        target_data = process_user(target.id, target.first_name)
        if user_data['blood'] < 100 or target_data['blood'] < 100:
            return await message.answer("❌ Для дуэли у обоих должно быть минимум 100🩸!")

        duel_id = f"d_{message.message_id}"
        cooldowns['duel'][message.from_user.id] = now
        
        # Сохраняем в ОЖИДАЮЩИЕ дуэли
        pending_duels[duel_id] = {
            'p1': message.from_user.id, 'p1_name': user_data['nick'], 'p1_role': user_data['role'],
            'p2': target.id, 'p2_name': target_data['nick'], 'p2_role': target_data['role'],
            'chat_id': message.chat.id
        }
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🩸 Принять вызов", callback_data=f"{duel_id}_accept")],
            [InlineKeyboardButton(text="❌ Сбежать (Трус)", callback_data=f"{duel_id}_decline")]
        ])
        
        await message.answer(
            f"⚔️ <a href='tg://user?id={target.id}'>{target.first_name}</a>, тебя вызывает на смертельную дуэль <b>{user_data['nick']}</b>!\n"
            f"Ставка: 100🩸. Примешь бой или струсишь?", 
            reply_markup=kb, parse_mode="HTML"
        )
        return

    # --- СИСТЕМА КЛАНОВ: ВСТУПЛЕНИЕ ---
    if text_low.startswith("выбрать клан"):
        # Список доступных кланов из Сумерек
        clans_list = ["Каллены", "Вольтури", "Денали", "Квилеты", "Египетский клан"]
        
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            clans_str = ", ".join(clans_list)
            return await message.answer(f"🏮 <b>Доступные кланы:</b>\n{clans_str}\n\nНапиши: <code>выбрать клан [Название]</code>", parse_mode="HTML")

        chosen_clan = parts[2].strip()
        if chosen_clan not in clans_list:
            return await message.answer("❌ Такого клана не существует в мире Сумерек!")

        if user_data['clan'] != 'Одиночка':
            return await message.answer(f"⚠️ Ты уже состоишь в клане <b>{user_data['clan']}</b>. Предательство карается смертью!", parse_mode="HTML")

        conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
        cursor.execute('UPDATE users SET clan = ? WHERE user_id = ?', (chosen_clan, message.from_user.id))
        conn.commit(); conn.close()
        
        await message.answer(f"🤝 Поздравляем! Теперь ты часть семьи <b>{chosen_clan}</b>.\nСражайся за честь своего клана!", parse_mode="HTML")
        return

    # --- МАГАЗИН ---
    if text_low == "магазин клана":
        shop_text = (
            "🏪 <b>КЛАНОВЫЙ МАГАЗИН</b>\n\n"
            "1️⃣ <b>Пакет крови</b> (10🩸) — 10 очков\n"
            "2️⃣ <b>Укусы</b> (10 шт) — 10 очков\n"
            "3️⃣ <b>Зелье скорости</b> (Сброс КД) — 15 очков\n\n"
            "Чтобы купить, пиши: <code>купить [номер]</code>"
        )
        await message.answer(shop_text, parse_mode="HTML")
        return

    # --- ЛОГИКА ПОКУПКИ ---
    if text_low.startswith("купить"):
        parts = text_low.split()
        if len(parts) < 2: return
        
        item = parts[1]
        user_id = message.from_user.id
        conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
        
        # Предмет 1: Кровь
        if item == "1" and user_data['points'] >= 30:
            cursor.execute('UPDATE users SET blood = blood + 30, clan_points = clan_points - 30 WHERE user_id = ?', (user_id,))
            msg = "✅ Куплено 30🩸!"
        
        # Предмет 2: Укусы (просто списываем очки как за товар)
        elif item == "2" and user_data['points'] >= 5:
            cursor.execute('UPDATE users SET clan_points = clan_points - 5 WHERE user_id = ?', (user_id,))
            msg = "✅ Куплено 5 укусов!"
            
        # Предмет 3: СКОРОСТЬ (Сброс КД)
        elif item == "3" and user_data['points'] >= 15:
            # Сбрасываем все твои таймеры в 0
            cooldowns['duel'][user_id] = 0
            if 'bite' in cooldowns: cooldowns['bite'][user_id] = 0
            
            cursor.execute('UPDATE users SET clan_points = clan_points - 15 WHERE user_id = ?', (user_id,))
            msg = "⚡️ <b>Зелье скорости выпито!</b>\nТвои кулдауны на битву и укус сброшены."
            
        else:
            msg = "❌ Недостаточно очков или неверный номер предмета!"
            
        conn.commit();
        conn.close()
        await message.answer(msg, parse_mode="HTML")
        return

    # 5. ТРИГГЕРЫ
    if is_private or is_reply_to_bot or is_mentioned:
        for trig, ans in TRIGGERS.items():
            if trig in text_low:
                await message.answer(f"{user_tag}, {random.choice(ans)}", parse_mode="HTML")
                return

    # 6. ВБРОСЫ (раз в 5 сообщений)
    if chat_message_counters[chat_id] % 10 == 0:
        if random.choice(['stk', 'voc']) == 'stk': await message.answer_sticker(random.choice(STICKERS))
        else: await message.answer_voice(random.choice(VOICE_MESSAGES))
# --- ДВИЖОК RPG ДУЭЛЕЙ (Кнопки) ---
# --- ДВИЖОК RPG ДУЭЛЕЙ И ПРИНЯТИЕ ВЫЗОВА ---
# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ---
clan_battle_participants = []

# --- 1. ОБРАБОТКА КНОПОК ДУЭЛИ ---
@dp.callback_query(F.data.startswith("d_"))
async def duel_engine(call: types.CallbackQuery):
    parts = call.data.split("_")
    duel_id = f"d_{parts[1]}"
    action = parts[2]
    user_id = call.from_user.id 

    # Обработка принятия/отказа от вызова
    if action in ["accept", "decline"]:
        if duel_id not in pending_duels:
            return await call.answer("⏳ Время вызова истекло или бой уже идет.", show_alert=True)
            
        duel = pending_duels[duel_id]
        if call.from_user.id != duel['p2']:
            return await call.answer("⛔️ Этот вызов брошен не тебе!", show_alert=True)
            
        if action == "decline":
            del pending_duels[duel_id]
            return await call.message.edit_text(f"🐔 <b>{duel['p2_name']}</b> отказался от боя с <b>{duel['p1_name']}</b>.", parse_mode="HTML")
            
        if action == "accept":
            active_duels[duel_id] = duel
            active_duels[duel_id].update({
                'p1_hp': 100, 'p2_hp': 100, 'turn': duel['p2'], 
                'last_action_time': time.time()
            })
            del pending_duels[duel_id]
            
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🗡 Ударить", callback_data=f"{duel_id}_strike")],
                [InlineKeyboardButton(text="🧠 Стратегия", callback_data=f"{duel_id}_strat"),
                 InlineKeyboardButton(text="💨 Убегать", callback_data=f"{duel_id}_run")],
                [InlineKeyboardButton(text="🏳 Сдаться", callback_data=f"{duel_id}_surr")]
            ])
            
            await call.message.edit_text(
                f"⚔️ <b>БИТВА НАЧАЛАСЬ!</b>\n\n"
                f"[{duel['p1_role']}] <b>{duel['p1_name']}</b>: 100 HP\n⚡️ VS ⚡️\n"
                f"[{duel['p2_role']}] <b>{duel['p2_name']}</b>: 100 HP\n\n"
                f"Ход: <a href='tg://user?id={duel['turn']}'>{duel['p2_name']}</a>",
                reply_markup=kb, parse_mode="HTML"
            )
            asyncio.create_task(check_duel_timeout(duel_id, active_duels[duel_id]['last_action_time'], call.message.chat.id, call.message.message_id))
            return

    # Обработка самой драки
    if duel_id not in active_duels: return await call.answer("Битва окончена.")
    duel = active_duels[duel_id]
    if call.from_user.id != duel['turn']: return await call.answer("Не твой ход!", show_alert=True)
    
    me = 'p1' if call.from_user.id == duel['p1'] else 'p2'
    opp = 'p2' if me == 'p1' else 'p1'
    my_role = duel[f'{me}_role']
    dmg, heal, msg = 0, 0, ""
    
    if action == "strike":
        if my_role == "Бог": dmg = 100; msg = "⚡️ <b>БОЖЕСТВЕННЫЙ УДАР!</b>"
        elif my_role == "Вампир": dmg = random.randint(25, 40); msg = "🧛‍♂️ Смертельный укус!"
        elif my_role == "Страж Вольтури": dmg = 30; msg = "⚖️ Удар Стража!"
        else: dmg = random.randint(15, 30); msg = "🗡 Точный удар!"
    elif action == "strat":
        if my_role == "Провидец": dmg, heal = 15, 15; msg = "👁 Провидец увидел будущее!"
        elif my_role == "Щит": dmg, heal = 20, 10; msg = "🛡 Щит отразил атаку!"
        else: heal = random.randint(15, 25); msg = "🧠 Хитрая тактика."
    elif action == "run":
        if my_role == "Оборотень": heal = 30; msg = "🐺 Регенерация оборотня!"
        else: heal = random.randint(5, 15); msg = "💨 Попытка скрыться."
    elif action == "surr":
        duel[f'{me}_hp'] = 0; msg = "🏳 Смиренная сдача..."

    duel[f'{opp}_hp'] -= dmg
    duel[f'{me}_hp'] = min(100, duel[f'{me}_hp'] + heal)
    
    if duel[f'{opp}_hp'] <= 0 or duel[f'{me}_hp'] <= 0:
        winner_name = duel[f'{me}_name'] if duel[f'{opp}_hp'] <= 0 else duel[f'{opp}_name']
        winner_id = duel[me] if duel[f'{opp}_hp'] <= 0 else duel[opp]
        loser_id = duel[opp] if duel[f'{opp}_hp'] <= 0 else duel[me]
        
        conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
        # Добавляем кровь и очки (проверка существования колонки желательна)
        cursor.execute('UPDATE users SET blood = blood + 100 WHERE user_id = ?', (winner_id,))
        cursor.execute('UPDATE users SET blood = blood - 100 WHERE user_id = ?', (loser_id,))
        conn.commit(); conn.close()

        await call.message.edit_text(f"⚔️ <b>ФИНАЛ БИТВЫ!</b>\n<i>{msg}</i>\n\n🏆 <b>{winner_name}</b> победил и забирает 100🩸!", parse_mode="HTML")
        del active_duels[duel_id]
        return

    duel['turn'] = duel[opp]
    duel['last_action_time'] = time.time()
    
    await call.message.edit_text(
        f"⚔️ <b>ДУЭЛЬ В РАЗГАРЕ</b>\n🔔 <i>{msg}</i>\n\n[{duel['p1_role']}] <b>{duel['p1_name']}</b>: {duel['p1_hp']} HP\n[{duel['p2_role']}] <b>{duel['p2_name']}</b>: {duel['p2_hp']} HP\n\nХод: <a href='tg://user?id={duel['turn']}'>{duel[f'{opp}_name']}</a>", 
        reply_markup=call.message.reply_markup, parse_mode="HTML"
    )
    asyncio.create_task(check_duel_timeout(duel_id, duel['last_action_time'], call.message.chat.id, call.message.message_id))
    await call.answer()

# --- 2. ОБРАБОТКА БИТВЫ КЛАНОВ ---
@dp.callback_query(F.data == "join_clan_battle")
async def join_battle_handler(call: types.CallbackQuery):
    user_id = call.from_user.id
    if user_id in clan_battle_participants:
        return await call.answer("Ты уже в списке бойцов!", show_alert=True)
    clan_battle_participants.append(user_id)
    await call.answer("✅ Готов к бою!")
    await call.message.edit_text(
        f"{call.message.text.split('✅')[0]}\n\n✅ Участников собрано: <b>{len(clan_battle_participants)}</b>",
        reply_markup=call.message.reply_markup, parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("buy_"))
async def process_buying(call: types.CallbackQuery):
    user_id = call.from_user.id
    data = call.data.split("_")
    
    # Обработка покупки роли "БОГ" за рубли
    if data[1] == "god":
        # Ссылка на тебя (сделал кликабельной через HTML)
        owner_link = '<a href="https://t.me/Bradley_Ko">@Bradley_Ko</a>'
        await call.message.answer(
            f"👑 <b>ПОКУПКА СТАТУСА БОГА</b>\n\n"
            f"Эта роль дает абсолютную власть и уникальные привилегии.\n"
            f"💰 Стоимость: <b>3.000 рублей</b>.\n\n"
            f"Для совершения сделки напиши нашему Создателю: {owner_link}",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        await call.answer()
        return

    # Логика для покупок за кровь
    item_type = data[1] # role или boost
    item_name = data[2] # Название роли
    price = int(data[3]) # Цена

    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    # Проверка баланса
    cursor.execute("SELECT blood FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row or row[0] < price:
        await call.answer("❌ Твои жилы пусты! Недостаточно капель крови.", show_alert=True)
        conn.close()
        return

    if item_type == "role":
        # СМЕНА РОЛИ: Списание крови + Сброс силы до 10 (как ты и просил)
        cursor.execute(
            "UPDATE users SET role = ?, strength = 10, blood = blood - ? WHERE user_id = ?", 
            (item_name, price, user_id)
        )
        msg = f"✨ <b>Перерождение завершено!</b>\n\nТеперь твоя роль: <b>{item_name}</b>.\nТвоя сила сброшена до 10. Начни свой путь величия заново!"
    
    elif item_type == "boost":
        # ЛОТЕРЕЯ СИЛЫ: Рандом от 1 до 5
        bonus = random.randint(1, 5)
        cursor.execute(
            "UPDATE users SET strength = strength + ?, blood = blood - ? WHERE user_id = ?", 
            (bonus, price, user_id)
        )
        msg = f"⚡️ <b>Прилив древней мощи!</b>\n\nТы потратил кровь и получил <b>+{bonus}</b> к силе!"

    conn.commit()
    conn.close()
    
    await call.message.edit_text(msg, parse_mode="HTML")
    await call.answer("Сделка совершена успешно!")

@dp.callback_query(F.data.startswith("hunt_start_"))
async def hunt_start_callback(callback: types.CallbackQuery):
    data = callback.data.split("_") # hunt_start_animal_123456
    target_type = data[2]
    user_id = int(data[3])
    
    if callback.from_user.id != user_id:
        return await callback.answer("❌ Это не твоя охота!", show_alert=True)
        
    # Проверка кулдауна перед стартом
    last_hunt = cooldowns['hunt'].get(user_id, 0)
    time_passed = time.time() - last_hunt
    cooldown_time = 7200 if target_type == "animal" else 14400 # 2 часа или 4 часа в секундах
    
    if time_passed < cooldown_time:
        rem_h = int((cooldown_time - time_passed) // 3600)
        rem_m = int(((cooldown_time - time_passed) % 3600) // 60)
        return await callback.answer(f"⏳ Охота недоступна! Жди {rem_h}ч. {rem_m}мин.", show_alert=True)

    # Записываем кулдаун и начинаем игру
    cooldowns['hunt'][user_id] = time.time()
    
    # Настройки охоты: 5 шагов
    active_hunts[user_id] = {
        'type': target_type,
        'attempts': 5,
        'blood_collected': 0
    }
    
    map_kb = generate_hunt_map(user_id)
    text = (f"🌲 <b>Ты вошел в лес...</b>\n"
            f"🎯 Цель: {'Люди' if target_type == 'human' else 'Животные'}\n"
            f"👣 Осталось шагов: <b>5</b>\n\n"
            f"<i>Выбирай локацию осторожно, жертва постоянно перемещается!</i>")
            
    await callback.message.edit_text(text, reply_markup=map_kb, parse_mode="HTML")


@dp.callback_query(F.data.startswith("hunt_step_"))
async def hunt_step_callback(callback: types.CallbackQuery):
    data = callback.data.split("_")
    user_id = int(data[2])
    
    if callback.from_user.id != user_id:
        return await callback.answer("❌ Не мешай чужой охоте!", show_alert=True)
        
    if user_id not in active_hunts:
        return await callback.message.edit_text("❌ Твоя охота уже завершена.")
        
    hunt = active_hunts[user_id]
    hunt['attempts'] -= 1
    
    # --- ЛОГИКА РАНДОМА ---
    # Шансы: 30% найти жертву, 15% ловушка, 55% пусто
    event = random.choices(["prey", "trap", "empty"], weights=[40, 10, 50])[0]
    
    msg_addition = ""
    if event == "prey":
        reward = 100 if hunt['type'] == 'human' else 50
        hunt['blood_collected'] += reward
        target_name = "👤 Человека" if hunt['type'] == 'human' else "🦌 Животное"
        msg_addition = f"✅ <b>УСПЕХ!</b> Ты поймал {target_name} и выпил <b>{reward}🩸</b>!\n"
    elif event == "trap":
        penalty = 20
        hunt['blood_collected'] -= penalty
        msg_addition = f"⚠️ <b>ЛОШВУШКА!</b> Ты наступил на серебряный капкан и потерял <b>{penalty}🩸</b>!\n"
    else:
        msg_addition = "💨 <b>ПУСТО...</b> Здесь только ветер и старые следы.\n"

    # Если шаги закончились
    if hunt['attempts'] <= 0:
        total = hunt['blood_collected']
        
        # Обновляем БД
        if total != 0:
            conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
            # Убеждаемся, что кровь не уйдет в минус
            cursor.execute('UPDATE users SET blood = MAX(0, blood + ?) WHERE user_id = ?', (total, user_id))
            conn.commit(); conn.close()
            
        del active_hunts[user_id]
        
        result_text = "🎉 <b>Охота завершена!</b>\n" if total > 0 else "💀 <b>Охота провалилась!</b>\n"
        result_text += f"🩸 Итоговая добыча: <b>{total}🩸</b>"
        
        return await callback.message.edit_text(msg_addition + "\n" + result_text, parse_mode="HTML")

    # Если шаги еще есть — обновляем карту
    new_map = generate_hunt_map(user_id)
    text = (f"{msg_addition}\n"
            f"👣 Осталось шагов: <b>{hunt['attempts']}</b>\n"
            f"🩸 Собрано: <b>{hunt['blood_collected']}🩸</b>\n"
            f"<i>Жертва испугалась и сменила укрытие! Куда теперь?</i>")
            
    await callback.message.edit_text(text, reply_markup=new_map, parse_mode="HTML")


@dp.callback_query(F.data.startswith("hunt_escape_"))
async def hunt_escape_callback(callback: types.CallbackQuery):
    # Код побега (досрочное завершение с сохранением того, что успел собрать)
    user_id = int(callback.data.split("_")[2])
    if callback.from_user.id != user_id: return
    
    if user_id in active_hunts:
        total = active_hunts[user_id]['blood_collected']
        if total > 0:
            conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
            cursor.execute('UPDATE users SET blood = blood + ? WHERE user_id = ?', (total, user_id))
            conn.commit(); conn.close()
        del active_hunts[user_id]
        await callback.message.edit_text(f"🏃‍♂️ Ты сбежал из леса. \n🩸 Успел унести: <b>{total}🩸</b>", parse_mode="HTML")

# --- 3. ОБРАБОТКА СВАДЕБ ---
@dp.callback_query(F.data.startswith("marry_") | F.data.startswith("refuse_"))
async def marriage_buttons(call: types.CallbackQuery):
    parts = call.data.split("_")
    action = parts[0]
    if action == "refuse":
        return await call.message.edit_text("💔 Сердце разбито... Отказ.")
    
    initiator_id, target_id = int(parts[1]), int(parts[2])
    if call.from_user.id != target_id:
        return await call.answer("Это предложение не для тебя!", show_alert=True)
    
    conn = sqlite3.connect('vocabulary.db'); cursor = conn.cursor()
    cursor.execute('UPDATE users SET partner = ? WHERE user_id = ?', (target_id, initiator_id))
    cursor.execute('UPDATE users SET partner = ? WHERE user_id = ?', (initiator_id, target_id))
    conn.commit(); conn.close()
    await call.message.edit_text("🎉 <b>НОВАЯ СЕМЬЯ!</b> Вы теперь вместе в вечности.", parse_mode="HTML")
# --- ПРИВЕТСТВИЕ НОВЫХ ИГРОКОВ В ГРУППЕ ---
# Это нужно писать как отдельную функцию-обработчик (вне chat_handler)
@dp.message(F.new_chat_members) # Для Aiogram 3 (или content_types=['new_chat_members'] для Aiogram 2)
async def welcome_new_member(message: types.Message):
    for user in message.new_chat_members:
        # Не приветствуем других ботов
        if not user.is_bot:
            await message.answer(
                f"🩸 Свежая кровь в нашей обители! Приветствуем тебя, <a href='tg://user?id={user.id}'>{user.first_name}</a>.\n"
                f"Выбери свой путь, пока луна не скрылась.",
                parse_mode="HTML"
              )
    
@dp.callback_query(F.data.startswith("buy_"))
async def handle_purchases(call: types.CallbackQuery):
    user_id = call.from_user.id
    
    # Разбиваем data с кнопки (например: "buy_role_Человек_1000")
    data = call.data.split("_")
    
    # 1. ОБРАБОТКА ПОКУПКИ РОЛИ БОГА
    if data[1] == "god":
        await call.message.answer(
            f"👑 Чтобы получить роль <b>БОГА</b>, напиши моему создателю.\n"
            f"Цена: <b>3.000₽</b>. Сделка только в ЛС!",
            parse_mode="HTML"
        )
        await call.answer() # Останавливаем часики на кнопке!
        return

    # Извлекаем данные из кнопки для остальных ролей
    item_type = data[1]  # "role" или "boost"
    item_name = data[2]  # "Человек", "Вампир" и т.д.
    price = int(data[3]) # Цена: 1000, 10000 и т.д.

    conn = sqlite3.connect('vocabulary.db')
    cursor = conn.cursor()
    
    try:
        # 2. ИЩЕМ ПОЛЬЗОВАТЕЛЯ В БАЗЕ
        cursor.execute("SELECT blood, role FROM users WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            await call.answer("❌ Сначала напиши что-нибудь в чат, чтобы появиться в базе!", show_alert=True)
            return
            
        current_blood = user_data[0]
        current_role = user_data[1]
        
        # 3. ЗАЩИТА ТВОЕЙ РОЛИ (Бог не может случайно купить Человека)
        if item_type == "role" and current_role == "Бог":
            await call.answer("⚡️ Ты уже обладаешь божественной силой! Смена роли тебе не нужна.", show_alert=True)
            return
            
        # 4. ПРОВЕРКА БАЛАНСА
        if current_blood < price:
            await call.answer(f"❌ Не хватает крови! Нужно: {price}🩸, а у тебя: {current_blood}🩸", show_alert=True)
            return
            
        # 5. ВЫДАЧА РОЛИ И СПИСАНИЕ КРОВИ
        if item_type == "role":
            if current_role == item_name:
                await call.answer(f"⚠️ У тебя уже и так роль {item_name}!", show_alert=True)
                return
                
            # Обновляем базу: списываем кровь и меняем роль
            cursor.execute("UPDATE users SET role = ?, blood = blood - ? WHERE user_id = ?", (item_name, price, user_id))
            conn.commit()
            
            # Меняем текст сообщения с кнопками на текст успеха
            await call.message.edit_text(
                f"✨ Сделка совершена!\nТвоя новая роль: <b>{item_name}</b>\nПотрачено: {price}🩸", 
                parse_mode="HTML"
            )
            
        # сьебались часики уродливые
        await call.answer(f"✅ Успешно куплено: {item_name}!")
        
    except Exception as e:
        print(f"Ошибка в магазине: {e}")
        await call.answer("❌ Произошла системная ошибка при покупке.", show_alert=True)
    finally:
        # закрытааааа
        conn.close()

async def main():
    init_db(); print("Ботяра запущен, сэр! Патрик готов к работе, ПЫР ПЫР НИЩЕТА!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
