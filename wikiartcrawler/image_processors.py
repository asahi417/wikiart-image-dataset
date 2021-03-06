import os
import logging
from itertools import chain

import cv2
import mediapipe as mp
import numpy as np
from PIL import Image

from .util import new_file_path
from .isr import ISRModel


CONNECTIONS = {
    "face_oval": (mp.solutions.face_mesh_connections.FACEMESH_FACE_OVAL, False),
    "face_center": (mp.solutions.face_mesh_connections.FACEMESH_FACE_OVAL, True),
    "left_eye": (mp.solutions.face_mesh_connections.FACEMESH_LEFT_EYE, True),
    "right_eye": (mp.solutions.face_mesh_connections.FACEMESH_RIGHT_EYE, True),
    "lips": (mp.solutions.face_mesh_connections.FACEMESH_LIPS, True)
}


def get_angle(a):
    b = [1, 0]
    unit_vector_1 = a / np.linalg.norm(a)
    unit_vector_2 = b / np.linalg.norm(b)
    return np.arccos(np.dot(unit_vector_1, unit_vector_2)) / np.pi * 180


def connections_to_positions(connections):
    return sorted(list(set(chain(*connections))))


def filtering_by_co(landmarks, coordinates):
    return [x for n, x in enumerate(landmarks) if n in coordinates]


def absolute_coordinate(landmarks, image_shape, average=True):
    co_x = []
    co_y = []
    for landmark in landmarks:
        co_x.append(int(landmark.x * image_shape[1]))
        co_y.append(int(landmark.y * image_shape[0]))
    if average:
        center_co_x = int(sum(co_x) / len(co_x))
        center_co_y = int(sum(co_y) / len(co_y))
        return [center_co_x], [center_co_y]
    return co_x, co_y


def get_face_landmark(image_path=None, cv2_image=None):
    if cv2_image is None:
        assert image_path is not None
        cv2_image = cv2.imread(image_path)
        cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    mp_face_mesh = mp.solutions.face_mesh
    shape = cv2_image.shape
    with mp_face_mesh.FaceMesh() as face_mesh:
        results = face_mesh.process(cv2_image)
        if results.multi_face_landmarks is None:
            return None

    lm = results.multi_face_landmarks[0].landmark
    cos = {}
    for key, (connections, average) in CONNECTIONS.items():
        position = connections_to_positions(connections)
        lm_filtered = filtering_by_co(lm, position)
        co = absolute_coordinate(lm_filtered, shape, average)
        cos[key] = list(zip(*co))
    cos['nose_center'] = [tuple((sum([np.array(cos[i][0]) for i in
                                      ['left_eye', 'right_eye', 'lips']]) / 3).astype(int).tolist())]
    return cos


def get_face_box(image, margin_ratio: float = 0.25):
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=3, minSize=(30, 30))
    if faces is None or len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    margin_x = int(w * margin_ratio)
    margin_y = int(h * margin_ratio)
    x, y, w, h = x - margin_x, y - margin_y, w + 2 * margin_x, h + 2 * margin_y
    if x <= 0 or y <= 0:
        return None
    return x, y, w, h


def rotate_image(image, center, angle):
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)


def mirror_padding(image, size: int):
    return cv2.copyMakeBorder(image, size, size, size, size, cv2.BORDER_REFLECT)


def get_face_angle(image):
    co = get_face_landmark(cv2_image=image)
    if co is None:
        return None

    # eye line
    horizontal_face_vector = np.array(co['left_eye'][0]) - np.array(co['right_eye'][0])
    # angle between horizon and the eye line
    angle = int(get_angle(horizontal_face_vector))
    return angle, co


def blur_image(image):
    w, h, _ = image.shape
    center = (int(w/2), int(h/2))
    blurred_img = cv2.GaussianBlur(image, (21, 21), 0, cv2.BORDER_REFLECT)
    mask = np.zeros((w, h, 3), dtype=np.uint8)
    mask = cv2.circle(mask, center, 100, (255, 255, 255), -1)
    out = np.where(mask == (255, 255, 255), image, blurred_img)
    return out


