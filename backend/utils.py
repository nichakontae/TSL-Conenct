import os
import shutil
import cv2
from PIL import Image

predict_classes = ["SaRaA", "SaRaAr", "SaRaAe", "Mo", "No", "O", "SaRaE"]
preprocess = ["main_model", "extend_model"]


def capture_window(frame, folder_name, img_name):
    base_folder = "pre_processing"

    # define filename for capture screen
    filename = f"./{base_folder}/{folder_name}/{img_name}.jpg"

    # capture screen
    cv2.imwrite(filename, frame)

    return filename


def crop_image(folder_name, filename, x1, y1, x2, y2, img_name):
    base_folder = "pre_processing"

    # crop image by coordinate
    img = Image.open(filename)
    img_res = img.crop((x1, y1, x2, y2))

    # if it is main_model just resize don't crop
    if folder_name == "main_model":
        img_res = img_res.resize((400, 300))

    # save image
    crop_filename = f"./{base_folder}/{folder_name}/crop-{img_name}.jpg"
    img_res.save(crop_filename)
    return crop_filename


def paste_image_on_white_bg(crop_filename, img_name, folder_name):
    base_folder = "pre_processing"

    # Opening the primary image (used in the background)
    image = Image.open("./white-bg.jpg").convert("RGBA")

    # Opening the secondary image (overlay image)
    overlay = Image.open(crop_filename).convert("RGBA")

    # paste crop img on white background with specific coordinate
    image.paste(overlay, (150, 35), overlay)

    # Save the resulting image to a file
    white_bg_img = f"./{base_folder}/{folder_name}/white-bg-{img_name}.png"
    image.save(white_bg_img)


def create_predict_folder(base_folder):
    # path exist or not
    if not os.path.exists(base_folder):
        os.mkdir(base_folder)
        print(f"Folder '{base_folder}' has been created.")

    if base_folder == "predict":
        for predict_class in predict_classes:
            path = os.path.join(base_folder, predict_class)
            if not os.path.exists(path):
                os.mkdir(path)
                print(f"Folder '{path}' has been created.")
    else:
        for pre in preprocess:
            path = os.path.join(base_folder, pre)
            if not os.path.exists(path):
                os.mkdir(path)
                print(f"Folder '{path}' has been created.")


def delete_predict_folder():
    shutil.rmtree("predict", ignore_errors=True)
    shutil.rmtree("pre_processing", ignore_errors=True)
