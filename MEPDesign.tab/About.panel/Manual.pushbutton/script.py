# -*- coding: utf-8 -*-
""" Open about information in default browser.  """


__title__ = 'Manual'
__author__ = 'André Rodrigues da Silva feat. Philipp'

from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, TextBox,Separator, Button, CheckBox)

components = [Label('Hinweise:'),
                Separator(),
				Label('Längenparamter sind nicht zwingend nötig.'),
				Label('Nur wenn Längenparmater nicht Standart "Länge" ist.'),
                Separator(),
				Label('Typen von Luftkanälen solen auch die Form enthalten.'),
				Label('z.B. Rechteck_(Stutzen)'),
                Separator(),
				Label('Rahmen & Verbindungen dürfen keine eigene Länge haben.'),
				Label('Die zwei Anschlüsse müssen aneinander sein.'),
                Separator(),]
form = FlexForm('Manual', components)
form.show()



# Hinweis dass Rahmen bzw. Verbindungen keine eigene Länge haben dürfen, da sonst der Kanal oder die Pipe kürzer wird, ODER man rechnet das drauf