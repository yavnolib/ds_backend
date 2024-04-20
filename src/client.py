import io
import logging

import requests
from requests.adapters import HTTPAdapter, Retry


class PlateClient:
    def __init__(self, self_addr: str = "127.0.0.1:8080"):
        self.addr = self_addr
        self.path_plate = "read_plate"
        self.path_plate_id = "read_plate_by_id"
        self.path_plate_multiple_id = "read_plate_by_multiple_id"

        self.remote_path = "http://178.154.220.122:7777/images/"

        # create requests session with retry_limit
        self.s = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1)
        self.s.mount("http://", HTTPAdapter(max_retries=retries))

    def get_remote_image(self, img_id: int) -> bytes:
        """
        Used to allow the server to receive a remote image
        """
        r = self.s.get(self.remote_path + str(img_id), timeout=1)
        image, status = r.content, r.status_code
        if status >= 500:
            return {"plate_number": "error"}, status
        logging.info(f"{(self.remote_path + str(img_id))=}")
        return io.BytesIO(image)

    def read_plate_number(self, im: bytes) -> str:
        """
        Used to check the operation of the server by the image
        """
        res = self.s.post(
            f"http://{self.addr}/{self.path_plate}",
            data=im,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=2,
        )
        return res.json()

    def read_plate_by_id(self, img_id: int):
        """
        Used to check the operation of the server by id
        """
        res = self.s.get(
            f"http://{self.addr}/{self.path_plate_id}",
            params={"img_id": str(img_id)},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=2,
        )
        return res.json()

    def read_plate_by_multiple_id(self, img_ids: list[int]):
        if img_ids == []:
            img_ids = ""
        res = self.s.get(
            f"http://{self.addr}/{self.path_plate_multiple_id}",
            params={"img_id": img_ids},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=2,
        )
        return res.json()


if __name__ == "__main__":
    client = PlateClient()

    TEST_BY_ID = True
    TEST_MULTIPLE_ID = True
    if TEST_BY_ID:
        if TEST_MULTIPLE_ID:
            print(client.read_plate_by_multiple_id([9965, 1]))
            print(client.read_plate_by_multiple_id([]))
            print(client.read_plate_by_multiple_id([2, 1, 3]))
            print(client.read_plate_by_multiple_id([9965, 10022]))
        else:
            print(client.read_plate_by_id(9965))
    else:
        with open("../images/9965.jpg", "rb") as im:
            res = client.read_plate_number(im)
            print(res)
