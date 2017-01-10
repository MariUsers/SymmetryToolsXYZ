#symmetryToolsXYZ_mari3.1.3
#By David Eschrich
#Updated by Antonio Neto


# This is world space only. But as long as your model is centered at origin and is either symmetrical on the x,y, or z axis then this will allow for symmetrical baking. 
# Paint on one side of your model and then bake with symmetry across the desired axis with the details being mirrored properly.
# The camera and buffer will return to it's initial position after the symmetry baking is complete.
# No need for taking the time to setup symmetrical uvs :)

# In the last version 3.0.1 this script would only work correctly if your projection Baking Behavior was set to "Manual" and Projection as "Front" 
# And your paint buffer set Reset on Bake to Disabled.
# After Antonio's update(v3.1.3) this is no longer a limitation.


# In addition you can just invert the canvas/buffer on any axis without baking by using keyboard shortcuts listed below or via the deTools menu.
# Apart from the deTools menu there is also a symmetry tools palette included with x,y,and z baking buttons
# The palette includes x,y,and z symmetry baking buttons with a menu to specify the buffer behavior after a symmetrical bake. It can be set to Auto or Manual Clear


# Baking Shortcuts:
# Shift+X
# Shift+Y
# Shift+Z

# Canvas Inversion Shortcuts:
# Crtl+Shift+X
# Crtl+Shift+Y
# Crtl+Shift+Z


# This has been tested on the most recent windows and linux versions of mari 3. Please let me know if you find any issues.


import mari
import PySide
core = PySide.QtCore
gui = PySide.QtGui
w = gui.QWidget()

global paintBuffer
paintBuffer = mari.canvases.paintBuffer()

global scaleFactor
scaleFactor = [-1,1]


#Function to flips the paintBuffer 
def paintBufferFlip(currentBufferScale, scaleFactor):
    scale = currentBufferScale
    inverseScale = core.QSizeF( scale.width() * scaleFactor[0], scale.height() * scaleFactor[1] )
    paintBuffer.setScale( inverseScale )

#Function to rotate the paintBuffer 
def paintBufferRotate(currentBufferRotation):
    rotation = currentBufferRotation
    paintBuffer.setRotation( 360-rotation )

#Function to translate the paintBuffer 
def paintBufferTranslation(currentBufferTranslation):
    translation = currentBufferTranslation
    paintBuffer.setTranslation(core.QPointF(-translation.x(), translation.y()))


#General Camera Inverse Function
def cameraInverse(AXIS):
    camera = mari.canvases.current().camera()

    lookAt = camera.lookAt()
    up = camera.up()
    translation = camera.translation()

    if AXIS == "X":
        camera.setTranslation( mari.VectorN(-translation.x(),translation.y(),translation.z()))
        camera.setUp( mari.VectorN(-up.x(),up.y(),up.z()))
        camera.setLookAt( mari.VectorN(-lookAt.x(),lookAt.y(),lookAt.z()))
    if AXIS == "Y":
        camera.setTranslation( mari.VectorN(translation.x(),-translation.y(),translation.z()))
        camera.setUp( mari.VectorN(up.x(),-up.y(),up.z()))
        camera.setLookAt( mari.VectorN(lookAt.x(),-lookAt.y(),lookAt.z()))
    if AXIS == "Z":
        camera.setTranslation( mari.VectorN(translation.x(),translation.y(),-translation.z()))
        camera.setUp( mari.VectorN(up.x(),up.y(),-up.z()))
        camera.setLookAt( mari.VectorN(lookAt.x(),lookAt.y(),-lookAt.z()))

    currentBufferTranslation = paintBuffer.translation()
    currentBufferRotation = paintBuffer.rotation()
    currentBufferScale = paintBuffer.scale()
    
    paintBufferFlip(currentBufferScale, scaleFactor)
    paintBufferRotate(currentBufferRotation)
    paintBufferTranslation(currentBufferTranslation)


def cameraInverseX():
    cameraInverse("X")

def cameraInverseY():
    cameraInverse("Y")

def cameraInverseZ():
    cameraInverse("Z")



