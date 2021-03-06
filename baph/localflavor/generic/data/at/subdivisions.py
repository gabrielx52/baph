# encoding: utf8
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _


SUBDIVISIONS = ('STATES', 'DISTRICTS')

STATES = (
  ('BL', _('Burgenland')),
  ('KA', _('Carinthia')),
  ('NO', _('Lower Austria')),
  ('OO', _('Upper Austria')),
  ('SA', _('Salzburg')),
  ('ST', _('Styria')),
  ('TI', _('Tyrol')),
  ('VO', _('Vorarlberg')),
  ('WI', _('Vienna')),
)

DISTRICTS = (
  (1, u'Eisenstadt ', u'BL'),
  (2, u'Eisenstadt-Umgebung', u'BL'),
  (3, u'Güssing', u'BL'),
  (4, u'Jennersdorf', u'BL'),
  (5, u'Mattersburg', u'BL'),
  (6, u'Neusiedl am See', u'BL'),
  (7, u'Oberpullendorf', u'BL'),
  (8, u'Oberwart', u'BL'),
  (9, u'Rust ', u'BL'),
  (10, u'Feldkirchen', u'KA'),
  (11, u'Hermagor', u'KA'),
  (12, u'Klagenfurt ', u'KA'),
  (13, u'Klagenfurt Land', u'KA'),
  (14, u'Sankt Veit an der Glan', u'KA'),
  (15, u'Spittal an der Drau', u'KA'),
  (16, u'Villach ', u'KA'),
  (17, u'Villach Land', u'KA'),
  (18, u'Völkermarkt', u'KA'),
  (19, u'Wolfsberg', u'KA'),
  (20, u'Amstetten', u'NO'),
  (21, u'Baden', u'NO'),
  (22, u'Bruck an der Leitha', u'NO'),
  (23, u'Gmünd', u'NO'),
  (24, u'Gänserndorf', u'NO'),
  (25, u'Hollabrunn', u'NO'),
  (26, u'Horn', u'NO'),
  (27, u'Korneuburg', u'NO'),
  (28, u'Krems ', u'NO'),
  (29, u'Krems an der Donau ', u'NO'),
  (30, u'Lilienfeld', u'NO'),
  (31, u'Melk', u'NO'),
  (32, u'Mistelbach', u'NO'),
  (33, u'Mödling', u'NO'),
  (34, u'Neunkirchen', u'NO'),
  (35, u'Sankt Pölten ', u'NO'),
  (36, u'Sankt Pölten ', u'NO'),
  (37, u'Scheibbs', u'NO'),
  (38, u'Tulln', u'NO'),
  (39, u'Waidhofen an der Thaya', u'NO'),
  (40, u'Waidhofen an der Ybbs ', u'NO'),
  (41, u'Wien Umgebung', u'NO'),
  (42, u'Wiener Neustadt ', u'NO'),
  (43, u'Wiener Neustadt ', u'NO'),
  (44, u'Zwettl', u'NO'),
  (45, u'Braunau am Inn', u'OO'),
  (46, u'Eferding', u'OO'),
  (47, u'Freistadt', u'OO'),
  (48, u'Gmunden', u'OO'),
  (49, u'Grieskirchen', u'OO'),
  (50, u'Kirchdorf an der Krems', u'OO'),
  (51, u'Linz ', u'OO'),
  (52, u'Linz-Land', u'OO'),
  (53, u'Perg', u'OO'),
  (54, u'Ried im Innkreis', u'OO'),
  (55, u'Rohrbach', u'OO'),
  (56, u'Schärding', u'OO'),
  (57, u'Steyr ', u'OO'),
  (58, u'Steyr-Land', u'OO'),
  (59, u'Urfahr-Umgebung', u'OO'),
  (60, u'Vöcklabruck', u'OO'),
  (61, u'Wels ', u'OO'),
  (62, u'Wels-Land', u'OO'),
  (63, u'Hallein', u'SA'),
  (64, u'Salzburg ', u'SA'),
  (65, u'Salzburg-Umgebung', u'SA'),
  (66, u'Sankt Johann im Pongau', u'SA'),
  (67, u'Tamsweg', u'SA'),
  (68, u'Zell am See', u'SA'),
  (69, u'Bruck-Mürzzuschlag', u'ST'),
  (70, u'Deutschlandsberg', u'ST'),
  (71, u'Graz ', u'ST'),
  (72, u'Graz-Umgebung', u'ST'),
  (73, u'Hartberg-Fürstenfeld', u'ST'),
  (74, u'Leibnitz', u'ST'),
  (75, u'Leoben', u'ST'),
  (76, u'Liezen', u'ST'),
  (77, u'Murau', u'ST'),
  (78, u'Murtal', u'ST'),
  (79, u'Südoststeiermark', u'ST'),
  (80, u'Voitsberg', u'ST'),
  (81, u'Weiz', u'ST'),
  (82, u'Imst', u'TI'),
  (83, u'Innsbruck-Land', u'TI'),
  (84, u'Innsbruck-Stadt', u'TI'),
  (85, u'Kitzbühel', u'TI'),
  (86, u'Kufstein', u'TI'),
  (87, u'Landeck', u'TI'),
  (88, u'Lienz', u'TI'),
  (89, u'Reutte', u'TI'),
  (90, u'Schwaz', u'TI'),
  (91, u'Bludenz', u'VO'),
  (92, u'Bregenz', u'VO'),
  (93, u'Dornbirn', u'VO'),
  (94, u'Feldkirch', u'VO'),
  (95, u'Alsergrund ', u'WI'),
  (96, u'Brigittenau ', u'WI'),
  (97, u'Donaustadt ', u'WI'),
  (98, u'Döbling ', u'WI'),
  (99, u'Favoriten ', u'WI'),
  (100, u'Floridsdorf ', u'WI'),
  (101, u'Hernals ', u'WI'),
  (102, u'Hietzing ', u'WI'),
  (103, u'Innere Stadt ', u'WI'),
  (104, u'Josefstadt ', u'WI'),
  (105, u'Landstraße ', u'WI'),
  (106, u'Leopoldstadt ', u'WI'),
  (107, u'Liesing ', u'WI'),
  (108, u'Margareten ', u'WI'),
  (109, u'Mariahilf ', u'WI'),
  (110, u'Meidling ', u'WI'),
  (111, u'Neubau ', u'WI'),
  (112, u'Ottakring ', u'WI'),
  (113, u'Penzing ', u'WI'),
  (114, u'Rudolfsheim-Fünfhaus ', u'WI'),
  (115, u'Simmering ', u'WI'),
  (116, u'Wieden ', u'WI'),
  (117, u'Währing ', u'WI'),
)
