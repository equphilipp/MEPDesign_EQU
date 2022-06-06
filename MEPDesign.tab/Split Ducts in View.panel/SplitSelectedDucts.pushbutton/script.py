# -*- coding: utf-8 -*-
""" Split SELECTED Ducts by distance."""

__title__ = 'Split Selected Ducts'
__author__ = 'André Rodrigues da Silva feat. Philipp'

from rpw import revit, db
from rpw import ui
from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, TextBox,Separator, Button, CheckBox)

from Autodesk.Revit.DB import Transaction

from Autodesk.Revit.DB.Mechanical.MechanicalUtils import BreakCurve 

from rpw.db.xyz import XYZ

try:
	ducts = ui.Selection()

	components = [Label('Schusslänge (in Meter):'),
				   TextBox('distance', Text="1.5"),
				   Label('Längenparameter (nur falls nötig, trennen durch ","):'),
				   TextBox('parameters', Text=""),
				   Separator(),
				   Button('Ausführen')]
	form = FlexForm('Split selected Ducts', components)
	form.show()

	# Calculate foot to meters (1m=3.28084)
	L = float(form.values['distance'])*3.28084
	P = form.values['parameters']
	P = P.split(",")

	# Ducts longer than selected length
	ductsSelected = []
	for i in range(0,len(ducts)):
		if(ducts[i].Location.Curve.Length > L):
			ductsSelected.append(ducts[i])


	points = []
	pointsAUX = []		
	for i in range(0,len(ductsSelected)):
		if((ductsSelected[i].Location.Curve.Length/L)>int(ductsSelected[i].Location.Curve.Length/L)):
			t = int(ductsSelected[i].Location.Curve.Length/L) + 1
		else:
			t = int(ductsSelected[i].Location.Curve.Length/L)
		d = L *ductsSelected[i].Location.Curve.Direction
		for n in range(0,t):
			if(n ==0):
				continue
			else:
				pointsAUX.append(ductsSelected[i].Location.Curve.GetEndPoint(0) + n*d)
		points.append(pointsAUX)
		pointsAUX = []


	# Typical Transaction in Revit Python Shell / pyRevit
	doc = __revit__.ActiveUIDocument.Document
	transaction = Transaction(doc, 'Delete Object')
	transaction.Start()
	try:
		for t in range(0,len(ductsSelected),1):
			for i in range(0,len(points[t]),1):	
				dbPoint = points[t][i]
				duct = ductsSelected[t]
				newDuctId = BreakCurve(doc, duct.Id, dbPoint)
				newDuct = doc.GetElement(newDuctId)	
				
				if(P[0]!=''):
					for z in range(0,len(P)):
						newDuct.LookupParameter(P[z]).Set(str(duct.LookupParameter(P[z]).AsString()))
						
				newDuctConnectors = newDuct.ConnectorManager.Connectors
				connA = None
				connB = None
				for c in duct.ConnectorManager.Connectors:
					pc = c.Origin
					nearest = [x for x in newDuctConnectors if pc.DistanceTo(x.Origin) < 0.01]
					if nearest:
						connA = c
						connB = nearest[0]
				takeoff = doc.Create.NewUnionFitting(connA, connB)	
				
				if(P[0]!=''):
					for z in range(0,len(P)):
						takeoff.LookupParameter(P[z]).Set(str(duct.LookupParameter(P[z]).AsString()))
						
	except:
		transaction.RollBack()
	else:
		transaction.Commit()

except:
	pass