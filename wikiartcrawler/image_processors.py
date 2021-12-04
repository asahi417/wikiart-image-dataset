import cv2
import mediapipe as mp
from itertools import chain

import numpy as np


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
    shape = cv2_image.shape
    results = mp.solutions.face_mesh.FaceMesh().process(cv2_image)
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


def get_face_information(image):
    co = get_face_landmark(cv2_image=image)
    if co is None:
        return None

    # eye line
    horizontal_face_vector = np.array(co['left_eye'][0]) - np.array(co['right_eye'][0])
    # angle between horizon and the eye line
    angle = int(get_angle(horizontal_face_vector))
    # rotate image to align the face
    image = rotate_image(image, co['face_center'][0], -1 * angle)
    # get facial landmark again based on fixed image
    co = get_face_landmark(cv2_image=image)
    if co is None:
        return None
    return angle, co


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


def fix_image_pipeline(image_path,
                       min_horizontal_distance: int = 15,
                       min_image_size: int = 200,
                       mirror_padding_size: int = 100,
                       facebox_margin_ratio: float = 0.3,
                       output_size: int = 128):
    img = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
    # get facial landmark
    feature = get_face_information(img)
    if feature is None:
        return None
    angle, co = feature

    def _image_transform(cv_img, pad: bool = False):
        if pad:
            # mirror padding
            cv_img = mirror_padding(cv_img, mirror_padding_size)
        # rotate image to align the face
        cv_img = rotate_image(cv_img, co['face_center'][0], -1 * angle)
        box = get_face_box(cv_img, margin_ratio=facebox_margin_ratio)
        if box is None:
            return None
        x, y, w, h = box
        assert w == h, '{} != {}'.format(w, h)
        # cropping image
        cv_img = cv_img[y:y + h, x:x + w]
        return cv_img

    img_no_pad = _image_transform(img)
    img_pad = _image_transform(img, pad=True)
    if img_no_pad is None and img_pad is None:
        return None
    if img_no_pad is not None and img_pad is not None:
        img = img_pad
    else:
        img = img_pad if img_no_pad is None else img_no_pad

    if img.size < min_image_size:
        return None

    # get facial landmark again based on fixed image (not padded)
    feature = get_face_information(img)
    if feature is None:
        return None
    co = feature[1]
    # horizontal distance between nose_center and face_center: detect the face is side or front
    dist = np.abs(co['nose_center'][0][0] - co['face_center'][0][0])
    if dist > min_horizontal_distance:
        return None
    img = cv2.resize(img, (output_size, output_size))
    return img

