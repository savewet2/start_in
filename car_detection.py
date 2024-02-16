# car_detection.py
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

class CarDetector:
    def __init__(self, model_path, label_map_path):
        self.load_model(model_path)
        self.load_label_map(label_map_path)

    def load_model(self, model_path):
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(model_path, 'rb') as fid:
                od_graph_def.ParseFromString(fid.read())
                tf.import_graph_def(od_graph_def, name='')

    def load_label_map(self, label_map_path):
        label_map = label_map_util.load_labelmap(label_map_path)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=90, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

    def detect_objects(self, image_np):
        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

        (boxes, scores, classes, num) = self.sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: tf.expand_dims(image_np, axis=0)})

        output_image = image_np.copy()
        vis_util.visualize_boxes_and_labels_on_image_array(
            output_image,
            boxes[0],
            classes[0].astype(int),
            scores[0],
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=8)

        return output_image
