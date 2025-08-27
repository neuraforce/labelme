import os
import sys
import types
from PyQt5 import QtGui, QtWidgets

# Ensure the repository root is on the path so that "import labelme" works
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import labelme.app
import labelme.utils


def test_rotate_image_preserves_color(tmp_path):
    # ensure headless operation
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    # create a simple image with known color
    image = QtGui.QImage(1, 1, QtGui.QImage.Format_ARGB32)
    image.setPixelColor(0, 0, QtGui.QColor(10, 20, 30, 255))

    # stub MainWindow attributes needed for rotateImage
    dummy = types.SimpleNamespace(
        image=image,
        imageData=b"",
        labelList=[],
        canvas=types.SimpleNamespace(
            loadPixmap=lambda *args, **kwargs: None,
            storeShapes=lambda *args, **kwargs: None,
        ),
        imagePath=str(tmp_path / "image.png"),
        setDirty=lambda: None,
        saveFile=lambda: None,
        paintCanvas=lambda: None,
    )

    # rotate clockwise
    labelme.app.MainWindow.rotateImage(dummy, clockwise=True)

    arr = labelme.utils.img_qt_to_arr(
        dummy.image.convertToFormat(QtGui.QImage.Format_RGB888)
    )
    assert arr[0, 0, :3].tolist() == [10, 20, 30]
