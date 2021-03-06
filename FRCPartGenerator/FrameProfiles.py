
import adsk.core, adsk.fusion, adsk.cam, traceback
import json, os


def debugPrint(message):
	ui = adsk.core.Application.get().userInterface
	ui.messageBox(message)

def decodeProfile(dct):

	objtype = dct.get("objtype")
	if objtype == "HoleProfile":
		return HoleProfile(offset=dct["offset"], edgeDistance=dct["edgeDistance"], spacing=dct["spacing"], diameter=dct["diameter"])
	if objtype == "GenericFrameProfile":
		retval = FrameObject(width=dct["width"], height=dct["height"], wallThickness=dct["wallThickness"])
		retval.verticalHoles.extend(dct["verticalHoles"])
		retval.horizontalHoles.extend(dct["horizontalHoles"])
		retval.setId(dct["id"])
		return retval
	if objtype == "BoxTubeFrameProfile":
		retval = BoxTubing(width=dct["width"], height=dct["height"], wallThickness=dct["wallThickness"])
		retval.verticalHoles.extend(dct["verticalHoles"])
		retval.horizontalHoles.extend(dct["horizontalHoles"])
		retval.setId(dct["id"])
		return retval
	return dct


class HoleProfile():

	def __init__(self, offset=0, edgeDistance=0, spacing=0, diameter=0):
		self.objtype = "HoleProfile"
		self.offset = offset
		self.edgeDistance = edgeDistance
		self.spacing = spacing
		self.diameter = diameter


class FrameObject():

	def __init__(self, width=0, height=0, wallThickness=0):
		self.objtype = "GenericFrameProfile"
		self.verticalHoles = []
		self.horizontalHoles = []
		self.width = width
		self.height = height
		self.wallThickness = wallThickness
		self.id = ""

	def saveProfile(self, directory):
		jsonString = json.dumps(self, sort_keys=True, indent=4, separators=(',', ': '), default=lambda o: o.__dict__)

		output = open(os.path.join(directory, self.id + '.json'), 'w')
		output.writelines(jsonString)
		output.close()

	def setId(self, val):
		self.id = val


class BoxTubing(FrameObject):

	def __init__(self, width=0, height=0, wallThickness=0):
		super().__init__(width, height, wallThickness)
		self.objtype = "BoxTubeFrameProfile"

	def drawSketch(self, sketch):

		origin = adsk.core.Point3D.create(0, 0, 0)
				
		innerVertices = []
		outerVertices = []
		for i in range(0, 4):

			xSign = 1 - 2 * (((i + 1) % 4) // 2)
			ySign = 1 - 2 * (i // 2)

			outerVertex = adsk.core.Point3D.create(origin.x + xSign*(self.width/2.0), origin.y + ySign*(self.height/2.0), 0)
			outerVertices.append(outerVertex)

			innerVertex = adsk.core.Point3D.create(origin.x + xSign*(self.width/2.0 - self.wallThickness), origin.y + ySign*(self.height/2.0 - self.wallThickness), 0)
			innerVertices.append(innerVertex)
		
		for i in range(0, 4):
			sketch.sketchCurves.sketchLines.addByTwoPoints(outerVertices[(i+1) % 4], outerVertices[i])
			sketch.sketchCurves.sketchLines.addByTwoPoints(innerVertices[(i+1) % 4], innerVertices[i])

		profile = max(sketch.profiles, key=lambda prof : prof.boundingBox.maxPoint.x - prof.boundingBox.minPoint.x)

		return profile


def saveVersaframeProfiles(directory):

	profiles = []

	profile = BoxTubing(1*2.54, 2*2.54, 0.1*2.54)
	profile.verticalHoles.append(HoleProfile(0.5*2.54, 0.5*2.54, 1*2.54, 0.163*2.54))
	profile.setId('1 x 2 x 0.100 VersaFrame')
	profiles.append(profile)

	profile = BoxTubing(1*2.54, 2*2.54, 0.05*2.54)
	profile.verticalHoles.append(HoleProfile(0.5*2.54, 0.5*2.54, 1*2.54, 0.163*2.54))
	profile.setId('1 x 2 x 0.050 VersaFrame')
	profiles.append(profile)

	profile = BoxTubing(1*2.54, 1*2.54, 0.1*2.54)
	profile.horizontalHoles.append(HoleProfile(0.5*2.54, 0.5*2.54, 1*2.54, 0.163*2.54))
	profile.setId('1 x 1 x 0.100 VersaFrame')
	profiles.append(profile)

	profile = BoxTubing(1*2.54, 1*2.54, 0.04*2.54)
	profile.horizontalHoles.append(HoleProfile(0.5*2.54, 0.5*2.54, 1*2.54, 0.163*2.54))
	profile.verticalHoles.append(HoleProfile(0, 0.5*2.54, 1*2.54, 0.163*2.54))
	profile.setId('1 x 1 x 0.040 VersaFrame')
	profiles.append(profile)

	for prof in profiles:
		prof.saveProfile(directory)