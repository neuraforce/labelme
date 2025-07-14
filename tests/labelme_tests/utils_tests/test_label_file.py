import base64
import json
import numpy as np
from pathlib import Path
import PIL.Image

from labelme.label_file import LabelFile


def test_load_corrects_height_width(tmp_path: Path):
    # create simple image
    img = np.zeros((10, 20, 3), dtype=np.uint8)
    img_path = tmp_path / "test.png"
    PIL.Image.fromarray(img).save(img_path)

    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    data = {
        "version": "5.8.2",
        "imageData": img_b64,
        "imagePath": str(img_path.name),
        "shapes": [],
        "flags": {},
        "imageHeight": 1,
        "imageWidth": 1,
    }
    json_path = tmp_path / "test.json"
    with open(json_path, "w") as f:
        json.dump(data, f)

    lf = LabelFile(str(json_path))
    assert lf.imageHeight == 10
    assert lf.imageWidth == 20


def test_load_shapes(tmp_path: Path):
    data = {
        "shapes": [
            {
                "label": "cat",
                "points": [[0, 0], [1, 1]],
                "shape_type": "rectangle",
            }
        ]
    }
    json_path = tmp_path / "ann.json"
    with open(json_path, "w") as f:
        json.dump(data, f)

    shapes = LabelFile.load_shapes(str(json_path))
    assert shapes[0]["label"] == "cat"
    assert shapes[0]["points"] == [[0, 0], [1, 1]]
