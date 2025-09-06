"""
Usage:
    python manage.py seed_data
"""

from __future__ import annotations

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import User
from restaurants.models import Restaurant, Product
from django.db import transaction


# Opening-hours you can customize per restaurant. Any missing name falls back to the default.
DEFAULT_OPEN_HOURS = "08:00-23:00"
OPEN_HOURS = {
    'Amigos Centar': '08:00-23:00',
    'Amigos Ljubljanska': '08:00-23:00',
    'Amigos Zeleznicka': '08:00-23:00',
    'Beer Garden Debar Maalo': '08:00-23:00',
    'Enriko': '08:00-23:00',
    'Forza Restaurant': '08:00-23:00',
    'Plaza De Toros': '08:00-23:00',
    'Revija Bar & Food': '08:00-23:00',
    'Royal Burger Debar Maalo': '08:00-23:00',
    'Skara Bar': '08:00-23:00',
    'Spizzicotto - EU': '08:00-23:00',
    'SushiCo Zen': '08:00-23:00',
    'Teteks - Karposh': '08:00-23:00'
}

# --- Seed dataset ----------------------------------------------------------------
# Each item: (restaurant_name, description, image_url, cuisine, delivery_time_estimate, [products...])
# Each product: (name, description, price, quantity, image_url, category)
DATA = [
    (
        'Amigos Centar',
        'Доставуваме до Вашата врата',
        'https://korpa.ba/restaurant_uploads/dpkyYY48d8Kn70RlCBxJkc0HoK6mGjS6.jpg',
        'Mexican',
        25,
        [
            (
                'Nachos',
                'Мексикански чипс прелиен со топен кашкавал и пикантен начос кашкавал, сервиран со салса и крем сос',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/BsQOsbCBZe6eKxKzvvXBz0b0aGd0uTJT.jpg',
                'Стартери 🧀'
            ),
            (
                'Guacamole',
                'Свежа кремаста салата од авокадо зачинета со свежи домати, кромид, лимета и коријандер, сервирана со Мексикански чипс',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/3LCIpZNOyaBCDyw4bowAZ0Te9cQTgAvX.jpg',
                'Стартери 🧀'
            ),
            (
                'Roll de pollo',
                'Пилешко филе во крцкава тортиља сервирано со крем сос',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/73I4j0qh7SHlfjweX4xGphalYCW80LE1.jpg',
                'Стартери 🧀'
            ),
            (
                'Onion Rings',
                'Вкусен похован кромид сервиран со сос од мед и сенф, салса и крем сос',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/rwXmagsLeUCnD8F1tLHMqJkxLApI8ZyR.jpg',
                'Стартери 🧀'
            ),
            (
                'Corn Fritters',
                'Вкусни зачинети ќофтиња од пченка, сервирани со пико де гајо, авокадо, крем сос и салса',
                370.0,
                100,
                'https://www.korpa.ba/product_uploads/c71vEsHD07gZaSXvveMEDCCxpOO0Bgs8.jpg',
                'Стартери 🧀'
            ),
            (
                'Cheesy Croquettes',
                'Вкусни крокети од компир и семки од афион сервирани со кремаст сос од растопена горгонзола',
                410.0,
                100,
                'https://www.korpa.ba/product_uploads/WolgJek0aZOKdyh4XJ9LY6Wcjt8z6x2F.jpg',
                'Стартери 🧀'
            ),
            (
                'Shared Platter',
                'Селекција на пршута, пармезан, намаз од горгонзола, маслинки, шери домати и крекери',
                870.0,
                100,
                'https://www.korpa.ba/product_uploads/4SG3wQT7l84wHMZGjMv0u3vhYHULbAuN.jpg',
                'Стартери 🧀'
            ),
            (
                'Salmon Roll',
                'Тортиља, крем сос, лосос, авокадо, спанаќ, киноа, дресинг',
                620.0,
                100,
                'https://www.korpa.ba/product_uploads/2wBpsH6RPvSqY9SCxjEmChrji1lW29WY.jpg',
                'Стартери 🧀'
            ),
            (
                'Grande Totopos',
                'Традиционален Мексикански чипс сервиран со салса, крем сос, начос кашкавал и пико де гајо',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/Mkg8xxLVgsldVGHSfclznkE9ACjAydlU.jpg',
                'Стартери 🧀'
            ),
            (
                'Shrimp Tempura',
                'Панирани шкампи, сервирани со кремаст аиоли сос',
                590.0,
                100,
                'https://www.korpa.ba/product_uploads/OH6XqLGBpIi9Q1fWDdMovpv0jKEKYqN9.jpg',
                'Стартери 🧀'
            ),
            (
                'Cheff Salad',
                'Салата со марула, ајсберг, авокадо, печурки, пиперки, морков, прелиена со свеж дресинг од лимета и крцкава сланина',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/xz1R9iaxvtWWgc7gY0rPaHOjoBFmYdk3.jpg',
                'Салати 🥗'
            ),
            (
                'Amigos Salad',
                'Салата од марула, сецкано пилешко филе и печурки, гарнирана со пармезан, маслинки, мексикански микс и вкусен дресинг',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/iqtDBNxMOFCj28Uyt6l3fweA7rgxXF8E.jpg',
                'Салати 🥗'
            ),
            (
                'Quinoa Salad',
                'Салата со киноа, авокадо, наут, марула, црвен кромид, грашак, грав и пченка, зачинета со дресинг од маслиново масло, сенф и лимон',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/zBy8hR8RKzcPrQt4FDgvhQxIffh4PxeO.jpg',
                'Салати 🥗'
            ),
            (
                'Beef Salad',
                'Сотиран бифтек сервиран врз рукола, шери домат и пармезан прелиено со балсамико дресинг',
                850.0,
                100,
                'https://www.korpa.ba/product_uploads/9k4npQ7VVJHl2Mq5xAbif680tfl2dx3N.jpg',
                'Салати 🥗'
            ),
            (
                'Roncalina Salad',
                'Салата со печени тиквички, модар домат и пиперки, збогатенa со кашкавал, сервирани врз марула и вкусен дресинг',
                440.0,
                100,
                'https://www.korpa.ba/product_uploads/W8KaMz4isIhK9RVx8zZYbIidt14UsPPo.jpg',
                'Салати 🥗'
            ),
            (
                'Caesar Salad',
                'Традиционална Цезар салата со марула, ајсберг, пилешко филе, тостиран леб и пармезан, прелиена со дресинг',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/5Ps3vCqE93CeP4DuScFSGH0UiBCGJXt0.jpg',
                'Салати 🥗'
            ),
            (
                'Cobb Salad',
                'Здрава протеинска салата со авокадо, пилешко филе, варено јајце, домати и крцкава сланина, сервирани врз марула и рукола со дресинг од мед и сенф',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/MnL7X05ukdx0xFJcbgvbOiN7VXT6x73F.jpg',
                'Салати 🥗'
            ),
            (
                'Goat Cheese Salad',
                'Вкусна салата со свеж спанаќ, авокадо, поховано козјо сирење, лешници, домати, маслинки, балзамико дресинг',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/7qKonfVw22HMTU32ItQEtbtfiPVhSfQq.jpg',
                'Салати 🥗'
            ),
            (
                'Rucola Salad',
                'Свежа салата со рукола, шери домати и пармезан, прелиена со балсамик сос',
                410.0,
                100,
                'https://www.korpa.ba/product_uploads/V6OtGnWp7c2vpvBCgk9By39xvlJekIRR.jpg',
                'Салати 🥗'
            ),
            (
                'Quesadilla',
                'Традиционален Мексикански оброк од две тортиљи полнети со растопен кашкавал и ваш избор од пилешко филе, печурки или печени зеленчуци, сервиран со салса и крем сос',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/3DWqFGbUcqzb5pPk0P3s6y5BS8basim8.jpg',
                'Tortillas 🌮'
            ),
            (
                'Burrito',
                'Голема тортиља полнета со ориз, топен кашкавал, крем сос и ваш избор од пилешко филе, телешки рамстек или мешани зеленчуци, сервирано со салса',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/CNBRIRjs9OS6eHNnHUC5vS1BxEHWXnPB.jpg',
                'Tortillas 🌮'
            ),
            (
                'Fajitas',
                'Ваш избор од пилешко, телешко, или свинско месо, припремено со микс од зеленчуци и растопен кашкавал, послужено со свежа салата, шест тортиљи, ориз, пико де гајо, салса и крем сос (Совршено за двајца)',
                950.0,
                100,
                'https://www.korpa.ba/product_uploads/z1Uiy5qqJqm4wiueuHfduvyG0nkeY12a.jpg',
                'Tortillas 🌮'
            ),
            (
                'Taco',
                'Препознатливо Mексиканско јадење од две превиткани тортиљи полнети со зеленчуци, кашкавал, начос сирење и избор од пилешко, телешко или свинско месо. Сервирано со ориз, салса и крем сoс',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/r0WyfLiV30wX8pbsyizrMedWIacFS5Di.jpg',
                'Tortillas 🌮'
            ),
            (
                'Chimichanga',
                'Пикантен оброк од три тортиљи полнети со ориз, два вида кашкавал, халапењос и избор од пилешко, свинско или телешко месo, зачинет со цимет',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/OSchhbdyQcNpOG0GeOvvoTw7qVnA6Phb.jpg',
                'Tortillas 🌮'
            ),
            (
                'Nachos Enchilada',
                'Вкусен и сочен оброк со две тортиљи полнети со растопен кашкавал, пикантен начос кашкавал и пилешко или телешко месо, сервирано со пико де гајо',
                630.0,
                100,
                'https://www.korpa.ba/product_uploads/jkhrEDMHdjsdltsBQiBvr6n7bdNUgEZb.jpg',
                'Tortillas 🌮'
            ),
            (
                'Flautas',
                'Три крцкави тортиљи полнети со фета сирење и пилешко филе, сервирани со пико де гајо',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/wiqpzCoFl6AvHNxCirvGRSXCH30Cnbvo.jpg',
                'Tortillas 🌮'
            ),
            (
                'Tаmpico',
                'Вкусен специјалитет од ориз со печени зеленчуци, печурки, кашкавал и пилешко филе, сервирано во крцкава тортиља со салса и крем сос',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/B8sbQvc2WfekoP6uFl8e5tYMbNbxH5l7.jpg',
                'Tortillas 🌮'
            ),
            (
                'Espinacas Chimichanga',
                'Мексикански специјалитет, домашно тесто полнето со спанаќ, печурки и кромид, сервиран со пико де гајо',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/Msmb7NJGFvu42f5c4ToOyv5TKIDSDQtQ.jpg',
                'Tortillas 🌮'
            ),
            (
                'Amigos Chicken',
                'Пикантно пилешко филе приготвено со микс од зеленчуци, сервирано со компир',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/u5xIzDUEbnLwhMjyvRKhUxdOCN0NN8YT.jpg',
                'Specials 🥩🥘'
            ),
            (
                'Garlic-sage Chicken',
                'Сотирано пилешко филе приготвено со жалфија и лук, сервирано со компир',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/OEp1fNZRwHE0uYVhrnZ8rPcrttUdfSmm.jpg',
                'Specials 🥩🥘'
            ),
            (
                'Parma Chicken',
                'Поховано пилешко филе прелиено со доматен сос и моцарела, сервирано со компир',
                610.0,
                100,
                'https://www.korpa.ba/product_uploads/wxgeLFFQwOnrigioCisJm2W0dut69IZ5.jpg',
                'Specials 🥩🥘'
            ),
            (
                'Herb-pork Saute',
                'Сотирано свинско филе приготвено со микс од ароматични тревки, сервирано со компир',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/whk3ku30zcqHKelcfFWXPkXp6iBwkHUm.jpg',
                'Specials 🥩🥘'
            ),
            (
                'Porcini pork',
                'Сотирано свинско филе прелиено со кремаст сос од вргањ, сервирано со компир',
                810.0,
                100,
                'https://www.korpa.ba/product_uploads/QcOquryp14KHNJWUP9RNyRM0dZcWEDtf.jpg',
                'Specials 🥩🥘'
            ),
            (
                'Summer Paella',
                'Морски плодови готвени на путер со зачинет ориз, зеленчук, лук, шафран и други зачини',
                990.0,
                100,
                'https://www.korpa.ba/product_uploads/ZIsLziqrilwX3LtjUDir9bxdZbh51W0T.jpg',
                'Specials 🥩🥘'
            ),
            (
                'Pepper Beef',
                'Сотиран бифтек прелиен со кремаст сос од шарен бибер, сервиран со компир',
                1650.0,
                100,
                'https://www.korpa.ba/product_uploads/JAQjiesPtuK5jtLE1jufdGfKWziWoNJ6.jpg',
                'Specials 🥩🥘'
            ),
            (
                'Rosemary Beef',
                'Сотиран бифтек прелиен со топол сос од рузмарин, лук и маслиново масло, сервиран со компир',
                1450.0,
                100,
                'https://www.korpa.ba/product_uploads/iD6NaQwwzvIBTzBPjgns8UOsDgwzXVY4.jpg',
                'Specials 🥩🥘'
            ),
            (
                'Chilli Con Carne',
                'Пикантно бавно печено јунешко месо прелиено со кашкавал, сервирано врз ориз со чипс, салца, и павлака',
                790.0,
                100,
                'https://www.korpa.ba/product_uploads/wJjaZf0drr1h5GURYZ6wcwL6DRczVXPs.jpg',
                'Specials 🥩🥘'
            ),
            (
                'Grilled Porcini',
                'Сотиран вргањ на путер, хумус, шери домат, лук, интегрален леб, микросалата',
                550.0,
                100,
                'https://www.korpa.ba/product_uploads/8lcrdhpQKMvTjIZftmaMigLg1MkyvnsW.jpg',
                'Specials 🥩🥘'
            ),
            (
                'Choco Frita',
                'Крцкави тортиљи полнети со растопено чоколадо и лешници',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/wbiead93SnR2f8sf67gPKkWPnSOBwMkn.jpg',
                'Desserts 🍮'
            ),
            (
                'Creme Brulee',
                'Богат млечен крем покриен со крцкава карамела',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/3H5p2bnYM2EeOLv5ghKD5L9gUN3e1pX1.jpg',
                'Desserts 🍮'
            ),
            (
                'Apple Burrito',
                'Тортиља полнета со јаболка и ореви, зачинета со цимет, сервирана со сладолед од ванила',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/brgf7DyJBVDYb5TmwnMgbAWnp06vtp3j.jpg',
                'Desserts 🍮'
            ),
            (
                'Lava Cake',
                'Топол колач полнет со растопено чоколадо сервиран со сладолед',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/SBHBvFSDiQs2Bux4Vdor0pYYB1bZdyi0.jpg',
                'Desserts 🍮'
            ),
            (
                'Churros',
                'Традиционални Мексикански тулумби сервирани со топено чоколадо',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/CcUSldUtNFrFOwHkxGEbkkKyfrvDit2Y.jpg',
                'Desserts 🍮'
            ),
            (
                'Munchmallow Wrap',
                'Tортиља полнета со путер од кикирики, крем од бело чоколадо и манчмалоу, сервирана со сладолед',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/KWJPZgsgF6ZCNpZtLO8LO99cicGK5sg3.jpg',
                'Desserts 🍮'
            ),
            (
                'Peanutbutter Cheesecake',
                'Чизкејк со маскарпоне, кикирики, путер од кикирики, бисквити и чоколадо',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/QzlTYu22vbK5dYclbclrA7H1zK1IvC6W.jpg',
                'Desserts 🍮'
            )
        ]
    ),
    (
        'Amigos Ljubljanska',
        'Доставуваме до Вашата врата',
        'https://korpa.ba/restaurant_uploads/58uf5cfYp70Ai50SkHyIknzFtu2LKg4E.jpg',
        'Mexican',
        25,
        [
            (
                'Burger Amigos',
                '100% јунешки бургер во бриош лепче, начос сос, гвакамоле, крцкава сланина, домат, кромид, ајсберг и чипотле',
                630.0,
                100,
                'https://www.korpa.ba/product_uploads/fQwfsWw392WbZBGssajLWQHdWyj4QckS.jpg',
                'BURGER DAY! 🍔🍟'
            ),
            (
                'Veggie Burger',
                'Ќофте од наут, морков, куркума, ајзберг, сув домат, карамелизиран кромид, пармезан, домат, сенф, бриош лепче, сервиран со помфрит од сладок компир и чипотле сос',
                550.0,
                100,
                'https://www.korpa.ba/product_uploads/l1B68Dz6WSlzuWLxOUU9lNLPSWrTZLHc.jpg',
                'BURGER DAY! 🍔🍟'
            ),
            (
                'Amigos Breakfast',
                'Здрав појадок со две јајца на око, гвакамоле, рукола, интегрален леб, крем сос и пршута',
                370.0,
                100,
                'https://www.korpa.ba/product_uploads/vUZ5jW4d7JJDrdoQRFfZq5LRDgYuJfOY.jpg',
                'Breakfast 🍳'
            ),
            (
                'Breakfast Burrito',
                'Топол тортиља врап полнет со пржени јајца, гвакамоле, едамер и по избор сланина или мешан зеленчук',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/BKTecszf1RkvTLBKKwLxTONFPWZFU1n4.jpg',
                'Breakfast 🍳'
            ),
            (
                'Avocado Humus',
                'Две интеграални лепчиња сервирани со гвакамоле, хумус, јајце и лајм',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/0uTl2N8BWA2GrF8CjXHXdSOfyKMm2fza.jpg',
                'Breakfast 🍳'
            ),
            (
                'Wrap',
                'Тортиља врап полнет со пилешко филе, печени зеленчуци, кашкавал, печурки и фрижол',
                270.0,
                100,
                'https://www.korpa.ba/product_uploads/TT1kgOuuVLuib7IVEKGOU6SAjNZj23nX.jpg',
                'Breakfast 🍳'
            ),
            (
                'Eggs Benedict',
                'Две поширани јајца сервирани со лебче и сланина, прелиени со холандез сос',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/aDYVtF0XjBABQP2BgxPtC3dSxtISvZfB.jpg',
                'Breakfast 🍳'
            ),
            (
                'Amigos Toast',
                'Тортиља полнета со кашкавал и избор од сланина или печурки, сервирана со зачинет компир, крем сос и салса',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/81Ekbd00utv5MBgYpAeZFg8ErIBQqbep.jpg',
                'Breakfast 🍳'
            ),
            (
                'Huevo Rancheros',
                'Традиционален Мексикански појадок со две пржени јајца сервирани врз две тортиљи збогатени со колбас, авокадо, фета сирење и пико де гајо',
                320.0,
                100,
                'https://www.korpa.ba/product_uploads/ddyePdkY4v4Thhzama3ymZKgljCX8NUr.jpg',
                'Breakfast 🍳'
            ),
            (
                'Pancakes',
                'Пет американски палачинки сервирани со крем од маскарпоне и путер од кикирики, јаворов сируп и сезонско овошје',
                370.0,
                100,
                'https://www.korpa.ba/product_uploads/tmFKQ4WBpGxvmglQqJHCsHfDldbfR3xm.jpg',
                'Breakfast 🍳'
            ),
            (
                'Omelette',
                'Омлет со 3 јајца полнет по избор со кашкавал и сланина / кашкавал и печурки',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/u9dvo6lVjVrxh0rUYx04neyHCwnFm5HG.jpg',
                'Breakfast 🍳'
            ),
            (
                'Ljubljanska Sandwich',
                'Бриош лепче, козјо сирење, авокадо, цвекло, рукола, мед, сенф во зрно, зачинет компир и афион',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/ygo0wcPPaHfhB1Drgnr2KERP3hvTyXFL.jpg',
                'Breakfast 🍳'
            ),
            (
                'Salmon Sandwich',
                'Интегрално лепче премачкано со песто, димен лосос, домат, рукола, кромид, сервиран со компири',
                340.0,
                100,
                'https://www.korpa.ba/product_uploads/bnZLpUVjAuvxKdN4Lu69lOXvMZBfOPjD.jpg',
                'Breakfast 🍳'
            ),
            (
                'Nachos',
                'Тотопос прелиен со топен едамер и пикантен начос кашкавал, сервиран со салса и крем сос',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/hDLlyORenRGpghgjzFtxLEkYNnqVJEWj.jpg',
                'To Share 🥰'
            ),
            (
                'Guacamole',
                'Свежа кремаста салата од авокадо зачинета со свежи домати, кромид, лимета и коријандер, сервирана Мексикански чипс',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/dkvV2Hr9RNDNErymk8vZuNmzP2vSjiNj.jpg',
                'To Share 🥰'
            ),
            (
                'Totopos Ljubljanska',
                'Чипс од пченкарна тортиља сервиран со салса, крем сос, начос кашкавал и пико де гајо',
                410.0,
                100,
                'https://www.korpa.ba/product_uploads/CRgjJLGqZ3ouRx9nFagLts1EUCg7UMWI.jpg',
                'To Share 🥰'
            ),
            (
                'Roll de pollo',
                'Пилешко филе во крцкава тортиља сервирано со крем сос',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/ZwsJyce5faHgCoLsmZ6YNxgXZTFqpcEC.jpg',
                'To Share 🥰'
            ),
            (
                'Hummus',
                'Кремаста салата од наут, лук, таан, лимон и маслиново масло, сервирана со крцкава тортиља',
                410.0,
                100,
                'https://www.korpa.ba/product_uploads/iEZqxt6zfLt3xfcV8JbtkaLbnUzfW3Ik.jpg',
                'To Share 🥰'
            ),
            (
                'Salmon Roll',
                'Тортиља, крем сос, лосос, авокадо, спанаќ, киноа, дресинг',
                620.0,
                100,
                'https://www.korpa.ba/product_uploads/SMIX91dm8FgZIVZpct9x2gYA2274hUrz.jpg',
                'To Share 🥰'
            ),
            (
                'Sweet Potato Fries',
                'Зачинет пржен сладок компир сервиран со пикантен чипотле дресинг',
                370.0,
                100,
                'https://www.korpa.ba/product_uploads/yXRpTSBKRnotytXbQYWsxajsPmi0DdZg.jpg',
                'To Share 🥰'
            ),
            (
                'Crispy Goat Cheese',
                'Коцки козјо сирење со афион, послужени со џем од пиперки',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/sYU3EkiK0zksLCZnB55ABJT5IDTXIUQg.jpg',
                'To Share 🥰'
            ),
            (
                'Carnitas Taco',
                'Пикантно бавно печено цепкано свинско месо, кромид, начос кашкавал, фрижол, коријандер и пико де гајо',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/iflIg5dExaqTUnLs9rsvrWBxIKwiRlid.jpg',
                'Tacos 🌮'
            ),
            (
                'Chilli Taco',
                'Традиционално подготвено пикантно телешко месо, начос кашкавал, пико де гајо, свеж коријандер',
                550.0,
                100,
                'https://www.korpa.ba/product_uploads/Msia0UkdTUcic0GlqAntAwDs8LHzfd2t.jpg',
                'Tacos 🌮'
            ),
            (
                'Pollo Taco',
                'Пилешки надкопан, лимета, халапењос, колслау салата и авокадо',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/ns441lsx1duqDzZi8e2UYwyjibIA8WUe.jpg',
                'Tacos 🌮'
            ),
            (
                'Avocado Taco',
                'Печен сладок компир со сос од авокадо, црвен кромид, црвен грав и салата',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/UXSZdqhskTnOWNWQTqcRDsg5LNm6lRIM.jpg',
                'Tacos 🌮'
            ),
            (
                'Shrimp Taco',
                'Ракчиња, авокадо, црвен кромид, дресинг, ајсберг',
                650.0,
                100,
                'https://www.korpa.ba/product_uploads/MW4TdR4bKiTJoV5j0ffouoAoWSznjned.jpg',
                'Tacos 🌮'
            ),
            (
                'Classic Taco',
                'Нашиот препознатлив такос со кашкавал, начос кашкавал, ориз и месо по избор, сервиран со салса и крем сoс',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/Do1cPxpA6ELCDrS50nx1IDdnSR8nxYew.jpg',
                'Tacos 🌮'
            ),
            (
                'Carnitas Special',
                'Бавно печено, зачинето свинско месо сервирано со гвакамоле, пико де гајо, фижол, ајсберг и лимета и топли тортиљи (Совршено за двајца)',
                950.0,
                100,
                'https://www.korpa.ba/product_uploads/r9mFXY7qnffVe8DqIwu2UC19Tejdm4PV.jpg',
                'Specials ✨'
            ),
            (
                'Chili Con Carne',
                'Пикантно бавно печено јунешко месо прелиено со кашкавал, сервирано врз пире од сладок компир со чипс, салца, и павлака',
                790.0,
                100,
                'https://www.korpa.ba/product_uploads/98wJqRMTYaLQamFecjhrYr8HZUxNKo4U.jpg',
                'Specials ✨'
            ),
            (
                'Summer Paella',
                'Морски плодови готвени на путер со зачинет ориз, зеленчук, лук, шафран и други зачини',
                990.0,
                100,
                'https://www.korpa.ba/product_uploads/w5Afl8zaadgVEY19iMBphSedfnyotoR9.jpg',
                'Specials ✨'
            ),
            (
                'Marocan Chicken',
                'Специјалитет од зачинет пилешки надкопан сервиран со хумус, фалавел и колслоу',
                650.0,
                100,
                'https://www.korpa.ba/product_uploads/dPShDl6o5tljO23QGknIfR3YytJN6b5i.jpg',
                'Specials ✨'
            ),
            (
                'Beef Grill',
                'Маринирано јунешко месо печено на оган сервирано со пире од сладок компир, колслоу и микросалата',
                1590.0,
                100,
                'https://www.korpa.ba/product_uploads/EZfmedMKIx9b4It5U1oWKUODul21aFhj.jpg',
                'Grill 🥩'
            ),
            (
                'Pork Grill',
                'Маринирано свинско филе печено на оган сервирано пире од сладок компир, колслоу и микросалата',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/YgKlQavDsNE2PRAPdqb4pAWps20tfyX2.jpg',
                'Grill 🥩'
            ),
            (
                'Chicken Grill',
                'Маринирано пилешко месо печено на оган сервирано со пире од сладок компир, колслоу и микросалата',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/WWkKx0MSWBuSNFTlxMNjHfh9i9U73IL7.jpg',
                'Grill 🥩'
            ),
            (
                'Baby Ribs',
                'Зачинети пикантни свински ребренца маринирани во барбикју сос со зачини, печени на тивок оган, сервирани со пире од сладок компир, колслоу и чипотле сос',
                690.0,
                100,
                'https://www.korpa.ba/product_uploads/z7hhMkEO2jD6YJBsLbkXY2W6U7AgnkgI.jpg',
                'Grill 🥩'
            ),
            (
                'Octopus',
                'Октопод печен на оган сервиран со сладок компир, спанаќ и лајм',
                1800.0,
                100,
                'https://www.korpa.ba/product_uploads/VsdNOZGWwrZ7HmvKCBoGEtxkos0Kfb9m.jpg',
                'Grill 🥩'
            ),
            (
                'Burger Amigos',
                '100% јунешки бургер во бриош лепче, начос сос, гвакамоле, крцкава сланина, домат, кромид, ајсберг и чипотле',
                630.0,
                100,
                'https://www.korpa.ba/product_uploads/DZ9RBXvyFiQnZP4mV6qsnk0LQK07prQY.jpg',
                'Grill 🥩'
            ),
            (
                'Rosemary Beef',
                'Таљата бифтек прелиен со топол сос од рузмарин, лук и маслиново масло, сервиран со пире од сладок компир и микросалата',
                1450.0,
                100,
                'https://www.korpa.ba/product_uploads/xWE0CQUSu8r5f0DNLjuxFot7Kig0yMXa.jpg',
                'Grill 🥩'
            ),
            (
                'Quesadilla',
                'Традиционален Мексикански оброк од две тортиљи полнети со растопен кашкавал и ваш избор од пилешко филе, печурки или печени зеленчуци, сервиран со салса и крем сос',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/XJrNS98FCU4C2rC93bcfTxXw1FmPD2a3.jpg',
                'Classics 🌯'
            ),
            (
                'Burrito',
                'Голема тортиља полнета со ориз, начос кашкавал, едамер, крем сос и ваш избор од пилешко филе, телешки рамстек или мешани зеленчуци, сервирано со салса',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/GzTECGL8GWjFL8J7bUHIKDsBSfx38p8c.jpg',
                'Classics 🌯'
            ),
            (
                'Fajitas',
                'Ваш избор од пилешко, телешко, или свинско месо, припремено со микс од зеленчуци и растопен кашкавал, послужено со свежа салата, шест тортиљи, ориз, пико де гајо, салса и крем сос (Совршено за двајца)',
                950.0,
                100,
                'https://www.korpa.ba/product_uploads/Xkkfb3563sJRTuteVW3xl2Q3Xc8Y2VeJ.jpg',
                'Classics 🌯'
            ),
            (
                'Nachos Enchilada',
                'Вкусен и сочен оброк со две тортиљи полнети со едамер, пикантен начос кашкавал и пилешко или телешко месо',
                630.0,
                100,
                'https://www.korpa.ba/product_uploads/SenMbaFGSlvjxoyBsCMnaP3XafMOnpAA.jpg',
                'Classics 🌯'
            ),
            (
                'Flautas',
                'Три крцкави тортиљи полнети со фета сирење и пилешко филе, сервирани со пико де гајо',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/SlldREh6ewsTImvkvUejAZgGZWGzMR4j.jpg',
                'Classics 🌯'
            ),
            (
                'Falafel',
                'Топчести ќофтиња од наут, кромид, морков и магдонос, сервирани со авокадо дресинг, колслоу и хумус',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/CNSHHqw9vXwbgwfBzj1dRdA5or6JZ9Rr.jpg',
                'Vege 🌿'
            ),
            (
                'Tampico Veggie',
                'Ориз со печени зеленчуци, печурки, и кашкавал, сервирани во топла тортиља со салса и крем сос',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/duiIXf65gEt1tVoXs6AMOpqtqsir8euJ.jpg',
                'Vege 🌿'
            ),
            (
                'Porcini',
                'Сотиран вргањ на путер, хумус, шери домат, лук, интегрален леб, микросалата',
                550.0,
                100,
                'https://www.korpa.ba/product_uploads/xcBRixE8iKA0NznWdQHMvMjzuQtPxud3.jpg',
                'Vege 🌿'
            ),
            (
                'Veggie Burger',
                'Ќофте од наут, морков, куркума, ајзберг, сув домат, карамелизиран кромид, пармезан, домат, сенф, бриош лепче, сервиран со помфрит од сладок компир и чипотле сос',
                550.0,
                100,
                'https://www.korpa.ba/product_uploads/MIW8wLyh4zDiycP23iRZ1ArgwKusGemf.jpg',
                'Vege 🌿'
            ),
            (
                'Ljubljanska Salad',
                'Микс зелена салата, горгонзола, сладок компир, авокадо и карамелизиран орев зачинета со дресинг од маслиново масло, мед и лимон',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/Zh4AlnOyIdYTJthmw30BQnfFPntbTC7p.jpg',
                'Salads 🥗'
            ),
            (
                'Amigos Salad',
                'Нашата препознатлива салата од марула, сецкано пилешко филе и печурки, гарнирана со пармезан, маслинки и вкусен дресинг',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/kN9iPrj9NyBE3ffKMKRzfDLMLympU6gI.jpg',
                'Salads 🥗'
            ),
            (
                'Quinoa Salad',
                'Салата со киноа, црвен кромид, пиперка, грашак, грав и пченка, зачинета со дресинг од маслиново масло, сенф и лимон',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/2iN3EllrT4Iq8GAqkrKBwR1hHbKKHc6G.jpg',
                'Salads 🥗'
            ),
            (
                'Beef Salad',
                'Сотиран бифтек сервиран врз рукола, шери домат и пармезан прелиено со балсамико дресинг',
                850.0,
                100,
                'https://www.korpa.ba/product_uploads/uXcQDIT12ALZOb0UbkmzHNtwRTYwls2w.jpg',
                'Salads 🥗'
            ),
            (
                'Goat Cheese Salad',
                'Вкусна салата со свеж спанаќ, авокадо, поховано козјо сирење, лешници, домати, маслинки и крема балсамико',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/Dk5XVTSqf42xALqetJX8aei5rmjpMv99.jpg',
                'Salads 🥗'
            ),
            (
                'Caesar Salad',
                'Традиционална Цезар салата со марула, ајсберг, пилешко филе, тостиран леб, и пармезан, прелиена со цезар дресинг',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/exwFY5PWvoA2i0YUgEWk9jAYDR50wZiF.jpg',
                'Salads 🥗'
            ),
            (
                'Cobb Salad',
                'Здрава протеинска салата со авокадо, пилешко филе, варено јајце, домати и крцкава сланина, сервирани врз марула и рукола со дресинг од мед и сенф',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/pmNcb6dHFr5lYwXQIJ0JZGbtVXBhXBVY.jpg',
                'Salads 🥗'
            ),
            (
                'Choco Frita',
                'Крцкави тортиљи полнети со растопено чоколадо и лешници',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/QNjO3QoL8yWaebBssHIRwldWvRH5VS5k.jpg',
                'Desserts 🍮'
            ),
            (
                'Peanutbutter Cheesecake',
                'Чизкејк со маскарпоне, кикирики, путер од кикирики, бисквити и чоколадо',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/XMsEWkG3LfOHOq244oQpvZ3yPYYZmJsS.jpg',
                'Desserts 🍮'
            ),
            (
                'Apple Burrito',
                'Тортиља полнета со јаболка и ореви, зачинета со цимет, сервирана со сладолед од ванила',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/NVmtRIk91udTcjQHd3FBYMBMsFC0Fpcj.jpg',
                'Desserts 🍮'
            ),
            (
                'Lava Cake',
                'Топол колач полнет со растопено чоколадо сервиран со сладолед',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/k1zCyZiDBhnlOVr02Kl4V0idEk1QPh0G.jpg',
                'Desserts 🍮'
            ),
            (
                'Churros',
                'Традиционални Мексикански тулумби сервирани со топено чоколадо',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/10CBoPOybuPkE7Gc1hzDHXdJdU7rCs2t.jpg',
                'Desserts 🍮'
            ),
            (
                'Churros Parfait',
                'Млечен ладен крем со лешници и шумско овошје, сервиран врз плетенка од чурос',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/ot1vDwuOBgKw6oArH7b9VGvdZp2xUxVX.jpg',
                'Desserts 🍮'
            ),
            (
                'Pestinos',
                'Пржени топчиња од путер-тесто, сервирани со карамелизирана праска, јаворов сируп и цимет',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/96XnI8lPqijOxkEyrTI5WjKamOO7K73w.jpg',
                'Desserts 🍮'
            )
        ]
    ),
    (
        'Amigos Zeleznicka',
        'Доставуваме до Вашата врата',
        'https://korpa.ba/restaurant_uploads/bWHnrQtlO3bHFacmuEe1NjG7zTvs5ar3.jpg',
        'Mexican',
        25,
        [
            (
                'Класик чизбургер',
                'Блек ангус јунешка плескавица и чедар, врз лепче, сервирани со домати, корнишони, кромид, кечап и сенф, ајсберг, сладок компир, чипотле сос',
                690.0,
                100,
                'https://www.korpa.ba/product_uploads/5pXjnKgsKy9BC7xhZGu7iiBOf5pguIOa.jpg',
                'BURGER DAY! 🍔🍟'
            ),
            (
                'Фета бургер',
                'Блек ангус јунешка плескавица, кремасто зачинето фета сирење, свежи домати и краставица, сервирани со, сладок компир, чипотле сос.',
                690.0,
                100,
                'https://www.korpa.ba/product_uploads/Rs4qH9rFBXyZM2bKmIVygc2zTbP6F4xz.jpg',
                'BURGER DAY! 🍔🍟'
            ),
            (
                'Железничка бургер',
                'Блек ангус јунешка плескавица и сос од горгонзола врз лепче, со додаток на корнишони и сланина, сладок компир и чипотле сос',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/uz92RFciD1fmUuBo6v2VFg0OXWgN7jwB.jpg',
                'BURGER DAY! 🍔🍟'
            ),
            (
                'Фалафел бургер',
                'Фалафел плескавица врз лепче, ајсберг, домат и кромид со црвен хумус. Збогатен со кремасто зазики, слаток компир и чипотле сос.',
                610.0,
                100,
                'https://www.korpa.ba/product_uploads/L1kzdevI7swQlYcvoT30gd2MusDcowy6.jpg',
                'BURGER DAY! 🍔🍟'
            ),
            (
                'Медитеранска салата со киноа',
                'Свежа и хранлива салата со шери домати, краставички, црвен кромид, морков и ајсберг, комбинирана со црн наут и шарена киноа. Зачинета со освежителен лимонов дресинг',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/tmka922X0vpn9gsiADyzprXAnuwfCJlJ.jpg',
                'Салати 🥗'
            ),
            (
                'Пољо салата',
                'Печен пилешки копан, крцкав ајсберг, парчиња авокадо и шери домати и крцкави тортиљи.',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/Cwj6b36l542jnxt3kos2BfPWeOgTkKyw.jpg',
                'Салати 🥗'
            ),
            (
                'Лосос салата',
                'Свеж ајсберг и рукола, надополнети со резанки црвен кромид, маслинки и пржен лосос во афион, збогатени со капери, слатки пиперчиња и микротревки.',
                590.0,
                100,
                'https://www.korpa.ba/product_uploads/c0Q1ucDIiOl3wwTRqcpVMLv4LHX5AIy2.jpg',
                'Салати 🥗'
            ),
            (
                'Бифтек салата',
                'Салата со сочен бифтек, разни зеленчуци, ароматично нане, и рукола, дополнета со микс од печурки и лимонов дресинг',
                890.0,
                100,
                'https://www.korpa.ba/product_uploads/fdTnBb9TDMv89EZ9cVqb8JsaNB3ebvOj.jpg',
                'Салати 🥗'
            ),
            (
                'Дакос класик салата',
                'Јачменов леб натопен во доматен пелат и домати, зачинет со маслиново масло, оригано, кромид парчиња, фета и маслинки.',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/w9ObcvOaOEmtQolEjLOORzkarHFdWIpT.jpg',
                'Салати 🥗'
            ),
            (
                'Железничка салата',
                'Рукола и ајсберг, збогатени со слатко цвекло, кремаста фета, крцкави ореви и црни маслинки со лимонов дресинг',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/TCOmtV5huHJ1uD8VTMfCQBDsFIZv3xJW.jpg',
                'Салати 🥗'
            ),
            (
                'Мароканско мезе',
                'Селекција на хумус, послужен со маслинки, свежи краставици, маринирани артичоки, козјо сирење, урми и шери домати во две бои. Сервирано со топол леб, парченца лимон и крцкави фалафел топчиња.',
                950.0,
                100,
                'https://www.korpa.ba/product_uploads/l4OXmEZUnsIgoF3dd1USzRHegCiL3lKg.jpg',
                'Мезе 🧀'
            ),
            (
                'Мексиканско мезе',
                'Гвакамоле и кремаста кесадија со топен кашкавал, дополнети со начос кашкавал, свежа салса верде и пикантна Сан Маркос салса. Послужено со чипс од тортиља.',
                850.0,
                100,
                'https://www.korpa.ba/product_uploads/54pYgaltVs60dpHRPKcaHcWZTVUfqPaq.jpg',
                'Мезе 🧀'
            ),
            (
                'Медитеранско мезе',
                'Мешавина од кремасти салати од модар патлиџан, фета дип, и класичен зазики, послужени со маслинки и топла пита леб. Комплетирано со маринирани пиперчиња со туна и свеж лимон.',
                990.0,
                100,
                'https://www.korpa.ba/product_uploads/MVr9vvguv8Z9vK7WR9hIUdJ488zb9mYZ.jpg',
                'Мезе 🧀'
            ),
            (
                'Фалафел врз црвен хумус',
                'Четири крцкави фалафел топчиња, послужени со богат доматен хумус и дресинг од зазики, украсено со свежи микротревки',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/6clSqU7PNMKGrNranQ6J1oKBjPKrEZOU.jpg',
                'Предјадења🍴'
            ),
            (
                'Сладок компир со чипотле',
                'Зачинет пржен сладок компир сервиран со пикантен чипотле дресинг',
                370.0,
                100,
                'https://www.korpa.ba/product_uploads/Wtv8JgTyTArexnP7tWqhjYgCUgByDYeY.jpg',
                'Предјадења🍴'
            ),
            (
                'Ќофтиња од тиквичка со зазики',
                'Сочни ќофтиња направени од тиквички, лесни и воздушни, послужени со освежителен зазики сос и фета',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/YgK7yXSfbBH117OXG8fhxDDsTfR5LfW5.jpg',
                'Предјадења🍴'
            ),
            (
                'Шкампи темпура',
                'Панирани шкампи, сервирани со кремаст аиоли сос',
                590.0,
                100,
                'https://www.korpa.ba/product_uploads/hkJSVcEIT7TJVm3nkGOVrAgY5PZ3cKOY.jpg',
                'Предјадења🍴'
            ),
            (
                'Вргањ со хумус',
                'Сотиран вргањ на путер, хумус, шери домат, лук, интегрален леб, микросалата',
                590.0,
                100,
                'https://www.korpa.ba/product_uploads/mFN0YCQ0gM8blWhAgiryobZex0458SN6.jpg',
                'Предјадења🍴'
            ),
            (
                'Начос Железничка',
                'Крцкав тортиља чипс, прелиен со начос кашкавал, пикантни халапењос, свежи домати, и кремаст фрижол. Сервирани со гвакамоле',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/XCiYnuigvMzOGWzodCTzPU15SW6FHl9X.jpg',
                'Предјадења🍴'
            ),
            (
                'Пикантна кесадија',
                'Tортиља полнета со кремасто сирење фета, во придружба на кисела павлака, сочни шери домати, сечкани маслинки и свежа рукола',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/3Dmx6i3mEr4jA4z4dokgWKbLrx4ppg73.jpg',
                'Предјадења🍴'
            ),
            (
                'Крцкаво козјо сирење',
                'Коцки козјо сирење со афион, послужени со џем од пиперки',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/afMgIWURJsd1EaDjJj83nfK3JEUD9Lzn.jpg',
                'Предјадења🍴'
            ),
            (
                'Флаутас со слатко чили',
                'Две панирани тортиљи полнети со грилован батак , кашкавал, слатко чили и кромид.',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/WsWyKrzk4rRz8DpCSyWlTGes1pmqN7dg.jpg',
                'Предјадења🍴'
            ),
            (
                'Фета Гвакамоле',
                'Традиционално кремасто гвакамоле наросено со фета и корен од свеж анасон, сервирано со крцкава тортиља.',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/IgnqUWdFAJaE66nzLCN1zFz9KJgnOX6y.jpg',
                'Предјадења🍴'
            ),
            (
                'Фахита со шарени бабури',
                'Мариниран пилешки батак, сервиран со карамелизиран кромид и шарени бабури. Сервиран со топли тортиљи, гвакамоле, фрижол, течен начос и свеж лајм',
                960.0,
                100,
                'https://www.korpa.ba/product_uploads/Pub1ZpcXVO9IKyYE1tg1rU3S997hDchs.jpg',
                'Специјалитети 🍖'
            ),
            (
                'Домашно Рагу со њоки',
                'Рагу од свинско и телешко месо послужено со њоки. Збогатено со рендан пармезан и свеж босилек',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/ETQzUkXtCPCMeTK0Hmi7vJk2PpOlTm0W.jpg',
                'Специјалитети 🍖'
            ),
            (
                'Рижото со вргањ',
                'Класичено ризото со арботио ориз, збогатено со вргањ. Завршен со путер и рендан пармезан',
                610.0,
                100,
                'https://www.korpa.ba/product_uploads/YtKwMcViEnQYIpCoCrkIYZdPIBR19s8p.jpg',
                'Специјалитети 🍖'
            ),
            (
                'Карне асада со чимичури сос и домашно гвакамоле',
                'Сецкан јунешки рамстек, сервиран со чимичури и свежо гвакамоле, дополнет со микс од црвени и жолти шери домати и пикантни халапењоси. Сервирани со топли тортиљи и гвакамоле',
                1290.0,
                100,
                'https://www.korpa.ba/product_uploads/t23Bg2ULr1aviwBnyoMSBTGk6c1i3o68.jpg',
                'Специјалитети 🍖'
            ),
            (
                'Рижото со шафран',
                'Кремасто ризото приготвен со арборио ориз и путер. Зачинет со шафран и комплетиран со рендан пармезан',
                590.0,
                100,
                'https://www.korpa.ba/product_uploads/4iZ07A7KFvJqqJdRqoT3atWPSihPyCUG.jpg',
                'Специјалитети 🍖'
            ),
            (
                'Шиш кебап со три вида месо и хумус',
                'Пилешки копан, свинско филе и бифтек печени на жар, сервирани со кремаст хумус, зазики и пита лепче',
                820.0,
                100,
                'https://www.korpa.ba/product_uploads/tEzHGZpRgnuZmvOXEEHzzpxKfJFwXjh4.jpg',
                'Специјалитети 🍖'
            ),
            (
                'Фалафел бургер',
                'Фалафел плескавица врз лепче, ајсберг, домат и кромид со црвен хумус. Збогатен со кремасто зазики, слаток компир и чипотле сос.',
                610.0,
                100,
                'https://www.korpa.ba/product_uploads/egugi6IYKMKNdtI6D0EiNDqJjTal3a3f.jpg',
                'Бургери 🍔'
            ),
            (
                'Железничка бургер',
                'Блек ангус јунешка плескавица и сос од горгонзола врз лепче, со додаток на корнишони и сланина, сладок компир и чипотле сос',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/r0xx41e0rhAsTy0aZCJZy2L02KS46jk8.jpg',
                'Бургери 🍔'
            ),
            (
                'Класик чизбургер',
                'Блек ангус јунешка плескавица и чедар, врз лепче, сервирани со домати, корнишони, кромид, кечап и сенф, ајсберг, сладок компир, чипотле сос',
                690.0,
                100,
                'https://www.korpa.ba/product_uploads/6SjNuvYIqfco7cvxe3IrVEZBzhM5oKeQ.jpg',
                'Бургери 🍔'
            ),
            (
                'Фета бургер',
                'Блек ангус јунешка плескавица, кремасто зачинето фета сирење, свежи домати и краставица, сервирани со, сладок компир, чипотле сос.',
                690.0,
                100,
                'https://www.korpa.ba/product_uploads/OTvVD4Ns2Ly64MDd7fOOZ471Ti167nYR.jpg',
                'Бургери 🍔'
            ),
            (
                'Маргарита пица',
                'Доматен сос, моцарела, босилек, маслиново масло, пармезан',
                540.0,
                100,
                'https://www.korpa.ba/product_uploads/icbcn87oOf4xQ1AqwxXpnBIJff3s09Ac.jpg',
                'Наполитанска пица 🍕'
            ),
            (
                'Прошуто и рукола пица',
                'Доматен сос, моцарела, пармезан, рукола, пршута, шери домат',
                720.0,
                100,
                'https://www.korpa.ba/product_uploads/AsII4hqnpyTFikJikCJVGPvtyPlTPVWY.jpg',
                'Наполитанска пица 🍕'
            ),
            (
                'Капричиоза пица',
                'Доматен сос, моцарела, срца од артичоки, шунка, маслинки, пармезан и печурки',
                680.0,
                100,
                'https://www.korpa.ba/product_uploads/PvddoVmGP87UmYXS11nOSYtcKjylpm78.jpg',
                'Наполитанска пица 🍕'
            ),
            (
                'Мортаца пица',
                'Моцарела, мортадела, фстаци, пистачо паста робо, рикота и маслиново масло',
                680.0,
                100,
                'https://www.korpa.ba/product_uploads/aAKfBgYnxJjknhbDOFL8m2sCmClXgsBC.jpg',
                'Наполитанска пица 🍕'
            ),
            (
                'Маринара пица',
                'Доматен сос, лук, маслиново, шери робо, босилок',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/UEnoK5PqiYpyDJXICA2bJJjKmfnNGt1f.jpg',
                'Наполитанска пица 🍕'
            ),
            (
                'Калцоне',
                'Рикота, моцарела, пармезан, шунка и доматен сос',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/dWVXKspgScpYPeCm1NwMuYIBC0HkkJ96.jpg',
                'Наполитанска пица 🍕'
            ),
            (
                'Чинкве формаџи пица',
                'Моцарела, бри, горгонзола, пармезан, рикота',
                570.0,
                100,
                'https://www.korpa.ba/product_uploads/eAT80hNPloKyVSPl4KifjrfUGg7NSm5L.jpg',
                'Наполитанска пица 🍕'
            ),
            (
                'Диавола пица',
                'Доматен сос, моцарела, корте буена пиканте салама и пармезан',
                640.0,
                100,
                'https://www.korpa.ba/product_uploads/pa1r5Gi011daySai21OlkcXw6Qz7dL9R.jpg',
                'Наполитанска пица 🍕'
            ),
            (
                'Фунги и Тартуфо',
                'Моцарела, пармезан, тартуфата, печурки, вргањ, маслиново масло',
                560.0,
                100,
                'https://www.korpa.ba/product_uploads/FYp1su1Wu1L2AugfcU7S1NgqKmBmw1q0.jpg',
                'Наполитанска пица 🍕'
            ),
            (
                'Наполи пица',
                'Доматен сос, моцарела, капери, инчуни, босилок',
                590.0,
                100,
                'https://www.korpa.ba/product_uploads/G4on9HdJ0xul6hnwFUtXd8cMCRB8lqje.jpg',
                'Наполитанска пица 🍕'
            ),
            (
                'Буфалина пица',
                'Доматен сос, биволска моцарела, свеж босилек',
                920.0,
                100,
                'https://www.korpa.ba/product_uploads/RbNO43WvRu1ELkwcBnUur9HdamC6Sz2U.jpg',
                'Наполитанска пица 🍕'
            ),
            (
                'Брезаола пица',
                'Доматен сос, моцарела, пармезан, рукола, брезаола, шери домат',
                830.0,
                100,
                'https://www.korpa.ba/product_uploads/KndP2kCnvSMqFoWaOENGXYh2R4PbqjX8.jpg',
                'Наполитанска пица 🍕'
            ),
            (
                'Аргентински рибај стек',
                'Аргентински рибај стек печен на жар, сервиран со микс печен зеленчук и салата од цвекло и целер',
                2700.0,
                100,
                'https://www.korpa.ba/product_uploads/sHT8NnKnrrAYTPWiyXXTgmmgepgDYMWP.jpg',
                'Мибраса скара 🔥'
            ),
            (
                'Јунешки бифтек',
                'Јунешки бифтек печен на жар, сервиран со микс печен зеленчук и салата од цвекло и целер',
                1790.0,
                100,
                'https://www.korpa.ba/product_uploads/QdfZcBT49DtyIt4uDA1UtszSHQtQ09Hz.jpg',
                'Мибраса скара 🔥'
            ),
            (
                'Свинско филе',
                'Свинско филе печено на жар, сервирано со микс печен зеленчук и салата од цвекло и целер',
                790.0,
                100,
                'https://www.korpa.ba/product_uploads/6QXpCvjVrx2KDUe6eAzC3ixrlsqtlQ7l.jpg',
                'Мибраса скара 🔥'
            ),
            (
                'Пилешки батак',
                'Пилешки батак печен на жар, сервиран со микс печен зеленчук и салата од цвекло и целер.',
                590.0,
                100,
                'https://www.korpa.ba/product_uploads/MwlfeNT38yON7JxJc4ZfOE2WhqFP23bb.jpg',
                'Мибраса скара 🔥'
            ),
            (
                'Бејби свински ребра',
                'Свински ребра печени на жар, сервирани со микс печен зеленчук и салата од цвекло и целер',
                1190.0,
                100,
                'https://www.korpa.ba/product_uploads/yw6twkrjvqjwXu0mzaOEUzB0RUr7yhTE.jpg',
                'Мибраса скара 🔥'
            ),
            (
                'Поркета',
                'Маринирано, бавно печено роловано свинско месо, срвирано со микс печен зеленчук и кремаста салата од цвекло и целер',
                890.0,
                100,
                'https://www.korpa.ba/product_uploads/vXr5HnEHjTcyyvjAvtrpAY2hlfFkAXGE.jpg',
                'Мибраса скара 🔥'
            ),
            (
                'Шпански октопод со пире од целер',
                'Октопод печен на жар, сервиран со пире од целер',
                1800.0,
                100,
                'https://www.korpa.ba/product_uploads/omY1RrFetvnUWgahxom1770Z1Q3TkQjx.jpg',
                'Морско 🐙'
            ),
            (
                'Лосос со пире од целер',
                'Лосос печен на жар, сервиран со пире од целер',
                1100.0,
                100,
                'https://www.korpa.ba/product_uploads/BNIf3z8VZT2hIfHhY1fTg56lmqeS9rRv.jpg',
                'Морско 🐙'
            ),
            (
                'Печен зеленчук',
                '',
                250.0,
                100,
                'https://www.korpa.ba/product_uploads/3SuszwRcjAz7ArxbATdLykzuqTIAsQHN.jpg',
                'Додатоци 🍅'
            ),
            (
                'Пире од целер',
                '',
                250.0,
                100,
                'https://www.korpa.ba/product_uploads/IEdqms5G3hqZ1WseMaOaTricHezfhSMe.jpg',
                'Додатоци 🍅'
            ),
            (
                'Чурос со чоколаден крем',
                '',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/Meicmiy8yfw9jFIlBheVYvMCF6tbYfqs.jpg',
                'Десерти 🥞'
            ),
            (
                'Баскијски чизкејк',
                '',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/arabngpBmcCCRyJX6VF1wiSxGGtUxudf.jpg',
                'Десерти 🥞'
            ),
            (
                'Профитерол со сорбе од малина',
                '',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/IkPUWuWNqngTK6kIOxyOsgeXJzxtkAxS.jpg',
                'Десерти 🥞'
            ),
            (
                'Пита со портокал со сладолед од ванила',
                '',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/NVSJSy9HzsmpzKNKLgqPotZFhf9OhYw1.jpg',
                'Десерти 🥞'
            ),
            (
                'Чоколадна торта',
                '',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/OjZ1PepAHkaYSNLggXqayhH9WfLyiwUw.jpg',
                'Десерти 🥞'
            ),
            (
                'Лава колач со фстак',
                '',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/DZX88f1ymuJX3DCnTFH21W95xqXko926.jpg',
                'Десерти 🥞'
            )
        ]
    ),
    (
        'Beer Garden Debar Maalo',
        'Доставуваме до Вашата врата',
        'https://korpa.ba/restaurant_uploads/CzXlVP5pPXhTSEOBDaPormqc54Qave6j.jpg',
        'Bar & Grill',
        25,
        [
            (
                'Цезар салата 310 гр.',
                'Марула, шери, пилешки стек, кубети, мајонез, коњак, павлака, сенф, пармезан, портокал',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/izgSVqGJQGIpwwRNKxTV544yilDcTGRn.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Похована даска 700 гр.',
                'Зденки, едамер, крокети, моцарела, маслинки, кромид, пилешки прсти',
                1260.0,
                100,
                'https://www.korpa.ba/product_uploads/GQJ3Zywf8F29qHHgaQ4b8TYQBNbwDx1V.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Бир Гарден крилца 500 гр.',
                'Пилешки крилца, зачин',
                340.0,
                100,
                'https://www.korpa.ba/product_uploads/KjHVjuupmEMhQunC5tD8xXLdU4P1sGbG.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'BBQ крилца 500 гр.',
                '',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/xCSkeWjBV2iVsP9ChY8DQt6K7nGmqWoT.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Лути крилца 500 гр.',
                '',
                340.0,
                100,
                'https://www.korpa.ba/product_uploads/Y08UKjcmKa7FWNug6J2Sf4lFPuCyeb4m.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Пилешки прсти 250 гр.',
                'Пилешки стек, јајце, презла, сенф-мед сос, кану помфрит, сусам',
                360.0,
                100,
                'https://www.korpa.ba/product_uploads/K5CM9wKhKrL66fOJfHTLFNO5GTAtmqie.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Бургер Чедар',
                'Блек ангус телешка плескавица, лепче, домат, ајсберг, корнишони, мајонез, кари, кечап, чедар, бургер сос, кану помфрит',
                560.0,
                100,
                'https://www.korpa.ba/product_uploads/45zg3zA1639psHsMRQIlK2zY0MLc8GUe.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Бургер Сланина',
                'Блек Ангус телешка плескавица, лепче, домат, ајсберг, корнишони, зденка, свинска сланина, мајонез, кечап, кари, бургер сос, кану помфрит',
                580.0,
                100,
                'https://www.korpa.ba/product_uploads/QKtu16XRrF8pARhZZKg93EIp0DUiObCh.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Беер Гарден Микс Бургери',
                'Блек Ангус телешка плескавица, лепчиња, домат, свинско ребро, ајсберг, корнишони, бургер сос, зденка, мајонез, кари, кечап, кану помфрит',
                680.0,
                100,
                'https://www.korpa.ba/product_uploads/zw2lw9BsCTxXQycm8letXac7Uw3LecVd.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Чикен бургер',
                'Похован пилешки стек, лепче, домат, ајсберг, корнишони, кану помфрит, мајонез, кари, кечап, сусам',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/7ecIx0T3UqXF2ta73aFwAKJQtGJhlJAP.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Гурманска даска 1кг.',
                'Виенска шницла, свинско ребро, плескавица, пилешки крилца, дебел колбас, тенок колбас, пекарски компир',
                1680.0,
                100,
                'https://www.korpa.ba/product_uploads/EMXsDxyyQOtyfL1FZC0iFgJnOcU8ICjY.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Беер Гарден колбас даска 1кг.',
                'Кезе краинер, брат вурст, бернер вурс, тенок колбас мечка, дебел колбас мечка, тенок колбас атанасовски, пекарски компир',
                1480.0,
                100,
                'https://www.korpa.ba/product_uploads/2gNbpUpsV5HzMz12eTwsZKGxIYlml8Rm.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Тексас кременадла 650 гр.',
                'Свинска кременадла, компир, шери, оригано, босилок, копар',
                1144.0,
                100,
                'https://www.korpa.ba/product_uploads/J75DXWNkyEuFmDW81KXKjiAkrSmqxf9n.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Бејби Рибс 550 гр.',
                'Свински ребра, компир, мед, соја сос, кечап, кафеав шеќер, ворчестер сос',
                690.0,
                100,
                'https://www.korpa.ba/product_uploads/2t2GNJyidyxDWzro1KALL2iOJYWe9dky.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Свинско филе Бир Гарден 400 гр.',
                'Свинско филе, оригано, босилек, копар, компир, сенф',
                708.0,
                100,
                'https://www.korpa.ba/product_uploads/xl2Bm5stuf5N9iOTF367ghPKgTIVouTk.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Пивска Плескавица парче 1кг.',
                'Мелено месо, свинско каре, свинско филе, компир',
                1150.0,
                100,
                'https://www.korpa.ba/product_uploads/JcdGlwKuUPIrOvkhqRvdLmzF6NgWYlKL.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Тенок колбас Атанасовски 200 гр.',
                'Тенок свински колбас, сенф',
                320.0,
                100,
                'https://www.korpa.ba/product_uploads/moeKpqq4brIAMSvFZk3bXAg3Ca2yj1UO.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Дебел колбас Мечка 200 гр.',
                'Дебел свински колбас, сенф',
                360.0,
                100,
                'https://www.korpa.ba/product_uploads/4J26E6K5Et2pZ31dmuaH1R21B37rAIuf.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Кезе Крајнер 200 гр.',
                '2 парчиња свински колбас, сенф',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/hripvutpYVTq5DloUQv9sKieVy7EZHWZ.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Брат Вурст 200 гр.',
                '2 парчиња свински колбас, сенф',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/Lk6QkqwpF7CR6F9BEWluWaQ7sqB4119H.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Бернер Вурст 220 гр.',
                'Австриска виршла, сланина, кашкавал, сенф',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/eSmRTwRR6NUqHv6XpKOzAJJiRPKKMWwA.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Беергарден Штека Ребро 850гр.',
                '',
                1403.0,
                100,
                'https://www.korpa.ba/product_uploads/Rx1OIXzDYiXMrdSPS4z8NRbZyqdQ4wjL.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Телешка кременадла 1кг',
                'Телешки кременадли, зеленчук',
                2050.0,
                100,
                'https://www.korpa.ba/product_uploads/0K1nLvrFKzvZvk5C4pgPWAUwwSF0SsU8.jpg',
                'Акциска понуда - храна 🍗🥨'
            ),
            (
                'Augustiner Hell 0.5',
                '',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/gTqavfcggI4mz41i9bYLdbMLr9CBOcLT.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Benedikter Weiss 0.5',
                '',
                270.0,
                100,
                'https://www.korpa.ba/product_uploads/fC1ct13lK9KbgbNNrx31zFe8xvvkWZA1.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Benediktiner Hell 0.5',
                '',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/L6oh6B1kjGBXq6jcrqSFjhtGYWZdgzQN.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Bitburger 0.5',
                '',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/G1Ix38diPM9GxAtQan3gW7PRKS51YRpI.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Erdinger Weissbier 0.5',
                '',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/7zOA3ckkVXsWHyzUjQ3T39UWTr2zRqio.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Franziskaner Dunkel 0.5',
                '',
                270.0,
                100,
                'https://www.korpa.ba/product_uploads/zYxLGdT9Ee0I7ts5habVOWhTVoAzvgsD.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Franziskaner Weiss 0.5',
                '',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/DhWrnAkbWhFcyBVfoEDNG3nPaBIPOHzU.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Hasen Brau Ausburger non filtered 0.5',
                '',
                330.0,
                100,
                'https://www.korpa.ba/product_uploads/bHsnjETXfNAPecVVl7AXcp7YSYBOD1A6.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Hasen Brau Dunkler Hase 0.5',
                '',
                330.0,
                100,
                'https://www.korpa.ba/product_uploads/gLNcgqCFJKvHQVOqF0kXxLdukafyqlwc.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Hasen Brau Weiser Hase 0.5',
                '',
                330.0,
                100,
                'https://www.korpa.ba/product_uploads/4FGfayy2Z2Zttxp4IC5CaGkjR8E9shiE.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Paulaner Munchener 0.33',
                '',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/iRVzlVy1bC49ja67oAG5zs0w6nJNqMDE.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Paulaner Salvator 0.33',
                '',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/W3QvGxdi6IBjdV9sEb7WTmRMUrJrWMBJ.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Paulaner Weiss 0.33',
                '',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/KbYqu2zo6eWQkdI7Hl0GVj9fHj1l7aCK.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Paulaner Weissbier Dunkel 0.55',
                '',
                270.0,
                100,
                'https://www.korpa.ba/product_uploads/GBRVtTb9pPKQou6GV7k3FYQ3p1GsxcXu.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Schofferhofer Heffewizen Dunkel 0.5',
                '',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/bhXDO1RZujQwFRT3PfYFgFKmbfUa4WRX.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Schofferhofer Kristall Weizen 0.5',
                '',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/bf9s7tVN1ZssPVPHpdWEWl9xjEaecvHz.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Schofferhofer Weiss 0.5',
                '',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/8YzjY0V6ewH6A28vbWl1BM3MsqFb15sb.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Weihenstephaner Heffe Dunkel 0.5',
                '',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/bhmHlzykvqkiTluAwMqJAxFlpvCfU2Yr.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Weihenstephaner Vitus 0.5',
                '',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/CYQV8LtF9ESxRnu2xyJfnsJKFAKL6sTG.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Weihenstephaner Weissbier 0.5',
                '',
                330.0,
                100,
                'https://www.korpa.ba/product_uploads/SJQubwSEShWhLySX53tfptl0iJvR88mN.jpg',
                'Акциска понуда - пиво 🍺'
            ),
            (
                'Бургер Чедар',
                'Блек ангус телешка плескавица, лепче, домат, ајсберг, корнишони, мајонез, кари, кечап, чедар, бургер сос, кану помфрит',
                560.0,
                100,
                'https://www.korpa.ba/product_uploads/vGFw7nrpG7U1GpBunbKnuUbnB2HaFGCM.jpg',
                'BURGER DAY! 🍔'
            ),
            (
                'Бургер Сланина',
                'Блек Ангус телешка плескавица, лепче, домат, ајсберг, корнишони, зденка, свинска сланина, мајонез, кечап, кари, бургер сос, кану помфрит',
                580.0,
                100,
                'https://www.korpa.ba/product_uploads/FpmKwEscEg8K1yrNeE5oeiA5NThryzsa.jpg',
                'BURGER DAY! 🍔'
            ),
            (
                'Беер Гарден Микс Бургери',
                'Блек Ангус телешка плескавица, лепчиња, домат, свинско ребро, ајсберг, корнишони, бургер сос, зденка, мајонез, кари, кечап, кану помфрит',
                680.0,
                100,
                'https://www.korpa.ba/product_uploads/U8HK2Ltqsao524UNrrLbvgmn2WJrbkm8.jpg',
                'BURGER DAY! 🍔'
            ),
            (
                'Чикен бургер',
                'Похован пилешки стек, лепче, домат, ајсберг, корнишони, кану помфрит, мајонез, кари, кечап, сусам',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/zIxc9gkxPUoFg7OkZNgea1yyQ1OSVeyC.jpg',
                'BURGER DAY! 🍔'
            ),
            (
                'Македонска салата 410 гр.',
                'Домат, црвен кромид, пиперка, магдонос, сол, масло',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/vd2gatD2nfYogbyy3QqPGTEsosNLhBIH.jpg',
                'Салати 🥗'
            ),
            (
                'Витаминска салата 320 гр.',
                'Зелена зелка, марула, морков, цвекло, краставица, јаболко, сончоглед, семки, шери',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/Xnq5fOh0zVMWWFRCA7aC3zRMA0qXctcu.jpg',
                'Салати 🥗'
            ),
            (
                'Млечна даска 330 гр.',
                'Овчо сирење, овчи кашкавал, бри сирење, рокфорт сирење, пармезан, сирење во кора',
                1100.0,
                100,
                'https://www.korpa.ba/product_uploads/qmk7l1CpLe5C6UmBlmPzrgfEAS4U8A0H.jpg',
                'Ладни предјадења 🧀'
            ),
            (
                'Сувомесната даска 400 гр.',
                'Свинска пршута, панцета, говедска пршута, мортадела, домашен кулен, миланска салама, сремски колбас',
                1260.0,
                100,
                'https://www.korpa.ba/product_uploads/H5ahqdDJcZ58sCFihP954AaPq4DSEfaF.jpg',
                'Ладни предјадења 🧀'
            ),
            (
                'Овчо сирење 100 гр.',
                '',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/DyMOfbdeT2ycjIcdJYvmFT8V14daraLp.jpg',
                'Ладни предјадења 🧀'
            ),
            (
                'Овчи кашкавал 100 гр.',
                '',
                320.0,
                100,
                'https://www.korpa.ba/product_uploads/GA1aWOKR5IU6gdTP9iknU3YDGYsvmXQ3.jpg',
                'Ладни предјадења 🧀'
            ),
            (
                'Бри сирење 125 гр.',
                '',
                340.0,
                100,
                'https://www.korpa.ba/product_uploads/6DzWD5PQm3jkD7xuYHTJNuKg3RpCufRs.jpg',
                'Ладни предјадења 🧀'
            ),
            (
                'Пармезан 100 гр.',
                '',
                330.0,
                100,
                'https://www.korpa.ba/product_uploads/38SSwgqhtkJmo5Kk7XAdXviVZzsEm1J0.jpg',
                'Ладни предјадења 🧀'
            ),
            (
                'Похован кашкавал едамер',
                '',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/mNIANnlBbwAbR3nAiKKDglVwxrHZMpjM.jpg',
                'Топли предјадења 🍟'
            ),
            (
                'Похован кромид',
                '',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/q7PrKVvYkn0NvymSVrxAI61zq84WN6C4.jpg',
                'Топли предјадења 🍟'
            ),
            (
                'Похована моцарела',
                '',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/JXcXiAGKGVyDvK4HWQUAe7rVxLEU8n11.jpg',
                'Топли предјадења 🍟'
            ),
            (
                'Поховани крокети со печурки',
                '',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/ShfriVXX6sXVRGMw8B8umkAE8bhAchkO.jpg',
                'Топли предјадења 🍟'
            ),
            (
                'Тиквички чипс',
                '',
                250.0,
                100,
                'https://www.korpa.ba/product_uploads/UAk3DK9iRdAIRiiJNJbo4R6n0tUed62N.jpg',
                'Топли предјадења 🍟'
            ),
            (
                'Сланина свинска чипс',
                '',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/zLCg6VDk8LSYbdrjQasnPwUpCpwYX5Z9.jpg',
                'Топли предјадења 🍟'
            ),
            (
                'Сирење во кора',
                'Кравјо сирење, кашкавал, зденка, кора',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/Cj83LE6LiibnbRpi1gbytqwR6RskqtGX.jpg',
                'Топли предјадења 🍟'
            ),
            (
                'Тортиљи со пилешко',
                'Пилешки стек, тортиљи',
                330.0,
                100,
                'https://www.korpa.ba/product_uploads/mSwydF9bBNwMMPds5FpGcPfRnIMSOKWS.jpg',
                'Топли предјадења 🍟'
            ),
            (
                'Помфрит 200 гр.',
                '',
                170.0,
                100,
                'https://www.korpa.ba/product_uploads/Zxztoruh6nQ5mlNOjJxRJ5ifNfi2ElpC.jpg',
                'Топли предјадења 🍟'
            ),
            (
                'Помфрит Беер Гарден 200 гр.',
                'Помфрит, лук, оригано, путер',
                200.0,
                100,
                'https://www.korpa.ba/product_uploads/mgK4Y6D8lij2vKUf65wgE5MvK4rFAy5z.jpg',
                'Топли предјадења 🍟'
            ),
            (
                'Кану помфрит 200 гр.',
                '',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/Y6VCuRoejgIrmRCQKheBTLsGkRTY28zc.jpg',
                'Топли предјадења 🍟'
            ),
            (
                'Помфрит со сирење 200 гр.',
                '',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/3hrplZZlSWnFNnlUZgnSs28tgaKqnmAH.jpg',
                'Топли предјадења 🍟'
            ),
            (
                'Пекарски компир со зачини 200 гр.',
                '',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/Z9Lvqpsq3GHvNAsmUNVsB2BxEQFWcYSV.jpg',
                'Топли предјадења 🍟'
            ),
            (
                'Пивски помфрит 250 гр.',
                'Помфрит, свинско ребро, кашкавал, кечап',
                360.0,
                100,
                'https://www.korpa.ba/product_uploads/u5FGe2Oe67zjiUH6RdisqbX4yAV7uWxG.jpg',
                'Топли предјадења 🍟'
            ),
            (
                'Виенска шницла свинска 400 гр.',
                '',
                530.0,
                100,
                'https://www.korpa.ba/product_uploads/urnTOtMYA3bDCaFLhJKCIXH3tr64sZIU.jpg',
                'Главни јадења 🍖'
            ),
            (
                'Беер Гарден шницла 620 гр.',
                'Свинско каре, јајца, презла, компир, тартар сос',
                990.0,
                100,
                'https://www.korpa.ba/product_uploads/ZUZZx9N90qPrKpoCkrd9mz0yz4uGaNG9.jpg',
                'Главни јадења 🍖'
            ),
            (
                'Виенска шницла мисиркина 400 гр.',
                'Мисиркин стек, јајца, презла, помфрит, тартар сос',
                590.0,
                100,
                'https://www.korpa.ba/product_uploads/xn3cR3bhUR1pXBG9qJOs8vpFMJhvNAdM.jpg',
                'Главни јадења 🍖'
            ),
            (
                'Плескавица свинска 300 гр.',
                'Мелено свинско месо, компир',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/AR7P3dQJZVCyYjpx3NvJCRjoMFj6S1Qp.jpg',
                'Главни јадења 🍖'
            ),
            (
                'Плескавица телешка 300 гр.',
                'Мелено телешко месо, компир',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/cQW8LlwHkR8BCxhqnFPhGSQrNKI6R6Ni.jpg',
                'Главни јадења 🍖'
            ),
            (
                'Heineken 0.33',
                '',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/Hlv4kjFRQqhsrZ37vAAUwBRuSNRE7Fgq.png',
                'Пиво 🍺'
            ),
            (
                'Heineken 0.0% 0.33',
                '',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/xLIn2kFnUZ6GpNkFAUhaJY0PRmhWxoAQ.jpg',
                'Пиво 🍺'
            ),
            (
                'Leffe Blond 0.33',
                '',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/AHPTubC0OvZGSy2tfjvge8i6PbKzwb94.jpg',
                'Пиво 🍺'
            ),
            (
                'Peroni Nastro Azzurro 0.33',
                '',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/DCOXMSxEs5vP2eqgVTaZ1BfHRma6sL9R.jpg',
                'Пиво 🍺'
            ),
            (
                'Peroni Red 0.33',
                '',
                170.0,
                100,
                'https://www.korpa.ba/product_uploads/8K7CfyfYzMSiqTFvxEub5agd79uXKIjz.jpg',
                'Пиво 🍺'
            ),
            (
                'Asahi 0.33',
                '',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/hLv3A8GH4xDS3iqNXeIOjPU1SbZQYuvt.jpg',
                'Пиво 🍺'
            ),
            (
                'Bavaria 0.25',
                '',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/SvxlvYVc5Ju9Ho23Plh9BGqODDdnnfOw.jpg',
                'Пиво 🍺'
            ),
            (
                'Bavaria 0.33',
                '',
                170.0,
                100,
                'https://www.korpa.ba/product_uploads/xknrYk1ukUOvDo0cXecRGSe6YQXJMjR5.jpg',
                'Пиво 🍺'
            ),
            (
                'Blue Moon 0.33',
                '',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/3VI8eJAVUHShq2niNhcq6iEF6ysNRCuc.jpg',
                'Пиво 🍺'
            ),
            (
                'Chimay Belo 0.33',
                '',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/NOzHGw20n8xR8iTqTzAjB4Rrcg3qOEon.jpg',
                'Пиво 🍺'
            ),
            (
                'Chimay Plavo 0.33',
                '',
                480.0,
                100,
                'https://www.korpa.ba/product_uploads/q89DuWzvDT1JYXEDjZH2R68cAL0XQn69.jpg',
                'Пиво 🍺'
            ),
            (
                'Corona 0.33',
                '',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/aFpX58TDCy10OocbhX9UeDgqJPWq7XUF.jpg',
                'Пиво 🍺'
            ),
            (
                'Daura Damm (bez gluten) 0.33',
                '',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/kupyxmB0GiROvYm25pPVcDX3snhwmCBd.jpg',
                'Пиво 🍺'
            ),
            (
                'Daura Marzen Damm (bez gluten) 0.33',
                '',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/Z1EI9lCKKscCxbqpwDgOh3CSTEMzE3xG.jpg',
                'Пиво 🍺'
            ),
            (
                'Esb 0.5',
                '',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/ZfvFpLcFx6e35L2H97DG6q3J83S4fTuD.jpg',
                'Пиво 🍺'
            ),
            (
                'Grolsch 0.45',
                '',
                270.0,
                100,
                'https://www.korpa.ba/product_uploads/lRcuvpyT7OuKXX1mAuKz3HxNDMeoMLre.jpg',
                'Пиво 🍺'
            ),
            (
                'Gulden-Draak 0.33',
                '',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/blCCd66ir2QWhwOcC8lQz7ynq3FYdMAP.jpg',
                'Пиво 🍺'
            ),
            (
                'Kwak 0.33',
                '',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/sfg8sMFWQtrVQqLWCbxFxdjuClotjMnX.jpg',
                'Пиво 🍺'
            ),
            (
                'La Trap Blond 0.75',
                '',
                840.0,
                100,
                'https://www.korpa.ba/product_uploads/iU8ebkaS4ZEubI38biKvlmvgqN3fEk0J.jpg',
                'Пиво 🍺'
            ),
            (
                'La Trap Isidor 0.75',
                '',
                900.0,
                100,
                'https://www.korpa.ba/product_uploads/eFkEjBadrvLHQrmi9CUG7xHgssMlE5fd.jpg',
                'Пиво 🍺'
            ),
            (
                'La Trap Witte Trapist 0.33',
                '',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/AL2apvbgupsbUrFzbFxrOHiz9QrIBaZV.jpg',
                'Пиво 🍺'
            ),
            (
                'La Trap Witte Trapist 0.75',
                '',
                790.0,
                100,
                'https://www.korpa.ba/product_uploads/qH4Eocjf7lb0Zv29VgqEMKcHi8Lu1OWB.jpg',
                'Пиво 🍺'
            ),
            (
                'La Trape Blond 0.33',
                '',
                330.0,
                100,
                'https://www.korpa.ba/product_uploads/l0IUrPCSYrMhaHIDDkyIvxwrj5PS7xSl.jpg',
                'Пиво 🍺'
            ),
            (
                'La Trap Isidor 0.33',
                '',
                340.0,
                100,
                'https://www.korpa.ba/product_uploads/toh1ynTJgG0AgExH38qQg1N5TmqYrEme.jpg',
                'Пиво 🍺'
            ),
            (
                'La Trappe Quadrupel 0.33',
                '',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/xgWgeXcLmD7zjTt7V0oe3qwqz8H2HELt.jpg',
                'Пиво 🍺'
            ),
            (
                'La Trap Witte Trapist 0.75',
                '',
                790.0,
                100,
                'https://www.korpa.ba/product_uploads/RS5ZSCMLFsnPF3fEnq4vhrFu0afb697u.jpg',
                'Пиво 🍺'
            ),
            (
                'La Trap Witte Trapist 0.33',
                '',
                340.0,
                100,
                'https://www.korpa.ba/product_uploads/5L461GF8K5mrgEsmUw7PHqcXpB0jsmtQ.jpg',
                'Пиво 🍺'
            ),
            (
                'London Pride 0.33',
                '',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/l32nqYLopZHDQUl5ks2llaeVFETqVE4O.jpg',
                'Пиво 🍺'
            ),
            (
                'Pilsner Urquell 0.33',
                '',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/tC16ja2NRrUctySHCRRcuTBYoImVc3wZ.jpg',
                'Пиво 🍺'
            ),
            (
                'Tripel Karmeliet 0.33',
                '',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/9y8pClRbej9ZxXCv4xekHzHX2PhrcKOx.jpg',
                'Пиво 🍺'
            ),
            (
                'Weichenstephaner Kellerbier 1516 0.5',
                '',
                370.0,
                100,
                'https://www.korpa.ba/product_uploads/urE3yB6DXhvOn9FD2Fk9vheoBoPFsEsk.jpg',
                'Пиво 🍺'
            )
        ]
    ),
    (
        'Enriko',
        'Доставуваме до Вашата врата',
        'https://korpa.ba/restaurant_uploads/wxj8DkfJAMPwyEC8YvIxDjA3n6csuZ7E.JPG',
        'Italian / Pizza',
        25,
        [
            (
                'Енрико сендвич',
                'Лепиња со сусам, сос од домати, кашкавал, свинска шунка, печурки, мајонез, павлака, оригано (Алергени - глутен, јајца, суcам, млеко)',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/MlERfkHw0uaTvOnFXAGK6zTs8gJCV9td.jpg',
                'Сендвичи 🥪🌮'
            ),
            (
                'Домашен сендвич',
                'Лепиња со сусам, кашкавал, печеница, печурки, мајонез, домати, корнишони, оригано (Алергени - Глутен, сусам, млеко, јајца)',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/VdAsoNAB7CfgekBoQffWPeZxmcL0mkQF.jpg',
                'Сендвичи 🥪🌮'
            ),
            (
                'Туна сендвич',
                'Лепиња со сусам, кашкавал, туна, домати, кромид, зелена салата, мајонез (Алергени - јајца,глутен,сусам,млеко,риби)',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/Sf5Dohg0Q6gWW39IhlRWa0ic3c4Q91MK.jpg',
                'Сендвичи 🥪🌮'
            ),
            (
                'Кулен сендвич',
                'Лепиња со сусам, кашкавал, кулен, печурки, домати, зелена салата, мајонез, павлака (Алергени - јајца,глутен,млеко,сусам)',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/HLTnXU069wYN0ZdCyJoo7zfLBdomWobJ.jpg',
                'Сендвичи 🥪🌮'
            ),
            (
                'Телешкa - Свинскa пршутa сендвич',
                'Лепиња со сусам, кашкавал, марула,домати, телешкa-свинскa пршутa, мајонез (Алергени - јајца,млеко,глутен,сусам)',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/kTudGEv5zILbjZAMqm2zMkDIwwH77maz.jpg',
                'Сендвичи 🥪🌮'
            ),
            (
                'Вегетаријански сендвич',
                'Лепиња со сусам, марула, домати, моцарела, горгонзола, свежи печурки, мајoнез (Алергени - јајца,глутен,млеко,сусам)',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/P3sv2xWEaE8xWPM7xTreafaQAGgLqI2m.jpg',
                'Сендвичи 🥪🌮'
            ),
            (
                'Рукола сендвич',
                'Лепиња со сусам, домати, моцарела,рукола, пршута, босилок, маслинки (Алергени - јајца,млеко,глутен,сусам)',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/6UiceqdKEjX3J70TuDyaGxRsmkSoyQqx.jpg',
                'Сендвичи 🥪🌮'
            ),
            (
                'Пилешки сендвич',
                'Лепиња, пилешки стек, ајдамер, кромид, сенф, шери домати, марула, корнишони, мајонез (Алeргени - јајца,млеко,сусам,сенф,глутен)',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/FKhFLhCoTciNY6Ipz3CIRcVYE2p9mVNW.jpg',
                'Сендвичи 🥪🌮'
            ),
            (
                'Пилешки сендвич со пaрмезан',
                'Лепиња, пилешки стек, пармезан, шери домати, рукола, сенф, мајонез (Алергени - јајца,млеко,глутен,сусам,сенф)',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/QmKfXdXgo8y86qlnG4OfpkPe1w7NMe5K.jpg',
                'Сендвичи 🥪🌮'
            ),
            (
                'Италијански сендвич',
                'Лепиња, мортадела, пармезан, шери домати, рукола, мајонез, јајце (Алергени - јајца, сусам,млеко,глутен)',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/eC0UymhTsVbolZDA0CNDvJoARoACfCr0.jpg',
                'Сендвичи 🥪🌮'
            ),
            (
                'Пилешки сендвич со сланина',
                'Лепиња, пилешки стек, ајдамер, корнишони, кромид, сенф, шери домати, марула, пржена сланина (Алергени - јајца, млеко, сенф, сусам, глутен)',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/KTJYL8XUk7CoikuuEKNkNXs9h5Dnpu3g.jpg',
                'Сендвичи 🥪🌮'
            ),
            (
                'Пилешки сендвич со авокадо',
                'Лепиња, крем од авокадо (авокадо, кравјо сирење, лук), пилешки стек, пржена сланина, шери домати (Алeргени - јајца,глутен,млеко,сусам)',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/jr05T69GT0aHeuzIHjEDa5szIcRO5nFk.jpg',
                'Сендвичи 🥪🌮'
            ),
            (
                'Пилешки песто сендвич',
                'Лепиња, пилешки стек, моцарела, песто сос, шери домати, кромид (Алeргени - јајца,млеко,сусам,глутен,јаткасти)',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/qn1rUnIRPrRCvJPGQspAJ79eECRJU9KQ.jpg',
                'Сендвичи 🥪🌮'
            ),
            (
                'Шопска салата',
                'Домати, краставица, кромид, сирење, маслинка  (Алeргени - Млеко)',
                320.0,
                100,
                'https://www.korpa.ba/product_uploads/YoT24mjlnp7jrKiyk0RcfIgPjcZHCg9f.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Грчка салата',
                'Домати, краставица, кромид, сирење, маслинки, оригано (Алергени - млеко)',
                340.0,
                100,
                'https://www.korpa.ba/product_uploads/sGCeJ56OGhmEohyP9MqSzwV4DZwzoh5r.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Мешана салата',
                'Зелка, марула, ајсберг, краставица, морков, пченка, ротква, маслинка, цвекло',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/d83rxaVk4MCpg5vXUHtnMQchePGYu8hN.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Туна салата',
                'Марула, ајсберг, краставица, лимон, кромид, туна, ротква, маслинка (Алергени - риби)',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/fPdaayNb324PHKVqBiVbgK484fP6C8qg.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Енрико салата',
                'Рукола, марула, ајсберг, маслинки, шери домати, пармезан, пршута',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/F2KvWZ4f1MHTpU8nZdFAzrRF2vLMsI4t.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Рукола - Шери домат салата',
                'Рукола, шери, домат, пармезан  (Алергени - млеко)',
                320.0,
                100,
                'https://www.korpa.ba/product_uploads/8Q5BApDY8QOSrssZKyMd3JvqqwgZaw5p.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Тробојна салата',
                'Домати, моцарела, авокадо, босилок  (Алергени- млеко)',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/ZEzxGlzotULlRosHaRkHs1YEaqtG2OaK.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Капрезе салата',
                'Домати, босилок, моцарела, маслиново масло',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/DncCu4snpLp4gV9CLFfewXz2tlC9B2UT.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Цезар салата',
                'Марула, ајсберг, пилешки стек, печени лепчиња, пармезан, јајцe (Алергени - глутен, јајца, млеко)',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/yK1RmaTKiVOyUsQOFL8z1mkVm5ZnQRtq.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Ница салата',
                'Туна, рукола, ајсберг, кромид, јајце, шери домати, маслинки, лимон (Алергени - јајца, риба)',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/JwwTPpywv6D3Xo0ujKs5jhnKLWNmBqrD.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Шкампи салата',
                'Шкампи, авокадо, рукола, ајсберг, шери домати, лимон  (Алeргени - черупници)',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/LeZ2sCzdNIRWXs5CQymyBZ8LGAcfF92F.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Горгонзола Ореви салата',
                'Ајсберг, рукола, плаво сирење, јаболко, ореви, шери домати (Алергени - јаткасти, млеко)',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/2GM2aydCVpOkMxiwFPYt7ZVl4WBaXAt2.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Брокула салата',
                'Брокула, шери домат, млад кромид, пармезан, борово семе, маслинки  (Алергени - млеко, јаткасти)',
                360.0,
                100,
                'https://www.korpa.ba/product_uploads/pQnfCZg8dtDV0v6SiEOKSnUTctUd1Ibb.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Спанаќ - јагоди салата',
                'Млад спанаќ, јагоди, кравјо сирење, карамелизиран ореви, дресинг (Алергени - млеко, јаткасти)',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/80PB9u4gseFWPOhdoEWX03ExUBY9idqJ.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Спанаќ - Сланина салата',
                'Млад спанаќ, авокадо, дресинг,сушен домат, црвен кромид, сланина пржена',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/5HcUL1a08RjDMhpLQ9X537ja6unFynN9.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Шампињони на путер',
                '(Алергени - млеко)',
                320.0,
                100,
                'https://www.korpa.ba/product_uploads/DOnpmB4PIfjz8yooFsnyk6923Enp4RXJ.jpg',
                'Ордевери 🧀🥓'
            ),
            (
                'Похован кашкавал',
                '(Алeргени - глутен, млеко, јајца)',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/JYCWT1JOzM0NcKAGA7l4AYo75aIjB2uk.jpg',
                'Ордевери 🧀🥓'
            ),
            (
                'Италијанска Паста салата',
                'Фусили, шери домат, авокадо, моцарела, босилок, маслиново масло (Алергени- јаткасти,млеко)',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/pw6Ltyv5872O5bNng0y3r2fES9cxxbnL.jpg',
                'Паста Салати 🥗🍝'
            ),
            (
                'Туна Паста салата',
                'Фусили, шери домат, млад кромид, маслинки, туна, магдонос, јајце (Алeргени, јајца, риби)',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/nHrZKTf9MrZFFbBLzJOFeRAI0zpRx0Al.jpg',
                'Паста Салати 🥗🍝'
            ),
            (
                'Брокула Пилешка Паста салата',
                'Фусили, шери домат, брокула, млад кромид, пилешки стек, пармезан  (Алергени - млеко)',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/mCazleeoWmZPLycvg9hr1xSozWPnEcjb.jpg',
                'Паста Салати 🥗🍝'
            ),
            (
                'Омлет Енрико',
                'Јајца, кашкавал, шунка, печурки, павлака, маслинки, феферони, оригано, фурнарина (Алергени - јајца, млеко)',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/c7XnwHYNrdb81IEcJSw0fcHH5IE392hf.jpg',
                'Омлети 🥘🥚🧈'
            ),
            (
                'Маргарита пица',
                'Сос од домати, кашкавал, оригано, маслинка (Алергени - глутен, млеко, јајца)',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/KeVHRjyfnGMd3uwn9vhUiBTuagMX7yJn.jpg',
                'Пици 🍕'
            ),
            (
                'Вегетаријана пица',
                'Сос од домати, кашкавал, печурки, оригано (Алергени - глутен, млеко, јајца)',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/YUzYal9sUf2h7duf4PV3llW1mgxgi6Mv.jpg',
                'Пици 🍕'
            ),
            (
                'Наполитана пица',
                'Сос од домати, кашкавал, шунка, оригано (Алергени - глутен, јајца, млеко)',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/6Q1asUJ7JaXqY6xy9lRZJydShIY1VJdt.jpg',
                'Пици 🍕'
            ),
            (
                'Капричиоза пица',
                'Сос од домати, кашкавал, шунка, печурки, оригано (Алергени - глутен, јајца, млеко)',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/AqgYZj8u6H4fKhQ1pI4ePkFqP6QszHjT.jpg',
                'Пици 🍕'
            ),
            (
                'Преклопена пица',
                'Сос од домати, кашкавал, шунка, печурки, сусам, оригано (Алергени - глутен, јајца, млеко,)',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/njLOskbIQJJnwpvyeVzJQ7zBJvcoONaU.jpg',
                'Пици 🍕'
            ),
            (
                'Везувио пица',
                'Сос од домати, кашкавал, шунка, печурки, јајце, оригано (Алергени - глутен, јајца, млеко)',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/HtbS91pMHDLU73DRwUhinnKAT3uxRs8R.jpg',
                'Пици 🍕'
            ),
            (
                'Стелато пица',
                'Сос од домати, кашкавал, шунка, печурки, павлака, оригано (Алргени - глутен, јајца, млеко)',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/9NQGYerVAMayXZPdV1gHDrilpC1EdfHE.jpg',
                'Пици 🍕'
            ),
            (
                'Мајонеза пица',
                'Сос од домати, кашкавал, шунка, печурки, мајонез, оригано (Алергени - глутен, јајца, млеко)',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/1ITfsqCfFyzJfFxNvWaMBHY4ZtBH0s7T.jpg',
                'Пици 🍕'
            ),
            (
                'Кватро стаџоне пица',
                'Сос од домати, кашкавал, шунка, сланина, колбас, оригано, павлака, печурки, феферони, маслинка (Алергени - глутен, јајца, млеко)',
                500.0,
                100,
                'https://www.korpa.ba/product_uploads/9DpYQbRnwWRaX4GzASFbhnS81kX86W8x.jpg',
                'Пици 🍕'
            ),
            (
                'Морски свет пица',
                'Сос од домати, кашкавал, туна, школки, ракчиња, октопод, маслинки, лук, оригано (Алергени - глутен, млеко, јајца, мекотелци, черупници)',
                560.0,
                100,
                'https://www.korpa.ba/product_uploads/w0okQ30tpQKMlCoqNIi5EajRMTqzhEr0.jpg',
                'Пици 🍕'
            ),
            (
                'Зелена пица',
                'Сос од домати, кашкавал, домати,пиперки, кромид, маслинки, оригано (Алергени - глутен, млеко, јајца)',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/LLHD2lji1zIrw79qNY9UPhdxzQyiUOX1.jpg',
                'Пици 🍕'
            ),
            (
                'Капричиоза со зеленчук',
                'Сос од домати, кашкавал, шунка, печурки,домати, пиперки, кромид, маслинки (Алергени - глутен, млеко, јајца)',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/RDHopyiksgfZKdHT1LjRkm6faxcnFPBW.jpg',
                'Пици 🍕'
            ),
            (
                'Наполитана со зеленчук',
                'Сос од домати, кашкавал, домати,пиперки, кромид, маслинки (Алергени - глутен, јајца, млеко)',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/DQNZcpZvZIngCmtK2dUbtSkjiB4dyR0v.jpg',
                'Пици 🍕'
            ),
            (
                'Вегетаријана со зеленчук',
                'Сос од домати, кашкавал, печурки, домати, пиперки, кромид, маслинки, оригано (Алергени - Глутен, јајца, млеко)',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/ytgRPgjKAcSD0twkTpHlJ5qyPQL2J4V0.jpg',
                'Пици 🍕'
            ),
            (
                'Кватро салами пица',
                'Сос од домати, кашкавал, сланина, свински пршут, кулен, суџук, маслинка, феферони, павлака, оригано (Алергени - глутен, јајца, млеко)',
                520.0,
                100,
                'https://www.korpa.ba/product_uploads/lCt0Z0IEUNFKz5iyeZKj5AnNv3LLqXuB.jpg',
                'Пици 🍕'
            ),
            (
                'Помодорина пица',
                'Сос од домати, кашкавал, шери домати, босилок, лук, маслинки (Алергени - глутен, млеко, јајца)',
                440.0,
                100,
                'https://www.korpa.ba/product_uploads/hkwvJxbGnlkTeOLNnQg37cOYfguKgmcv.jpg',
                'Пици 🍕'
            ),
            (
                'Енрико пица',
                'Сос од домати, кашкавал, шунка, печурки,сланина, јајце, феферони, маслинки, оригано(Алергени - глутен, јајца,млеко)',
                500.0,
                100,
                'https://www.korpa.ba/product_uploads/AknyCsvx9hpqPfCCrLNhTYaBMIx1fEnr.jpg',
                'Пици 🍕'
            ),
            (
                'Свински-Телешки пршут пица',
                'Сос од домати, кашкавал, пршут, оригано (Алергени - глутен, јајца, млеко)',
                500.0,
                100,
                'https://www.korpa.ba/product_uploads/1QKuKot3KUT7n8dXnIrJF3JmDy3NyiMS.jpg',
                'Пици 🍕'
            ),
            (
                'Кулен пица',
                'Сос од домати, кашкавал, кулен, маслинки, оригано (Алергени - глутен, јајца, млеко)',
                500.0,
                100,
                'https://www.korpa.ba/product_uploads/qItsDEDBtpNCRKzWgx2mjocJid9VqlC3.jpg',
                'Пици 🍕'
            ),
            (
                'Ориентална пица',
                'Сос од домати, кашкавал, суџук, јајце, маслинки, оригано (Алергени - глутен, јајца, млеко)',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/0OfioKmWjqGQpCKxng9bjuVTN1gXKF2N.jpg',
                'Пици 🍕'
            ),
            (
                'Диавло пица',
                'Сос од домати, кашкавал, кулен, пиперка, кромид, феферони, маслинки (Алергени - глутен, млеко , јајца)',
                500.0,
                100,
                'https://www.korpa.ba/product_uploads/xJ2CCLGBcey0vatZQw1ta6HYLPVZ1zlq.jpg',
                'Пици 🍕'
            ),
            (
                'Шкампи пица',
                'Соc со домати, моцарела, шкампи, рукола, маслинки, пармезан, лук (Алергени - глутен, јајца, млеко, черупници)',
                520.0,
                100,
                'https://www.korpa.ba/product_uploads/PKCIitqSXxxgUHoAOo0kDFyunRjw525Z.jpg',
                'Пици 🍕'
            ),
            (
                'Кватро формаџи пица',
                'Сос од домати, ајдамер, горгонзола,моцарела, пармезан, оригано (Алeргени - глутен, млеко, јајца)',
                500.0,
                100,
                'https://www.korpa.ba/product_uploads/vMvHQ3PDzlH5uU6o6tH2WxXAPNHqrcam.jpg',
                'Пици 🍕'
            ),
            (
                'Пармиџана пица',
                'Сос од домати, кашкавал, лук, пармезан, модар патлиџан, оригано (Алергени - глутен, јајца, млеко)',
                440.0,
                100,
                'https://www.korpa.ba/product_uploads/ep9UoGK3d9nH3I2b7R2OOAccCljH1Eq8.jpg',
                'Пици 🍕'
            ),
            (
                'Вргањ пица',
                'Сос од домати, кашкавал, вргањ, оригано, лук, магдонос (Алергени - глутен, јајца, млеко)',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/G8YE1rrVKVYmUEPZ0S12pgXxae2OLdjV.jpg',
                'Пици 🍕'
            ),
            (
                'Рукола пица',
                'Сос од домати, моцарела, рукола, пршут, босилок, маслинки (Алергени - глутен, млеко, јајца)',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/Zb6WxbVl7smRtkRnbpamserngIRPpJMF.jpg',
                'Пици 🍕'
            ),
            (
                'Карбонара пица',
                'Сос од домати, кашкавал, сланина, јајце, пармезан, оригано (Алергени - глутен, јајца,млеко)',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/6cbouq40KryNidF2NPlm8cvX7mxZRPdz.jpg',
                'Пици 🍕'
            ),
            (
                'Кари пица',
                'Сос од домати, кашкавал, пилешки стек, кромид, кари (Алергени - глутен, јајца, млеко)',
                480.0,
                100,
                'https://www.korpa.ba/product_uploads/55CZoqSEhVaJjZtcVXuixwP1jw11bI1x.jpg',
                'Пици 🍕'
            ),
            (
                'Пица Брокула',
                'Сос од домати, кашкавал, брокула, шери домат, лук, пармезан, борово семе (Алергени - глутен, млеко, јајца)',
                440.0,
                100,
                'https://www.korpa.ba/product_uploads/mcR0PrgJS0zMEbav58pthVrcuOK7Ptau.jpg',
                'Пици 🍕'
            ),
            (
                'Кордон блу пица',
                'Сос од домати, кашкавал, шунка, пилешки стек, презла, пармезан (Алергени - глутен ,млеко, јајца)',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/d3tNcbdsJdLALJvTqkSV26Vl5jTZkCOz.jpg',
                'Пици 🍕'
            ),
            (
                'Хаваи пица',
                'Сос од домати, кашкавал, оригано, шунка, ананас (Алергени - глутен, млеко, јајца)',
                480.0,
                100,
                'https://www.korpa.ba/product_uploads/MyZKXVCyj8tBPFV65W4BprQnVWDQrFGR.jpg',
                'Пици 🍕'
            ),
            (
                'Тиквици пица',
                'Сос од домати, тиквици, шери домати, лук, кашкавал, кравјо сирење, босилок (Алергени - глутен, јајца,млеко)',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/dCTOPTYBWtliX8azxqbadQeISc15L2h6.jpg',
                'Пици 🍕'
            ),
            (
                'Панцерота Кордон блу',
                'Доматен сос, кашкавал, шунка, пилешки стек (Алергени - глутен,јајца,млеко)',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/o4663OAhyzMXSONMIET6IPUOzGLo5UMS.jpg',
                'Панцероти 🧀👨\u200d🍳'
            ),
            (
                'Панцерота',
                '',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/X55OR8fr007cXlIqvxntZDmclu9fK3CW.jpg',
                'Панцероти 🧀👨\u200d🍳'
            ),
            (
                'Пастрмајлија - Свинско месо и зачини',
                '(Алергени - глутен)',
                360.0,
                100,
                'https://www.korpa.ba/product_uploads/mKMU9h53KBropgi1tZKq3csbeTXX2U4O.jpg',
                'Пастрмајлии 👩\u200d🍳'
            ),
            (
                'Пастрмајлија - Свинско месо, зачини и јајце',
                '(Алергени - Глутен, јајца)',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/PSOJTzqT3t9lZ7dPcgccePYVMGqPOUEh.jpg',
                'Пастрмајлии 👩\u200d🍳'
            ),
            (
                'Пастрмајлија - Свинско месо, зачини и сирење',
                '(Алергени - Глутен, млеко)',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/ftVHxsJSgD8aJ5OBuzkPhgrauCflU6jc.jpg',
                'Пастрмајлии 👩\u200d🍳'
            ),
            (
                'Пастрмајлија - Свинско месо, зачини, јајце и сирење',
                '(Алергени - Глутен, jajца, млеко)',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/L9DyYYVmiLYj0JCi8L6XNogtjXnyZVer.jpg',
                'Пастрмајлии 👩\u200d🍳'
            ),
            (
                'Фурнарини со сусам',
                '(Алергени - Глутен)',
                140.0,
                100,
                'https://www.korpa.ba/product_uploads/ZYa4I5F5qOOAZU0cNg6uzQhEPeGhFjhl.jpg',
                'Фурнарини 🥖'
            ),
            (
                'Фурнарини со лук',
                '(Алергени - Глутен)',
                140.0,
                100,
                'https://www.korpa.ba/product_uploads/cGv1sFs5kriDVVD3XY2V9qZKwzCVsagx.jpg',
                'Фурнарини 🥖'
            ),
            (
                'Фурнарини со маслинки',
                '(Алергени - Глутен)',
                160.0,
                100,
                'https://www.korpa.ba/product_uploads/paSE9tdZ5JbtlT015W6DqtTlP5Wqrq2M.jpg',
                'Фурнарини 🥖'
            ),
            (
                'Фурнарини со кашкавал',
                '(Алергени - Глутен)',
                160.0,
                100,
                'https://www.korpa.ba/product_uploads/kkFrbcXpTVqY6fJSaeV38QVPxOsNLSZs.jpg',
                'Фурнарини 🥖'
            ),
            (
                'Болоњезе сос - сува паста',
                'Сос од домати, телешко мелено месо, зачини (Алергени - сулфур диоксид, целер)',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/B3eEhFnErTKHl054jgzmqj2CUrLBgLrO.jpg',
                'Паста 🍝'
            ),
            (
                'Фунги сос - сува паста',
                'Слатка павлака, шунка, печурки, путер, зачини, кашкавал (Алергени - млеко)',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/esQSTVIcmV5hq1kBVkWmwBJBRMFNSoH3.jpg',
                'Паста 🍝'
            ),
            (
                'Фунги сос - свежа паста',
                'Слатка павлака, шунка, печурки,путер, зачини, кашкавал (Алергени - млеко)',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/T6XbdM6I5MsDJCXtHNGka9ys4ju61luA.jpg',
                'Паста 🍝'
            ),
            (
                'Аматричијано сос - сува паста',
                'Слатка павлака, сос од домати, печеница, путер, кромид, чили (Алергени- млеко)',
                410.0,
                100,
                'https://www.korpa.ba/product_uploads/fv53Otzoo0Vism5n593R0S8hxIYNp1Hg.jpg',
                'Паста 🍝'
            ),
            (
                'Аматричијано сос - свежа паста',
                'Слатка павлака, сос оддомати, печеница, путер, кромид, чили (Алергени млеко)',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/uJ55bPBfNGQz5teThZIf8GRiMZw6eGZp.jpg',
                'Паста 🍝'
            ),
            (
                'Песто сос - сува паста',
                'Mагдонос, босилок, лук, борово семе, пармезан, маслиново масло (Алергени - јаткасти, млеко)',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/cEZ1vXq3KgyZL6h1vW8X866KhV9JdL9n.jpg',
                'Паста 🍝'
            ),
            (
                'Песто сос - свежа паста',
                'Магдонос, босилок, лук, борово семе,пармезан, маслиново масло (Алергени - јаткасти, млеко)',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/nCjfG7BWnjNmL2kCOj09TR8Btek4IR43.jpg',
                'Паста 🍝'
            ),
            (
                'Базилико - сува паста',
                'Cос од домати, босилок, лук, пармезан, маслиново масло (Алергени - млеко)',
                410.0,
                100,
                'https://www.korpa.ba/product_uploads/O5KTai1YoVllyUlzoAmslULc4s3P65mJ.jpg',
                'Паста 🍝'
            ),
            (
                'Базилико - свежа паста',
                'Сос од домати, босилок, лук, пармезан, маслиново масло(Алергени - млеко)',
                440.0,
                100,
                'https://www.korpa.ba/product_uploads/ndAgBW0jvEAcOK2syhFySVEAZ7c7kYqw.jpg',
                'Паста 🍝'
            ),
            (
                'Арабијата - сува паста',
                'Чили, лук, домати, босилок, маслиново масло',
                410.0,
                100,
                'https://www.korpa.ba/product_uploads/OgVWwJPImyE7xB57GpZqG2lybm8T1HlK.jpg',
                'Паста 🍝'
            ),
            (
                'Арабијата - свежа паста',
                'Чили, лук, домати, босилок, маслиново масло',
                440.0,
                100,
                'https://www.korpa.ba/product_uploads/w6Xvdjqol9rMGYHgI44gRSsF6Do9MR6o.jpg',
                'Паста 🍝'
            ),
            (
                'Морски свет - сува паста',
                'Слатка павлака, ракчиња, школки, октопод, магдонос, зачини, белo вино (Алергени - млеко, риби, черупници, целер)',
                520.0,
                100,
                'https://www.korpa.ba/product_uploads/uCvfn9MJFzFqkVnSxlOkIceFmBXKm8kN.jpg',
                'Паста 🍝'
            ),
            (
                'Морски свет - свежа паста',
                'Слатка павлака, ракчиња, школки, октопод, магдонос, зачини, белo вино (Алергени - млеко, риби, черупници, целер)',
                540.0,
                100,
                'https://www.korpa.ba/product_uploads/X89Cjf6llWSyVOScUIsvXqF1WsnOAqsv.jpg',
                'Паста 🍝'
            ),
            (
                'Сос со вргањ - сува паста',
                'Слатка павлака, вргањ, лук, пармезан, магдонос (Алергени - млеко)',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/1MVbO4uOBiQzRmYc6daQlAUxULw6HhqI.jpg',
                'Паста 🍝'
            ),
            (
                'Сос со вргањ - свежа паста',
                'Слатка павлака, вргањ, лук, пармезан, магдонос (Алергени - млеко)',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/Amy16yz1zb77lpL1HQGepknqjWd2LyLN.jpg',
                'Паста 🍝'
            ),
            (
                'Пилешки сос со зелен лимон - сува паста',
                'Слатка павлака, пилешко, зелен лимон, лук, пармезан (Алергени - млеко)',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/1sld3yt2ySQlkGIWtxBzhjbbOCMlGETo.jpg',
                'Паста 🍝'
            ),
            (
                'Пилешки сос со зелен лимон - свежа паста',
                'Слатка павлака, пилешко, зелен лимон, лук, пармезан (Алергени - млеко)',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/efBqbm2N16N03R9iySYJzWpbLzI4QlZH.jpg',
                'Паста 🍝'
            ),
            (
                'Пилешки сос со кари - сува паста',
                'Слатка павлака, пилешко, свежи печурки, кари, пармезан (Алергени - млеко)',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/a09Gjx0JCkPywoMHRsfUq0lqpBZmWc16.jpg',
                'Паста 🍝'
            ),
            (
                'Пилешки сос со кари - свежа паста',
                'Слатка павлака, пилешко, свежи печурки, кари, пармезан (Алергени - млеко)',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/M5WE1yFwwHr3d8IxPTgTPae8GKlN9yEf.jpg',
                'Паста 🍝'
            ),
            (
                'Пршут - сува паста',
                'Слатка павлака, путер, пршут, зачини, пармезан (Алергени - млеко)',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/8SZEK8StyXWxFvOqdxHSzjpqtYMpHTaf.jpg',
                'Паста 🍝'
            ),
            (
                'Пршут - свежа паста',
                'Слатка павлака, путер,пршут, зачини, пармезан (Алергени - млеко)',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/zNq9wdTPArANu7wUBar8wliNC1GWWxTV.jpg',
                'Паста 🍝'
            ),
            (
                'Пилешко со спанаќ - сува паста',
                'Слатка павлака, пилешко, песто, кромид, шери домати, спанаќ, маслиново масло (Алергени - млеко)',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/EB13nUy6VJyPnsLG38LHGozMFEAaCnAR.jpg',
                'Паста 🍝'
            ),
            (
                'Пилешко со спанаќ - свежа паста',
                'Слатка павлака, пилешко, песто, кромид, шери домати, спанаќ, маслиново масло (Алергени - млеко)',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/fGvoSBzpH1kZYMSF3KfoOyuxPvYIBbNU.jpg',
                'Паста 🍝'
            ),
            (
                'Горгонзола - Ореви - свежа паста',
                'Слатка павлака, плаво сирење,ореви, пармезан (Алергени - черупници, млеко)',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/R0Wky1WqBtNNJnuLRoGK6aovqRI62kYN.jpg',
                'Паста 🍝'
            ),
            (
                'Горгонзола - Ореви - сува паста',
                'Слатка павлака, плаво сирење,ореви, пармезан (Алергени - черупници, млеко)',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/MhwaMGgIIuXtERXlBU1gbpj8Sp2hLLJB.jpg',
                'Паста 🍝'
            ),
            (
                'Лазањи со свежо тесто',
                'Бoлоњезе сос, бешамел, пармезан, кашкавал (Алергени - целер, сулфур диоксид, млеко)',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/PWLFvVncalspHWepv8GFhN7NbCd8FyWn.jpg',
                'Паста 🍝'
            ),
            (
                'Болоњезе сос - свежа паста',
                '',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/py8iKbzh4NvP19FOv5hgz1DEKekvZ5dh.jpg',
                'Паста 🍝'
            ),
            (
                'Тирамису',
                '(Алергени - глутен, јајца, млеко, јакасти)',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/hxBbGra66qEunkK783af5iNa9SI8DH1g.jpg',
                'Десерти 🍰🍮'
            ),
            (
                'Топло ладно',
                '(Алергени - Jajца, млеко)',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/IL87i2s0MQO5qi7hP93INEcyrHDkz7vH.jpg',
                'Десерти 🍰🍮'
            ),
            (
                'Палачинки',
                '2 палачинки со додаток по избор',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/jSPYQY85pq3ioVeg3U9Ucrspijvy4ici.jpg',
                'Палачинки 🥞'
            )
        ]
    ),
    (
        'Forza Restaurant',
        'Доставуваме до Вашата врата',
        'https://korpa.ba/restaurant_uploads/0JDyoHzEriqnVJXDzPUpuqALJWkXzzRL.jpg',
        '',
        25,
        [
            (
                'Брускети со доматен џем & Фета сирење',
                'Брускети, џем од домати, фета сирење',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/bhvmYwSVe4fn4gqLwxBZoXvw236SgOGA.jpg',
                'Предјадења🍴'
            ),
            (
                'Брускети Форца',
                'Брускети со тапанада од маслинки и сушен домат, мус од козјо сирење и мармалад од црвени пиперки',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/MMRn1KdtoUSLR6L1605Ij3jgUDY0f8cV.jpg',
                'Предјадења🍴'
            ),
            (
                'Брускети со лосос',
                'Брускети со лосос, крем сир, чери домат, копар',
                270.0,
                100,
                'https://www.korpa.ba/product_uploads/dJsQQ2er52hJ7FVMtRf9KV2U3ZQIYUf2.jpg',
                'Предјадења🍴'
            ),
            (
                'Мус од козјо сирење со слатко шумско овошје',
                'Козјо сирење, крем сир, шумско овошје, тортиља',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/UToYozYpMVNVAQjkyjJGyJJo3EJ6e3lz.jpg',
                'Предјадења🍴'
            ),
            (
                'Паштета од 4 сирења со мармалад од пиперки',
                'Паштета од мешани сирења, ореви, мармалад од црвени свежи пиперки, брускети',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/ewi9tHkV3mVtkXi4cxIewRKZbFJjbGcX.jpg',
                'Предјадења🍴'
            ),
            (
                'Лепиња со кајмак',
                'Пица лепиња, кајмак, црн сусам',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/a4O3ZI1BjW7mVBbkzXJ23c4FdXCR8O9E.jpg',
                'Предјадења🍴'
            ),
            (
                'Бомба Иберико со пикантен сос',
                'Крокета од компир и свинско Иберико, со Aglio Olio и томато пикантен сос',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/qGnoHTEKNSun3NyykBTBigqzdjM9bIv1.jpg',
                'Предјадења🍴'
            ),
            (
                'Крокети со пршута во Aglio e Olio сос',
                'Поховани крокети со свинска пршута со Aglio Olio сос',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/YgTCajqSIdr1vrwnAfV3rNOMN3Qi80KA.jpg',
                'Предјадења🍴'
            ),
            (
                'Пататас Бравас',
                'Зачинет компир со пикантен сос',
                250.0,
                100,
                'https://www.korpa.ba/product_uploads/hBfC4cEqTBaIBDy0FDsdSK9GCQZCKNSd.jpg',
                'Предјадења🍴'
            ),
            (
                'Школки во маринада',
                'Школки во маринада со тостирани брускети',
                480.0,
                100,
                'https://www.korpa.ba/product_uploads/r5e8uYszXAZ4KBDgLNmg8bMWYl54Bem1.jpg',
                'Мезе 🧀'
            ),
            (
                'Бејби лигњи',
                '200гр поховани бејби лигњи, 100гр помфрит, сос од лимон и маслинов зејтин, прилог листови крцкав компир',
                640.0,
                100,
                'https://www.korpa.ba/product_uploads/oqjYvQFd9asHa2uuMnh8WhmBVLzkFHHY.jpg',
                'Мезе 🧀'
            ),
            (
                'Ракчиња во лук Al Ajillo',
                'Ракчиња гамбери, лук, маслиново масло, чили пиперка, брускети',
                660.0,
                100,
                'https://www.korpa.ba/product_uploads/crAhFzokGK75q5D5JeUKBDzYKSrzNhcz.jpg',
                'Мезе 🧀'
            ),
            (
                'Форца Шеф салата',
                'Марула, рукола, димен кашкавал, свежи шампињони, свеж домат, сушен домат, пармезан, дресинг со балсамико',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/iLThRKMUoYwTKKKL0Ec8rxor8hO5LgQ6.jpg',
                'Салати 🥗'
            ),
            (
                'Капрезе салата',
                'Домати, свежа моцарела, босилек, екстра маслинов зејтин',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/KME1tSvCbZeIBmUtGNpQBJySpAUT68Bl.jpg',
                'Салати 🥗'
            ),
            (
                'Тиквица модар патлиџан салата',
                'Тиквица, модар патлиџан, краставица, рукола, моцарела, пармезан, пченка, чери домат, сусам',
                270.0,
                100,
                'https://www.korpa.ba/product_uploads/i5qm3MEWBQcGGEI5HP3EAcb3lA1bGsIR.jpg',
                'Салати 🥗'
            ),
            (
                'Салата со козјо сирење со дресинг од бадем',
                'Марула, рукола, козјо сирење, бадем, крушка, маслиново масло, дресинг од бадеми',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/xiisEN6QKAJWlBMuuWtyFVCseEl0SL4K.jpg',
                'Салати 🥗'
            ),
            (
                'Ајсберг салата со димен лосос и закиселен лимон',
                'Ајсберг салата, димен лосос, закиселен лимон, капари, копар, сенф, маслинов зејтин',
                410.0,
                100,
                'https://www.korpa.ba/product_uploads/APQ926rofDcLkn95qtvQLFfXtJID2Vcg.jpg',
                'Салати 🥗'
            ),
            (
                'Микс зелени салати со зачинети ракчиња и лимон',
                'Марула, рукола, радич, ракчиња, манго, лимон, маслинов зејтин',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/jNQyelfjKaDwolwHKxI7Vrt8g67IogRt.jpg',
                'Салати 🥗'
            ),
            (
                'Салата со бифтек, праска и горгонзола',
                'Рукола, спанаќ, бифтек таљата, праска, горгонзола, екстра маслинов зејтин',
                440.0,
                100,
                'https://www.korpa.ba/product_uploads/0KOgiTZ3IJQJ71jm8ReG6QgTw9al31Vc.jpg',
                'Салати 🥗'
            ),
            (
                'Протеинска салата со пилешко и авокадо',
                'Криспи пилешки стек, рукола, спанаќ, краставица, кромид, шери домат, ѓумбир, авокадо, ореви, фета сирење, дресинг од калинка',
                360.0,
                100,
                'https://www.korpa.ba/product_uploads/HjGtOF6JGOBJndXHCCOhDiZNMdGi6V8q.jpg',
                'Салати 🥗'
            ),
            (
                'Цезар салата',
                'Ајсберг марула, пилешко на скара, кубети, пченка, шери домат, оригинален цезар дресинг, пармезан',
                340.0,
                100,
                'https://www.korpa.ba/product_uploads/BtM8stuCTm8ZjG984VzWHrGIYjiguUG4.jpg',
                'Салати 🥗'
            ),
            (
                'Грчка салата',
                'Домати, краставица, зелена пиперка, кромид, маслинки, магдонос, екстра маслинов зејтин, фета сирење, оригано',
                250.0,
                100,
                'https://www.korpa.ba/product_uploads/xDIMkDOR3TgJa0pPHIAmqm8Qxkfu4oBD.jpg',
                'Салати 🥗'
            ),
            (
                'Грин салата',
                'Марула, рукола, зелка, краставица, домати, фета сирење, балзамов оцет, маслинов зејтин, микс зачини за салата',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/bz6ywDIalGX4vpCB1v93uWeAYtVnetmm.jpg',
                'Салати 🥗'
            ),
            (
                'Тзатзики таратор салата',
                '',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/dwEuyj86VDLcZShXLMSZDVL6FaKDfxqm.jpg',
                'Салати 🥗'
            ),
            (
                'Фета и црвена пиперка',
                '',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/n3k3t1BsPeMIQkHTTeZN59rxt2VWyKzI.jpg',
                'Салати 🥗'
            ),
            (
                'Македонска домашна салата',
                'Домат цел, печена пиперка, овчо сирење, магдонос, маслиново',
                270.0,
                100,
                'https://www.korpa.ba/product_uploads/2kkiLZvjl70yRPL1izfTMIktKrd6Grn4.jpg',
                'Салати 🥗'
            ),
            (
                'Ravioli Burro E Salvia',
                'Домашни равиоли полнети со спанаќ и рикота, во сос од путер и жалфија',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/mN3X2nGJlKKUVPZ5a6IuKZQDiKYTvhAZ.jpg',
                'Паста 🍝'
            ),
            (
                'Ravioli Di Mortadella E Pistacchi',
                'Домашни равиоли полнети со мортадела и рикота, во сос од путер и ф’стаци',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/xFjKvrr0GdauAMQyEYxqazlLjTDulud8.jpg',
                'Паста 🍝'
            ),
            (
                'Ravioli E Ricotta Di Limone',
                'Домашни равиоли полнети со лимон и рикота, во сос од путер и пармезан',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/5nVVIvRAZl2TtJeLKpFkR7d0sLsissgq.jpg',
                'Паста 🍝'
            ),
            (
                'Linguine Frutti Di Mare',
                'Лингвини паста со месо од школки, вонголи, ракчиња, лигњи, пелат сос, пармезан',
                560.0,
                100,
                'https://www.korpa.ba/product_uploads/lCsaTzKRk1a4ybRRGeHTHS0PH01MkZRP.jpg',
                'Паста 🍝'
            ),
            (
                'Tagliatelle Gamberi',
                'Таљатели паста, гамбери, праз, бело вино, пармезан',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/DF7aAqjFvykiqvlB3SA3huQ4zKllBsGn.jpg',
                'Паста 🍝'
            ),
            (
                'Linguini Alle Vongole',
                'Лигвини со школки вонголи, чери, босилок, лук, пармезан, чили пиперка',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/9Ndleyy1vZF3lvUrSSLHdFXga9Nwv9zG.jpg',
                'Паста 🍝'
            ),
            (
                'Tagliatelle Al Fungi',
                'Таљатели, пире од вргањ, шампињони, тартуфа крема, пармезан',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/5nJ9X6S3dxYoDbcYbv4X054MJVjLD2p7.jpg',
                'Паста 🍝'
            ),
            (
                'Gnocchi Toscana',
                'Домашно месени њоки, jунешки бифтек, говедска пршута, печурки, пармезан',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/7eAldmE2H8q4ayEQem9stBtxoy8WaQWU.jpg',
                'Паста 🍝'
            ),
            (
                'Gnocchi Quattro Formaggi',
                'Домашно месени њоки, алфредо сос',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/NRsCPlV1whx2eoVIkKecbEDl9sTHBbc5.jpg',
                'Паста 🍝'
            ),
            (
                "All'Amatriciana",
                'Паста по избор, сос од домати, кромид, панчета, пекорино',
                160.0,
                100,
                'https://www.korpa.ba/product_uploads/7YmbhBpOrUW6njIWP0zppWR1zpVVvHzE.jpg',
                'Паста 🍝'
            ),
            (
                'Alla Carbonara',
                'Паста по избор, јајца, сланина, пекорино',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/N5OubOvwPJPD9GFECoqhEElQ5UtQjDeN.jpg',
                'Паста 🍝'
            ),
            (
                'Linguini 4 Pomodorini',
                'Лингвини со 4 врсти домати, пармезан',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/0K8tlDbIMhfAOqDKIJSx6OD7WUy9PXRE.jpg',
                'Паста 🍝'
            ),
            (
                'Рижото со морски плодови',
                'Арборио ориз, месо од школки, вонголи, чистени ракчиња, лигњи, пелат, пармезан',
                560.0,
                100,
                'https://www.korpa.ba/product_uploads/5QZnrUcyz867e5NQ2LcejxPktvnytyv2.jpg',
                'Рижото 🍚'
            ),
            (
                'Рижото со вргањ и јунешко',
                'Арборио ориз, пире од вргањ, јунешки стек, деми глас сос, жалфија, пармезан',
                580.0,
                100,
                'https://www.korpa.ba/product_uploads/BBt1AvwOibsptIfineeJhM0Myz5AveGS.jpg',
                'Рижото 🍚'
            ),
            (
                'Зелено рижото со пилешко и лимон сос',
                'Арборио ориз, пире од спанаќ, пилешко во сос од лимон, пармезан',
                440.0,
                100,
                'https://www.korpa.ba/product_uploads/LgKb769HCOBQucRXMnDZsAndQy3LhyxU.jpg',
                'Рижото 🍚'
            ),
            (
                'Рижото со лаврак',
                'Арборио ориз, пире од пченка и праз, лаврак филе, пармезан, ромеско сос',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/oaq6yJUMw0R8wMIBa7XxFuCC8G7Jnkrg.jpg',
                'Рижото 🍚'
            ),
            (
                'Паеља Форца',
                'Ориз со зеленчук и пилешко, лигњи, шкампи, школки, вонголи *30-40 мин време на подготовка, се пакуваат во амбалажа за носење',
                1000.0,
                100,
                'https://www.korpa.ba/product_uploads/GuCKUPawGltDMSXmYdzfUntJMAQsEWAw.jpg',
                'Паеља - за 2 лица 🥘'
            ),
            (
                'Паеља Де Мариско',
                'Ориз со зеленчук и морски плодови: лигњи, шкампи, школки, вонголи *30-40 мин време на подготовка, се пакуваат во амбалажа за носење',
                1090.0,
                100,
                'https://www.korpa.ba/product_uploads/BvZ9bsV7YGu9ladDjoJFYzjANzpGInOB.jpg',
                'Паеља - за 2 лица 🥘'
            ),
            (
                'Пилешко со сос од ромеско и печен лешник',
                '220гр свеж пилешки стек со ромеско сос и лешници, прилог печен компир со путер',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/Bv063jOocSsBcg3yW4MJSXAz6YUlduID.jpg',
                'Специјалитети - пилешко 🍗'
            ),
            (
                'Пилешко со алфредо сос',
                '220гр свеж пилешки стек со алфредо сос, прилог компирови њоки',
                480.0,
                100,
                'https://www.korpa.ba/product_uploads/NvFweFubbDC8C47XVpzKQorijiQnwl3i.jpg',
                'Специјалитети - пилешко 🍗'
            ),
            (
                'Пилешко со слатко кисел сос',
                '150гр пилешко, јајце, црвена и зелена пиперка, кромид, ананас, ѓумбир, томато паста, коријандер, прилог јасмин ориз',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/sqNdOQPVLABq9o893WfnCeiArayw5xHx.jpg',
                'Специјалитети - пилешко 🍗'
            ),
            (
                'Пилешко суфлаки',
                '200гр пилешки ражниќ, помфрит, салата од домати, таратор салата',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/wCmtKzbZG9XwvtEZkSfrE4oNJYis5H8q.jpg',
                'Специјалитети - пилешко 🍗'
            ),
            (
                'Пилешки стек свеж со ориз',
                '220гр свеж пилешки стек, прилог ориз',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/7F80GCtNmFdHP7P0dpCyqS4F6sQWsCwy.jpg',
                'Специјалитети - пилешко 🍗'
            ),
            (
                'Пилешки стек свеж со листови крцкав компир',
                '220гр свеж пилешки стек, прилог листови крцкав компир',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/dAhN9eld1Y08mzMslviDkNu3N07Dfj49.jpg',
                'Специјалитети - пилешко 🍗'
            ),
            (
                'Мисиркино со алфредо сос',
                '220гр мисиркин стек со алфредо сос, прилог печен компир со путер',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/hriEEJUHSRh83VHaGAisJxPWjyO6hAY8.jpg',
                'Специјалитети - мисиркино 🍗'
            ),
            (
                'Мисиркин стек со ориз',
                '220гр мисиркин стек, прилог ориз',
                410.0,
                100,
                'https://www.korpa.ba/product_uploads/QzRRXC01zU5TyynZmOf570oRL1aqVg1u.jpg',
                'Специјалитети - мисиркино 🍗'
            ),
            (
                'Мисиркин стек со листови крцкав компир',
                '220гр мисиркин стек, прилог листови крцкав компир',
                410.0,
                100,
                'https://www.korpa.ba/product_uploads/dg4fXgktkpgE5yQikIpxFmNmY21Gf9QS.jpg',
                'Специјалитети - мисиркино 🍗'
            ),
            (
                'Патка бутче со сос и пире',
                '260-300гр патка бутче со Опорто сос, прилог пире',
                790.0,
                100,
                'https://www.korpa.ba/product_uploads/DFNSzX4iApIDOTzd9yvojzWDyC2OjJNn.jpg',
                'Специјалитети - мисиркино 🍗'
            ),
            (
                'Baby back Ribs во BBQ-виски сос',
                '450-500гр. свински задни ребра со сос од барбикју-виски сос, прилог листови крцкав компир',
                770.0,
                100,
                'https://www.korpa.ba/product_uploads/AWWZPs2uaAhSVeZKF1OfFey58aMC3bVn.jpg',
                'Специјалитети - свинско 🍖'
            ),
            (
                'Свинска кременадла Ala Parilla',
                '450-500гр маринирана кременадла со ребро, прилог листови крцкав компир',
                560.0,
                100,
                'https://www.korpa.ba/product_uploads/n8xP6QWOYp2kNFzGuXYDCw82CUX8BxUP.jpg',
                'Специјалитети - свинско 🍖'
            ),
            (
                'Свинско филе со вргањ',
                '230гр свинско филе, вргањ, лук, бело вино, неутрална павлака, прилог печен компир со путер',
                620.0,
                100,
                'https://www.korpa.ba/product_uploads/Zl5WY6I2NXwGQIxwf1WxrVCDEvERU9kA.jpg',
                'Специјалитети - свинско 🍖'
            ),
            (
                'Свинска коленица 400-450гр',
                '400-450гр свинска коленица сервирана во сопствен сос и пире',
                440.0,
                100,
                'https://www.korpa.ba/product_uploads/WyDz6CeK7zvr1CygHIZ1lA4QjmECdvmg.jpg',
                'Специјалитети - свинско 🍖'
            ),
            (
                'Chef Beef filet',
                'Јунешки бифтек, деликатес foie gras, тартуф, Порто винo, прилог печен компир со путер',
                1750.0,
                100,
                'https://www.korpa.ba/product_uploads/UJ0d6YS4crB7xxThaRfHXdkCS4DTmoVc.jpg',
                'Специјалитети - јунешко 🥩'
            ),
            (
                'Pilot Beef filet',
                'Јунешки бифтек, свежи таљатели со вргањ и тартуфата',
                1440.0,
                100,
                'https://www.korpa.ba/product_uploads/LaCdsBGqbAHFO8EJs7ywBJcMIcqpRtYz.jpg',
                'Специјалитети - јунешко 🥩'
            ),
            (
                'Beef Тenderloin Tagliata',
                'Јунешки сецкан бифтек, сервиран во маслиново масло и рузмарин',
                1240.0,
                100,
                'https://www.korpa.ba/product_uploads/vsFNlLUqGvrfEXlLkpDlgAmP2FvhH4na.jpg',
                'Специјалитети - јунешко 🥩'
            ),
            (
                'Beef Rib-eye steak',
                'Риб-ај стек, со пармезан и рукола, прилог печен компир на путер',
                990.0,
                100,
                'https://www.korpa.ba/product_uploads/GAc3I4UxIhERg2i1QU5BB9LWTsT5ggfL.jpg',
                'Специјалитети - јунешко 🥩'
            ),
            (
                'Скопјанка - Бееф плескавица',
                '300гр јунешка плескавица, со сос од димено сирење, кајмак и црвена пиперка, прилог листови крцкав компир',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/Fj5JOObu7s50cPTNPUsypp1zgdvIIHbq.jpg',
                'Специјалитети - јунешко 🥩'
            ),
            (
                'Телешки Baby back ribs со BBQ-виски сос',
                '450-500гр телешки задни ребра со сос од барбикју - виски сос, прилог листови крцкав компир',
                1050.0,
                100,
                'https://www.korpa.ba/product_uploads/C8z7ZYc0SR3bFPQTtDmWdOuJJdevs6h2.jpg',
                'Специјалитети - јунешко 🥩'
            ),
            (
                'Биф Броколи',
                '150гр. јунешки риб-ај стек, брокула, ојстерс и соја сос, јасмин ориз, лук',
                550.0,
                100,
                'https://www.korpa.ba/product_uploads/aXIwJg0rmhR0lShEniBQXKRoFIKxIJUA.jpg',
                'Специјалитети - јунешко 🥩'
            ),
            (
                'Блек ангус јазик',
                '180-200гр паниран ангус јазик со рустик грејви сос, прилог пире & наут со маслинки',
                560.0,
                100,
                'https://www.korpa.ba/product_uploads/CzMvTW7K2808LJVM7IgC0mbh1FnqHnJ5.jpg',
                'Специјалитети - јунешко 🥩'
            ),
            (
                'Јунешки ќофтиња',
                '180гр јунешки ќофтиња, сервирани во доматен сос и компирово пире',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/ij98AdRhZUDRYcWQrB1KscRteGwFSquX.jpg',
                'Специјалитети - јунешко 🥩'
            ),
            (
                'Телешки образи',
                '200гр телешки образи, натурален деми глас сос, компирово пире',
                790.0,
                100,
                'https://www.korpa.ba/product_uploads/zahxDuHNW4hZ3sDIh5ENyaSpVOnWNsUx.jpg',
                'Специјалитети 🤌🏻'
            ),
            (
                'Лаврак со зелен сос',
                '150гр. филе од лаврак, вонголе школки, италијанки бел грав, зелен коријандер сос',
                820.0,
                100,
                'https://www.korpa.ba/product_uploads/riH39uj7Ahxra1NlS7agDN8IZNPJ4Ig2.jpg',
                'Риба и морски специјалитети 🐟'
            ),
            (
                'Лосос во сос од кајен пипер',
                '220гр лосос филе во сос од пикантен кајен пипер, прилог печен компир со путер',
                920.0,
                100,
                'https://www.korpa.ba/product_uploads/P0dsgjCWv0ASrcjIsY8ePL8hWAikvQtF.jpg',
                'Риба и морски специјалитети 🐟'
            ),
            (
                'Mедитерански Бејби Октопод',
                '185гр бејби октопод со пелат и маслинки, прилог хумус, печен компир со путер',
                990.0,
                100,
                'https://www.korpa.ba/product_uploads/Y9PLurysfVEk86ezCy2xeQjj073vN5c4.jpg',
                'Риба и морски специјалитети 🐟'
            ),
            (
                "Ракчиња во лук 'Al Ajillo'",
                'Ракчиња гамбери, лук, маслиново масло, чили пиперка, брускети',
                660.0,
                100,
                'https://www.korpa.ba/product_uploads/rWwajEZ5OJFvRgfnXYw2cOBcXcYWg4UQ.jpg',
                'Риба и морски специјалитети 🐟'
            ),
            (
                'Бејби лигњи поховани',
                '200гр поховани бејби лигњи, 100гр крцкав компир, сос од лимон и маслинов зејтин',
                640.0,
                100,
                'https://www.korpa.ba/product_uploads/ARzwbeDOzmODResbVNgVTHKsk067yz0a.jpg',
                'Риба и морски специјалитети 🐟'
            ),
            (
                'Лигњи гриловани со чермула сос',
                '200гр грилувани бејби лигњи, 100 гр помфрит, чермула сос од билки',
                660.0,
                100,
                'https://www.korpa.ba/product_uploads/2m1l44jZRgpd1eIhfs210A2DB1oPEflq.jpg',
                'Риба и морски специјалитети 🐟'
            ),
            (
                'Бурито со пилешко',
                'Тортиља, свеж пилешки стек, пиперка, домати, кромид, чедар, неутрална павлака, соја сос, слатко лут сос, прилог листови крцкав компир',
                370.0,
                100,
                'https://www.korpa.ba/product_uploads/kwulZ7P8XkTKGu4xJoAAxreEpAMXKo6R.jpg',
                'Snacks 🌯'
            ),
            (
                'Мексичко бурито',
                'Тортиља, јунешки риб-ај стек, пилешки стек, чедар кашкавал, фахита зачин, црвен грав, пиперки, кромид, неутрална павлака, соја сос, слатко лут сос, прилог листови крцкав компир',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/2ZOJ41EQwgnXiOQf5UIyb9g9WXaFCfZa.jpg',
                'Snacks 🌯'
            ),
            (
                'Веге Филе тава',
                'Вегански филе парченца, подготвен во вог тава со пиперка, кромид и ананас, со слатко кисел сос',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/oaZoho8knyvQXxSu3nzjKiNRR3ll0fcu.jpg',
                'Snacks 🌯'
            ),
            (
                'Juicy Lucy Burger',
                'Бриош лепиња, 150гр јунешки бургер полнет со чедар, екстра чедар кашкавал, ајзберг салата, домати, корнишони, прилог листови крцкав компир',
                360.0,
                100,
                'https://www.korpa.ba/product_uploads/B6MMKB4aTbtvIKaEjFqjVFBagxudhvmt.jpg',
                'Burgers 🍔'
            ),
            (
                'New York style Burger',
                'Бриош лепиња, 200гр јунешки бургер, крцкава сланина, ајзберг салата, домати, кромид, корнишони, бургер сос, сенф, прилог листови крцкав компир',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/bJVoeZEGMDTjCXoksO5rWow6JrqgZLYU.jpg',
                'Burgers 🍔'
            ),
            (
                'Forza Burger',
                'Бриош лепиња, 200гр јунешки бургер, димен кашкавал, рукола, криспи кромид, мармалад од црвени свежи пиперки, аиоли сос, прилог листови крцкав компир',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/8RjHmEFiZyiXyzKd4TcWGsOSX8A8H6kv.jpg',
                'Burgers 🍔'
            ),
            (
                'Smashed Burger',
                'Бриош лепиња, 2 јунешки бургери, двоен чедар кашкавал, грилуван кромид, корнишони, бургер сос, прилог листови крцкав компир',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/zKz23Bh761kYW4ova2ItvENbvNJmxXPb.jpg',
                'Burgers 🍔'
            ),
            (
                'Crispy Chicken Burger',
                'Бриош лепиња, пилешки паниран стек, рендан пармезан, рукола, пченка, домати, песто мајо сос, прилог листови крцкав компир',
                410.0,
                100,
                'https://www.korpa.ba/product_uploads/1uHT2Xl9rgzioec7Hi4ZV2XmDr5WxGXU.jpg',
                'Burgers 🍔'
            ),
            (
                'Margarita pizza',
                'Пелат сос, кашкавал, оригано',
                340.0,
                100,
                'https://www.korpa.ba/product_uploads/4WJ6p0HGtOhuo8Ckysd67yT0D3WapvmN.jpg',
                'Pizza 🍕'
            ),
            (
                'Margarita Mozarella pizza',
                'Пелат сос, свежа моцарела, свеж босилек, маслинов зејтин',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/0KanxtY6NRTTQDtyrGcHiGcbZBBpXzvD.jpg',
                'Pizza 🍕'
            ),
            (
                'Capricciosa pizza',
                'Кашкавал, пелат сос, шунка, печурки, оригано',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/q6grEmD8omA7WU0T9aKx7XyVs1UgX4u5.jpg',
                'Pizza 🍕'
            ),
            (
                'Bacon Cheddar pizza',
                'Кашкавал, чедар кашкавал, пелат сос, сланина, маслинки',
                410.0,
                100,
                'https://www.korpa.ba/product_uploads/vQmGK276eNdiZRraJuxvw3Dk6mIXMGBI.jpg',
                'Pizza 🍕'
            ),
            (
                'Vegetariana pizza',
                'Пелат, овчо сирење, домати, пиперка, кромид, маслинки, рукола',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/OpCLN9kt5QokHLKql6zi8LQLL0aaVMOF.jpg',
                'Pizza 🍕'
            ),
            (
                'Tartufata pizza',
                'Неутрална павлака, тартуфата крема, кашкавал, шунка, печурки',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/R4BNzEb5CE8ZRVqb8PsGW918PlEMJc87.jpg',
                'Pizza 🍕'
            ),
            (
                'Gluten free Capricciosa pizza',
                'Безглутенско тесто, кашкавал, пелат сос, шунка, печурки, оригано',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/UxbhzFK8eiWm1wvu0ScmSzmxPOlr52dd.jpg',
                'Pizza 🍕'
            ),
            (
                'Детски Бургер',
                'Бриош мини лепче, 80гр јунешки бургер, домати, марула, сос, помфрит',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/gyEhARr6j6w8qviZo4RLD7C9D888iFAL.jpg',
                'Детско мени 🦁'
            ),
            (
                'Фереро роше десерт',
                'Нутела крем, лешник пралине, глазура од чоколадо и лешник',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/PmsMwb5JpF0YYO0nct5DIVgY0IyrQmPC.jpg',
                'Десерти 🍰'
            ),
            (
                'Рафаело десерт',
                'Кокосов крем, бело чоколадо, млечен мус, бадеми',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/PugLSViGfRsWLcftA4Prkj9Sd5cy5vlW.jpg',
                'Десерти 🍰'
            ),
            (
                'Мус од чоколадо со пекан орев',
                'Мус од чоколадо, брауни бисквит, тофи, печен пекан орев',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/hbodprTpxiF3OYoCXGVk9yCGEH29EGKn.jpg',
                'Десерти 🍰'
            ),
            (
                'Ројал десерт',
                'Чоколаден бисквит, мус од темно и млечно чоколадо, тонка зачин',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/UCu0GQC0UZ3IqIwHC11cmHpLqh9opB8C.jpg',
                'Десерти 🍰'
            ),
            (
                'Блек форест',
                'Чоколаден бисквит, мус од бело чоколадо, мармалад од вишна',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/MRy3s0sn75rQ0JlOmzWhtubEEwtA4AGJ.jpg',
                'Десерти 🍰'
            ),
            (
                'Тирамису',
                'Крем сирење, ванила, чоколадо, какао',
                200.0,
                100,
                'https://www.korpa.ba/product_uploads/383hpdPpcN78LWdLv696M0jpvwWZPCw7.jpg',
                'Десерти 🍰'
            ),
            (
                'Буено десерт',
                'Киндер буено крем, мус од темно и млечно чоколадо, чоколадно тесто',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/hxRI4pLRarHG5lpP2yfa2YY5PAXby9nV.jpg',
                'Десерти 🍰'
            ),
            (
                "Ф'стак колач со малина",
                'Крем со ф’стак паста, мармалад од малина, ванила крем, бисквит со портокал',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/jVmG5r0D057uJWQhkT67IpgbVFhDTVo8.jpg',
                'Десерти 🍰'
            ),
            (
                'Чизкејк со малина',
                'Плазма, маскарпоне, крем сир, малина',
                200.0,
                100,
                'https://www.korpa.ba/product_uploads/3MwNdOSmfiP1yWwZOr4pZGBsOJxKtRKN.jpg',
                'Десерти 🍰'
            ),
            (
                'Керот колач со ѓумбир',
                'Крем од морков и цимет, желе од морков, бисквит со ѓумбир и цимет',
                200.0,
                100,
                'https://www.korpa.ba/product_uploads/N8L9lTlsF9S07MZlcuLz95cFJz2ddmqG.jpg',
                'Десерти 🍰'
            ),
            (
                'Руби Хана десерт',
                'Бисквит од бадем, крем сирење, јагоди, руби чоколадо',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/hAjskk2IybSHP50mTVeOYHbBcXGEZt7G.jpg',
                'Десерти 🍰'
            ),
            (
                'Чизкејк манго',
                'Плазма, крем сирење, манго полнеж',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/uqpyd2AWPRPz7XivoBgT3vhJG3tFvBqO.jpg',
                'Десерти 🍰'
            ),
            (
                'Кит Кет палачинка',
                'Киткат крем, лешници',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/W4khF0f6br0ZSV7pzrYhlmEhWfoq45mY.jpg',
                'Палачинки 🥞'
            )
        ]
    ),
    (
        'Plaza De Toros',
        'Доставуваме до Вашата врата',
        'https://korpa.ba/restaurant_uploads/otcdJ6KgJKL2elYH6UiR8IlNt4I7N2Xt.jpg',
        '',
        25,
        [
            (
                'Англиски појадок',
                'Сланина на грил, две јајца на око, домашни колбасички, топло лепче, путер, мармалад, со еспресо или чај и чаша од портокал',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/09ixICXD5P3Qy2NfWQo5psgH5KjfxTbJ.jpg',
                'Појадок 🍳'
            ),
            (
                'Мекици',
                'Две мекици, сирење, мармалад',
                200.0,
                100,
                'https://www.korpa.ba/product_uploads/JTZ9TrTGECbSvKg1twXycsvW2pChmaSJ.jpg',
                'Појадок 🍳'
            ),
            (
                'Тост јајце',
                'Кашкавал, шунка, јајце, кечап, сервирано со помфрит',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/lKkwiWSbOjERWDj5Afn82R4XAQ2IpjWj.jpg',
                'Појадок 🍳'
            ),
            (
                'Преклопен омлет',
                'Три јајца, шунка, кашкавал, топло печено лепче',
                270.0,
                100,
                'https://www.korpa.ba/product_uploads/13OVmYhGjj8Te3WFkqZxcNE4vneoGv8g.jpg',
                'Појадок 🍳'
            ),
            (
                'Македонски омлет',
                'Три јајца со сирење, салата од домат, топло печено лепче',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/oSqdCfZsHRRcnMpfABMhwcqgmpb1AihN.jpg',
                'Појадок 🍳'
            ),
            (
                'Избацивач',
                'Три јајца на око, сервирани на лепчиња со кашкавал и деликатесна шунка',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/qyhdEGeUx2TwDtxZaLFJhhC8CanQGKgL.jpg',
                'Појадок 🍳'
            ),
            (
                'Турски појадок (за 2-4 лица)',
                'Различни видови на сувомеснати, кашкавал и сирење, домат, краставица, маслинки, варено јајце, омлет со кулен, топли лепчиња, мали мекици и благи и солени намази',
                1200.0,
                100,
                'https://www.korpa.ba/product_uploads/LIREKjqO4bWhb6myv0sPN0lUPAcahMPF.jpg',
                'Појадок 🍳'
            ),
            (
                'Торо даска',
                'Богато сервирана даска со свинска колбасица, мали плескавици, пилешки прсти, прстени од паниран кромид, полнети печурки, пилешки крилца, полнета пиперка, тиквички, сланина чипс, лепчиња со кајмак',
                1520.0,
                100,
                'https://www.korpa.ba/product_uploads/oL9hpcnOLNVnYTckpVk4zXNugEw4KAhj.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Мезе даска',
                'Помфрит со сирење, панирани прстени од кромид, пилешки прсти, панирана зденка, полнети печурки со песто и пармезан',
                970.0,
                100,
                'https://www.korpa.ba/product_uploads/VYJN56shtpkEynqEDDR2DTH3SRjfn11V.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Панирани прстени од кромид',
                'Со пикантен салса сос',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/PaGxu7vXMvHE522a38u5C4szs4hqH6R4.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Пилешки прсти',
                'Со тартар сос',
                360.0,
                100,
                'https://www.korpa.ba/product_uploads/upRcm9JQSpp1x5Hyd16gwbC1SR9Zdwvo.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Пилешки крилца',
                'Пилешки крилца со салса сос',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/cRVUVN79xoy8J6NOmtbfTdtKVTV7Cs9A.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Компир во фурна',
                'Компир, кашкавал и сланина потпечени во фурна',
                270.0,
                100,
                'https://www.korpa.ba/product_uploads/Qh21zYY4H9iVbOPbi1E7yKCelTBayAZp.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Тиквички',
                'Пржени тиквички со тартар сос',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/6wg4QET35VTcV52JNqKokPPoK1fYhFJj.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Овчо сирење',
                '',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/x4Wog9iZR1pXWSfZZUw7A9hYLmzACeEe.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Сирење а ла торо',
                'Сирење на скара со сланина',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/Y1AJuEvWrnFDaausfqHfz2TsCX8aDTHX.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Тиаголничиња со зачини и путер',
                '',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/SQwUZGfwZvf1TVQzPyQIGerSja014RxT.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Триаголничиња со кајмак',
                '',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/jCKeRpr7vEgNYZWSZSrpEoGOrrM9tAOw.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Фурнаринки',
                '',
                140.0,
                100,
                'https://www.korpa.ba/product_uploads/5Qxg7laVv9qvOGg6M0Eie6Pa4GMYnfE1.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Фурнаринки со стопен кашкавал',
                '',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/Xmdgt6Ni5M96EANfv6GIXCVi7abPTO6z.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Крушевски колбас',
                '',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/tMjPViswic7wjDMXBg2G0lRXOFFrFyRP.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Сланина чипс',
                '',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/8yoiVi48p9yFZ1Fr4lpekrPEj0YX0FGi.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Спеки',
                'Парчиња пилешки стек завиткани во кашкавал и сланина',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/JioJQfkNjgQCfsd9mi8yPnllE183rr40.jpg',
                'Мезиња 🍗🧀'
            ),
            (
                'Сендвич чикен',
                'Пилешки стек, рендано сирење, домат, марула, помфрит',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/Riyz7vCWudTXYU6xvmLr5EkzfDudJDW8.jpg',
                'Топли печени сендвичи 🥪'
            ),
            (
                'Лепче плескавица',
                'Плескавица, марула, домат, кисели крставички, кромид, пикантен сос, помфрит',
                320.0,
                100,
                'https://www.korpa.ba/product_uploads/VQZ3OLJnWwUXX9qxnJZl5lKHwsI7Sw44.jpg',
                'Топли печени сендвичи 🥪'
            ),
            (
                'Клуб сендвич',
                'Гриловано пилешко месо, домат, сланина, кашкавал, домат, кисели крставички, пикантен сос, помфрит',
                320.0,
                100,
                'https://www.korpa.ba/product_uploads/92X5jIkLT6PfON6kGLmgC5kcIm2fnjzL.jpg',
                'Топли печени сендвичи 🥪'
            ),
            (
                'Торо пица',
                'Доматен сос, кашкавал, кулен, сланина, печурки, маслинки, капари, феферони, кромид',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/9r46mg7QTDoLvqTafEHIQKOGWCQu2YTi.jpg',
                'Pizza 🍕'
            ),
            (
                'Prosciutto (свинска пршута) пица',
                'Доматен сос, кашкавал, свинска пршута, печурки',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/UB8qWteoETBzRJFtqtAoHWfW0aKy1aK9.jpg',
                'Pizza 🍕'
            ),
            (
                'Prosciutto (говедска пршута) пица',
                'Доматен сос, кашкавал, говедска пршута, печурки',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/G3kFvMySH3rrg9c9RnRP8bzYCKyk9tyC.jpg',
                'Pizza 🍕'
            ),
            (
                'Пилешка пица',
                'Доматен сос, кашкавал, пилешко месо, печурки',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/V85l4KFnwI5FcCzANvHiy3UHA3q7WMSh.jpg',
                'Pizza 🍕'
            ),
            (
                'Диавола пица',
                'Доматен сос, кашкавал, кулен, рукола, сусам',
                360.0,
                100,
                'https://www.korpa.ba/product_uploads/XbGWSVWfA9GWp1UB9OpNUTT14MpQqycd.jpg',
                'Pizza 🍕'
            ),
            (
                'Капричиоза пица',
                'Доматен сос, кашкавал, шунка, печурки',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/Vw9sRnx4y4syq5Ot9RUikQus81UKNwiR.jpg',
                'Pizza 🍕'
            ),
            (
                'Пилешка Пастрмајлија',
                '',
                330.0,
                100,
                'https://www.korpa.ba/product_uploads/9xYPh264Y6O3EFYQ15fdEZ0SDhadjAtf.jpg',
                'Пастрмајлија 👨🏽\u200d🍳'
            ),
            (
                'Свинска Пастрмајлија',
                '',
                330.0,
                100,
                'https://www.korpa.ba/product_uploads/L76cvJTkv0bhpZYQq3hXvcSiO3WMCEMN.jpg',
                'Пастрмајлија 👨🏽\u200d🍳'
            ),
            (
                'Пенне Рома',
                'Бел сос со шунка и печурки',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/FlO82KufigFIonYXSgmWV25kBsGKgBPd.jpg',
                'Тестенини 🍝'
            ),
            (
                'Шпагети доматело',
                'Доматен сос, пармезан',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/kuojB9YTXWlWgQn146gM8Gy9bPeWbiBF.jpg',
                'Тестенини 🍝'
            ),
            (
                'Пенне Медитерана',
                'Домашно песто, пармезан',
                320.0,
                100,
                'https://www.korpa.ba/product_uploads/I4avJ9yK5HiQwg0eIVu1UjAFSxBXKKLJ.jpg',
                'Тестенини 🍝'
            ),
            (
                'Шпагети карбонара',
                'Сланина, јајце, пармезан',
                330.0,
                100,
                'https://www.korpa.ba/product_uploads/MsSGI0nbVr2qgBAmF6gee20yi2KOyP9A.jpg',
                'Тестенини 🍝'
            ),
            (
                'Шпагети болоњезе',
                'Доматен сос, телешко мелено месо, зеленчук',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/AWwXq1h2Pxs5g4iZ7LXBd9yaTApP2gHR.jpg',
                'Тестенини 🍝'
            ),
            (
                'La carne de cerdo',
                'Мариниран свински врат, припремен на домашен начин, севиран со зеленчук и помфрит',
                480.0,
                100,
                'https://www.korpa.ba/product_uploads/1JFNxPdJRiGnJ2CFmY3HAzWr1yCCXm2D.jpg',
                'Главно јадење 🍖'
            ),
            (
                'Грчко ребро',
                'Свинско ребро, ориз, компир, чипс, шпански сос',
                600.0,
                100,
                'https://www.korpa.ba/product_uploads/B6cqNOizmnJnxk29tbA9Z56Y2sIfiF2h.jpg',
                'Главно јадење 🍖'
            ),
            (
                'Кременадла',
                'Две кременадли, сервирани со помфрит, ориз, зеленчук на грил и шпански сос',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/qIS06NK9TkAueGg15ZrkvJBifiSzhOAS.jpg',
                'Главно јадење 🍖'
            ),
            (
                'Salchiacha',
                'Домашна пикантна колбасица, сервирано со помфрит и шпански сос',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/DvTbqfTlIDTs9F3S3I8svOJZeiaekwv0.jpg',
                'Главно јадење 🍖'
            ),
            (
                'Тава Торо',
                'Мешано месо со печурки и потпечен кашкавал со топло лепче',
                590.0,
                100,
                'https://www.korpa.ba/product_uploads/QcNNA85gS41n5cGlvOgbNbRAI5CFe5Hc.jpg',
                'Главно јадење 🍖'
            ),
            (
                'Шарска',
                'Плескавица со кашкавал, сервирано со помфрит и шпански сос',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/hdAsc7bUUiOsYadI1ODyV46UEiTaHRFe.jpg',
                'Главно јадење 🍖'
            ),
            (
                'Плескавица а ла Торо',
                'Плескавица, лепче, кајмак, сланина, кромид, пикантен сос, помфрит',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/3PdvsNr4ouuw8pjiL9qUEbZNURjwtmHe.jpg',
                'Главно јадење 🍖'
            ),
            (
                'Бифтек',
                'Сервиран со путер, зеленчук на грил, ориз, помфрит',
                1380.0,
                100,
                'https://www.korpa.ba/product_uploads/3p2FgAVCeL4OA5W8rf7eiWqfw1tvRiyg.jpg',
                'Главно јадење 🍖'
            ),
            (
                'Јунешка кременадлa',
                'Сервирано со помфрит и ориз',
                790.0,
                100,
                'https://www.korpa.ba/product_uploads/ljbLGMFCeNqx5fhm1HDLD9OibzfU1ZIK.jpg',
                'Главно јадење 🍖'
            ),
            (
                'Мешана скара',
                'Плескавица, карабатак, кременадла, отворено ребро, ориз и помфрит',
                1420.0,
                100,
                'https://www.korpa.ba/product_uploads/KT4NmaoFf0UyrfQZZ9hhoIOxzy3NWZdX.jpg',
                'Главно јадење 🍖'
            ),
            (
                'Бело пири',
                'Пилешки стек во бел сос со печурки, помфрит',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/fP4g9UTrJso4l83AcO13w7JcBdW7wHnr.jpg',
                'Главно јадење 🍖'
            ),
            (
                'Кари пири',
                'Пилешки стек во сос од кари и печурки, помфрит',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/M1FKjhwPYVNisYlq4U5wO8FJOrv73fOq.jpg',
                'Главно јадење 🍖'
            ),
            (
                'Ражниќ од пилешко месо и зеленчук',
                'Сервирано со помфрит',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/3PCWmlMVH7bcnDdCjbKS63zv4rSx05PE.jpg',
                'Главно јадење 🍖'
            ),
            (
                'Кралска салата',
                'Богато сервирана салата со пилешко месо, мешавина од зелена салата, краставица, шери домати и кромид. Зачинета со бел кралски сос',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/xhu9t3Ri2ZPCtIKrLBvKZHCkapBfA1W1.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Мезе салата',
                'Мешавина од зелена салата, зелка, морков, црвена пиперка, пченка, краставица, домат, пршута. Зачинето со балсамико крем и коктел сос, сервирано со топло лепче',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/N6iQ0RZkg1aVa8lFatcYgoB5ldtZbhx7.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Шеф салата',
                'Богато сервирана салата со пилешко, варено јајце, кашкавал, домат, марула, маслинки, зачинета со винегрете сос',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/bAGYnvh6jSPE59rxemwhptkRfptNsziQ.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Торо салата',
                'Богато сервирана салата со туна, варено јајце, кромид, домат, марула, маслинки, зачинета со пикантен дресинг од сенф',
                330.0,
                100,
                'https://www.korpa.ba/product_uploads/zGy2BcpQOnvWDehgQvzxswspjWpwSFgB.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Здрава салата',
                'Мешавина од зелена салата, рукола, краставица, шери домат, печурки, пченка, зачинета со дресинг од маслиново масло, балсамико и кромид',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/C83rRLQFA3mQAghTNBlsIaijOVKjaldV.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Грчка салата',
                'Домат, крставица, пиперка, кромид, маслинки, магдонос, оригано, сирење',
                250.0,
                100,
                'https://www.korpa.ba/product_uploads/q4tciwcvnu1ghIncm7u9Ux0WwMJvy6u7.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Македонска салата',
                'Домат, печена пиперка, кромид, магдонос',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/UsXNvDiQdZo6lE835Wvk3YZqKIKsRlJ1.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Шопска салата',
                'Домат, крставица, пиперка, кромид, маслинки,магдонос, оригано, сирење',
                250.0,
                100,
                'https://www.korpa.ba/product_uploads/8dzInQacdmjYaujD65gW2dG1jZfZIgSO.jpg',
                'Салати 🥗🥬'
            ),
            (
                'Бомби',
                'Палачинка полнета со ванила сладолед прелиена со чоколадно пралине и шумско овошје',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/NmCN1mndlaLiGeiqeCfBA6VQfVBzwn6q.jpg',
                'Десерти 🍩'
            ),
            (
                'Холандска торта (сезонски)',
                'Торта од јаболки, сладолед, шлаг',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/8rxG4hArb0hh43vCImIY5uhjOxGaohtR.jpg',
                'Десерти 🍩'
            ),
            (
                'Торо торта',
                'Домашна торта со мелени ореви, чоколадо и топка ванила сладолед',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/UuwS6Xrs5XFMOTKiy1ohYhb7tWMljL2f.jpg',
                'Десерти 🍩'
            ),
            (
                'Десерт за четворица',
                'Разновидни благи задоволства',
                900.0,
                100,
                'https://www.korpa.ba/product_uploads/jTEieFX6O8pWvxGqpqKSCZ3dANUxLJKx.jpg',
                'Десерти 🍩'
            ),
            (
                'Вафла  Баначоко',
                'Со чоколадно пралине, банана, шлаг',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/T3bbmBCWATNeHwvE4Q6Kix4JRn8dy7n5.jpg',
                'Домашни Белгиски Вафли - благи 🧇'
            ),
            (
                'Вафла Crunchy',
                'Кранчи чоколадо, вишни, топка ванила сладолед',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/QURmka0jrDW3yEDT2768CBg8q10FbH1t.jpg',
                'Домашни Белгиски Вафли - благи 🧇'
            ),
            (
                'Вафла Орео - Фрути',
                'Орео крем, шумско овошје, топка ванила сладолед',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/CO2iLob9j1RBtdg1JFfGVROo2R4aEdfV.jpg',
                'Домашни Белгиски Вафли - благи 🧇'
            ),
            (
                'Вафла Торо',
                'Шумско овошје, топка ванила сладолед, шлаг',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/3wlBGbI57u3FIkMQ7RBuUXLLJrBd6Yay.jpg',
                'Домашни Белгиски Вафли - благи 🧇'
            ),
            (
                'Кралска Вафла',
                'Бел кралски сос, сирење, домат',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/XB3C4Z8ulPZLwicBp1OwIgDL81DuEMmw.jpg',
                'Домашни Белгиски Вафли - солени 🧇'
            ),
            (
                'Вафла Чикен',
                'Павлака, пилешко месо, ајсберг, краставица, шери домати',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/YzSxGtUDpeNtaDHG4fnM2GrKiUpLrCWi.jpg',
                'Домашни Белгиски Вафли - солени 🧇'
            ),
            (
                'Вафла Екстра',
                'Павлака, кашкавал, пржена сланина, јајце на око',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/U9zEH1WOZTupk9pNpwEXjXcVV8N1DAcS.jpg',
                'Домашни Белгиски Вафли - солени 🧇'
            ),
            (
                'Вафла Каjмак',
                'Кајмак, деликатесна шунка, домат, краставица, кромид',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/IZdpkt2c26nwZQC3ZMwL2ihIVFH2uSap.jpg',
                'Домашни Белгиски Вафли - солени 🧇'
            )
        ]
    ),
    (
        'Revija Bar & Food',
        'Доставуваме до Вашата врата',
        'https://korpa.ba/restaurant_uploads/rEye1wynuqMD6DcYXmkhSQbJ40nMGshJ.jpg',
        '',
        25,
        [
            (
                'Биг Кинг бургер',
                'Чисто телешко месо, домат, кисели краставички, чедар, црвен кромид, зеленчук, дресинг, компир',
                670.0,
                100,
                'https://www.korpa.ba/product_uploads/DpgbLh4Qq3VbF5H6Zma99WpTG8t8IOOo.jpg',
                'BURGER DAY! 🍔'
            ),
            (
                'Криспи Кинг бургер',
                'Крцкав пилешки стек, чедар, домат, црвен кромид, зеленчук, компир',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/1git8sDuv2eH8D83fsueVZ4OVQ06Kj6I.jpg',
                'BURGER DAY! 🍔'
            ),
            (
                'Ревија појадок',
                'Говедски пршут, 2 јајца на око, домат, краставица, 2 тост лепчиња, овчо сирење, помфрит',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/77wjvG3ntuWM2oHu2Lf8rtPFWWicm43p.jpg',
                'Појадок 🍳'
            ),
            (
                'Омлет по избор',
                'Овчо сирење/Овчи Кашкавал/Шунка/Кашкавал/Печурки/Вегетаријански',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/3oWGN8gKT3xTWoXMPns7Bk7gVMT6f4XP.jpg',
                'Појадок 🍳'
            ),
            (
                'Eggs Benedict',
                '2 јајца, сланина, рукола, шери домат, потпечено лепче, холандез сос',
                320.0,
                100,
                'https://www.korpa.ba/product_uploads/I45MEELEQ2VKoJpAq6ACkR98JTEDrqZn.jpg',
                'Појадок 🍳'
            ),
            (
                'Потпечени Макарони',
                'Јајца, овчо сирење, кашкавал',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/gVlvh9pRcHHvyA3GL6YapXXRvzCWiOwO.jpg',
                'Појадок 🍳'
            ),
            (
                'Мекици',
                '2 мекици, овчо сирење, ајвар, домат',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/FC8exqbGeAJTutz0e2s1lFRTgc7Th0Mk.jpg',
                'Појадок 🍳'
            ),
            (
                'Клуб сендвич',
                'Пилешка шунка, кашкавал, домат, краставица, помфрит, кари сос',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/uEkDuTPKyNYTKqftgNnOW2o95DD2Tagu.jpg',
                'Појадок 🍳'
            ),
            (
                'Breakfast burger',
                'Лепче бургер, 2 јајца на око, сланина, кашкавал ајдамер, кашкавал овчи, помфрит',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/fUf0JbuOaeSsl3sB3Bsy0XuwmkfldrGj.jpg',
                'Појадок 🍳'
            ),
            (
                'Телешка чорба',
                '',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/rnpMfNIZ663m1TiBO9yfz7GIICWVHxay.jpg',
                'Чорби 🥣'
            ),
            (
                'Пилешка чорба',
                '',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/S5GK5fCa4wCMTuEIqHpMIa65omSmjSXZ.jpg',
                'Чорби 🥣'
            ),
            (
                'Лепче',
                '',
                40.0,
                100,
                'https://www.korpa.ba/product_uploads/E8MX8198tH5U5XmLuNF5fdNjWbbJpVAM.jpg',
                'Чорби 🥣'
            ),
            (
                'Шопска салата',
                'Домат, краставица, сирење, маслинка',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/Enjko5ZfVzkTr7Dz2Z0ke1qx7gxSeRp2.jpg',
                'Салати 🥗'
            ),
            (
                'Македонска салата',
                'Домат, пиперка, кромид, маслинки, магдонос',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/K7UQpPPGYKZFSCe72imej6gY7Orj1JsP.jpg',
                'Салати 🥗'
            ),
            (
                'Грчка салата',
                'Краставица, домат, пиперка, маслинки, сирење, кромид',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/GBkFC2x9m787I8v3MmQ91ubTTYtLlr5U.jpg',
                'Салати 🥗'
            ),
            (
                'Туна салата',
                'Туна, ајсберг, марула, пченка, кромид, маслинка, краставица',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/QSJnwNbbYIJUf7DS8ZbwGvMYvGjQxa6P.jpg',
                'Салати 🥗'
            ),
            (
                'Рукола салата',
                'Рукола, шери, пармезан',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/WNyjTnsp9FlldjoVGh5uwhu2txryf9NT.jpg',
                'Салати 🥗'
            ),
            (
                'Цезар салата со крцкаво пилешко',
                'Марула, пченка, пилешки стек, ајсберг, кубети, дресинг',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/FWaU9eP0zApWrSWynHJX4RMuVWd4oycF.jpg',
                'Салати 🥗'
            ),
            (
                'Брускети со лосос',
                'Димен лосос, путер, копар, шери',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/0LV4jUytR9wd9KG4HGkvCmSKGT5XvonY.jpg',
                'Стартери 🧀'
            ),
            (
                'Брускети италијано',
                'Босилок, домат, маслиново масло, сирење',
                270.0,
                100,
                'https://www.korpa.ba/product_uploads/TynNhY8VviT2jyjcxuLh4TAtW1sAFtHU.jpg',
                'Стартери 🧀'
            ),
            (
                'Брускети дуомо',
                'Домат, песто, пармезан, маслиново масло',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/qHsB5DiHacA5VqLk0LekfaNuPPe6pSbH.jpg',
                'Стартери 🧀'
            ),
            (
                'Чипс тиквици',
                '',
                270.0,
                100,
                'https://www.korpa.ba/product_uploads/byqb1G3kDFClAv5soM00dsqY9MUoZH28.jpg',
                'Стартери 🧀'
            ),
            (
                'Пилешки прсти',
                '',
                370.0,
                100,
                'https://www.korpa.ba/product_uploads/0D5jyiNPVL86CN2zhgP13Os00Lb6fbxh.jpg',
                'Стартери 🧀'
            ),
            (
                'Помфрит',
                '',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/E5vAI8DZIn4fnHoafCrzDkghG2aEQHi9.jpg',
                'Стартери 🧀'
            ),
            (
                'Похован Кромид',
                '',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/MRdm3gXgeIOqIXzG1TGPhwLSc7zWPMH0.jpg',
                'Стартери 🧀'
            ),
            (
                'Крилца',
                '',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/cnyy4BbxFawsl1Xj9LPpp6ziUFsSt4Lc.jpg',
                'Стартери 🧀'
            ),
            (
                'Зеленчук на жар',
                'Модар домат, пиперка, печурки, кромид',
                340.0,
                100,
                'https://www.korpa.ba/product_uploads/cfW7fJTiIdJt9BN1IA4Uwm41tKL27Svr.jpg',
                'Стартери 🧀'
            ),
            (
                'Шампињони со путер',
                '',
                340.0,
                100,
                'https://www.korpa.ba/product_uploads/IuvimLRnG1pSLpRgLlN3wcjtpvWpcs3v.jpg',
                'Стартери 🧀'
            ),
            (
                'Сирење во фурна',
                'Пиперка, домат, овчо сирење, кашкавал, плаво сирење',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/8WsGl2Es8btbzyP1JW2F033fD8zpaQeu.jpg',
                'Стартери 🧀'
            ),
            (
                'Мексикански рол чикен',
                'Пилешки стек, тортиља, ревија бел сос, салса',
                360.0,
                100,
                'https://www.korpa.ba/product_uploads/Zh3gPAqG9xMALy2kZYqbk4sYy741onWg.jpg',
                'Стартери 🧀'
            ),
            (
                'Начос чипс',
                'Начос чипс, растопен чедар, лут сос, салса',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/bgYMaFyxUZsIxTCL2gGIQyPiukfQOtK2.jpg',
                'Стартери 🧀'
            ),
            (
                'Мезе за пиво за 4 лица',
                'Пилешки крилца, чипс тиквици, похован кромид, похована зденка, похована маслинка, пилешки прсти, пекарски компир',
                1490.0,
                100,
                'https://www.korpa.ba/product_uploads/zmHtqf0dvl45JMdDbext6Eik1dd4dkk3.jpeg',
                'Мезе 🧀'
            ),
            (
                'Мезе за вино за 4 лица',
                'Млечни производи, сувомеснати производи, шампињони на путер, овошје',
                1600.0,
                100,
                'https://www.korpa.ba/product_uploads/YcyJWc0KGhTc8tkSTxdNeiH9d81HjbS1.jpg',
                'Мезе 🧀'
            ),
            (
                'Пилешки стек со помфрит',
                '',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/uHm9njuL6no1ytFQViuCNPWKXFFUjvIJ.jpg',
                'Пилешко 🍗'
            ),
            (
                'Пилешко со Кари сос',
                '',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/OhNJM4D5ZWDCp5Zvo9mUuexvR5viFzGT.jpg',
                'Пилешко 🍗'
            ),
            (
                'Пилешко во сос од Кикирики',
                '',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/PgMHLg9jfgaxn7t30oiPgTQeY3SkMdRb.jpg',
                'Пилешко 🍗'
            ),
            (
                'Полнето Пилешко',
                'Стек, кашкавал, печурки, пршута',
                520.0,
                100,
                'https://www.korpa.ba/product_uploads/SqnbuLFFm3evPo109LsIBD9Bw0J4shGS.jpg',
                'Пилешко 🍗'
            ),
            (
                'Пилешко во зеленчук',
                '',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/1zlEeruJFgylHbfBqXW9VrL5xShLYtAv.jpg',
                'Пилешко 🍗'
            ),
            (
                'Пилешко во Бел сос',
                '',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/bvfxB8TBokvhx5M8JT47QWhdUYYoYy8t.jpg',
                'Пилешко 🍗'
            ),
            (
                'Салтимбока',
                'Пилешко, сланина, хопла, рукола, пармезан, лук, магдонос',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/DBQEDCWOt1NUlAOklsgsSpBrDf8eli17.jpg',
                'Пилешко 🍗'
            ),
            (
                'Sweet & Hot',
                'Пилешко, говедски пршут, пелати, лут сос, мед, помфрит',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/LEFElFtvdC4ZWsoaRLsI2m3jFbVFC5Te.jpg',
                'Пилешко 🍗'
            ),
            (
                'Виенска шницла',
                '',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/UK16c7eisOdHWjADfsYfN3ttPQ1v68gi.jpg',
                'Свинско 🍖'
            ),
            (
                'Ребро BBQ',
                '',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/d95Zd9eH0Fgj6nu4LVFphVYi5IQYCEPa.jpg',
                'Свинско 🍖'
            ),
            (
                'Полнето Свинско Филе',
                'Печурки, сланина, кашкавал, помфрит',
                540.0,
                100,
                'https://www.korpa.ba/product_uploads/OzNcNvfkDKICItbkfRorjYQWzfnRcA3G.jpg',
                'Свинско 🍖'
            ),
            (
                'Свинско Филе',
                '',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/XZAdE6LTtXmj4zquae9JrMY35goscigy.jpg',
                'Свинско 🍖'
            ),
            (
                'Свински медаљони',
                'Медаљони, еспањол сос',
                530.0,
                100,
                'https://www.korpa.ba/product_uploads/ddcrE5tSUKrlxlLJJPLfQbKB4KGhSfS5.jpg',
                'Свинско 🍖'
            ),
            (
                'Класик Бургер',
                'Чисто телешко месо, кромид, чедар, домат, лепиња, марула, компир',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/ZDBiR1WqrvXjNF3UmYqVhgNfH8R3ByRd.jpg',
                'Бургери 🍔'
            ),
            (
                'Ревија Бургер',
                'Чисто телешко месо, кромид, сланина, чедар, домат, марула, јајца, BBQ сос, лепиња, компир',
                440.0,
                100,
                'https://www.korpa.ba/product_uploads/qXUUytQChP227QRjmZ03hS3BC4l228OX.jpg',
                'Бургери 🍔'
            ),
            (
                'Jalapeno Burger',
                'Чисто телешко месо, кромид, чедар, марула, Jalapeno пиперка, компир',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/zvPaiQ1JiAyQLVRPX5oxyfHTC98RdjQc.jpg',
                'Бургери 🍔'
            ),
            (
                'Rockstar Burger',
                'Чисто телешко месо, кромид, чедар, домат, марула, компир',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/DUSIzV0awKIpeL9huLSKbc6TjD1BQzut.jpg',
                'Бургери 🍔'
            ),
            (
                'Chicken burger',
                'Пилешка плескавица, кромид, чедар, домат, марула, компир',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/UjH4hCFzOUh5GCPLunsrl0wUhMxU2eF5.jpg',
                'Бургери 🍔'
            ),
            (
                'Биг Кинг бургер',
                'Чисто телешко месо, домат, кисели краставички, чедар, црвен кромид, зеленчук, дресинг, компир',
                670.0,
                100,
                'https://www.korpa.ba/product_uploads/no2Qt4XfyO9qcc4fDWDokkolt14SmQls.jpg',
                'Бургери 🍔'
            ),
            (
                'Криспи Кинг бургер',
                'Крцкав пилешки стек, чедар, домат, црвен кромид, зеленчук, компир',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/I3fuc45cMLUlh9s2llUKL8rl6KgAtzYR.jpg',
                'Бургери 🍔'
            ),
            (
                'Туна бурито',
                'Тортиља, туна, марула, пченка, маслинка, црвен кромид, мајонез, помфрит',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/w2a42aROD1n08wTysyjWHylzuvshUtBG.jpg',
                'Бурита 🌯'
            ),
            (
                'Цезар бурито',
                'Тортиља, стек, марула, ајсберг, пченка, дресинг, пармезан, шери, помфрит',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/jY8tJC9D8YNKxGGdNsHw74qt9zXAk0d7.jpg',
                'Бурита 🌯'
            ),
            (
                'Honey бурито',
                'Тортиља, сланина, марула, кашкавал, BBQ Сос, пченка, кромид, помфрит',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/ANOCCnmo5FQChbfKgCORAn08H5TGrlzF.jpg',
                'Бурита 🌯'
            ),
            (
                'Мексиканско бурито',
                'Тортиља, стек, чили сос, пченка, чедар, марула, црвена пиперка, помфрит',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/yHN4X9R1bPcqn6sN0Xv1ITeluAHYbf2z.jpg',
                'Бурита 🌯'
            ),
            (
                'Пилешко рижото',
                'Пилешко месо, модар домат, тиквица, црвена пиперка, печурки, пармезан, ориз',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/Srfv82EOBA7vTlta7vvuGskIzuZRtkPP.jpg',
                'Рижото 🍚'
            ),
            (
                'Примавера рижото',
                'Модар домат, црвена пиперка, тиквица, печурки, пармезан, ориз',
                440.0,
                100,
                'https://www.korpa.ba/product_uploads/6f2r3S58W35iSIveMFAyp3eckiF1W7Fi.jpg',
                'Рижото 🍚'
            ),
            (
                'Маргарита пица',
                'Пелати, кашкавал',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/wd4r0NjmroX0lMEWStAEpoI87VWL1Upf.jpg',
                'Пици 🍕'
            ),
            (
                'Везувио пица',
                'Пелати, кашкавал, шунка',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/wp0VsmNTEYrlymsQbKjuKbHqDmMteLmv.jpg',
                'Пици 🍕'
            ),
            (
                'Капричиоза пица',
                'Пелати, кашкавал, печурки, шунка',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/OFMsf4GrAF4oRrZxe4UtZxRSEpChriNr.jpg',
                'Пици 🍕'
            ),
            (
                'Кватро формаџи пица',
                'Пелати, плаво сирење, чедар, пармезан, ајдамер',
                480.0,
                100,
                'https://www.korpa.ba/product_uploads/ATtLUlbIgnHJtvSMvEZzWmlCf3bbH4LH.jpg',
                'Пици 🍕'
            ),
            (
                'Сланина пица',
                'Пелати, кашкавал, сланина, лук, печурки',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/pf0YWqiKtkYgDrzAqiJH6JKRnSXr8Klc.jpeg',
                'Пици 🍕'
            ),
            (
                'Вегетаријана пица',
                'Пелати, растителен кашкавал, маслинки, пиперка, домат, печурки, тиквици',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/2lnDstYbf21zV999JuCXK1My5bHrfty6.jpg',
                'Пици 🍕'
            ),
            (
                'Кулен пица',
                'Пелати, кашкавал, кулен',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/zv3ZmpQ0cRftZ0x6Jo9OH8RL1og83Px5.jpg',
                'Пици 🍕'
            ),
            (
                'Пршута пица',
                'Пелати, пршута, кашкавал, рукола',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/OTEvc9oIQuW2trPwkUvRXIUKaHgXYPOP.jpg',
                'Пици 🍕'
            ),
            (
                'Туна пица',
                'Пелати, кашкавал, туна, кромид',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/L41eKgdfRq09KaEmQeVt6aRg3ZiSzxt6.jpeg',
                'Пици 🍕'
            ),
            (
                'Ревија пица',
                'Пелати, моцарела, пилешки стек, пршута, рукола, BBQ',
                590.0,
                100,
                'https://www.korpa.ba/product_uploads/kNkgSmP2IVB3zpQOejbX7wm3TPxMrBep.jpg',
                'Пици 🍕'
            ),
            (
                'Лепчиња со кајмак и пршута',
                '',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/K2ccaiRUYr6Ly8mZ3pfvR7u7s1n1CLBr.jpg',
                'Лепчиња 🍞'
            ),
            (
                'Лепчиња со кајмак и магдонос',
                '',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/sA6eF5SDvdyPxiScCT5qQnEXb353ZtQu.jpg',
                'Лепчиња 🍞'
            ),
            (
                'Лепчиња со моцарела и сланина',
                '',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/0IAeLGZ9lvuL0zBD6zmRhUtyRIXp61QK.jpg',
                'Лепчиња 🍞'
            ),
            (
                'Вртени со лук и путер',
                '',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/suNEtpXXfSrOzMt6nL4OsUj8Ojd4LYJE.jpg',
                'Лепчиња 🍞'
            ),
            (
                'Фурнарини со кашкавал и сланина',
                '',
                320.0,
                100,
                'https://www.korpa.ba/product_uploads/lm3L5a9AGN2XRwnfhq4X1avtG87lqgTw.jpg',
                'Лепчиња 🍞'
            ),
            (
                'Такос',
                'Тортиља, пилешки стек, марула, ајсберг, чедар, домат, кромид, магдонос, јалапено пиперчиња',
                550.0,
                100,
                'https://www.korpa.ba/product_uploads/FKWacKVBvtRtj2ZKxflyA139AYOXtxhZ.jpg',
                'Такос и Кесадиља 🌮'
            ),
            (
                'Кесадиља пилешка',
                'Тортиља, пилешки стек, ајдамер, зеленчук, зачини',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/Tai2GqfNGKz13wTHMoxT9T9cnJmiZ9mg.jpg',
                'Такос и Кесадиља 🌮'
            ),
            (
                'Кесадиља зеленчук',
                'Тортиља, ајдамер, зеленчук, зачин',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/d5YmxdmV4yRnISQV1YzN9BBhVbc1aQPZ.jpg',
                'Такос и Кесадиља 🌮'
            ),
            (
                'Пилешка Паеља за 2 особи',
                'Ориз, кромид, морков, лук, црвена пиперка, шафран, пилешко месо, бело вино',
                900.0,
                100,
                'https://www.korpa.ba/product_uploads/Pb8gmSdREcynTnRIKsV4M2EgR8P8Fyfz.jpg',
                'Паеља🍤'
            ),
            (
                'Морска Паеља за 2 особи',
                'Ориз, кромид, морков, лук, црвена пиперка, шафран, морски плодови, бело вино',
                1520.0,
                100,
                'https://www.korpa.ba/product_uploads/SkGZvjmBrmgGq1U8t8xKA1DjYI3g4sJv.jpeg',
                'Паеља🍤'
            ),
            (
                'Парма паста',
                'Пршута, пелати, хопла, пармезан, лук',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/OvVrBLH3QsWDPdipxEbrxoUqsCHCEwhE.jpg',
                'Паста 🍝'
            ),
            (
                'Фунги паста',
                'Печурки, хопла, пармезан, лук',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/qCMe8ypsXQ9RNDAottVIt5Els99eNAvP.jpg',
                'Паста 🍝'
            ),
            (
                'Арабиата паста',
                'Црвена пиперка, кромид, маслинки, маслиново масло, магдонос, пармезан, лук',
                410.0,
                100,
                'https://www.korpa.ba/product_uploads/LuOZb0xHYr8pHUn0M307hfqNJMTkQGbH.jpg',
                'Паста 🍝'
            ),
            (
                'Карбонара паста',
                'Сланина, хопла, јајца, пармезан, лук',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/hupqU5MEsE7OaxZradTyJBIgDCNCeJb0.jpg',
                'Паста 🍝'
            ),
            (
                'Песто паста',
                'Лук, ореви, хопла, пармезан',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/o11DWmFy2rFna1u3oLRL7VMBGq2m75xy.jpg',
                'Паста 🍝'
            ),
            (
                'Базилко паста',
                'Пелати, босилок, лук, пармезан',
                440.0,
                100,
                'https://www.korpa.ba/product_uploads/s6qRRb3fvYTLywnhn6eubDNeuXQLjV0Z.jpg',
                'Паста 🍝'
            ),
            (
                '4 вида сирење паста',
                'Ајдамер, чедар, плаво сирење, пармезан',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/W0ZmrNZNM13iggp9lfGFtDT5HgEfROuf.jpg',
                'Паста 🍝'
            ),
            (
                'Италиано паста',
                'Домат, пармезан, лук, магдонос, путер, моцарела',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/NfobTL4JcSQ6bkfUXBCuCNRQAEyHhmDo.jpg',
                'Паста 🍝'
            ),
            (
                'Алио Олио паста',
                'Шпагети, маслиново масло, благ буковец, лук, магдонос, феферони',
                430.0,
                100,
                'https://www.korpa.ba/product_uploads/62cpj9mXsNM9JFGuYu34FVYzC8h7AcO7.jpg',
                'Паста 🍝'
            ),
            (
                'Болоњезе шпагети',
                'Шпагети, телешко мелено месо, пелати',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/H7RXQDLkVFpNbK5ScTeWra444L5G6UE5.jpg',
                'Паста 🍝'
            ),
            (
                'Топло Ладно',
                '',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/2uIGTZCUyeP3ogexBaBJFS95hERjnMOq.jpg',
                'Десерти 🍰'
            ),
            (
                'Вафла по избор',
                '',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/c5sJqFeT4TRKZq3huSgkkDhNJBUCN0Om.jpg',
                'Десерти 🍰'
            ),
            (
                'Палачинка по избор',
                '',
                250.0,
                100,
                'https://www.korpa.ba/product_uploads/2V0IAIDmW6ta7lz6APfk8SuACDyRpseg.jpg',
                'Десерти 🍰'
            ),
            (
                'Миа Леве',
                'Смокви, сладолед од ванила, ореви',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/otzoivCw8YnzfbhLbxAas1M52nFHquad.jpg',
                'Десерти 🍰'
            ),
            (
                'Домашна пастрмајлија пилешка',
                'Пилешко месо, сланина, феферони',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/V9ml8jZgKam1GX1x1Mf4Xgk0t4dwarNR.jpg',
                'Пастрмајлија 👨🏼\u200d🍳'
            ),
            (
                'Домашна пастрмајлија свинска',
                'Свинско месо, сланина, феферони',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/caEkegX2H9eFOCdcdKumnTR4I67Kxw1t.jpg',
                'Пастрмајлија 👨🏼\u200d🍳'
            ),
            (
                'Ветаријанска пастрмајлија',
                'Растителен кашкавал, маслинка, пиперка, домат, печурки, модар домат',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/OSB5fST0T5eLTyLz7vs9oasTIFoAxyNd.jpg',
                'Пастрмајлија 👨🏼\u200d🍳'
            ),
            (
                'Пастрмајлија пилешка',
                'Пилешко месо, феферони',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/zlZqyt3lKpMQIwawKlW4WWphGh5jCWfG.jpg',
                'Пастрмајлија 👨🏼\u200d🍳'
            ),
            (
                'Пастрмајлија свинска',
                'Свинско месо, феферони',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/38VHVs2Qxd7ioXVsHnO6a0qeCBiZkYAG.jpg',
                'Пастрмајлија 👨🏼\u200d🍳'
            )
        ]
    ),
    (
        'Royal Burger Debar Maalo',
        'Доставуваме до Вашата врата',
        'https://korpa.ba/restaurant_uploads/Gay0IEPWugE4a5KHek6gMw28AUEY2SLC.jpg',
        'Burgers',
        25,
        [
            (
                'Combo 1',
                '3 x Chicken Tenders (пилешки прсти), 1 x French Fries, 1 x Ranch sauce',
                165.0,
                100,
                'https://www.korpa.ba/product_uploads/3lD3PSZm7cM3CiRpZj7txrQDljcOTr3R.jpg',
                'ROYAL COMBO 👑'
            ),
            (
                'Combo 2',
                '5 x Chicken Tenders (пилешки прсти), 1 x French Fries, 1 x Ranch sauce',
                200.0,
                100,
                'https://www.korpa.ba/product_uploads/IoIQ0hArzKeZdAGMPGcA4TsMit48025B.jpg',
                'ROYAL COMBO 👑'
            ),
            (
                'Combo 3',
                '4 x Nuggets, 4 x Chili Cheese Nuggets, Ranch Sauce',
                140.0,
                100,
                'https://www.korpa.ba/product_uploads/5ynAwx2iIevMSA4GjGsowAgxcfrcBiZE.jpg',
                'ROYAL COMBO 👑'
            ),
            (
                'Combo 4',
                '2 x Chicken Tenders (пилешки прсти), 4 x Chicken Nuggets, 6 x Onion Rings, 1 x Ranch sauce',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/ZRdG29KRaOi1PhGK891Hy8YH3JGcPxRU.jpg',
                'ROYAL COMBO 👑'
            ),
            (
                'Hamburger',
                'Лепче, кромид, домат, кари сос, кисели краставички, плескавица, розев сос, марула',
                170.0,
                100,
                'https://www.korpa.ba/product_uploads/jJeUKOPaEI9B7zgWU2oH9fD0EJ7W80KN.jpg',
                'Burger 🍔'
            ),
            (
                'Cheeseburger',
                'Лепче, кромид, домат, кари сос, кисели краставички, две парчиња кашкавал, плескавица, розев сос, марула',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/LFPbiIHmGN5xvISH2rIYzh6DsZ7JPuwG.jpg',
                'Burger 🍔'
            ),
            (
                'Baconburger',
                'Лепче, кромид, домат, две парчиња сланина, кари сос, кисели краставички, кашкавал, плескавица, розев сос, марула',
                200.0,
                100,
                'https://www.korpa.ba/product_uploads/fBWylBpIi3fpyC5Ia79ZkxM4EJxzalM4.jpg',
                'Burger 🍔'
            ),
            (
                'Doubleburger',
                'Лепче, кромид, домат, кари сос, кисели краставички, четири парчиња кашкавал, две плескавици, розев сос, марула',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/Rhq69iz3KYVOWEZu5F6MFrlCto5cYkJy.jpg',
                'Burger 🍔'
            ),
            (
                'Royalburger',
                'Лепче, кромид, домат, сланина, кари сос, кисели краставички, кајмак, плескавица, розев сос, марула',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/fGsgepnJNNzFjlsOsTFV2bCCNX5pfyJS.jpg',
                'Burger 🍔'
            ),
            (
                'Vege Burger',
                'Лепче, кромид, домат, кари сос, кисели краставички, кашкавал x 3, розев сос, марула',
                120.0,
                100,
                'https://www.korpa.ba/product_uploads/Xia3u2tiATZyiQIKXnETmMTwGTTJd3Mb.jpg',
                'Burger 🍔'
            ),
            (
                'Crispy Chicken',
                'Лепче, кромид, домат, кари сос, кисели краставички, две парчиња похован стек, розев сос, марула',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/ZSiyHLVITpZf7atFPdhHDf2CvHESylqR.jpg',
                'Chicken Burger 🍗🍔'
            ),
            (
                'Cheese Chicken',
                'Лепче, кромид, домат, кари сос, кисели краставички, две парчиња кашкавал, две парчиња похован стек, розев сос, марула',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/Muoo7vncO83FmUdDHPnbLaJUSDipiYWj.jpg',
                'Chicken Burger 🍗🍔'
            ),
            (
                'Bacon Chicken',
                'Лепче, кромид, домат, две парчиња сланина, кари сос, кисели краставички, кашкавал, две парчиња похован стек, розев сос, марула',
                200.0,
                100,
                'https://www.korpa.ba/product_uploads/HtnIKDsKTgtiWepEV8OkNye9TdeuNdnW.jpg',
                'Chicken Burger 🍗🍔'
            ),
            (
                'Spicy Chicken',
                'Лепче, марула, розев сос, две парчиња поховано пилешко, кисели краставички, кари сос, чили зачин, домат, кромид',
                185.0,
                100,
                'https://www.korpa.ba/product_uploads/gEIDNisaMuZMbrScIo72pSpKXiwQGZ1A.jpg',
                'Chicken Burger 🍗🍔'
            ),
            (
                'Royal Chicken',
                'Лепче, кромид, домат, две парчиња сланина, кари сос, кисели краставички, кајмак, две парчиња похован стек, розев сос, марула',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/4TozrDOGJWNsnTTaGIXLjNTOHdyqkOEu.jpg',
                'Chicken Burger 🍗🍔'
            ),
            (
                'Chicken Burger',
                'Лепче, кромид, домат, кари сос, кисели краставички, две парчиња стек на скара, розев сос, марула',
                185.0,
                100,
                'https://www.korpa.ba/product_uploads/CtBZAqc5hVTLe8gkCLb2zsipQb2cyOMa.jpg',
                'Chicken Burger 🍗🍔'
            ),
            (
                '6 pc. Chicken Wings',
                '',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/1YxAZ01ZgjITn2Hl2W44Wlz7TBf0myI8.jpg',
                'Chicken 🍗'
            ),
            (
                '9 pc. Chicken Wings',
                '',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/rNOjWer7YQSBnwLFJr2VzkPcMYPmkVcK.jpg',
                'Chicken 🍗'
            ),
            (
                '6 pc. Nuggets + F. Fries',
                '',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/kAKbsinuBDX3Sef6WEsEEJnlyJ4BLEvx.jpg',
                'Chicken 🍗'
            ),
            (
                '9 pc. Nuggets + F. Fries',
                '',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/5SwAjKhtqH48TyIkf7Lez1i8X3nW9Y5Z.jpg',
                'Chicken 🍗'
            ),
            (
                '15 pc. Nuggets + F. Fries',
                '',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/j0avvQDXGLUnRBO2lHhMpW27Y4SzM8ms.jpg',
                'Chicken 🍗'
            ),
            (
                '6 pc.  Hot Chicken Wings',
                '',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/wUzLsdUx7j13fYvcsOcSNrB6HoHHg6lP.jpg',
                'Chicken 🍗'
            ),
            (
                '9 pc. Hot Chicken Wings',
                '',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/J0oE1O9AiXOM4qWAFrojwJVweWMI7KBz.jpg',
                'Chicken 🍗'
            ),
            (
                '4 pc. Chili Cheese Nuggets',
                '',
                90.0,
                100,
                'https://www.korpa.ba/product_uploads/fD4EJyS5LMRGln7KBk1v4x0c6jUVgXWo.jpg',
                'Chicken 🍗'
            ),
            (
                '7 pc.  Chili Cheese Nuggets',
                '',
                130.0,
                100,
                'https://www.korpa.ba/product_uploads/vJ7orfDwIef0E61V8cvN0DVEwlARvbuT.jpg',
                'Chicken 🍗'
            ),
            (
                'Royal Wrap',
                'Тортиља, марула, розев сос, домат, две парчиња поховано пилешко, кари сос',
                185.0,
                100,
                'https://www.korpa.ba/product_uploads/YD958eiggOHJudT8m7cReqVzwPQ2FIrP.jpg',
                'Wrap 🌯'
            ),
            (
                'Chicago Hot Dog',
                'Лепче, кромид, домат, кечап, кари сос, виршла, розев сос, кисели краставички',
                140.0,
                100,
                'https://www.korpa.ba/product_uploads/R51iUFi3uTqZDbpOmBQaDhxZVNhzZinV.jpg',
                'Hot Dog 🌭'
            ),
            (
                'Fish Burger',
                'Лепче, кромид, домат, кари сос, кисели краставички, похована риба, розев сос, марула',
                215.0,
                100,
                'https://www.korpa.ba/product_uploads/iE2jp46jwqUsS4s6XrbJJsARjgQBOLrG.jpg',
                'Fish 🐠'
            ),
            (
                'Calamari Burger',
                'Лепче, кромид, домат, тартар сос, 5 лигњи, розев сос, марула, лепче',
                195.0,
                100,
                'https://www.korpa.ba/product_uploads/C0zPw3UiUPTB2KsWSsDd3Q9oSb32mNBF.jpg',
                'Fish 🐠'
            ),
            (
                'Caesar Salad',
                'Сецкан стек x 2, кубети, доматни коцки, розев сос, марула',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/Uy2O2bOBUwqrpMsaCcqNZhq70EHdm64I.jpg',
                'Salad 🥙'
            ),
            (
                'Chicken Salad',
                'Похован стек, доматни коцки, розев сос, марула',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/uoSPTMTi1oiUOhq8831bvaaezEsno1sS.jpg',
                'Salad 🥙'
            ),
            (
                'Coral Salad',
                'Поховани лигњи x 4, пченка, доматни коцки, розев сос, марула',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/Djp9GMHWQK4wiXbNdK9m106ecnzECaUk.jpg',
                'Salad 🥙'
            ),
            (
                'Kids Burger Menu',
                'Бургер со плескавица, помфрит, детско сокче + играчка',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/xzMcvB0PwrHz1xPr1YoGSY50O1Do0qET.jpg',
                'Kids Menu 🌈'
            ),
            (
                'Kids Chicken Menu',
                'Бургер со печен или похован стек, помфрит, детско сокче + играчка',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/btljPt9xFA4pMs3VDybgcg6DMa1KCEwZ.jpg',
                'Kids Menu 🌈'
            ),
            (
                'Small French Fries',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/6PaI7IPlMnDsW7grOPGY8vFtR7LOUW4F.jpg',
                'Extras 🍟'
            ),
            (
                'Big French Fries',
                '',
                90.0,
                100,
                'https://www.korpa.ba/product_uploads/Xd6JgWP1j83pl8vj1cnfIpjn9HsADs0k.jpg',
                'Extras 🍟'
            ),
            (
                'Small Canoe French Fries',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/CzK3ZJX6vjUSaXWJ8vkAOoeiglOGMSxM.jpg',
                'Extras 🍟'
            ),
            (
                'Big Canoe French Fries',
                '',
                100.0,
                100,
                'https://www.korpa.ba/product_uploads/C5afYF0FjDt3aNOB797HbNZdZK0jgZzs.jpg',
                'Extras 🍟'
            ),
            (
                'Кари Сос',
                '',
                25.0,
                100,
                'https://www.korpa.ba/product_uploads/3ZXVrSFOPradBHi9Qe9JLbWPPiGgeixH.jpg',
                'Extras 🍟'
            ),
            (
                'Розев Сос',
                '',
                25.0,
                100,
                'https://www.korpa.ba/product_uploads/ivGDufQMIg0RWG5MTiWOPmQ3eJroUcCq.jpg',
                'Extras 🍟'
            ),
            (
                'Кечап',
                '',
                25.0,
                100,
                'https://www.korpa.ba/product_uploads/g8XRHyB1iCaIhsfqtwOuwWIWFcoV3QGC.jpg',
                'Extras 🍟'
            ),
            (
                'Coca Cola 0.45',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/NNBIJtovHgCa8weAqgJAYBHLHiNuzNkH.jpg',
                'Drinks 🥤'
            ),
            (
                'Coca Cola 0.33',
                '',
                60.0,
                100,
                'https://www.korpa.ba/product_uploads/uf23v7HXawRkHwCOQvfUa3gz2SfxaWXg.jpg',
                'Drinks 🥤'
            ),
            (
                'Fanta 0.33',
                '',
                60.0,
                100,
                'https://www.korpa.ba/product_uploads/ik2mM9FwIt3F3Y53a4EzdA6D3K7ANQSU.jpg',
                'Drinks 🥤'
            ),
            (
                'Fanta 0.45',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/uR93rozpCz3moCzdO68lZ7VrQVKEbDeC.jpg',
                'Drinks 🥤'
            ),
            (
                'Sprite 0.33',
                '',
                60.0,
                100,
                'https://www.korpa.ba/product_uploads/3NVA3IlqU3wYzKcASiSTzEO80qu4G4dP.jpg',
                'Drinks 🥤'
            ),
            (
                'Sprite 0.45',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/qGp9Fa9OP19HCTWAyZ2xeIQkMndn9Egw.jpg',
                'Drinks 🥤'
            ),
            (
                'Schweppes 0.33',
                '',
                60.0,
                100,
                'https://www.korpa.ba/product_uploads/TuHHIbuHzm7I88YptVi5MXGojfBBJLHC.jpeg',
                'Drinks 🥤'
            ),
            (
                'Schweppes 0.5',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/Ea9p8neavQPkkfTbGTysEeNvVmlGSPis.jpg',
                'Drinks 🥤'
            ),
            (
                'Rosa 0.5',
                '',
                50.0,
                100,
                'https://www.korpa.ba/product_uploads/3AY0aGXqy7w6an7v9g7UZdJ0Gdy11F1w.png',
                'Drinks 🥤'
            ),
            (
                'Fuze Ice Tea Peach 0.5',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/XOBrkUGEIP3yD4ypjvjXB2XsbnA6lf3y.png',
                'Drinks 🥤'
            ),
            (
                'Fuze Ice Tea Lemon 0.5',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/GzfsWI7V3XHnB0XcJZK3dOTwE4pybhMr.png',
                'Drinks 🥤'
            ),
            (
                'Next Joy Bozel 0.5',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/yF9mPWammmt9BVgxpsm1xs7FihOwYkAH.png',
                'Drinks 🥤'
            ),
            (
                'Next Joy Cherry 0.5',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/xGK07JL7CImZ4Ef0u1QNnSc2Dt66GbyF.png',
                'Drinks 🥤'
            ),
            (
                'Next Lemonade 0.4',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/4JhMrjmPcgGTrXpg6YZmDIGXDkrocrMi.jpg',
                'Drinks 🥤'
            ),
            (
                'Next Lemonade Mint 0.4',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/7jKFnjoLGEZjVfGUcdwMqzIHj99y5pLM.jpg',
                'Drinks 🥤'
            ),
            (
                'Heineken 0.33',
                '',
                90.0,
                100,
                'https://www.korpa.ba/product_uploads/HOUzmNeZYRpRxz6GivdfeT5dci4QWMl8.jpg',
                'Beer 🍺'
            ),
            (
                'Skopsko 0.33',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/af9vqKg7OWxXVuOhfqhHam7HSJa85gzU.jpg',
                'Beer 🍺'
            ),
            (
                'Skopsko 0.5',
                '',
                90.0,
                100,
                'https://www.korpa.ba/product_uploads/TaSyOSYU3pf0TW3tQibkZpVr7MLj9kir.jpg',
                'Beer 🍺'
            ),
            (
                'Amstel 0.33',
                '',
                90.0,
                100,
                'https://www.korpa.ba/product_uploads/s68J5ZnofrVfkqrH44GoqXZMKlTfjZgs.png',
                'Beer 🍺'
            )
        ]
    ),
    (
        'Skara Bar',
        'Доставуваме до Вашата врата',
        'https://korpa.ba/restaurant_uploads/Juan0br6rzzPYpQT0znOgM0XnsAflenI.jpg',
        'Grill / Balkan',
        25,
        [
            (
                'Телешка чорба',
                '',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/PDywTaDyztGGxZMbCIDsSLFDrupStJgn.jpg',
                'Чорби🍵'
            ),
            (
                'Чорба од лосос',
                '',
                200.0,
                100,
                'https://www.korpa.ba/product_uploads/FNepT6pbnuxGGAqjEIwQNOeg6vO2cnD4.jpg',
                'Чорби🍵'
            ),
            (
                'Македонски доручек',
                'Тост лепчиња, јајца на око, ајвар, овчо сирење',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/2YAPg7CYvSijQCGBa2LMRE8fXmHOQESn.jpg',
                'Појадок🥘'
            ),
            (
                'Англиски доручек',
                'Тост лепчиња, јајца на око, колбас, печурки, помфрит',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/AAZ6Na9xMRmebmjescRBVBuLVMp8Qowd.jpg',
                'Појадок🥘'
            ),
            (
                'Омлет со сланина',
                '',
                200.0,
                100,
                'https://www.korpa.ba/product_uploads/jMU7wrXAp3nIkjiRojLd7YiU0BPVkEEE.jpg',
                'Појадок🥘'
            ),
            (
                'Омлет со сирење и зеленчук',
                '',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/x56QcLNo44beXkRIhcNg9OIsZgd0J36U.jpg',
                'Појадок🥘'
            ),
            (
                'Meшaнa cвeжa caлaтa',
                'Сeзонcки зеленчук',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/gxGIVbLUhTJJ7UfhZuG7yXieziCkc0aE.jpg',
                'Салати🥗'
            ),
            (
                'Шопска салата',
                'Домат, краставица, овчо сирење',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/U2aEkxnMCMWwJfWjkKjNLAcN76aItqJQ.jpg',
                'Салати🥗'
            ),
            (
                'Грчка салата',
                'Домат, краставица, овчо сирење, маслинки, кромид',
                240.0,
                100,
                'https://www.korpa.ba/product_uploads/4KhOm7tx3yYYh1hlqhQVg9IIcSLJSjrJ.jpg',
                'Салати🥗'
            ),
            (
                'Македонска салата',
                'Домат, потпечени пиперки, кромид',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/CPL35o7JibN3VWEoreaGHUO3JTz7uUr2.jpg',
                'Салати🥗'
            ),
            (
                'Таратор',
                'Краставица, павлака, лук',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/Uc72P8QAZ9aIc0QF6yTfLiZrGxTq1wkk.jpg',
                'Салати🥗'
            ),
            (
                'Селска салата',
                'Пиперки, домат, краставица, овчо сирење',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/Kf6FQagXIo9P3snndXeolkT8yYv9AoEK.jpg',
                'Салати🥗'
            ),
            (
                'Рукола салата',
                'Рукола, шери домати, пармезан, моцарела, брусница',
                340.0,
                100,
                'https://www.korpa.ba/product_uploads/55FK3lGqFTuH9lCFJxxnurB9YpZFBep4.jpg',
                'Салати🥗'
            ),
            (
                'Салата Скара бар',
                'Марула, рукола, суви домати, пармезан, сусам, сланина, модар домат',
                360.0,
                100,
                'https://www.korpa.ba/product_uploads/MCfcOR23gWPp6YY4OCfsiktDQTpn5OiS.jpg',
                'Салати🥗'
            ),
            (
                'Цезар салата',
                'Марула, пилешко, пармезан, кубети, дресинг сос',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/Vhm8HWkxOTV1uxvWzy6ELwd1cVjOrWWo.jpg',
                'Салати🥗'
            ),
            (
                'Кајмак 100гр',
                '',
                160.0,
                100,
                'https://www.korpa.ba/product_uploads/cZHUWQSNuYNoeCmWvMcH7JWc1YqqYKOe.jpg',
                'За не многу гладни🧀'
            ),
            (
                'Печурки шампињони 250гр',
                '',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/kMHVHW6dXXov4Qno0db2sriY1dcBSPhI.jpg',
                'Лесна варијанта🥯'
            ),
            (
                'Печурки вргањ 250гр',
                '',
                440.0,
                100,
                'https://www.korpa.ba/product_uploads/F6zZkbyT2ZGI7DImqPr4haCAvvCeYvGj.jpg',
                'Лесна варијанта🥯'
            ),
            (
                'Прасечко печење 1кг',
                '',
                1990.0,
                100,
                'https://www.korpa.ba/product_uploads/OzHpuDksC469Q5lAotdgiyCQMgM9i9nW.jpg',
                'Печење🥩'
            ),
            (
                'Јагнешко печење 1кг',
                '',
                2190.0,
                100,
                'https://www.korpa.ba/product_uploads/G68Rpc3A8OkDLHnyZOZ1KltkRWMWDvup.jpg',
                'Печење🥩'
            ),
            (
                'Ребро во фурна 350гр',
                '',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/2rnBMs76A6wK7zIlUmu1kqLrQCtOj1vu.jpg',
                'Печење🥩'
            ),
            (
                'Ребро во фурна со bbq сос 350гр',
                '',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/24NpmadP2kUFyWfEf0hmLN8EbKl5dJ8O.jpg',
                'Печење🥩'
            ),
            (
                'Гравче тавче',
                '',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/mykIH3EyVQG2w4fXk9SdbrAibE5JHyHn.jpg',
                'Готвени јадења🫕'
            ),
            (
                'Пилешки прсти 250гр',
                '',
                340.0,
                100,
                'https://www.korpa.ba/product_uploads/HQzRzWEJFxmttYtBDWtNS98wlg2fR7Ts.jpg',
                'Скара🍖'
            ),
            (
                'Полнето пилешко со моцарела и сув домат 250гр',
                '',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/hYF1zukrT4DoQmyyZcmKCFsTd5r9j99A.jpg',
                'Скара🍖'
            ),
            (
                'Пилешко во кари 250гр',
                '',
                360.0,
                100,
                'https://www.korpa.ba/product_uploads/RYrB9nC0f8f3SbFhCF27BXqpUmyyON20.jpg',
                'Скара🍖'
            ),
            (
                'Пилешко соте со кикирики 300гр',
                'Пилешко, кромид, печурки, кикирики, крем сос',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/YZR008LfulqX8zsOTZFOc5FGO1hk1qSZ.jpg',
                'Скара🍖'
            ),
            (
                'Свински медаљони со прелив 250гр',
                'Свинско филе, печурки',
                550.0,
                100,
                'https://www.korpa.ba/product_uploads/AIO1PsHJvBimI1Qsb9TnNuXvyA72y90p.jpg',
                'Скара🍖'
            ),
            (
                'Свинска бела вешалица 250гр',
                '',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/a96mHhRYjCf0DsRxrXogBCfEcU59TboY.jpg',
                'Скара🍖'
            ),
            (
                'Свинско ребро 350гр',
                '',
                360.0,
                100,
                'https://www.korpa.ba/product_uploads/G7Ndz15b1gdNzv4NdOj9BSiKGa46RhQX.jpg',
                'Скара🍖'
            ),
            (
                'Бечка шницла 350гр',
                '',
                480.0,
                100,
                'https://www.korpa.ba/product_uploads/qMPXnZYEFpqTI8LKo7qC0pFkQ8rEMId2.jpg',
                'Скара🍖'
            ),
            (
                'Свинско филе со праз и сува пиперка 300гр',
                '',
                510.0,
                100,
                'https://www.korpa.ba/product_uploads/L8LPzayZbiYyNLq2qfo0vlTV6rgc5C7a.jpg',
                'Скара🍖'
            ),
            (
                'Свинско филе полнето со моцарела и рукола 350гр',
                '',
                580.0,
                100,
                'https://www.korpa.ba/product_uploads/Ml9YTpb4dsv1OAZ3Co8zSOVqTUBwgELY.jpg',
                'Скара🍖'
            ),
            (
                'Тава Скара Бар (за две лица)',
                'Пилешко и свинско месо, кашкавал, печурки и зеленчук',
                890.0,
                100,
                'https://www.korpa.ba/product_uploads/hLwT50HRnLRogZLPVFQuU58JLzNjBRKD.jpg',
                'Скара🍖'
            ),
            (
                'Телешки бејби бифтек со бејби морков со пепер сос 250гр',
                '',
                1390.0,
                100,
                'https://www.korpa.ba/product_uploads/TgSR94XAIB6QTWggFug6ROgT0fgmlgeQ.jpg',
                'Скара🍖'
            ),
            (
                'Плескавица 200гр',
                '',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/qC5LP7EuvyIfPtfHXoMsi6G9MsLMLd1Q.jpg',
                'Скара🍖'
            ),
            (
                'Шарска плескавица 250гр',
                '',
                310.0,
                100,
                'https://www.korpa.ba/product_uploads/TvyYVK6zm7iaeQioEodaqkKpmqMxvygw.jpg',
                'Скара🍖'
            ),
            (
                'Плескавица Скара бар со кајмак 350гр',
                '',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/7s03HI2yBMoLMvy8mtkal6VVS4wqAgbN.jpg',
                'Скара🍖'
            ),
            (
                'Плескавица Скара бар со кајмак во домашно лепче со сусам',
                '440гр',
                470.0,
                100,
                'https://www.korpa.ba/product_uploads/l9oaS1Q60iUGidVTchRwND88VVFFljbd.jpg',
                'Скара🍖'
            ),
            (
                'Чаден димен дебел колбас 200гр',
                'Сецкано месо, праз, сува пиперка',
                250.0,
                100,
                'https://www.korpa.ba/product_uploads/MlbydukBGuaOYHhNS1Y5au0Ez1nJHylZ.jpg',
                'Скара🍖'
            ),
            (
                'Телешки мускул во сос од вргањ',
                '',
                690.0,
                100,
                'https://www.korpa.ba/product_uploads/pKZoMxdK19CuNmVGyY0miydNmEjEXjFw.jpg',
                'Скара🍖'
            ),
            (
                'Орада на скара 400гр',
                '',
                560.0,
                100,
                'https://www.korpa.ba/product_uploads/rj43fgoCOArYSTpadrP4S0x2Z4uxpmUF.jpg',
                'Риба🐟'
            ),
            (
                'Лосос на скара 250гр',
                '',
                690.0,
                100,
                'https://www.korpa.ba/product_uploads/emyUDdpaxSc92F7RH1QkcGvb2ljqFtbx.jpg',
                'Риба🐟'
            ),
            (
                'Пастрмка 350гр',
                '',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/J0vYHhlKRprW8ou2ELw0uzOLU6ivKFEx.jpg',
                'Риба🐟'
            ),
            (
                'Лигњи свежи 300гр',
                '',
                520.0,
                100,
                'https://www.korpa.ba/product_uploads/Z5kUXjmEG2imHIRY22xcbwT3aXkJO21Q.jpg',
                'Риба🐟'
            ),
            (
                'Лигњи поховани 300гр',
                '',
                520.0,
                100,
                'https://www.korpa.ba/product_uploads/qnbzzSJUHLNmNFZd8qIRJ4yzognWQrMn.jpg',
                'Риба🐟'
            ),
            (
                'Баклава',
                '',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/HMwIKbn04CiDjyTwu9STH6eGwq6wZSuJ.jpg',
                'Десерти🧁'
            )
        ]
    ),
    (
        'Spizzicotto - EU',
        'Доставуваме до Вашата врата',
        'https://korpa.mk/restaurant_uploads/LpswBaW75yVEQjwnggxxCXav6I8LJHj4.jpg',
        'Italian / Pizza',
        25,
        [
            (
                'Парче пица - Маргарита',
                '',
                100.0,
                100,
                'https://www.korpa.ba/product_uploads/kMEgruWu4DV0868d5x9tTS6tBgwigGkY.jpg',
                'Pizza 🍕'
            ),
            (
                'Парче пица - Капричиоза',
                '',
                100.0,
                100,
                'https://www.korpa.ba/product_uploads/mmbIuY3U30CxjINyzhwiLFBDEEFGVbFz.jpg',
                'Pizza 🍕'
            ),
            (
                'Парче пица - Кулен',
                '',
                100.0,
                100,
                'https://www.korpa.ba/product_uploads/jRsD5mr5b5SNxuDZSE5gYxCUPiPCNJtj.jpg',
                'Pizza 🍕'
            ),
            (
                'Калцоне',
                'Тесто, моцарела, доматен сос, пилешка шунка',
                60.0,
                100,
                'https://www.korpa.ba/product_uploads/5ey4brYP5LxqLyqHKo1oJcHPuSgOi1TU.jpg',
                'Pizza 🍕'
            ),
            (
                'Везуиво',
                'Тесто, моцарела, јајце, доматен сос',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/LwccaretNPmnXib1owO3YDmYUzxBx9oT.jpg',
                'Pizza 🍕'
            ),
            (
                'Фантазија',
                'Лепче, моцарела, пилешка шунка, домат, краставица, марула',
                100.0,
                100,
                'https://www.korpa.ba/product_uploads/BBaSHCq5bGfzPYERCSAa5q9jlwNaQfwU.jpg',
                'Сендвичи 🥪'
            ),
            (
                'Олива',
                'Лепче, марула, зелка, морков, домат, краставица, сирење, моцарела',
                120.0,
                100,
                'https://www.korpa.ba/product_uploads/2NOWWAdaWLHkiSBKRAcR8ifZUGOhyF6R.jpg',
                'Сендвичи 🥪'
            ),
            (
                'Домашен Француски',
                'Кифла, пилешка шунка, моцарела, марула, домат, краставица',
                140.0,
                100,
                'https://www.korpa.ba/product_uploads/Uw93zTyo7pbDkvXqjUw5oRzIMu1mCEyX.jpg',
                'Сендвичи 🥪'
            ),
            (
                'Тост пилешка шунка',
                'Лепче, кашкавал, пилешка шунка',
                120.0,
                100,
                'https://www.korpa.ba/product_uploads/R3OsPjZvqm6CoIn0Jwd7aKFzFoJmJA35.jpg',
                'Сендвичи 🥪'
            ),
            (
                'Сендвич кулен',
                'Лепче, кашкавал, кулен',
                140.0,
                100,
                'https://www.korpa.ba/product_uploads/M354bEvnJyzEbJorauKeHTeCxA9DB2q6.jpg',
                'Сендвичи 🥪'
            ),
            (
                'Рустико',
                'Кифла, кашкавал, сланина, урнебес салата',
                140.0,
                100,
                'https://www.korpa.ba/product_uploads/6PkX4k8iEqI2uh0pURmO6Bxiz8yHIbHR.jpg',
                'Сендвичи 🥪'
            ),
            (
                'Сендвич со тиквичка',
                'Лепче, зелка, морков, тиквица, марула',
                120.0,
                100,
                'https://www.korpa.ba/product_uploads/y3EtD0hBYa4ODELdRyjDAw88nkpHrqH5.jpg',
                'Сендвичи 🥪'
            ),
            (
                'Сендвич со омлет',
                'Лепче, јајце, домат, сирење',
                130.0,
                100,
                'https://www.korpa.ba/product_uploads/H9UEfTlMcnMmBPfslvK7yFs7s1KZ1OJ9.jpg',
                'Сендвичи 🥪'
            ),
            (
                'Цезар салата',
                'Марула, рукола, двопек, рендан кашкавал, пилешко месо',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/Dvt9Di84daGVJK4fynYVt2gs8psWjNrO.jpg',
                'Салати 🥗'
            ),
            (
                'Туна салата',
                '',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/Vhma9zAaus4pjubEfzNCPClLEEaXvbg6.jpg',
                'Салати 🥗'
            ),
            (
                'Мимоза салата',
                'Марула, јајце, пченка',
                130.0,
                100,
                'https://www.korpa.ba/product_uploads/YXxbeg4NCv9Y2JEAVYYuc9s1yVQCcwzV.jpg',
                'Салати 🥗'
            ),
            (
                'Витаминска салата',
                '',
                130.0,
                100,
                'https://www.korpa.ba/product_uploads/rVSnRQCdxn1Ru0GsLUjU4KLOSqv9OlGx.jpg',
                'Салати 🥗'
            ),
            (
                'Перниче',
                'Тесто, пченка, печурки, кечап, пиперка, кашкавал',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/IszbGDqF0TkMjtsVe0yZoz3nP3fndQdI.jpg',
                'Пити 👩🏼\u200d🍳'
            ),
            (
                'Гибаница',
                'Кори, урда, јајца, блитва',
                100.0,
                100,
                'https://www.korpa.ba/product_uploads/5yaCxms9cWU5I0U3R6uj1hKMnVsT9lkm.jpg',
                'Пити 👩🏼\u200d🍳'
            ),
            (
                'Баничка со сирење мала',
                '',
                50.0,
                100,
                'https://www.korpa.ba/product_uploads/JyNzP44D47RHXPA0tw15g7m97f02kWX2.jpg',
                'Пити 👩🏼\u200d🍳'
            ),
            (
                'Баничка со сирење голема',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/vEfzS7XmsI8uyzmDihHs48xOK8NrWjBb.jpg',
                'Пити 👩🏼\u200d🍳'
            ),
            (
                'Баничка со зелка голема',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/is8t06hio2DVU67GuUEMHLTpptgiyaml.jpg',
                'Пити 👩🏼\u200d🍳'
            ),
            (
                'Баничка со праз голема',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/zP0n9XLUyxfFsp1C2kauxiIU5sRHQYmA.jpg',
                'Пити 👩🏼\u200d🍳'
            ),
            (
                'Баничка со печурки и маслинки голема',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/WMwKL14YUOQyly3tXFACuQntHeKbHF6o.jpg',
                'Пити 👩🏼\u200d🍳'
            ),
            (
                'Отворен Хот Дог',
                'Тесто, виршла, моцарела, доматен сос, пиперка',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/o6RA9E5Xb4dtIlnMD4tsrzsBWp3CfzOd.jpg',
                'Хот Дог 🌭'
            ),
            (
                'Хот Дог',
                'Тесто, виршла',
                60.0,
                100,
                'https://www.korpa.ba/product_uploads/DQntooEYPDAT1iBhoJ3OsV2hJVnKmlDA.jpg',
                'Хот Дог 🌭'
            ),
            (
                'Штрудла со вишни',
                'Кори, вишна',
                50.0,
                100,
                'https://www.korpa.ba/product_uploads/lTYf3bWK8Lr971UqJ7wNH0jdFxdFL9iW.jpg',
                'Штрудла 🥧'
            ),
            (
                'Пастрмајлија пилешка',
                'Тесто, пилешко месо',
                130.0,
                100,
                'https://www.korpa.ba/product_uploads/9NV2IrNdFIdgQfuPxSrkaguMoZezAqTl.jpg',
                'Пастрмајлии 👩🏼\u200d🍳'
            ),
            (
                'Пастрмајлија свинска',
                'Тесто, свинско месо',
                130.0,
                100,
                'https://www.korpa.ba/product_uploads/thNC2seZnZmbfwZttiZhmMTCxzS4MBsB.jpg',
                'Пастрмајлии 👩🏼\u200d🍳'
            ),
            (
                'Coca Cola 0.45',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/muqsEbpRXg9vGYUW0GnBjujrLvVfngN2.png',
                'Пијалоци 🥤'
            ),
            (
                'Fanta Orange 0.5',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/kzBaAPQMGxBHzOQrg7M37nilYkfjnYoJ.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Fanta Tropical 0.45',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/lDSLH5siS8DSdEsmWL7gU6c2dG59jfMp.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Fanta Shocata 0.5',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/O97ZwyfTS8lhcdsDYr4KdFsLQy0IYLK1.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Schweppes Bitter lemon 0.5',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/NIbxcsYXL0ZMMlYn0CVaujFhalT31x85.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Rosa газирана 0.5',
                '',
                50.0,
                100,
                'https://www.korpa.ba/product_uploads/aUgtOeX7oVY8YXZvXNjjXqgfkvaU0Qh4.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Rosa негазирана 0.5',
                '',
                50.0,
                100,
                'https://www.korpa.ba/product_uploads/HQUxOX57PBxtOcgfU0aMZ0e0r7LNGTkF.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Fuze Tea Peach 0.5',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/rxCbQeADQz2aZKFvJ6vXNB2p1nfIHFrw.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Fuze Tea Lemon 0.5',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/aBUMoth29omO5REXZbr7WebFrwkm0yw0.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Next Lemonade Mint 0.4',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/JlV2OGbBvU9wq2iMjzHmaCCouPs0BUqK.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Next Joy Multivitamin 0.45',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/EPBpJECRGJANoCNi9lpZLJpURB6QL8pF.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Скопско 0.5',
                '',
                100.0,
                100,
                'https://www.korpa.ba/product_uploads/KKuYSWYLTIuOPrHxotQjDIVljqoTyYns.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Coca Cola Zero 0.45',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/r4eYQqTJksABuUsQSgbcYzSC45Vj85q5.png',
                'Пијалоци 🥤'
            ),
            (
                'Sprite 0.45',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/Xyctu1ux8TxhC7IPxQAzwLcDrDxfbf8k.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Skopsko Smooth 0.5',
                '',
                100.0,
                100,
                'https://www.korpa.ba/product_uploads/kTo2hdS8UlSgn2BycENfY9LOPMIvkUEp.png',
                'Пијалоци 🥤'
            ),
            (
                'Heineken 0.5',
                '',
                120.0,
                100,
                'https://www.korpa.ba/product_uploads/KfnHomhbxSFYZX7QcWvtb4VhNCeWFQae.jpg',
                'Пијалоци 🥤'
            )
        ]
    ),
    (
        'SushiCo Zen',
        'Доставуваме до Вашата врата',
        'https://korpa.ba/restaurant_uploads/1da4LvVTiP5VPzBbf8jLjhifUXA8GvCA.jpg',
        'Japanese / Sushi',
        25,
        [
            (
                'Органски соја зрна',
                '',
                370.0,
                100,
                'https://www.korpa.ba/product_uploads/q4W8uxTGdrntq6VePMNwqHcKarWvfQsl.jpg',
                'Предјадење  🍴'
            ),
            (
                'Зачинети органски соја зрна',
                '*луто',
                370.0,
                100,
                'https://www.korpa.ba/product_uploads/gF7I55Tf41MCOmj6NFcIU0OsETEdRLVL.jpg',
                'Предјадење  🍴'
            ),
            (
                'Крекери од морски ракчиња',
                '',
                370.0,
                100,
                'https://www.korpa.ba/product_uploads/JFT772yfJx4rkDfQsEnOH6pWrQKsyLV2.jpg',
                'Предјадење  🍴'
            ),
            (
                'Пилешки топчиња',
                '8 парчиња',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/BiWs9OUWIyT1z0QPYXqzUJNt3efgANe0.jpg',
                'Предјадење  🍴'
            ),
            (
                'Крцкав лаврак и чипс',
                '*подготвено со свеж лаврак',
                660.0,
                100,
                'https://www.korpa.ba/product_uploads/g1zB0fyeRjXxS2l84JqcmW6NH5VV5MAM.jpg',
                'Предјадење  🍴'
            ),
            (
                'Ракчиња со кореан сос',
                '10 парчиња *луто',
                700.0,
                100,
                'https://www.korpa.ba/product_uploads/jDOckxtnMn0ETCBCyajV6fjfrMyv7WfE.jpg',
                'Предјадење  🍴'
            ),
            (
                'Крцкави ракчиња',
                '10 парчиња',
                700.0,
                100,
                'https://www.korpa.ba/product_uploads/3yW0gH9QrSMvWzJF9IB6zyMxr1jMiYUz.jpg',
                'Предјадење  🍴'
            ),
            (
                'Темпура бејби лигњи',
                '',
                880.0,
                100,
                'https://www.korpa.ba/product_uploads/vDDzndCwv7rJIaUCKjQA3G9HBqeif3Iv.jpg',
                'Предјадење  🍴'
            ),
            (
                'Темпура ракчиња',
                '',
                1080.0,
                100,
                'https://www.korpa.ba/product_uploads/x39TK6PQzXkq3CzUVoxksIzAU9X4bwDu.jpg',
                'Предјадење  🍴'
            ),
            (
                'Темпура пченка',
                '',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/AZT6UkkP0eW5kKEtXHkgnNm0hO8zJSVC.jpg',
                'Предјадење  🍴'
            ),
            (
                'Карпачо од лосос со понзу сос',
                '',
                920.0,
                100,
                'https://www.korpa.ba/product_uploads/nQIzcUzekIWrHJCCinxOWf6Np1T5mrO3.jpg',
                'Предјадење  🍴'
            ),
            (
                'Крцкав модар патлиџан',
                '',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/ZnIibxZrKnpGNJdQzFZZ5baMbmh9SbFZ.jpg',
                'Предјадење  🍴'
            ),
            (
                'Пилешки катсу прсти',
                '',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/6RwSZAo4ADwYFKo5LcpGXQ9hDEfp1E3G.jpg',
                'Предјадење  🍴'
            ),
            (
                'Јапонски помфрит',
                '',
                370.0,
                100,
                'https://www.korpa.ba/product_uploads/rTZ9jFZgz95mr8PYQ9RM8i4obXpyHcSA.jpg',
                'Предјадење  🍴'
            ),
            (
                'Татаки бифтек со тарфтуфи',
                '',
                850.0,
                100,
                'https://www.korpa.ba/product_uploads/o5pvmKR0PEGnVgVlaWey8zcllK37UC73.jpg',
                'Предјадење  🍴'
            ),
            (
                'Вонтон супа',
                '',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/97XCDBmQNwYK8pNkTcqOabndsYBdYX9s.jpg',
                'Супи 🍵'
            ),
            (
                'Лута и кисела супа',
                '*луто',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/Hl8k8KLW8Vd2fzj4UDTE0JMTPe2HRcig.jpg',
                'Супи 🍵'
            ),
            (
                'Мисо супа',
                '*Содржи алкохол',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/Dt0DcKpW34EtFjL3bkXQrbgkNp1vSwB7.jpg',
                'Супи 🍵'
            ),
            (
                'Том Јам супа',
                '*луто',
                480.0,
                100,
                'https://www.korpa.ba/product_uploads/kQfweVgMdUj1AQKljRCmYSDGym6QKbCY.jpg',
                'Супи 🍵'
            ),
            (
                'Таи супа со морски плодови',
                '*луто',
                530.0,
                100,
                'https://www.korpa.ba/product_uploads/jriEOhuuppL4E8LvHKSOgwlWWm0IPKmk.jpg',
                'Супи 🍵'
            ),
            (
                'Том Ка Гаи',
                '*луто',
                500.0,
                100,
                'https://www.korpa.ba/product_uploads/oRH0HAnkWMo0MIgiCeUV5V9rjq2r7Ys3.jpg',
                'Супи 🍵'
            ),
            (
                'Рамен нудли со димено Тофу',
                '',
                660.0,
                100,
                'https://www.korpa.ba/product_uploads/PQ7UIguNyOHe2VQN4kpUjp2I9q9pbOy2.jpg',
                'Рамен нудли 🍜'
            ),
            (
                'Рамен нудлс со Телешко',
                '',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/hq2zzmQnErXSI3ot5XoDvDNKcgPPWeXN.jpg',
                'Рамен нудли 🍜'
            ),
            (
                'Рамен нудлс со Ракчиња',
                '',
                810.0,
                100,
                'https://www.korpa.ba/product_uploads/UHj3eVnstTxTBuNrTle1D0UB9g0hpdpm.jpg',
                'Рамен нудли 🍜'
            ),
            (
                'Спринг ролс',
                '2 парчиња',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/JxhWEVrWztUHC9E6OqSxnXXFlNr2h2fU.jpg',
                'Дим Сам (Традиционална кинеска храна) 🥟'
            ),
            (
                'Веге Спринг ролс',
                '2 парчиња',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/NNs0Q10nHppML4gV5NAmignHrLvWfpA1.jpg',
                'Дим Сам (Традиционална кинеска храна) 🥟'
            ),
            (
                'Крцкав Вонтон',
                '4 парчиња',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/6D0B0KQujQ6Cmf3gUZCTDieuuB9a9jXp.jpg',
                'Дим Сам (Традиционална кинеска храна) 🥟'
            ),
            (
                'Телешки кнедли',
                '5 парчиња',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/u3iozvorCX03Wtyh9KM2xAvHfAhYn8rU.jpg',
                'Дим Сам (Традиционална кинеска храна) 🥟'
            ),
            (
                'Веге Гиоза',
                '4 парчиња',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/Ki2ZCZb8npEqOi91SmX0169lBHGNvVBi.jpg',
                'Дим Сам (Традиционална кинеска храна) 🥟'
            ),
            (
                'Гиоза со морски плодови',
                '4 парчиња',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/OtPPd4BuESFnKDfPX1f6FxYWWr3GQ5sT.jpg',
                'Дим Сам (Традиционална кинеска храна) 🥟'
            ),
            (
                'Тофу Гиоза',
                '4 парчиња',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/daTxrGRfEWcnvIsm9XvzTmzjScbDq7hT.jpg',
                'Дим Сам (Традиционална кинеска храна) 🥟'
            ),
            (
                'Кореански Вонтон',
                '4 парчиња *луто',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/MYK8qHCzrL0kAiTxwqIritf88USqsYpn.jpg',
                'Дим Сам (Традиционална кинеска храна) 🥟'
            ),
            (
                'Кнедли со морски плодови',
                '5 парчиња',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/JbGe0DQUjbb23KafbBGWnlrvwW7SigE2.jpg',
                'Дим Сам (Традиционална кинеска храна) 🥟'
            ),
            (
                'Бун со пилешко',
                '2 парчиња *луто',
                570.0,
                100,
                'https://www.korpa.ba/product_uploads/6XF1oEB1rWBgJU8i38FH2OKDW7fEth8j.jpg',
                'Бун 🌮'
            ),
            (
                'Бун со патка',
                '2 парчиња *луто',
                680.0,
                100,
                'https://www.korpa.ba/product_uploads/dItEWQLgY6YGQSMMPKLkdfL6a9hA6Xja.jpg',
                'Бун 🌮'
            ),
            (
                'Салата од зачинета зелка',
                '*луто',
                380.0,
                100,
                'https://www.korpa.ba/product_uploads/9JqFdX3fRSQeVE9SWQqxRZULqyW6lsWS.jpg',
                'Салати 🥗'
            ),
            (
                'SushiCo вакаме салата',
                '',
                480.0,
                100,
                'https://www.korpa.ba/product_uploads/tNG9DQPKg83vNnC1saiFLE8D9zsJyBXm.jpg',
                'Салати 🥗'
            ),
            (
                'Кимчи салата',
                'Кинеска зелка *луто',
                410.0,
                100,
                'https://www.korpa.ba/product_uploads/kJUkbFlRcvhZ2fBIS3SzorfRX7t7qK0N.jpg',
                'Салати 🥗'
            ),
            (
                'Азиска салата',
                '',
                460.0,
                100,
                'https://www.korpa.ba/product_uploads/kWfooGJTVbqwLSVgUoGCZaPrT3IHHBB7.jpg',
                'Салати 🥗'
            ),
            (
                'Азиска салата со крцкави ракчиња',
                '',
                740.0,
                100,
                'https://www.korpa.ba/product_uploads/3Qo1sH5ZWqLb8ChfMUdHbf10BBxpYDRk.jpg',
                'Салати 🥗'
            ),
            (
                'Запржен зеленчук',
                '',
                500.0,
                100,
                'https://www.korpa.ba/product_uploads/zO4q87x3fnqtPClIQdr4zgoFchwJXhFO.jpg',
                'Зеленчук 🥦🥬'
            ),
            (
                'Запржен зачинет зеленчук',
                '*луто',
                500.0,
                100,
                'https://www.korpa.ba/product_uploads/s7zy61RVwFrBm6LIPJwPiYzKqM7GRvwF.jpg',
                'Зеленчук 🥦🥬'
            ),
            (
                'Органски соја зрна и аспарагус',
                '',
                740.0,
                100,
                'https://www.korpa.ba/product_uploads/H0QsB8iFbYN73AoYqtqzeynlZhpJGQv2.jpg',
                'Зеленчук 🥦🥬'
            ),
            (
                'Брокула со сос од лук',
                '',
                570.0,
                100,
                'https://www.korpa.ba/product_uploads/8CjNTVKCEPrPcMlmmaRQcxzF7hfnk9O1.jpg',
                'Зеленчук 🥦🥬'
            ),
            (
                'Димено Тофу со зеленчук',
                '*луто',
                740.0,
                100,
                'https://www.korpa.ba/product_uploads/fYhse642nXpjtfJsdmmDTdZWUKY81s5e.jpg',
                'Зеленчук 🥦🥬'
            ),
            (
                'Слатко и кисело пилешко',
                '',
                710.0,
                100,
                'https://www.korpa.ba/product_uploads/4r321edIMTFbgKHAxceqm3i81uCK8lKQ.jpg',
                'Пилешко 🍗'
            ),
            (
                'Генерал Цо пилешко',
                '*луто',
                710.0,
                100,
                'https://www.korpa.ba/product_uploads/jPWM5mMsjXga7xRQW3NAGHjkf6noUgmv.jpg',
                'Пилешко 🍗'
            ),
            (
                'Таи пилешко со индиски ореви',
                '*луто',
                770.0,
                100,
                'https://www.korpa.ba/product_uploads/bjkwnr658y5PfOkYAkND5VKxiAqjm6kt.jpg',
                'Пилешко 🍗'
            ),
            (
                'Јапонско крцкаво пилешко',
                '* Со јапонска сурими салата',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/roKWUblw0MmwAjZoLtAPb8TTfQ9B4SG2.jpg',
                'Пилешко 🍗'
            ),
            (
                'SushiCo пилешко',
                'Сервирано со палачинки и ајсберг  *луто',
                830.0,
                100,
                'https://www.korpa.ba/product_uploads/dPj2ETKlP3s2NO1YrFrQMN7Jn8tREKvM.jpg',
                'Пилешко 🍗'
            ),
            (
                'Крцкаво пилешко со ѓумбир',
                '*луто',
                710.0,
                100,
                'https://www.korpa.ba/product_uploads/laSPCjjymuAPOz5PH0dKKsOQkTlEIolP.jpg',
                'Пилешко 🍗'
            ),
            (
                'Пилешко со црвено кари',
                'Сервирано со ориз *луто',
                770.0,
                100,
                'https://www.korpa.ba/product_uploads/GiDO3Y264Nsj2FqFiggeUzizCbdzefOy.jpg',
                'Пилешко 🍗'
            ),
            (
                'Слатко и кисело свинско',
                '',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/ygdqKw9lJcwqNY6NXrV8mnLryOSiBr5P.jpg',
                'Свинско 🥩'
            ),
            (
                'Свинско со барбикју сос',
                '',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/ZrXeca0H1bQYStncpmeKVTzmsIgG8S3q.jpg',
                'Свинско 🥩'
            ),
            (
                'Свинско со праз и чили сос',
                '*луто',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/AecwAMWaVXkUEPEJ7L9fEggzFgwNzihF.jpg',
                'Свинско 🥩'
            ),
            (
                'Телешко со тенко сечкани пиперки',
                '',
                990.0,
                100,
                'https://www.korpa.ba/product_uploads/8edhvOlN4SGrEnN0hJJUlYjgcNLs8SDH.jpg',
                'Телешко 🍖'
            ),
            (
                'Крцкаво телешко со лимон',
                '',
                990.0,
                100,
                'https://www.korpa.ba/product_uploads/FB9GcKpSgHFF9MEfmsPCrLzqils4Eueo.jpg',
                'Телешко 🍖'
            ),
            (
                'Телешко со шитаке',
                '',
                990.0,
                100,
                'https://www.korpa.ba/product_uploads/PkkNMiYmU72V55PW8EbVCEQZdN7TMooT.jpg',
                'Телешко 🍖'
            ),
            (
                'Телешко со црн лук',
                '',
                990.0,
                100,
                'https://www.korpa.ba/product_uploads/AHHAP1FBLwZWb7baE8vIgBKRwVvJxcs5.jpg',
                'Телешко 🍖'
            ),
            (
                'Телешко со крцкав модар патлиџан',
                '*луто',
                990.0,
                100,
                'https://www.korpa.ba/product_uploads/1rMdC71EDEYYsuhLPZEM14JIPaKiNrlb.jpg',
                'Телешко 🍖'
            ),
            (
                'Таи бифтек со чили и босилек',
                '*луто',
                990.0,
                100,
                'https://www.korpa.ba/product_uploads/mbdXIBZcZJWnS8fcwrprwa7qN0O34amz.jpg',
                'Телешко 🍖'
            ),
            (
                'Зу бифтек',
                '',
                990.0,
                100,
                'https://www.korpa.ba/product_uploads/n3xGErkkF0HQCHVjaUaeGDPHQHlgKceo.jpg',
                'Телешко 🍖'
            ),
            (
                'Тобанјаки бифтек',
                '',
                990.0,
                100,
                'https://www.korpa.ba/product_uploads/354yJFkCVrvZJXTf7NDlt7Ro7eBua189.jpg',
                'Телешко 🍖'
            ),
            (
                'Крцкав лаврак со ѓумбир',
                '*луто',
                970.0,
                100,
                'https://www.korpa.ba/product_uploads/bty7TgesMkLQpth58gUQKKrZHOVjCwSC.jpg',
                'Морска храна 🐟🦑🦪'
            ),
            (
                'Лосос на скара со теријаки',
                '',
                1100.0,
                100,
                'https://www.korpa.ba/product_uploads/KQRkRzCItsoqOY2QMsGolOqIIukozWZn.jpg',
                'Морска храна 🐟🦑🦪'
            ),
            (
                'Ракчиња со индиски ореви',
                '*луто',
                970.0,
                100,
                'https://www.korpa.ba/product_uploads/e1nyKYskxP4oevLASBRu2rBNHPzWDdH6.jpg',
                'Морска храна 🐟🦑🦪'
            ),
            (
                'Сушико Лаврак на пареа',
                '*потребно време за подготовка 25 минути',
                1000.0,
                100,
                'https://www.korpa.ba/product_uploads/3dh3jHvBP1DYUc1N0OdkSQtHsSwIKjib.jpg',
                'Морска храна 🐟🦑🦪'
            ),
            (
                'Лосос на пареа со кари',
                'Сервирано со ориз  *луто',
                1100.0,
                100,
                'https://www.korpa.ba/product_uploads/Jdhc5ITWU7K0vRSIbSrtQqbLPNQpEmxk.jpg',
                'Морска храна 🐟🦑🦪'
            ),
            (
                'Крцкава патка (половина)',
                '',
                2030.0,
                100,
                'https://www.korpa.ba/product_uploads/QWRWSfzO6ZczHsgBjHauquxHySgmtVA4.jpg',
                'Патка 🦃'
            ),
            (
                'Крцкава патка (четвртина)',
                '',
                1070.0,
                100,
                'https://www.korpa.ba/product_uploads/d2FXYXVjrO6tvnXrmB63erQK4yl5Jgx8.jpg',
                'Патка 🦃'
            ),
            (
                'Поке со лосос',
                '',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/C8wSAlHQFIThjXuNtHMMzVMKp3nCo4eI.jpg',
                'Поке 🍛'
            ),
            (
                'Поке со лосос и туна',
                '',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/3FxcbT0rRiQbAgYuLHgpmhbmlIoM4Q6j.jpg',
                'Поке 🍛'
            ),
            (
                'Веге Поке',
                '',
                660.0,
                100,
                'https://www.korpa.ba/product_uploads/Ywog9OO2EY9l96lET7uBZGA11CREFaKX.jpg',
                'Поке 🍛'
            ),
            (
                'Нудлс',
                '',
                360.0,
                100,
                'https://www.korpa.ba/product_uploads/8tzFnRqKQkW3CttsrWtXSete1EwTEQTQ.jpg',
                'Нудли 🍜'
            ),
            (
                'Нудлс со зеленчук',
                '',
                500.0,
                100,
                'https://www.korpa.ba/product_uploads/lBOXrx3kCuGmu0TgGcj9z7OQN45cqcge.jpg',
                'Нудли 🍜'
            ),
            (
                'Нудлс со пилешко',
                '',
                610.0,
                100,
                'https://www.korpa.ba/product_uploads/sMyHuecqmuoD2MWJSvvWnznnXxR2mJYA.jpg',
                'Нудли 🍜'
            ),
            (
                'Нудлс со телешко',
                '',
                660.0,
                100,
                'https://www.korpa.ba/product_uploads/t6mle80ji83aZLPqRByvdIhQCsPLgpXJ.jpg',
                'Нудли 🍜'
            ),
            (
                'Нудлс со ракчиња',
                '',
                680.0,
                100,
                'https://www.korpa.ba/product_uploads/PyxNVdekUY78LVhedhvqOnpWaz1MePHU.jpg',
                'Нудли 🍜'
            ),
            (
                'Сингапур нудлс со кари',
                '',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/GpsawtUi7zHuNf1rAb7YSivUN1tKGZJB.jpg',
                'Нудли 🍜'
            ),
            (
                'Пад Таи нудлс Пилешко',
                '',
                720.0,
                100,
                'https://www.korpa.ba/product_uploads/niSzNmOeVjyHvEFCjtFnVWtKmVnQmweO.jpg',
                'Нудли 🍜'
            ),
            (
                'Пад Таи нудлс Телешко',
                '',
                770.0,
                100,
                'https://www.korpa.ba/product_uploads/H6bRzMV0e2nWpcUDC2jS2tatnODVYfkJ.jpg',
                'Нудли 🍜'
            ),
            (
                'Пад Таи нудлс Ракчиња',
                '',
                800.0,
                100,
                'https://www.korpa.ba/product_uploads/lEzx9PYsY9mxnYXke8VYMgF8vN1LpQee.jpg',
                'Нудли 🍜'
            ),
            (
                'Кореан удон нудли со пилешко',
                '',
                610.0,
                100,
                'https://www.korpa.ba/product_uploads/h4q55ds7pa3ExoxnYa09s8SLPPjgkBEv.jpg',
                'Нудли 🍜'
            ),
            (
                'Кореан удон нудли со телешко',
                '',
                670.0,
                100,
                'https://www.korpa.ba/product_uploads/8SVU0pvOAa6hunB9WBS48Qtp9HPy0QvX.jpg',
                'Нудли 🍜'
            ),
            (
                'Кореан удон нудли со свинско',
                '',
                660.0,
                100,
                'https://www.korpa.ba/product_uploads/PaYbdX0PR6MIPuP3AlmSpj0dyb6bdwsY.jpg',
                'Нудли 🍜'
            ),
            (
                'Ориз на пареа 150 гр.',
                '',
                150.0,
                100,
                'https://www.korpa.ba/product_uploads/Fqs6rhUX9wleGs7ohE1hCJfiOZKiQLXj.jpg',
                'Ориз 🍚'
            ),
            (
                'Ориз на пареа 300 гр.',
                '',
                280.0,
                100,
                'https://www.korpa.ba/product_uploads/UDDBYQ2FokCtIoZHjzFlYM2IrIBuacR6.jpg',
                'Ориз 🍚'
            ),
            (
                'Ориз со зеленчук',
                '',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/yaNWGnNPIvgsDtCJSEtXdQsszBVKbLnS.jpg',
                'Ориз 🍚'
            ),
            (
                'Ориз со пржено јајце',
                '',
                450.0,
                100,
                'https://www.korpa.ba/product_uploads/4uAqZcdotj1lXsXYR2yHeTS60xIgfWnp.jpg',
                'Ориз 🍚'
            ),
            (
                'Ориз со пилешко',
                '',
                500.0,
                100,
                'https://www.korpa.ba/product_uploads/8oZVc66qjDYedWmxIZABHngJI9AxlFCA.jpg',
                'Ориз 🍚'
            ),
            (
                'Ориз со телешко',
                '',
                530.0,
                100,
                'https://www.korpa.ba/product_uploads/1izXMGB4mJvlkD7XPdbBn58lTgexzisk.jpg',
                'Ориз 🍚'
            ),
            (
                'Таи ориз со ананас',
                '',
                530.0,
                100,
                'https://www.korpa.ba/product_uploads/5YFOkJgNpvnBA6nJsEIFOnCWlytbNBkc.jpg',
                'Ориз 🍚'
            ),
            (
                'Ориз со ракчиња',
                '',
                620.0,
                100,
                'https://www.korpa.ba/product_uploads/wxRcc9nxfxCajLIaIxx1HIFXfqzQRAfB.jpg',
                'Ориз 🍚'
            ),
            (
                'Том Јам ориз',
                '',
                660.0,
                100,
                'https://www.korpa.ba/product_uploads/THQd1i3DJhzEKTZ8Vn7E0II7UHAB7eTO.jpg',
                'Ориз 🍚'
            ),
            (
                'Veggie Set Menu',
                '16 парчиња - Veggie Roll 8, Avocado Roll 3, Takuan Roll 3, Tamago Nigiri 2, Goma Wakame',
                1200.0,
                100,
                'https://www.korpa.ba/product_uploads/s01ZyXNDbHi1EgWd6gw3RgAZzx2nYwlB.jpg',
                'Суши сетови🥢'
            ),
            (
                'ABC Sushi Moriawase',
                '15 парчиња - Kappa Roll 6, Kani Roll 6, California Roll 3',
                1130.0,
                100,
                'https://www.korpa.ba/product_uploads/DTb4Mt5k8a61DmQEHJERDnMIHRxXdQ1W.jpg',
                'Суши сетови🥢'
            ),
            (
                'California Dream',
                '16 парчиња - California Roll 4, Spicy California Roll 4, Sesame California Roll 4, Black Sesame California Roll 4',
                1360.0,
                100,
                'https://www.korpa.ba/product_uploads/kW6dXMIGWBeCe50MM2PCXRjzk3Zab8Ta.jpg',
                'Суши сетови🥢'
            ),
            (
                'Sushi Queen',
                '11 парчиња - Sake Roll 3, Kani Roll 3, Maguro Nigiri 1, Ebi Nigiri 1, Sake Nigiri 1, Suzuki Nigiri 1, Kani Nigiri 1',
                1400.0,
                100,
                'https://www.korpa.ba/product_uploads/6dqs0ERsmwcxyGgR3ytLw6J0gn2nrAWg.jpg',
                'Суши сетови🥢'
            ),
            (
                'Salmon Dream',
                '16 парчиња - Philedelphia Roll 4, Spicy Philedelphia Roll 4, Tobiko Philedelphia 4, Black Sesame Philedelphia 4',
                1400.0,
                100,
                'https://www.korpa.ba/product_uploads/EHFxBuxoYsHo2JRa3KHIEqfyYgHWZF64.jpg',
                'Суши сетови🥢'
            ),
            (
                'Sushi King',
                '15 парчиња - Sake Roll 3, Kani Roll 3, California Roll 3, Maguro 1, Suzuki 1, Sake 1, Ebi 1, Saba 1, Kani 1',
                1740.0,
                100,
                'https://www.korpa.ba/product_uploads/FwOtnDJVhY9xDPaMkfb4VnY4Vv5wb7jk.jpg',
                'Суши сетови🥢'
            ),
            (
                'Hot Sushi Plate',
                '19 парчиња - Philly Roll 8, Baby Kalamar Roll 5, Sake Ten Roll 6',
                1940.0,
                100,
                'https://www.korpa.ba/product_uploads/YxWC8qwHM1KuVHeSOcFpvzin60XZpgwM.jpg',
                'Суши сетови🥢'
            ),
            (
                'Sushi Prince 1',
                '25 парчиња - California Roll 3, Spicy California Roll 3, Sakel Roll 3, Kappa Roll 3, Crunchy Roll 5, Sake Nigiri 2, Kani Nigiri 2, Ebi Nigiri 2, SushiCo Wakame Salad',
                2700.0,
                100,
                'https://www.korpa.ba/product_uploads/STBI4zj2DdvAM9gBrf8BzIJfA30YTnvl.jpg',
                'Суши сетови🥢'
            ),
            (
                'Tempura Shrimp Plate',
                '21 парче - Samurai Roll 8, Ebi Ten Roll 5, Salmon Aburi Roll 8  *луто',
                2070.0,
                100,
                'https://www.korpa.ba/product_uploads/mTWfhwniEnuw2UhahcoxeHXrQ4cQsXxP.jpg',
                'Суши сетови🥢'
            ),
            (
                'Best Off',
                '22 парчиња - California Roll 8, Philly Roll 8, Sake Roll 6',
                1830.0,
                100,
                'https://www.korpa.ba/product_uploads/gDkV9Rzx4NCygKmI7r5nE8UU7Ysp2BJQ.jpg',
                'Суши сетови🥢'
            ),
            (
                'Sushi 60 pcs',
                'Kani Roll 6, Sake Roll 6, Maguro Roll 6, Kappa Roll 6, California Roll 6, Canadian Roll 6, Rainbow Roll 6, Crunchy Roll 4, Tokyo Sandwich 4, Spicy Maguro Avocado Roll 6, Tamago Nigiri 2, Sake Nigiri 2',
                4190.0,
                100,
                'https://www.korpa.ba/product_uploads/0ec9XlctDOoHKYa4RKKuQycAkqwHEVPQ.jpg',
                'Големи Суши сетови 🍱'
            ),
            (
                'Sushi 39 pcs',
                'California Roll 6, Sesame Maki Roll 6, Canadian Roll 6, Kappa Roll 6, Sakr Roll 6, Tamago Nigiri 3, Suzuki Nigiri 3, Kani Nigiri 3',
                2990.0,
                100,
                'https://www.korpa.ba/product_uploads/PpAIm7b0ffcJzrcaluL30pvKdRtIPPWh.jpg',
                'Големи Суши сетови 🍱'
            ),
            (
                'Avocado Takuan Roll',
                '6 парчиња - Јапонска репка и авокадо',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/cyqPvhAsuZtGld6Oai19q49vJVv8fMPT.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Maguro Roll',
                '6 парчиња - Туна',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/9Nr0Mj6IKy3L0hAqdqQrceHc5fyL7JyW.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Kappa Roll',
                '6 парчиња - Краставица',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/xOrYWWA4ypUX8EtoIW6YY3bRGaE8bTaS.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Ebi Roll',
                '6 парчиња - Ракчиња',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/RVnWAaaQypByTgTpgILIvEggPjPRVSlo.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Kani Roll',
                '6 парчиња - Сурими',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/0jXURlaL52ouP4M3fKDDs4jr1zeIduEX.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Sake Roll',
                '6 парчиња - Лосос',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/TAMwVejTigIpcl2U0WOc3vU1bmctteqF.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Ebi Ten Roll',
                '5 парчиња - Темпура ракчиња, авокадо, мајонез, икра од летечка риба / надворешно сусам',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/SvGAtulOppR36odVdAZ1PwobHIuM3pec.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Samurai Roll',
                '8 парчиња - Темпура ракчиња, авокадо, марула, јапонска репка / надворешно сусам и икра од летечка риба',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/iJuq42wDEMDUcvUa5r54cjdC52r4WFbQ.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Baby Calamari Roll',
                '5 парчиња - Темпура бејби лигњи, авокадо, краставица, шрирача сос / надворешно црн сусам *луто',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/S0Qt5CyAsJ1wN9u1MP4BNovArek1kVcK.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Philly Roll',
                '8 парчиња - Сурими, авокадо, крем сирење / надворешно пржено печиво и теријаки сос',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/JfsfDEt6ZA8CyovO2Ml1FyGT0ioZ1SLu.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'SushiCo Roll',
                '5 парчиња - Темпура ракчиња, авокадо, мајонез, краставица, сусам / надворешно крцкав лосос и теријаки сос',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/1USHTRSdS0G33Ge7krBNPHKL4iJ206NF.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Tokyo Drift Roll',
                '8 парчиња - Темпура лосос, авокадо, краставица /  надворешно икра од летечка риба и крцкав компир',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/LD0BUzTHGItOBa8oSbjLVoMKt3aN7BZP.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Ebi Tempura Roll with Truffle',
                '8 парчиња - Темпура ракчиња, авокадо, краставица / надворешно мајонез од тартуфи, крцкав компир, теријаки сос бел и црн сусам',
                790.0,
                100,
                'https://www.korpa.ba/product_uploads/BkgQVDr5WUizehGSXVWm1ycI0Vdczvf7.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Salmon Aburi Roll',
                '8 парчиња - Темпура ракчиња, аспарагус / надворешно лосос, васаби сос, капари *луто',
                790.0,
                100,
                'https://www.korpa.ba/product_uploads/mfAYGzZkgaxSEIx0mhJFI65QDEDTEaea.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Sesame Maki Roll',
                '8 парчиња - Ракчиња, авoкадо, краставица, мајонез, марула / надворешно сусам',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/p7aEuvWaZfGGs35XFp7GBOungi7hCLMm.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Spicy Maguro Avocado Roll',
                '6 парчиња - Зачинета туна / надворешно авокадо  *луто',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/wpn6TCUgou7aTh5Xf1utCOeCGcDpwWfz.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'California Roll',
                '8 парчиња - Сурими, авокадо, краставица, мајонез, марула/ надворешно икра од летечка риба',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/PNJlCVpNu0iyGRIyEPVAJZ6JPtTG3Cq0.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Spicy California Roll',
                '8 парчиња - Сурими, авокадо, краставица, мајонез, марула / надворешно икра од летечка риба  *луто',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/FWs9uuzLGX2niMJQN63ouOaaEte9xeRW.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Philadelphia Roll',
                '8 парчиња - Марула, краставица, лосос, крем сирење / надворешно сусам',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/D8xMKcrLFNVTE9WYr4A2uUSo4V9IzzV7.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Spicy Philadelphia Roll',
                '8 парчиња - Марула, краставица, лосос, крем сирење / надворешно сусам  *луто',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/SEJq84pLngrX6CcxBp591lO7smflMZ0N.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Ebi California Roll',
                '8 парчиња - Ракчиња, авокадо, краставица, мајонез, марула / надворешно икра од летечка риба',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/HpB7kfDUGQ0gZmC5XFrD8pYo7AQ9sl9T.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'San Diego Roll',
                '6 парчиња - Лосос, авокадо, краставица/ надворешно икра од летечка риба',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/KkiNiPtJwqgKx41Owj7ugXqmE9lkvGLJ.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Mango Roll',
                '8 парчиња - Лосос, авокадо крем сирење / надворешно икри од летечка риба и манго',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/GlvbF9glWpxBohjnAh34zDYJZ1dpLoSx.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Crunchy Roll',
                '5 парчиња - Сурими салата, омлет, краставица, мајонез, корнфлекс / надворешно икра од летечка риба',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/BuCAzNg2IJpJT4B2Zig4Yh6NJiEUBv2p.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Omega Saba Roll',
                '6 парчиња - Јапонска репка, ѓумбир, краставица / надворешно потпечена скуша и сенф *луто',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/bQcCjJastwfxQThxNuKq8y09ljjEuQTJ.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Two Way Salmon Roll',
                '5 парчиња - Лосос, краставица, крем сирење / надворешно лосос, понзу сос и теријаки сос, ширача сос *луто',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/ROtIRaxyv1lvlXCJJ14VrtMNFwsFTlrf.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Veggie Roll',
                '8 парчиња - Авокадо, морков, краставица, аспарагус, марула / надворешно сусам',
                710.0,
                100,
                'https://www.korpa.ba/product_uploads/gcJqC5fu8S51K8R4giVVGI8rRxKze9qO.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Smoked Salmon Roll',
                '8 парчиња - Димен лосос, крем сирење, краставица / надворешно димен лосос и капари',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/ZkgsQoeWOMUhfYToaSKwbdTC8gnYFI98.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Geisha Roll',
                '8 парчиња - Лосос, авокадо / надворешно краставица, икра од лосос и васаби сос  *луто',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/55uXwKQ3IjWD5Uhh0Kg135Lli61Ac6ry.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Rainbow Roll',
                '6 парчиња - Сурими, краставица / надворешно микс од лосос, лаврак, туна и авокадо',
                750.0,
                100,
                'https://www.korpa.ba/product_uploads/17kX7sEboJoMRUYQDHIERuC8FKKu0MHn.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Unagi Roll',
                '6 парчиња - Јагула',
                620.0,
                100,
                'https://www.korpa.ba/product_uploads/C4m3l6Gs2T8bwYC9yuphCxW5iSxG34hh.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Jungle Roll',
                '8 парчиња - Јагула, авокадо, аспарагус, крем сирење / надворешно морски алги',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/RSYc9g4j8V6R0jfmzJQI5iGClc4DPtxi.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Tiger Roll',
                '5 парчиња - Јагула, авокадо, краставица, крем сирење, лут сос / надворешно ракчиња *луто',
                790.0,
                100,
                'https://www.korpa.ba/product_uploads/2aPOlQIXNhO7X94rkPJ1DkpR65OFB5B5.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Yuzu Special Roll',
                '8 парчиња - Темпура лаврак, краставица, авокадо / надворешно лаврак, икра од летечка риба, јузу сос',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/jyoMZbMokIjzkLhzQHm2jDZbbS1YlGlc.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'İki̇gai̇ Roll',
                '8 парчиња - Темпура лосос, краставица, авокадо, лут сос / надворешно чедар сирење, лут сос, икра од лосос *луто',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/5mWinfrCtNlgbTF4AZyXHiII3PyRR8Ac.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Zen Dragon Roll',
                '8 парчиња - Темпура ракчиња, краставица, авокадо / надворешно јагула, авокадо, сусам и теријаки сос',
                790.0,
                100,
                'https://www.korpa.ba/product_uploads/Va62RMAC0KdXl4SttkAB9hSyQvdzbreO.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Suzuki̇ss Roll',
                '8 парчиња - Авокадо, краставица / надворешно тартар од лаврак, јузу мајонез со тартуфи и крцкави Нори алги',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/6KzZZNlyNCgWzxvciVKP7ZWCyTe9HVzT.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Super Salmon Roll',
                '8 парчиња - Лосос, краставица, крем сирење / надворешно Тонкатсу, јузу мајонез со тартуфи',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/emsSchuaMLtWT2Nqdfxduf57NN6wmT8o.jpg',
                'Суши Ролс 🍥⭐'
            ),
            (
                'Nigiri Tamago',
                'Омлет',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/wgjztjc4eL1A29zlXpFfc6LMhsWXtd8f.jpg',
                'Нигири - 2 парчиња 🍣'
            ),
            (
                'Nigiri Saba',
                'Скуша',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/fLQwc0Xml0A8LdvXrn6L1nG2aDS26aut.jpg',
                'Нигири - 2 парчиња 🍣'
            ),
            (
                'Nigiri Maguro',
                'Туна',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/DMoXmfyIH5rkafRkVqPuQE3vMcVxG66M.jpg',
                'Нигири - 2 парчиња 🍣'
            ),
            (
                'Nigiri Suzuki',
                'Лаврак',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/kZfbvW8ApGVFNjELRPYEXWo1tcq4yz1y.jpg',
                'Нигири - 2 парчиња 🍣'
            ),
            (
                'Nigiri Sake',
                'Лосос',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/nWrmrdVR51aTO7gJJII88IdbH0dicHkP.jpg',
                'Нигири - 2 парчиња 🍣'
            ),
            (
                'Nigiri Sake Avocado',
                'Лосос и Авокадо',
                490.0,
                100,
                'https://www.korpa.ba/product_uploads/vBm3mhZquOMYMyCdHK7SJsWphFcwYUaq.jpg',
                'Нигири - 2 парчиња 🍣'
            ),
            (
                'Nigiri Ebi',
                'Ракчиња',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/83Ckek4n8gnw7L6OagBJ0joeY7EoVMHc.jpg',
                'Нигири - 2 парчиња 🍣'
            ),
            (
                'Nigiri Ikura',
                'Икри од лосос',
                680.0,
                100,
                'https://www.korpa.ba/product_uploads/4kx3hAssTy9Dt5nDythbzKx23Amo89ZX.jpg',
                'Нигири - 2 парчиња 🍣'
            ),
            (
                'Nigiri Unagi',
                'Јагула',
                630.0,
                100,
                'https://www.korpa.ba/product_uploads/79wjhfsEqheDAP0h35W7rh9gL00YK4QB.jpg',
                'Нигири - 2 парчиња 🍣'
            ),
            (
                'Sashimi Sake',
                'Лосос',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/BW5n7GzHq4bWo4pc6gPgJkQme6lYJJjk.jpg',
                'Сашими - 3 парчиња 🍤'
            ),
            (
                'Sashimi Suzuki',
                'Лаврак',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/VVd58ZPewDe0gVqsF4O91xke24oRqRDx.jpg',
                'Сашими - 3 парчиња 🍤'
            ),
            (
                'Sashimi Tamago',
                'Омлет',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/k9CKfND5s0Y1dpYMzoTmA49k1bqrMb1q.jpg',
                'Сашими - 3 парчиња 🍤'
            ),
            (
                'Sashimi Maguro',
                'Туна',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/LHiRQT1wQMKzQ2Qv3uUtoScj9lXkRHGw.jpg',
                'Сашими - 3 парчиња 🍤'
            ),
            (
                'Sashimi Saba',
                'Скуша',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/xZFHtUr5xhKWcIizruykxK1LCcKzXn5q.jpg',
                'Сашими - 3 парчиња 🍤'
            ),
            (
                'Sashimi Ebi',
                'Ракчиња',
                420.0,
                100,
                'https://www.korpa.ba/product_uploads/tDtxjPwptULkISeIW1hyAPygrQdefPEf.jpg',
                'Сашими - 3 парчиња 🍤'
            ),
            (
                'Sashimi Unagi',
                'Јагула',
                700.0,
                100,
                'https://www.korpa.ba/product_uploads/wZBz6mqLkACkVodnwulZDnXkuPw4SXRc.jpg',
                'Сашими - 3 парчиња 🍤'
            ),
            (
                'Sashimi Ikura',
                'Икра од лосос',
                760.0,
                100,
                'https://www.korpa.ba/product_uploads/ygzkCxhoAHCzb1d77PxlC6c2oglbXtQu.jpg',
                'Сашими - 3 парчиња 🍤'
            ),
            (
                'Бенто Мени 1',
                'Спринг ролс (1 парче) Телешко со зеленчук, Ориз со зеленчук, Салата од зачинета зелка, Безалкохолен пијалак',
                960.0,
                100,
                'https://www.korpa.ba/product_uploads/XqAXiBWZAUTTttlUoYnm1PEgVazx848r.jpg',
                'Бенто Мени 🍱'
            ),
            (
                'Бенто Мени 2',
                'Крцкав Вонтон (2 парчиња), Крцкаво пилешко со сос од ѓумбир, Нудлс со зеленчук, Салата од зачинета зелка, Безалкохолен пијалак *луто',
                960.0,
                100,
                'https://www.korpa.ba/product_uploads/5KKYVE5JkBzElmQEhIrPpeD3f8eUmWs1.jpg',
                'Бенто Мени 🍱'
            ),
            (
                'Детско мени 1',
                'Sushi Banda (6 парчиња), крцкав лаврак, нудли со зеленчук, мочи (2 парчиња)',
                900.0,
                100,
                'https://www.korpa.ba/product_uploads/7d1pX5INglIrmtTJqq3MjTYa85Rdq453.jpg',
                'Детско мени 🥡'
            ),
            (
                'Детско мени 2',
                'Крцкав Вонтон (2 парчиња), пилешки топчиња (6 парчиња), нудли со зеленчук, пржена банана (2 парчиња)',
                900.0,
                100,
                'https://www.korpa.ba/product_uploads/JrS8yTtHWbT8NaRWe0rVEco0oG9sEZAl.jpg',
                'Детско мени 🥡'
            ),
            (
                'Пржен сладолед ванила',
                '',
                330.0,
                100,
                'https://www.korpa.ba/product_uploads/VREIyaWUiFHtz7DRkXJNiiqLFp8jZXmx.jpg',
                'Десерти 🍨'
            ),
            (
                'Пржен сладолед чоколадо',
                '',
                330.0,
                100,
                'https://www.korpa.ba/product_uploads/lS22o7iwm13h20qT78eUGyDjLzVycSwk.jpg',
                'Десерти 🍨'
            ),
            (
                'Пржена банана',
                '',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/6Kxqt5bAHm2BzbinEERpWmQaGAWQwpWZ.jpg',
                'Десерти 🍨'
            ),
            (
                'Пржен ананас со цимет',
                '',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/nXVmeJ3xqU0TOkKiGJfY3tGRJqyqmqZl.jpg',
                'Десерти 🍨'
            ),
            (
                'Сладок суши ролс сладолед',
                '',
                520.0,
                100,
                'https://www.korpa.ba/product_uploads/QAGqiXLbk6dOTBGTUtWH739T5PyS8X9U.jpg',
                'Десерти 🍨'
            ),
            (
                'Сладок суши ролс овошје',
                '',
                520.0,
                100,
                'https://www.korpa.ba/product_uploads/xJjdYceQhej1mnfmtGsxbAcsO60QvRFp.jpg',
                'Десерти 🍨'
            ),
            (
                'Карамелизирани ореви',
                '',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/K54dsI5cn9nmLbrlKJikwqzrURwqiD8z.jpg',
                'Десерти 🍨'
            ),
            (
                'Мочи',
                '3 парчиња',
                400.0,
                100,
                'https://www.korpa.ba/product_uploads/ZEnwQJrZz8mwDKU2OcsPbZWx7mQlHkiK.jpg',
                'Десерти 🍨'
            ),
            (
                'Rosa негазирана 0.33l',
                '',
                100.0,
                100,
                'https://www.korpa.ba/product_uploads/Zb8Ce3KUI7IixPK5lkhXfcpdwalhFhZu.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Rosa негазирана 0.75l',
                '',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/JqwmnRgTyIP6qIuFLctny41Bc5rltiHq.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Coca Cola 0.25',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/Qwi9GduVhg0rp8Sua4DXtBGyFxj0ADEU.jpeg',
                'Пијалоци 🥤'
            ),
            (
                'Coca Cola Zero 0.25',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/Dt9FQQeElwhLLFc6tsbNTOkhro92qx3v.PNG',
                'Пијалоци 🥤'
            ),
            (
                'Fanta 0.25',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/PEmmNtRyZas8t1efWHGlCEeQnTSysFKu.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Sprite 0.25',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/6vqvjozTuA8FFTor5kcM3pEivjjgNLgP.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Schweppes Tonic 0.25',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/dvh2s1TjfPQANsWuRlKNkBqlgmcUBngw.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Schweppes Biter Lemon 0.25',
                '',
                70.0,
                100,
                'https://www.korpa.ba/product_uploads/foHaoY8Ksd35JbIiHmNgXtSq2kleL27s.jpeg',
                'Пијалоци 🥤'
            ),
            (
                'Three Cents Pink grapefriut 0.2',
                '',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/6cVmzWqQ9DGhkrpbDG05kTYNPvL82nPj.png',
                'Пијалоци 🥤'
            ),
            (
                'Three Cents Mandarin & bergamot 0.2',
                '',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/ovniDQmoFZ2AiewLqjaIaOgSfCDQWSOk.png',
                'Пијалоци 🥤'
            ),
            (
                'Three Cents Aegean tonic 0.2',
                '',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/1Mkl5AMv37EBiGwHL1XS7FVfu1qM1ykT.png',
                'Пијалоци 🥤'
            ),
            (
                'Three Cents Tonic water 0.2',
                '',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/IHPsSTF51lLNS9hioCkun8gYYIvh5INb.png',
                'Пијалоци 🥤'
            ),
            (
                'Three Cents Ginger beer 0.2',
                '',
                190.0,
                100,
                'https://www.korpa.ba/product_uploads/vtaJaEQSkH9qDwDyMZqBcF19jQLVwvqC.png',
                'Пијалоци 🥤'
            ),
            (
                'Next јаболко 0.2',
                '',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/6dfUlXus7V28Z10G4swsW2o9xd7PMq5j.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Next праска 0.2',
                '',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/bfYRzcY9ApdY21rhgr14MvTVZmnPRGWz.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Next боровница 0.2',
                '',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/1X2yguDQTnZ04DxkaeXA517i4wKEkoIX.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Next портокал 0.2',
                '',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/OnCqebuFx9d3iusmh9xktEsmz2gFDeQU.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Rosa газирана 0.33l',
                '',
                100.0,
                100,
                'https://www.korpa.ba/product_uploads/bkRJ5NzxHlSv6zqOS6NJGcaR0xEvUXj5.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Rosa газирана 0.75l',
                '',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/nx94gLMU25p1XDDib5F6sHLmEKnSacic.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Fuze Tea праска 0.25',
                '',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/BUnV0YVo962r5dpX00oZZBvIeYCbzGLq.jpg',
                'Пијалоци 🥤'
            ),
            (
                'San Benedetto Naturale 0.75l',
                '',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/lRccbbpqcw00DMAjKyKQzi46oDY1T5tg.jpg',
                'Пијалоци 🥤'
            ),
            (
                'San Benedetto Frizzante 0.75l',
                '',
                390.0,
                100,
                'https://www.korpa.ba/product_uploads/DCVpKt5XQJMRTIqDIfzET1UVRPlsZMQx.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Red Bull',
                '',
                330.0,
                100,
                'https://www.korpa.ba/product_uploads/JexCUJmYePWnMWMPojf5Qo5cbgyp7MCy.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Корона 0.35',
                '',
                370.0,
                100,
                'https://www.korpa.ba/product_uploads/biRy3oX9R04rzW71T8u7oDKU3zRapgHZ.jpg',
                'Саке и пиво 🍺'
            ),
            (
                'Асахи Јапонско пиво 0.33',
                '',
                370.0,
                100,
                'https://www.korpa.ba/product_uploads/C7cCny32eemmCvDnrB57PqqsrTVDmszo.jpg',
                'Саке и пиво 🍺'
            ),
            (
                'Саке Шочику 0.2',
                '',
                720.0,
                100,
                'https://www.korpa.ba/product_uploads/ONX71dwemhKKyfqYxHyqZpyaBI6LhpQW.jpg',
                'Саке и пиво 🍺'
            ),
            (
                'Heineken 0.33',
                '',
                210.0,
                100,
                'https://www.korpa.ba/product_uploads/Nt8qXPQwynvueTA98rpR69MHr9wq5N9f.png',
                'Саке и пиво 🍺'
            )
        ]
    ),
    (
        'Teteks - Karposh',
        'Доставуваме до Вашата врата',
        'https://korpa.ba/restaurant_uploads/jKWBG3Iy6dDdcFjdoFZ0zDWH9UdLUSEO.jpg',
        'Grill / Balkan',
        25,
        [
            (
                'Хамбургер',
                '',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/DboQNnAKjmqLGfubVfCd5U4LXCVJw9lx.jpg',
                'Бургери 🍔'
            ),
            (
                'Чизбургер',
                '',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/Pp6HP1pIQbCJc6prcTeW5L3RZ8wtxrqS.jpg',
                'Бургери 🍔'
            ),
            (
                'Бургер со шарска',
                '',
                300.0,
                100,
                'https://www.korpa.ba/product_uploads/B72Nm7oYAP4UA53MAwpjs5bbbbGflmPj.jpg',
                'Бургери 🍔'
            ),
            (
                'Бургер со батак',
                '',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/LvSA7c9qDv6iRldGtELDOD8aLsczMYAP.jpg',
                'Бургери 🍔'
            ),
            (
                'Чикенбургер',
                '',
                260.0,
                100,
                'https://www.korpa.ba/product_uploads/fy85aKbbbhDLwoSkJEJFPWU0KT2eHsyn.jpg',
                'Бургери 🍔'
            ),
            (
                'Кебап',
                '',
                23.0,
                100,
                'https://www.korpa.ba/product_uploads/u1vz3jtgi40zKI0tcCNo8uDLo2zeHfUh.jpg',
                'Кебапи 🧆'
            ),
            (
                '5-ка Сендвич',
                '',
                170.0,
                100,
                'https://www.korpa.ba/product_uploads/P3wMEUivCUiZoGThcFgD7ZwKnWeZryCm.jpg',
                'Кебапи 🧆'
            ),
            (
                '5-ка Сендвич + Помфрит',
                '',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/bW59ZkWydGnOwo0et40Jf1LnSlJvMHNB.jpg',
                'Кебапи 🧆'
            ),
            (
                '10-ка Сендвич',
                '',
                290.0,
                100,
                'https://www.korpa.ba/product_uploads/ugSgE0AJwz2mn5OmzkwPTRbuA7h8v88Y.jpg',
                'Кебапи 🧆'
            ),
            (
                '10-ка Сендвич + Помфрит',
                '',
                350.0,
                100,
                'https://www.korpa.ba/product_uploads/54BtnMCavsIuLMOlKBLq3VLA2sy0WE8e.jpg',
                'Кебапи 🧆'
            ),
            (
                '10 Кебапи',
                '',
                230.0,
                100,
                'https://www.korpa.ba/product_uploads/XHNeaxIfub3ZTHU5cihyfoZm1fPolxh0.jpg',
                'Кебапи 🧆'
            ),
            (
                'Сендвич со плескавица',
                '',
                200.0,
                100,
                'https://www.korpa.ba/product_uploads/zSU492iPTkIAaqBBnuPLbyYD6dcEogKt.jpg',
                'Сендвичи 🍔'
            ),
            (
                'Вегетаријански',
                '',
                180.0,
                100,
                'https://www.korpa.ba/product_uploads/5VzNwO3FTTB6r4PKQWFjKl8S4xAzWl0t.jpg',
                'Сендвичи 🍔'
            ),
            (
                'Комбиниран',
                '',
                200.0,
                100,
                'https://www.korpa.ba/product_uploads/Xep5JJXGL63cBjiFIxg8OpwAcvogbFNZ.jpg',
                'Сендвичи 🍔'
            ),
            (
                'Скопски сендвич со плескавица и кајмак',
                '',
                220.0,
                100,
                'https://www.korpa.ba/product_uploads/HZi2em0dCaVKOtGTHMFLxgombG2A9qOe.jpg',
                'Сендвичи 🍔'
            ),
            (
                'Плескавица',
                '',
                150.0,
                100,
                'https://www.korpa.ba/product_uploads/YDfxwzyYHgWISYtRTeh3Ns0nAS1GU5FW.jpg',
                'На парче 🍗'
            ),
            (
                'Шарска плескавица',
                '',
                250.0,
                100,
                'https://www.korpa.ba/product_uploads/gJ66YxLU4c63CNf4Vyr4M7IoXpTKoNYN.jpg',
                'На парче 🍗'
            ),
            (
                'Пилешки стек',
                '',
                200.0,
                100,
                'https://www.korpa.ba/product_uploads/SXOGPqxQ5m1KwH0jlPeVvgTquBH7EOzq.jpg',
                'На парче 🍗'
            ),
            (
                'Пилешки батак',
                '',
                200.0,
                100,
                'https://www.korpa.ba/product_uploads/lJxKyuOL5KwWO2gQxaxXmuLZehMOoV8Y.jpg',
                'На парче 🍗'
            ),
            (
                'Тост',
                '',
                150.0,
                100,
                'https://www.korpa.ba/product_uploads/lXhAAuHCzEY7cFJevclND2mZreyJcWGe.jpg',
                'На парче 🍗'
            ),
            (
                'Помфрит Порција',
                '',
                160.0,
                100,
                'https://www.korpa.ba/product_uploads/8QPrqh4X4D19WOSU1sRm9iUqrxEJEtF5.jpg',
                'Додатоци 🧅'
            ),
            (
                'Coca Cola 0.33',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/MIfRsuYT7Rp5fVUoYuWMSU3CKGkPoa01.png',
                'Пијалоци 🥤'
            ),
            (
                'Coca Cola Zero 0.33',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/hOmo4m5kBZFBLheaVbBgVE3rnjeszKqf.PNG',
                'Пијалоци 🥤'
            ),
            (
                'Coca Cola Lemon 0.33',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/WM6vlcri1VhovI1AYMWeN3iUvn4PKFfU.png',
                'Пијалоци 🥤'
            ),
            (
                'Фанта 0.33',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/GzRlremeLFogKOiAC9FAYucqFRHaWlOZ.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Швепс 0.33',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/2ymThEp4GsjdgC5iCg8m20ew7dgTfMUD.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Спрајт 0.33',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/n3j9VVazCsc63caF7l2biueN6S9kEoSj.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Вода Роса',
                '0.5',
                60.0,
                100,
                'https://www.korpa.ba/product_uploads/wIZmaBsejo72GeVwlP31UP9e9nLl1E8Y.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Леден чај',
                '0.5',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/17OhcYWm9Wz67UutJzDaTizjfrlM9dtl.png',
                'Пијалоци 🥤'
            ),
            (
                'Сок Next',
                '0.4',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/Hvd5gZcRKTXn6mduzswsMPiSDHHMGUab.jpg',
                'Пијалоци 🥤'
            ),
            (
                'Coca Cola 0.45',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/Qnh0mZ2TQg3KiWJQS5SSqvYtgY0kdMYv.png',
                'Пијалоци 🥤'
            ),
            (
                'Coca Cola Zero 0.45',
                '',
                80.0,
                100,
                'https://www.korpa.ba/product_uploads/TVkcFrXwnodLATWEbDFAyP4QU9lEUuoR.png',
                'Пијалоци 🥤'
            )
        ]
    )
]
# ---------------------------------------------------------------------------------


