import json
import time

import numpy as np
import numpy.typing as npt
from loguru import logger

# Make osam and onnxruntime optional
OSAM_AVAILABLE = False
try:
    import osam
    OSAM_AVAILABLE = True
except ImportError:
    logger.warning("osam module not available. AI functions will be disabled.")
    # Define empty placeholder to avoid errors when osam is not available
    class DummyOsam:
        class types:
            class GenerateRequest:
                def __init__(self, **kwargs):
                    pass
                    
            class Prompt:
                def __init__(self, **kwargs):
                    pass
            
            class GenerateResponse:
                def __init__(self):
                    self.annotations = []
                    
        class apis:
            @staticmethod
            def generate(**kwargs):
                return DummyOsam.types.GenerateResponse()
                
            @staticmethod
            def non_maximum_suppression(**kwargs):
                return np.array([]), np.array([]), np.array([])
                
    # If osam is not available, use the dummy implementation
    if not OSAM_AVAILABLE:
        osam = DummyOsam()


def get_bboxes_from_texts(
    model: str, image: np.ndarray, texts: list[str]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    request: osam.types.GenerateRequest = osam.types.GenerateRequest(
        model=model,
        image=image,
        prompt=osam.types.Prompt(
            texts=texts,
            iou_threshold=1.0,
            score_threshold=0.01,
            max_annotations=1000,
        ),
    )
    logger.debug(
        f"Requesting with model={model!r}, image={(image.shape, image.dtype)}, "
        f"prompt={request.prompt!r}"
    )
    t_start: float = time.time()
    response: osam.types.GenerateResponse = osam.apis.generate(request=request)

    num_annotations: int = len(response.annotations)
    logger.debug(
        f"Response: num_annotations={num_annotations}, "
        f"elapsed_time={time.time() - t_start:.3f} [s]"
    )

    boxes: npt.NDArray[np.float32] = np.empty((num_annotations, 4), dtype=np.float32)
    scores: npt.NDArray[np.float32] = np.empty((num_annotations,), dtype=np.float32)
    labels: npt.NDArray[np.float32] = np.empty((num_annotations,), dtype=np.int32)
    for i, annotation in enumerate(response.annotations):
        boxes[i] = [
            annotation.bounding_box.xmin,
            annotation.bounding_box.ymin,
            annotation.bounding_box.xmax,
            annotation.bounding_box.ymax,
        ]
        scores[i] = annotation.score
        labels[i] = texts.index(annotation.text)

    return boxes, scores, labels


def nms_bboxes(
    boxes: np.ndarray,
    scores: np.ndarray,
    labels: np.ndarray,
    iou_threshold: float,
    score_threshold: float,
    max_num_detections: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    num_classes: int = max(labels) + 1
    scores_of_all_classes: npt.NDArray[np.float32] = np.zeros(
        (len(boxes), num_classes), dtype=np.float32
    )
    for i, (score, label) in enumerate(zip(scores, labels)):
        scores_of_all_classes[i, label] = score
    logger.debug(f"Input: num_boxes={len(boxes)}")
    boxes, scores, labels = osam.apis.non_maximum_suppression(
        boxes=boxes,
        scores=scores_of_all_classes,
        iou_threshold=iou_threshold,
        score_threshold=score_threshold,
        max_num_detections=max_num_detections,
    )
    logger.debug(f"Output: num_boxes={len(boxes)}")
    return boxes, scores, labels


def get_shapes_from_bboxes(
    boxes: np.ndarray, scores: np.ndarray, labels: np.ndarray, texts: list[str]
) -> list[dict]:
    shapes: list[dict] = []
    for box, score, label in zip(boxes.tolist(), scores.tolist(), labels.tolist()):
        text: str = texts[label]
        xmin, ymin, xmax, ymax = box
        shape: dict = {
            "label": text,
            "points": [[xmin, ymin], [xmax, ymax]],
            "group_id": None,
            "shape_type": "rectangle",
            "flags": {},
            "description": json.dumps(dict(score=score, text=text)),
        }
        shapes.append(shape)
    return shapes
