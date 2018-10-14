# -*- coding: utf-8 -*-
import face_recognition
import cv2

# 读取图片
img = face_recognition.load_image_file("/home/zq/Pictures/o_neo.jpg")
# 得到人脸坐标
face_locations = face_recognition.face_locations(img)
print(face_locations)

# 显示原始图片
img = cv2.imread("/home/zq/Pictures/o_neo.jpg")
cv2.namedWindow("original")
cv2.imshow("original", img)

# 遍历每个人脸
faceNum = len(face_locations)
for i in range(0, faceNum):
    top = face_locations[i][0]
    right = face_locations[i][1]
    bottom = face_locations[i][2]
    left = face_locations[i][3]

    start = (left, top)
    end = (right, bottom)
    color = (247, 230, 16)
    thickness = 2
    cv2.rectangle(img, start, end, color, thickness)

# 显示识别后的图片
cv2.namedWindow("recognition")
cv2.imshow("recognition", img)

cv2.waitKey(0)
cv2.destroyAllWindows()