def get_face_image(
        image_path: str,
        export_path: str = None,
        export_dir: str = None,
        suffix: str = 'portrait',
        min_nose_face_distance: int = 20,
        min_image_size: int = None,
        mirror_padding_size: int = 100,
        facebox_margin_ratio: float = 0.3,
        output_size: int = 256,
        debug_mode: bool = False,
        overwrite: bool = False,
        isr_model=None,
        isr_model_name: str = 'noise-cancel'):
    """ Detect a human-face in the image, align the face angle, crop and super-resolution, to get the face image. """

    if isr_model is None:
        isr_model = ISRModel(isr_model_name)
    anchor_size = int(output_size / 2)
    if min_image_size is None:
        min_image_size = anchor_size

    def _get_face_image(_image_path):
        cv_img = cv2.cvtColor(cv2.imread(_image_path), cv2.COLOR_BGR2RGB)
        # get facial landmark
        feature = get_face_angle(cv_img)
        if feature is None:
            return None
        angle, co = feature
        # return none if face is not front
        dist = np.sum((np.array(co['nose_center'][0]) - np.array(co['face_center'][0])) ** 2) ** 0.5
        if dist > min_nose_face_distance:
            return None
        # mirror padding
        cv_img_pad = mirror_padding(cv_img, mirror_padding_size)
        center = co['face_center'][0]
        center_pad = [c + mirror_padding_size for c in center]
        # rotate image to align the face
        cv_img_ro = rotate_image(cv_img, center, -1 * angle)
        cv_img_pad_ro = rotate_image(cv_img_pad, center_pad, -1 * angle)
        # get square
        box = get_face_box(cv_img_ro, margin_ratio=facebox_margin_ratio)
        if box is None:
            return None
        x, y, w, h = box
        x_pad, y_pad = x + mirror_padding_size, y + mirror_padding_size
        assert w == h, '{} != {}'.format(w, h)
        # cropping image
        cv_img_crop = cv_img_pad_ro[y_pad:y_pad + h, x_pad:x_pad + w]
        if cv_img_crop.shape[0] >= output_size:
            cv_img_resize = cv2.resize(cv_img_crop, (output_size, output_size))
        else:
            # if the image is smaller than the output size, resize it as the half of the output size for ISR model
            if cv_img_crop.shape[0] < min_image_size:
                return None
            cv_img_resize = cv2.resize(cv_img_crop, (anchor_size, anchor_size))

        if debug_mode:
            cv_img_pad_copy = cv_img_pad.copy()
            cv_img_pad_ro_copy = cv_img_pad_ro.copy()
            for k, __co in co.items():
                color = (0, 0, 255) if k in ['face_oval', 'face_center'] else (0, 255, 0)
                for (x, y) in __co:
                    cv2.circle(cv_img_pad_copy,
                               (x + mirror_padding_size, y + mirror_padding_size),
                               radius=2,
                               color=color,
                               thickness=2)
                cv2.rectangle(cv_img_pad_ro_copy, (x_pad, y_pad), (x_pad + w, y_pad + h), (255, 0, 0), 2)
            return cv_img_resize, (cv_img_pad, cv_img_pad_copy, cv_img_pad_ro, cv_img_pad_ro_copy, cv_img_crop)
        del cv_img_pad
        del cv_img_pad_ro
        del cv_img_crop
        return cv_img_resize

    if export_path is None:
        export_path = new_file_path(image_path, suffix, export_dir)
    if os.path.exists(export_path) and not overwrite:
        logging.info('file exists {}'.format(export_path))
        return export_path
    try:
        cv_img_out = _get_face_image(image_path)
    except Exception:
        logging.exception('Error at _get_face_image')
        return None
    if cv_img_out is None:
        return None
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    if debug_mode:
        cv_img_out, sub = cv_img_out
        for _n, s in enumerate(sub):
            Image.fromarray(s).save(new_file_path(export_path, 'debug_{}'.format(_n), export_dir))
    assert cv_img_out.shape[0] in [output_size, anchor_size], cv_img_out.shape
    if cv_img_out.shape[0] == output_size:
        Image.fromarray(cv_img_out).save(export_path)
    else:
        pre_isr_image_path = new_file_path(export_path, 'pre_isr', export_dir)
        Image.fromarray(cv_img_out).save(pre_isr_image_path)
        isr_model.predict(pre_isr_image_path, export_path)
        if not debug_mode:
            os.remove(pre_isr_image_path)
    del cv_img_out
    return export_path
