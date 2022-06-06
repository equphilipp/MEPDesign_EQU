# -*- coding: utf-8 -*-
""" Split ALL Pipes in current View by PipeType and distance."""

__title__ = 'Split all Pipes'
__author__ = 'André Rodrigues da Silva feat. Philipp'

from rpw import revit, db
from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, TextBox,Separator, Button, CheckBox)

from Autodesk.Revit.DB import Transaction

from Autodesk.Revit.DB.Plumbing.PlumbingUtils import BreakCurve 

from rpw.db.xyz import XYZ

try:
	doc = __revit__.ActiveUIDocument.Document
	
	pipes = db.Collector(view=doc.ActiveView, of_category='OST_PipeCurves',is_not_type=True)

	pipeTypes = []
	for i in range(0,len(pipes)):
		pipeTypes.append(pipes[i].Name)

	pipeTypes = list(dict.fromkeys(pipeTypes))
	pipeTypes = dict(zip(pipeTypes, pipeTypes))


	components = [Label('Rohrtyp:'),
				   ComboBox('PipeType', pipeTypes),
				   Label('Schusslänge (in Meter):'),
				   TextBox('distance', Text="3.0"),
				   Label('Längenparameter (nur falls nötig, trennen durch ","):'),
				   TextBox('parameters', Text=""),
				   Separator(),
				   Button('Ausführen')]
	form = FlexForm('Split all Pipes', components)
	form.show()

	typeSelected = form.values['PipeType']
	L = float(form.values['distance'])*3.28084
	P = form.values['parameters']
	P = P.split(",")
	
	# Pipes with the right type
	allDuctsSelected = []
	for i in range(0,len(pipes)):
		if(pipes[i].Name == typeSelected):
			allDuctsSelected.append(pipes[i])

	# Pipes longer than selected length
	ductsSelected = []

	for i in range(0,len(allDuctsSelected)):
		if(allDuctsSelected[i].Location.Curve.Length > L):
			ductsSelected.append(allDuctsSelected[i])

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
				pipe = ductsSelected[t]
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