class Command(BaseCommand):
    help = "Seed users, restaurants, and products (with image_url) mirroring your Java data"

    @transaction.atomic
    def handle(self, *args, **options):
        UserModel = get_user_model()

        # --- Users ---
        admin, created = UserModel.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@email.com",
                "role": User.ROLE_ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("admin")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created admin user"))

        customer, created = UserModel.objects.get_or_create(
            username="customer",
            defaults={"email": "customer@email.com", "role": User.ROLE_CUSTOMER},
        )
        if created:
            customer.set_password("customer")
            customer.save()
            self.stdout.write(self.style.SUCCESS("Created customer user"))

        courier_user, created = UserModel.objects.get_or_create(
            username="courier",
            defaults={"email": "courier@email.com", "role": User.ROLE_COURIER},
        )
        if created:
            courier_user.set_password("courier")
            courier_user.save()
            self.stdout.write(self.style.SUCCESS("Created courier user"))

        owner, created = UserModel.objects.get_or_create(
            username="owner",
            defaults={"email": "owner@email.com", "role": User.ROLE_OWNER},
        )
        if created:
            owner.set_password("owner")
            owner.save()
            self.stdout.write(self.style.SUCCESS("Created owner user"))

        # --- Restaurants + Products ---
        created_any = False


        # --- Restaurants + Products ---
        created_any = False

        for r_name, r_desc, r_img, r_cuisine, r_eta, products in DATA:
            # Build defaults per Restaurant model
            r_defaults = {
                "description": r_desc,
                "owner": owner,
                "is_open": True,
                "open_hours": OPEN_HOURS.get(r_name, DEFAULT_OPEN_HOURS),
            }
            if hasattr(Restaurant, "image_url"):
                r_defaults["image_url"] = r_img
            if hasattr(Restaurant, "image"):
                r_defaults["image"] = r_img
            if hasattr(Restaurant, "category"):
                r_defaults["category"] = r_cuisine

            restaurant, r_created = Restaurant.objects.get_or_create(
                name=r_name,
                defaults=r_defaults,
            )
            if r_created:
                created_any = True
                self.stdout.write(self.style.SUCCESS(f"Created restaurant: {r_name}"))

            # Seed products for this restaurant
            for p_name, p_desc, p_price, p_qty, p_img, p_cat in products:
                p_defaults = {
                    "description": p_desc,
                    "price": Decimal(str(p_price)),
                    "quantity": p_qty,
                    "is_available": True,
                }
                if hasattr(Product, "category"):
                    p_defaults["category"] = p_cat
                if hasattr(Product, "image_url"):
                    p_defaults["image_url"] = p_img
                if hasattr(Product, "image"):
                    p_defaults["image"] = p_img

                product, p_created = Product.objects.get_or_create(
                    restaurant=restaurant,
                    name=p_name,
                    defaults=p_defaults,
                )
                if p_created:
                    created_any = True
                    self.stdout.write(self.style.SUCCESS(f"  Added product: {p_name}"))

        if not created_any:
            self.stdout.write(self.style.WARNING("No new data created; seed data already present."))