#General Symmetry Bake Function
def symmetryBake(AXIS):
    n = comboSymmetryXYZ.currentIndex()
    
    tempPaint = paintBuffer.savePaint()
    currentBufferTranslation = paintBuffer.translation()
    currentBufferRotation = paintBuffer.rotation()
    currentBufferScale = paintBuffer.scale()
    
    #First Bake, the regular side that was painted.
    paintBuffer.bake()
    
    #Flip Camera, reload Paint from the Image Manager into the paintBuffer. Then Flip the paintBuffer, and adjust it's parameters.
    cameraInverse(AXIS)
    paintBuffer.loadPaint(tempPaint)
    paintBufferFlip(currentBufferScale, scaleFactor)
    paintBufferRotate(currentBufferRotation)
    paintBufferTranslation(currentBufferTranslation)
    #Memorize the paintBuffer parameters in order to set it to what it was before the second bake.
    currentBufferTranslation = paintBuffer.translation()
    currentBufferRotation = paintBuffer.rotation()
    currentBufferScale = paintBuffer.scale()
    #Second Bake, the Symmetry side that was not painted.
    paintBuffer.bake()
    
    #Reset the camera
    cameraInverse(AXIS)
    #If "Manually Clear Buffer" from the UI is selected the paintBuffer parameters will be restored to how it was before the first bake and the paint will not be cleared.
    if n == 1:
        paintBuffer.loadPaint(tempPaint)
        paintBufferFlip(currentBufferScale, scaleFactor)
        paintBufferRotate(currentBufferRotation)
        paintBufferTranslation(currentBufferTranslation)
    else:
        #"Auto Clear Buffer" UI will clear the paintBuffer paint and leave it's parameters with default values.
        paintBuffer.clear()
    #Remove the image from the Image Manager.
    mari.images.remove(mari.images.list()[-1])



def symmetryBakeX():
    #call a general function
    symmetryBake("X")

def symmetryBakeY():
    #call a general function
    symmetryBake("Y")

def symmetryBakeZ():
    #call a general function
    symmetryBake("Z")




#Mari UI Definitions.
pal = mari.palettes.create("Symmetry Tools",w)
pal.setBodyWidget(w)
pal.show()
gui = PySide.QtGui
dir(PySide)
layout = gui.QHBoxLayout()
w.setLayout(layout)

pbSymmetryX = gui.QPushButton("Bake X")
layout.addWidget(pbSymmetryX)

pbSymmetryY = gui.QPushButton("Bake Y")
layout.addWidget(pbSymmetryY)

pbSymmetryZ = gui.QPushButton("Bake Z")
layout.addWidget(pbSymmetryZ)



connect(pbSymmetryX.clicked, symmetryBakeX)
connect(pbSymmetryY.clicked, symmetryBakeY)
connect(pbSymmetryZ.clicked, symmetryBakeZ)

comboSymmetryXYZ = gui.QComboBox()
comboSymmetryXYZ.addItem("Auto Clear Buffer")
comboSymmetryXYZ.addItem("Manually Clear Buffer")
layout.addWidget(comboSymmetryXYZ)




#Mari custom shortcuts actions.
actionSymmetryBakeX = mari.actions.create( 'Bake Symmetry X', 'symmetryBakeX()' )
actionSymmetryBakeX.setShortcut("Shift+X")
mari.menus.addAction( actionSymmetryBakeX, "MainWindow/d&eTools/&Symmetry" )

actionSymmetryBakeY = mari.actions.create( 'Bake Symmetry Y', 'symmetryBakeY()' )
actionSymmetryBakeY.setShortcut("Shift+Y")
mari.menus.addAction( actionSymmetryBakeY, "MainWindow/d&eTools/&Symmetry" )

actionSymmetryBakeZ = mari.actions.create( 'Bake Symmetry Z', 'symmetryBakeZ()' )
actionSymmetryBakeZ.setShortcut("Shift+Z")
mari.menus.addAction( actionSymmetryBakeZ, "MainWindow/d&eTools/&Symmetry" )

actionCameraInverseX = mari.actions.create( 'Invert Canvas X', 'cameraInverseX()' )
actionCameraInverseX.setShortcut("Ctrl+Shift+X")
mari.menus.addAction( actionCameraInverseX, "MainWindow/d&eTools/&Symmetry" )

actionCameraInverseY = mari.actions.create( 'Invert Canvas Y', 'cameraInverseY()' )
actionCameraInverseY.setShortcut("Ctrl+Shift+Y")
mari.menus.addAction( actionCameraInverseY, "MainWindow/d&eTools/&Symmetry" )

actionCameraInverseZ = mari.actions.create( 'Invert Canvas Z', 'cameraInverseZ()' )
actionCameraInverseZ.setShortcut("Ctrl+Shift+Z")
mari.menus.addAction( actionCameraInverseZ, "MainWindow/d&eTools/&Symmetry" )