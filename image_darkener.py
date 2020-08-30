import os
from PIL import Image


def create_darkened_picture(path):
    im = Image.open(path)
    # create new darkened image
    im2 = im.point(lambda p: p * 0.2)

    # save to new subfolder, 'darkened'
    new_path = f"{os.path.dirname(path)}/darkened/{os.path.basename(path)}"
    im2.save(new_path)


if __name__ == '__main__':
    pictures_dir = 'pictures/'

    files = [
        f for f in os.listdir(pictures_dir)
        if os.path.isfile(os.path.join(pictures_dir, f))
    ]

    for file in files:
        create_darkened_picture(f"{pictures_dir}{file}")
