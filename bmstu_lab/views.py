from django.http import HttpResponse
from django.shortcuts import render, redirect


all_maps = [
    {'id': 1, 'title': 'Left 2 Die', 'image_url': 'http://127.0.0.1:9000/mybucket/Left_2_Die.webp', 'description': 'Left 2 Die — это созданная Blizzard кооперативная карта для StarCraft II. Он был опубликован в апреле 2011 года.','players':'До 2', 'tileset':'Лунная','overview':'В зависимости от вспышки игроки могут выбрать уровень сложности (4 уровня сложности, как в миссиях WoL. По умолчанию выделена нормальная сложность). Они контролируют базу терранов. Они защищаются от атак «зомби», собирая биомассу, полученную путем убийства специальных отрядов зергов и разрушения зараженных зданий. Их можно потратить на научном объекте для исследования новых юнитов и структур. Эти улучшения применимы к обоим игрокам.' },
    {'id': 2, 'title': 'New Antioch', 'image_url': 'http://127.0.0.1:9000/mybucket/New_Antioch.webp', 'description': 'New Antioch была главным поселением протоссов в этом мире после падения Айура. Он стал местом расположения Цитадели Исполнителей. Протоссы проводили там военные советы с Рашагалом. Под городом была подземная железнодорожная система.', 'players':'До 4','tileset':'Пустошь', 'overview':'New Antioch появляется как карта сумеречной пустоши в StarCraft II. Разрушаемые камни блокируют проход через заднюю дверь на стартовые базы, а есть и другие проходы, заблокированные только блокаторами LoS.'},
    {'id': 3, 'title': 'Aiur Chef', 'image_url': 'http://127.0.0.1:9000/mybucket/Aiur_Chef.webp', 'description': 'Aiur Chef — карта для StarCraft II. Он был опубликован в апреле 2011 года.','players':'До 8', 'tileset': 'Джунгли','overview':'Фанатик (управляемый игроком) путешествует по Айуру, собирая ингредиенты (модели фруктов) и возвращая их на кухню стадиона для приготовления. Игроки также могут сражаться друг с другом, используя такое оружие, как пси-сковородки. Побеждает игрок, набравший наибольшее количество очков за три раунда. Его ведет председатель Кхала, который объявляет секретный ингредиент, необходимый в начале каждого раунда.'},
    {'id': 4, 'title': 'Lost Temple', 'image_url': 'http://127.0.0.1:9000/mybucket/Lost_temple.webp', 'description': 'Затерянный храм — древние руины, расположенные на БелШире. В какой-то момент его нашла группа фракций. Они вступили в конфликт в этом районе.','players':'До 4', 'tileset':'Джунгли','overview':'Lost Temple вернулся в StarCraft II, но был удален из списка рейтинговых игр в феврале 2011 года. Версия FFA была заменена на The Shattered Temple. По состоянию на май 2011 года она занимала пятое место в десятке самых популярных карт игры 1 на 1.Затерянный храм имеет четыре стартовые точки на возвышенности, каждая из которых соединена очень узким проходом с естественным расширением, охраняемым более широким проходом. Природа уязвима для атак наземных осадных единиц, таких как осадные танки. На карте также есть островные расширения и золотые минеральные расширения, охраняемые разрушаемыми камнями.'},
    {'id': 5, 'title': 'StarCraft Master', 'image_url': 'http://127.0.0.1:9000/mybucket/Starcraft_Master.webp', 'description': 'StarCraft Master — это серия из 30 однопользовательских задач по микроменеджменту, которые можно найти в специальном разделе интерфейса пользовательской игры.','players':'1', 'tileset':'Космическая платформа','overview':'У игроков есть возможность «переходить» от испытания к испытанию, а нажатие «F12» позволит игроку просматривать подсказки.StarCraft Master предлагает семь новых достижений, а также новый портрет.StarCraft Master вышел в свет 2 марта 2012 г.'},
    {'id': 6, 'title': 'Atlas Station', 'image_url': 'http://127.0.0.1:9000/mybucket/Atlas_Station.webp', 'description': 'Atlas station — космическая станция, используемая Терранским Доминионом.Когда корабль-тюрьма Доминиона «Морос» остановился на станции для пополнения запасов, на него поднялась Сара Керриган.','players':'До 6', 'tileset':'Космическая платформа','overview':'Космическая станция служит многопользовательской картой в StarCraft II. Он вмещает 8 игроков и был представлен в рейтинге 4 на 4 с выходом Heart of the Swarm. Он покинул рейтинг в начале 6-го сезона.'},
    {'id': 7, 'title': 'Bastion of the Conclave', 'image_url': 'http://127.0.0.1:9000/mybucket/Bastion_of_the_Conclave.webp', 'description': 'Bastion of the Conclave — это карта 3 на 3 для StarCraft II, добавленная в рейтинг во втором сезоне 2017 года. Он был удален из рейтинга в первом сезоне 2019 года.','players':'До 6', 'tileset':'Айур','overview':'Эта карта содержит четыре естественных расширения, а также два островных расширения.'},
    {'id': 8, 'title': 'Moebius Facility XX-1', 'image_url': 'http://127.0.0.1:9000/mybucket/Moebius_Facility_XX1.webp', 'description': '«Moebius Facility XX-1» — это карта 2 на 2 и 4 на 4, созданная для ладдера второго сезона 2016 года Legacy of the Void. Он по-прежнему используется в текущих пулах карт 2 на 2 и 4 на 4.','players':'8', 'tileset':'Платформа Корпуса Мебиуса','overview':'Маршруты расширения кардинально меняются в зависимости от того, где начинает команда противника. Разведайте заранее и спланируйте свою стратегию на ранней, средней и поздней стадии игры вместе со своим союзником.'},
]


def get_maps(request):
    query = request.GET.get('map', '')
    filtered_maps = [map for map in all_maps if query.lower() in map['title'].lower()]
    return render(request, 'maps.html', {'maps': filtered_maps})

def get_map_detail(request, id):
    map_detail = next((map for map in all_maps if map['id'] == id), None)
    if not map_detail:
        return HttpResponse('Карта не найдена', status=404)
    return render(request, 'map_detail.html', {'map': map_detail, 'request': request})


def add_to_cart(request, map_id):
    cart = request.session.get('cart', [])
    if map_id not in cart:
        cart.append(map_id)
    request.session['cart'] = cart
    return redirect('maps')


def view_cart(request):
    cart_maps = [{'id': 1, 'title': 'Left 2 Die', 'image_url': 'http://127.0.0.1:9000/mybucket/Left_2_Die.webp', 'description': 'Описание карты Left 2 Die...'},
                 {'id': 2, 'title': 'New Antioch', 'image_url': 'http://127.0.0.1:9000/mybucket/New_Antioch.webp', 'description': 'Описание карты New Antioch...'}]

    tournaments = [
        {'id': 1, 'name': 'Турнир 1'},
        {'id': 2, 'name': 'Турнир 2'},
        {'id': 3, 'name': 'Турнир 3'},
    ]
    return render(request, 'cart.html', {'cart_maps': cart_maps, 'tournaments': tournaments})