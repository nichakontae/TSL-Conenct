import cv2
from cvzone.HandTrackingModule import HandDetector
import math
import datetime

current_datetime = datetime.datetime.now()
timestamp_str = current_datetime.strftime("%Y-%m-%d:%H-%M-%S")
null_fingers = [0, 1, 2, 3, 4, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20]



def close_hand_detection(img_name, model):
    # initial data
    confidence = "0.0"
    predict_class = ""
    crop_filename = f"./pre_processing/extend_model/white-bg-{img_name}.png"

    # read image
    img = cv2.imread(crop_filename)
    print("crop filename: ", crop_filename)

    # BGR 2 RGB
    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # this part don't understand as well - copy internet ;-;
    # Set flag
    image.flags.writeable = False

    # Set flag to true
    image.flags.writeable = True

    # RGB 2 BGR
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    # crop image

    # predict class base on image will use model.predict
    class_list = model.names
    result = model.predict(source=crop_filename, conf=0.4)

    # it will get only 1 result
    # check whether result exist or not
    if len(result[0].boxes) != 0:
        # collect class_name, conf
        # ตอนนี้คือเอาแค่ predict class, bounding box อิงจาก main_model
        box = result[0].boxes[0]
        cls = int(box.cls)
        confidence = math.ceil((box.conf[0] * 100)) / 100

        # init predict class
        predict_class = class_list[cls]
        if confidence >= class_conf_close.get(predict_class):
            result_filename = f"./predict/{img_name}/{predict_class}-{timestamp_str}.jpg"
            print("saving image on ", result_filename)
            cv2.imwrite(result_filename, image)
            print("save successfully...")
        return predict_class, confidence
    return "", 0


