import io
import logging

from flask import Flask, request
from PIL import UnidentifiedImageError

from client import PlateClient
from models.plate_reader import PlateReader

app = Flask(__name__)
client = PlateClient("127.0.0.1:8080")
plate_reader = PlateReader.load_from_file("./model_weights/plate_reader_model.pth")


def run_model(im):
    try:
        res = plate_reader.read_text(im)
    except UnidentifiedImageError:
        return {"plate_number": "error"}, 404
    return {"plate_number": res}


@app.route("/read_plate", methods=["POST"])
def read_plate():
    """
    curl -X POST --data-binary
        @9965.jpg http://158.160.85.118:8080/read_plate
    """
    im = io.BytesIO(request.get_data())
    return run_model(im)


@app.route("/read_plate_by_id", methods=["GET"])
def read_plate_by_id():
    img_id = request.args.get("img_id", None)
    if (img_id is None) or (img_id.isdigit() is False):
        return {"plate_number": "error"}, 400
    res = client.get_remote_image(img_id)
    if isinstance(res, tuple):
        return {"plate_number": "error"}, res[1]
    return run_model(res)


@app.route("/read_plate_by_multiple_id", methods=["GET"])
def read_plate_by_multiple_id():
    img_ids = list(set(request.args.getlist("img_id", None)))
    if (
        (img_ids is None)
        or (img_ids == [None])
        or (max([i.isdigit() for i in img_ids]) == 0)
    ):
        # все id введены неверно (состоят не из цифр)
        return {k: "error" for k in img_ids}, 400

    result_dict = {}
    for img_id in img_ids:
        res = client.read_plate_by_id(img_id)
        if isinstance(res, tuple):
            res, _ = res
        plate_number = res["plate_number"]
        result_dict.update({img_id: plate_number})
    return result_dict


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(levelname)s] [%(asctime)s] %(message)s",
        level=logging.INFO,
    )

    app.json.ensure_ascii = False
    app.run(host="0.0.0.0", port=8080, debug=True)
