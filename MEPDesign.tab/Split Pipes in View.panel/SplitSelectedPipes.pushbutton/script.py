# -*- coding: utf-8 -*-
""" Split SELECTED Pipes by distance."""

__title__ = 'Split Selected Pipes'
__author__ = 'André Rodrigues da Silva feat. Philipp'

from rpw import revit, db
from rpw import ui
from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, TextBox,Separator, Button, CheckBox)

from Autodesk.Revit.DB import Transaction

from Autodesk.Revit.DB.Plumbing.PlumbingUtils import BreakCurve 

from rpw.db.xyz import XYZ

try:
	pipes = ui.Selection()

	components = [Label('Schusslänge (in Meter):'),
				   TextBox('distance', Text="1.5"),
				   Label('Längenparameter (nur falls nötig, trennen durch ","):'),
				   TextBox('parameters', Text=""),
				   Separator(),
				   Button('Ausführen')]

	form = FlexForm('Split selected Pipes', components)
	form.show()

	# Calculate foot to meters (1m=3.28084)
	L = float(form.values['distance'])*3.28084
	P = form.values['parameters']
	P = P.split(",")


	# Pipes longer than selected length
	pipesSelected = []
	for i in range(0,len(pipes)):
		if(pipes[i].Location.Curve.Length > L):
			pipesSelected.append(pipes[i])


	points = []
	pointsAUX = []		
	for i in range(0,len(pipesSelected)):
		if((pipesSelected[i].Location.Curve.Length/L)>int(pipesSelected[i].Location.Curve.Length/L)):
			t = int(pipesSelected[i].Location.Curve.Length/L) + 1
		else:
			t = int(pipesSelected[i].Location.Curve.Length/L)
		d = L *pipesSelected[i].Location.Curve.Direction
		for n in range(0,t):
			if(n ==0):
				continue
			else:
				pointsAUX.append(pipesSelected[i].Location.Curve.GetEndPoint(0) + n*d)
		points.append(pointsAUX)
		pointsAUX = []


	# Typical Transaction in Revit Python Shell / pyRevit
	doc = __revit__.ActiveUIDocument.Document
	transaction = Transaction(doc, 'Delete Object')
	transaction.Start()
	try:
		for t in range(0,len(pipesSelected),1):
			for i in range(0,len(points[t]),1):	
				dbPoint = points[t][i]
				pipe = pipesSelected[t]
				newPipeId = BreakCurve(doc, pipe.Id, dbPoint)
				newPipe = doc.GetElement(newPipeId)	
				
				if(P[0]!=''):
					for z in range(0,len(P)):
						newPipe.LookupParameter(P[z]).Set(str(pipe.LookupParameter(P[z]).AsString()))
						
				newPipeConnectors = newPipe.ConnectorManager.Connectors
				connA = None
				connB = None
				for c in pipe.ConnectorManager.Connectors:
					pc = c.Origin
					nearest = [x for x in newPipeConnectors if pc.DistanceTo(x.Origin) < 0.01]
					if nearest:
						connA = c
						connB = nearest[0]
				takeoff = doc.Create.NewUnionFitting(connA, connB)	
				
				if(P[0]!=''):
					for z in range(0,len(P)):
						takeoff.LookupParameter(P[z]).Set(str(pipe.LookupParameter(P[z]).AsString()))
						
	except:
		transaction.RollBack()
	else:
		transaction.Commit()

except:
	pass