def hand_pose_detection(img_name):
    filename = f"./pre_processing/main_model/{img_name}.jpg"

    predict_class = ""
    saraa = "SaRaA"
    saraar = "SaRaAr"
    saraae = "SaRaAe"
    null = "null"

    # open_img = Image.open(filename)
    detector = HandDetector(detectionCon=0.1, maxHands=2)

    img = cv2.imread(filename)
    img = cv2.resize(img, (800, 800))

    # BGR 2 RGB
    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Set flag
    image.flags.writeable = False

    # Set flag to true
    image.flags.writeable = True

    # RGB 2 BGR
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Detection
    hands, img = detector.findHands(image, flipType=False)

    # Assign value of hand open
    open_hand = [0, 1, 1, 1]

    # Initial value
    hand1_coor = []
    hand2_coor = []
    is_hand1_open = False
    is_hand2_open = False

    # TODO knowledge need to know
    # it will switch hand if you rise one hand and then another hand
    # if rise left hand first and then right hand
    # hand1 will be right, hand2 will be left

    if hands:
        # Define hand1 result
        hand1 = hands[0]
        lmList1 = hand1["lmList"]  # list of 21 landmarks point
        bbox1 = hand1["bbox"]  # Bounding box info x,y,w,h
        centerPoint1 = hand1["center"]  # center of hand cx,cy
        handType1 = hand1["type"]  # Hand type Left or Right
        finger1 = detector.fingersUp(hand1)
        id = 0
        # Append hand1 coordinate
        for lm in lmList1:
            coor = lmList1[id][0], lmList1[id][1]
            hand1_coor.append(coor)
            id += 1

        # Check whether it's open hand or not
        if all(open_hand == finger1 for open_hand, finger1 in zip(open_hand, finger1)):
            predict_class = null

            # left bae -> front hand: thumb > pinky
            # right bae -> front hand: thumb < pinky
            if hand1_coor[4][0] < hand1_coor[20][0]:
                is_hand1_open = True
                print("right front hand")
        # Rise two hands
        if len(hands) == 2:
            # Define hand2 result
            hand2 = hands[1]
            lmList2 = hand2["lmList"]  # list of landmarks point
            bbox2 = hand2["bbox"]  # Bounding box info x,y,w,h
            centerPoint2 = hand2["center"]  # center of hand cx,cy
            handType2 = hand2["type"]
            id = 0
            # Append hand2 coordinate
            for lm in lmList2:
                coor = lmList2[id][0], lmList2[id][1]
                hand2_coor.append(coor)
                id += 1

            # Check whether it's open hand or not
            finger2 = detector.fingersUp(hand2)

            # AFTER this part, please open mediapipe package ควบคู่ to more understand

            # check whether it open-hand or not
            if all(open_hand == finger1 for open_hand, finger1 in zip(open_hand, finger1)):
                # init predict class to null first
                # จริงๆตรงนี้ใส่เป็น else ด้านล่างน่าจะดีว่า lol
                predict_class = null

                # check whether it is หน้ามือ or not
                if hand2_coor[4][0] > hand2_coor[20][0] or hand1_coor[4][0] > hand1_coor[20][0]:
                    is_hand1_open = True
                    print("left front hand")

            if all(open_hand == finger2 for open_hand, finger2 in zip(open_hand, finger2)):
                # init predict class to null first
                # จริงๆตรงนี้ใส่เป็น else ด้านล่างน่าจะดีว่า lol
                predict_class = null

                # check whether it is หน้ามือ or not
                if hand2_coor[4][0] > hand2_coor[20][0] or hand1_coor[4][0] > hand1_coor[20][0]:
                    is_hand2_open = True
                    print("right front hand")

            if is_hand1_open:
                # กางนิ้วก้อย
                if hand1_coor[17][1] >= hand1_coor[18][1] + 15 and hand1_coor[17][1] >= hand1_coor[19][1] + 15 and \
                        hand1_coor[17][
                            1] >= hand1_coor[20][1] + 15:
                    # Right hand open
                    print("hand1open")
                    # Detect SaRaA
                    if hand1_coor[8][0] - 20 < hand2_coor[8][0] < hand1_coor[8][0] + 20 and hand1_coor[8][1] - 20 < \
                            hand2_coor[8][1] < hand1_coor[8][1] + 20:
                        print("SaRaA")
                        predict_class = saraa

                    # Detect SaRaAe
                    if hand1_coor[16][0] - 20 < hand2_coor[8][0] < hand1_coor[16][0] + 20 and hand1_coor[16][1] - 20 < \
                            hand2_coor[8][1] < hand1_coor[16][1] + 20:
                        print("SaRaAe")
                        predict_class = saraae

                    # Detect SaRaAr
                    if hand1_coor[6][1] < hand2_coor[8][1] < hand1_coor[5][1] and (
                            hand1_coor[5][0] - 10 < hand2_coor[8][0] < hand1_coor[6][0] + 10 or hand1_coor[6][0] - 10 <
                            hand2_coor[8][0] < hand1_coor[5][0] + 10):
                        cv2.putText(image, "TSL: SaRaAr", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        print("SaRaAr")
                        predict_class = saraar

                    # Check if the x and y coordinates of the index finger are within +/- 10 of the thumb finger position
                    for null_finger in null_fingers:
                        if (
                                hand1_coor[null_finger][0] - 10 <= hand2_coor[8][0] <= hand1_coor[null_finger][0] + 10
                                and hand1_coor[null_finger][1] - 10 <= hand2_coor[8][1] <= hand1_coor[null_finger][
                            1] + 10
                        ):
                            predict_class = null
                            print("null")
                else:
                    # งอนิ้วก้อย
                    predict_class = null
            elif is_hand2_open:
                # กางนิ้วก้อย
                if hand2_coor[17][1] >= hand2_coor[18][1] + 15 and hand2_coor[17][1] >= hand2_coor[19][1] + 15 and \
                        hand2_coor[17][
                            1] >= hand2_coor[20][1] + 15:

                    # Left hand open
                    print("hand2open")
                    # Detect SaRaA
                    if hand2_coor[8][0] - 20 < hand1_coor[8][0] < hand2_coor[8][0] + 20 and hand2_coor[8][1] - 20 < \
                            hand1_coor[8][1] < hand2_coor[8][1] + 20:
                        print("SaRaA")
                        predict_class = saraa

                    # Detect SaRaAe
                    if hand2_coor[16][0] - 20 < hand1_coor[8][0] < hand2_coor[16][0] + 20 and hand2_coor[16][1] - 20 < \
                            hand1_coor[8][1] < hand2_coor[16][1] + 20:
                        print("SaRaAe")
                        predict_class = saraae

                    # Detect SaRaAr
                    if hand2_coor[6][1] < hand1_coor[8][1] < hand2_coor[5][1] and (
                            hand2_coor[5][0] - 10 < hand1_coor[8][0] < \
                            hand2_coor[6][0] + 10 or hand2_coor[6][0] - 10 < hand1_coor[8][0] < hand2_coor[5][0] + 10):
                        cv2.putText(image, "TSL: SaRaAr", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        print("SaRaAr")
                        predict_class = saraar

                    # Check if the x and y coordinates of the index finger are within +/- 10 of the thumb finger position
                    for null_finger in null_fingers:

                        if (
                                hand2_coor[null_finger][0] - 10 <= hand1_coor[8][0] <= hand2_coor[null_finger][0] + 10
                                and hand2_coor[null_finger][1] - 10 <= hand1_coor[8][1] <= hand2_coor[null_finger][
                            1] + 10
                        ):
                            predict_class = null
                            print("null")
                else:
                    # งอนิ้วก้อย
                    predict_class = null

        # show the backhand
        if not is_hand1_open and not is_hand2_open:
            predict_class = null

        # fail to predict 2 hand, it predicts just 1 hand
        if len(hands) == 1:
            predict_class = saraae

        # it not has any assign value
        if predict_class == "":
            predict_class = saraae

        # saving result
        # result_filename = f"./predict/{img_name}/{predict_class}_{timestamp_str}.jpg"
        # print("saving image on ", result_filename)
        # cv2.imwrite(result_filename, image)
        # print("save successfully...")

    return predict_class
